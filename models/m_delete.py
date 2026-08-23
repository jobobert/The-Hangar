# -*- coding: utf-8 -*-
"""Guarded deletion for non-model inventory items.

Every `reference` field in this app defaults to ON DELETE CASCADE — pydal's
default, and no `ondelete=` is set anywhere in db.py. That makes a naive
delete dangerous, because three references sit on the PARENT side of a
cascade: db.model.transmitter, db.model.protocol and db.component.attr_protocol.
Deleting one transmitter or protocol row would take every model (and every
component) pointing at it along with it.

DELETE_RULES declares, per deletable table, what points at it and what should
happen to those rows. It is also the whitelist of what may be deleted at all.

Policies:
    'cascade'   delete the dependent row — a pure link row, nothing is lost
                beyond the association itself
    'destroy'   delete the dependent row, but it carries real data — the
                confirmation page calls these out separately and loudly
    'clear'     NULL the field and keep the row. This is what defuses the
                cascade landmines above
    'listclean' drop the id out of a list:reference column (no FK, so the
                database would otherwise leave a dangling id behind)
"""

DELETE_RULES = {
    'component':   [('model_component',    'component',     'cascade'),
                    ('eflite_time',        'motor',         'destroy')],
    'transmitter': [('model',              'transmitter',   'clear'),
                    ('transmitter_switch', 'transmitter',   'destroy')],
    'protocol':    [('model',              'protocol',      'clear'),
                    ('component',          'attr_protocol', 'clear'),
                    ('transmitter',        'protocol',      'listclean')],
    'tool':        [('model_tool',         'tool',          'cascade')],
    'battery':     [('model_battery',      'battery',       'cascade'),
                    ('eflite_time',        'battery',       'destroy')],
    'paint':       [('model_paint',        'paint',         'cascade')],
    'wtc':         [('model_wtc',          'wtc',           'cascade')],
    'tag':         [('article',            'tags',          'listclean')],
    # Leaf entities — nothing in the schema references them.
    'article':      [],
    'images':       [],
    'packingitems': [],
    'hardware':     [],
    'propeller':    [],
    'sailrig':      [],

    # --- Second hop. These tables are not deletable in their own right, but
    # they are reachable from one that is, and the walk below recurses through
    # them so the confirmation reports the full blast radius.
    # A model's switch assignment only exists to point at a transmitter's
    # switch, so removing the transmitter removes the assignment too.
    'transmitter_switch': [('model_switch',          'transmitter_switch', 'destroy')],
    'model_switch':       [('model_switch_position', 'model_switch',       'cascade')],
}

# The whitelist of what item/delete accepts, and where to return afterwards.
# Deliberately NOT the same as DELETE_RULES, which also carries second-hop
# tables that must never be deletable on their own.
DELETABLE = {
    'component':    ('component',   'listview'),
    'transmitter':  ('transmitter', 'listview'),
    'tool':         ('tool',        'listview'),
    'battery':      ('battery',     'listview'),
    'paint':        ('paint',       'listview'),
    'wtc':          ('wtc',         'listview'),
    'protocol':     ('protocol',    'listview'),
    'tag':          ('tag',         'listview'),
    'article':      ('library',     'index'),
    'images':       ('image',       'index'),
    'packingitems': ('packinglist', 'listview'),
    'hardware':     ('hardware',    'listview'),
    'propeller':    ('propeller',   'listview'),
    'sailrig':      ('sailrig',     'index'),
}

# Human wording for the impact summary.
TABLE_LABELS = {
    'model':              'models',
    'component':          'components',
    'model_component':    'model component links',
    'model_tool':         'model tool links',
    'model_battery':      'model battery links',
    'model_paint':        'model paint links',
    'model_wtc':          'model cylinder links',
    'eflite_time':           'flight-time records',
    'transmitter':           'transmitters',
    'transmitter_switch':    'transmitter switches',
    'model_switch':          'model switch assignments',
    'model_switch_position': 'switch positions',
    'article':               'library articles',
}

POLICY_HEADINGS = {
    'cascade':   'Links that will be removed',
    'destroy':   'Records that will be DELETED',
    'clear':     'References that will be cleared',
    'listclean': 'References that will be cleared',
}

# How many example rows to name on the confirmation page before summarising.
IMPACT_LABEL_LIMIT = 25


def deletable_tables():
    """Tables the guarded delete flow will accept."""
    return sorted(DELETABLE.keys())


def table_label(table):
    return TABLE_LABELS.get(table, table.replace('_', ' '))


def describe_row(table, row, prefer_model=True):
    """Human label for a row, safe against this schema's fragile format= lambdas.

    Several formats (db.tool, db.battery, db.hardware, model_wtc, model_switch)
    dereference a parent or concatenate a nullable column, so they raise on
    NULL or orphaned data — exactly the rows a delete-impact report deals with.

    prefer_model=False when describing the item being deleted: propeller,
    sailrig and hardware carry a `model` field of their own, and naming them
    after their owning model ("Deleted 'Test Model'" for a propeller) is wrong.
    """
    # Dependent rows are mostly model links, where the model's name is the
    # most useful thing to show, so prefer it there.
    if prefer_model and 'model' in db[table].fields and row.model:
        owner = db.model(row.model)
        if owner:
            return owner.name

    fmt = db[table]._format
    if fmt:
        try:
            return fmt(row) if callable(fmt) else fmt % row
        except Exception:
            pass

    for attr in ('name', 'item', 'todo'):
        if attr in db[table].fields and row[attr]:
            return row[attr]

    return '%s #%s' % (table_label(table).rstrip('s'), row.id)


def _dependent_set(dep_table, field, policy, ids):
    """The rows of dep_table whose `field` points at any of `ids`."""
    if not isinstance(ids, (list, tuple, set)):
        ids = [ids]
    ids = list(ids)

    if policy == 'listclean':
        # list:reference has no FK, so match on the serialised list contents.
        query = None
        for i in ids:
            clause = db[dep_table][field].contains(i)
            query = clause if query is None else (query | clause)
        return db(query)

    return db(db[dep_table][field].belongs(ids))


def _plan(table, row_id, _max_depth=6):
    """Walk the dependency graph and return the ordered steps a delete implies.

    Recursive, because some dependents have dependents of their own: deleting a
    transmitter removes its transmitter_switch rows, which removes the
    model_switch assignments pointing at them, which removes their positions.
    Reporting only the first hop would understate what is about to be lost.

    Each step is dict(table, field, policy, ids, rows, depth).
    """
    steps = []
    seen = set()

    def walk(src_table, ids, depth):
        if depth > _max_depth or not ids:
            return
        for dep_table, field, policy in DELETE_RULES.get(src_table, []):
            key = (src_table, dep_table, field)
            if key in seen:
                continue
            seen.add(key)

            rows = _dependent_set(dep_table, field, policy, ids).select()
            if not rows:
                continue

            steps.append(dict(table=dep_table, field=field, policy=policy,
                              ids=ids, rows=rows, depth=depth))

            # Only deletions propagate; clearing a field leaves the row alive.
            if policy in ('cascade', 'destroy'):
                walk(dep_table, [r.id for r in rows], depth + 1)

    walk(table, [row_id], 0)
    return steps


def delete_impact(table, row_id):
    """Read-only summary of what deleting this row would affect.

    Returns dict(label, groups, total, has_destroy) where each group is
    dict(policy, heading, table, table_label, count, labels, truncated).
    """
    row = db[table](row_id)
    groups = []
    total = 0
    has_destroy = False

    for step in _plan(table, row_id):
        rows = step['rows']
        total += len(rows)
        if step['policy'] == 'destroy':
            has_destroy = True

        groups.append(dict(
            policy=step['policy'],
            heading=POLICY_HEADINGS[step['policy']],
            table=step['table'],
            table_label=table_label(step['table']),
            count=len(rows),
            labels=[describe_row(step['table'], r) for r in rows[:IMPACT_LABEL_LIMIT]],
            truncated=len(rows) > IMPACT_LABEL_LIMIT,
        ))

    return dict(
        label=describe_row(table, row, prefer_model=False) if row else '',
        groups=groups,
        total=total,
        has_destroy=has_destroy,
    )


# Execution order. 'clear'/'listclean' must run before anything is deleted so
# the parent-side references are already NULL when the row goes — that is what
# stops SQLite's ON DELETE CASCADE from reaching db.model. Deletes then run
# deepest-first so children go before their parents.
_POLICY_ORDER = {'clear': 0, 'listclean': 1, 'cascade': 2, 'destroy': 2}


def perform_delete(table, row_id):
    """Delete a row and everything the plan says depends on it.

    Returns the impact summary computed before the deletion. The cascade
    deletes are issued explicitly rather than left to the database, so the
    action matches what the confirmation reported instead of depending on the
    connection's foreign_keys pragma.
    """
    steps = _plan(table, row_id)
    impact = delete_impact(table, row_id)

    steps.sort(key=lambda s: (_POLICY_ORDER[s['policy']], -s['depth']))

    for step in steps:
        policy, dep_table, field = step['policy'], step['table'], step['field']
        dep_set = _dependent_set(dep_table, field, policy, step['ids'])

        if policy == 'clear':
            dep_set.update(**{field: None})

        elif policy == 'listclean':
            drop = set(int(i) for i in step['ids'])
            for r in dep_set.select():
                kept = [v for v in (r[field] or []) if int(v) not in drop]
                r.update_record(**{field: kept})

        else:
            dep_set.delete()

    db(db[table].id == row_id).delete()
    return impact
