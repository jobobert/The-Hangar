# -*- coding: utf-8 -*-
import json

# Maps each lookup category to the data table(s) that store the name as a string field.
# Used for cascade rename and delete-usage checks.
LOOKUP_FIELD_MAP = {
    'articletype':                 [(db.article,        'articletype')],
    'modelcategory':               [(db.model,          'modelcategory'),
                                    (db.wishlist,       'modelcategory')],
    'modeltype':                   [(db.model,          'modeltype'),
                                    (db.wishlist,       'modeltype')],
    'modelorigin':                 [(db.model,          'modelorigin')],
    'controltype':                 [(db.model,          'controltype')],
    'powerplant':                  [(db.model,          'powerplant')],
    'attr_construction':           [(db.model,          'attr_construction')],
    'attr_copter_headtype':        [(db.model,          'attr_copter_headtype')],
    'attr_copter_tailrotor_drive': [(db.model,          'attr_copter_tailrotor_drive')],
    'subjecttype':                 [(db.model,          'subjecttype')],
    'attr_car_bodystyle':          [(db.model,          'attr_car_bodystyle')],
    'attr_car_drive':              [(db.model,          'attr_car_drive')],
    'attr_car_drivetrain':         [(db.model,          'attr_car_drivetrain')],
    'attr_sub_ballast':            [(db.model,          'attr_sub_ballast')],
    'activitytype':                [(db.activity,       'activitytype')],
    'attr_pump_type':              [(db.component,      'attr_pump_type')],
    'tooltype':                    [(db.tool,           'tooltype')],
    'attachmenttype':              [(db.attachment,     'attachmenttype')],
    'itemtype':                    [(db.packingitems,   'itemtype')],
    'hardwaretype':                [(db.hardware,       'hardwaretype')],
    'switchtype':                  [(db.switch,         'switchtype')],
    'pos':                         [(db.switch_position, 'pos')],
}


# Human-readable label for each category, derived from the DAL field definition.
CATEGORY_LABELS = {
    cat: tables[0][0][tables[0][1]].label
    for cat, tables in LOOKUP_FIELD_MAP.items()
    if tables
}

# Description for each category, from the DAL field's comment attribute.
CATEGORY_COMMENTS = {
    cat: (tables[0][0][tables[0][1]].comment or '')
    for cat, tables in LOOKUP_FIELD_MAP.items()
    if tables
}

# Overrides for table names that don't title-case cleanly.
_TABLE_NAME_OVERRIDES = {
    'packingitems': 'Packing Items',
}

def _table_display_name(tablename):
    return _TABLE_NAME_OVERRIDES.get(tablename, tablename.replace('_', ' ').title())


# ---------------------------------------------------------------------------
# Metadata editor helpers
# ---------------------------------------------------------------------------

# Card tab controllers available for model detail pages.
_CARD_CONTROLLERS = [
    'attachment', 'battery', 'component', 'diagram',
    'paint', 'propeller', 'rotor', 'sailrig',
    'supportitem', 'switch', 'tool', 'wtc',
]

# Categories that have structured metadata editors.
_METADATA_CATEGORIES = frozenset(['modeltype', 'modelcategory', 'activitytype'])

def _edge_options():
    """Return ordered list of edge type names from db.diagramedge."""
    return [r.name for r in db(db.diagramedge.id > 0).select(
        orderby=db.diagramedge.sort_order | db.diagramedge.name)]

def _parse_metadata(s):
    """Safely parse a JSON metadata string; returns {} on error or empty."""
    try:
        return json.loads(s or '{}')
    except (ValueError, TypeError):
        return {}


# Grouped model fields for the hide-fields editor.
_MODEL_FIELD_GROUPS = [
    ('General', [
        'modelorigin', 'description', 'notes', 'img', 'manufacturer',
        'kitnumber', 'kitlocation', 'subjecttype', 'attr_scale',
        'haveplans', 'havekit',
    ]),
    ('Control & Radio', [
        'controltype', 'powerplant', 'transmitter', 'protocol', 'configbackup',
    ]),
    ('Physical', [
        'attr_construction', 'attr_covering', 'attr_cog',
        'attr_length', 'attr_width', 'attr_height', 'attr_weight_oz', 'attr_flight_timer',
    ]),
    ('Airplane', [
        'attr_plane_rem_wings', 'attr_plane_rem_wing_tube', 'attr_plane_rem_struts',
        'attr_plane_wingspan_mm', 'attr_plane_wingarea',
        'attr_plane_throw_aileron', 'attr_plane_throw_elevator',
        'attr_plane_throw_rudder', 'attr_plane_throw_flap',
    ]),
    ('Helicopter / Gyro', [
        'attr_copter_headtype', 'attr_copter_mainrotor_length',
        'attr_copter_tailrotor_span', 'attr_copter_tailrotor_drive',
        'attr_copter_swashplate_type', 'attr_copter_size',
        'attr_copter_blade_count', 'attr_copter_tailrotor_blade_count',
    ]),
    ('Multirotor', ['attr_multi_rotor_count']),
    ('Rocket',    ['attr_rocket_parachute', 'attr_rocket_body_tube', 'attr_rocket_motors']),
    ('Boat / Submarine', ['attr_boat_draft', 'attr_sub_ballast']),
    ('Car / Vehicle', [
        'attr_car_scale', 'attr_car_drive', 'attr_car_drivetrain',
        'attr_car_bodystyle', 'attr_car_wheelbase',
    ]),
    ('Status & Notes', [
        'selected', 'final_disposition', 'final_value', 'fieldnotes', 'diagram',
    ]),
]

# Physical component attributes are universal — always shown for every component type.
_PHYSICAL_ATTRS = [
    'attr_length', 'attr_width', 'attr_height', 'attr_weight_oz',
    'attr_travel', 'attr_model_scale',
]

# Grouped component attr_ fields for the per-type attrs editor (physical excluded — always shown).
_COMPONENT_ATTR_GROUPS = [
    ('Electrical', [
        'attr_voltage_in', 'attr_voltage_out',
        'attr_amps_in', 'attr_amps_out',
        'attr_watts_in', 'attr_watts_out',
    ]),
    ('Motor / Engine', [
        'attr_displacement_cc', 'attr_motor_kv', 'attr_num_turns',
        'attr_gear_type', 'attr_torque',
    ]),
    ('Radio / Digital', [
        'attr_channel_count', 'attr_protocol',
        'attr_telemetry_port', 'attr_sbus_port', 'attr_pwr_port',
        'attr_firmware_version',
    ]),
    ('Pump & Switch', ['attr_pump_type', 'attr_switch_type']),
]


def _grouped_options(groups, table):
    """Return [(group_name, [(fieldname, label), ...]), ...] from a group spec and a DAL table."""
    return [
        (group_name, [(f, table[f].label) for f in fields if f in table.fields])
        for group_name, fields in groups
        if any(f in table.fields for f in fields)
    ]


def _model_hide_options():
    return _grouped_options(_MODEL_FIELD_GROUPS, db.model)


def _component_attr_options():
    return _grouped_options(_COMPONENT_ATTR_GROUPS, db.component)


def _physical_attr_options():
    """Return [(fieldname, label)] for the always-shown physical attrs."""
    return [(f, db.component[f].label) for f in _PHYSICAL_ATTRS if f in db.component.fields]


def _build_metadata_json(category, post_vars):
    """Build a JSON metadata string from the category-specific POST vars."""
    if category == 'modeltype':
        return json.dumps({
            'hide':        post_vars.getlist('meta_hide')        or [],
            'controllers': post_vars.getlist('meta_controllers') or [],
            'important':   post_vars.getlist('meta_important')   or [],
        })
    elif category == 'modelcategory':
        return json.dumps({
            'hide':        post_vars.getlist('meta_hide')        or [],
            'controllers': post_vars.getlist('meta_controllers') or [],
            'important':   post_vars.getlist('meta_important')   or [],
        })
    elif category == 'chemistry':
        try:
            volt = float(post_vars.get('meta_volt') or 3.7)
        except (ValueError, TypeError):
            volt = 3.7
        return json.dumps({'volt': volt})
    elif category == 'activitytype':
        return json.dumps({'color': (post_vars.get('meta_color') or '').strip()})
    return None


def _build_meta_config(category, meta):
    """Build the template context dict for a category's metadata editor."""
    if category in ('modeltype', 'modelcategory'):
        hide_set = set(meta.get('hide', []))
        hide_groups = [
            (grp, [(f, lbl, f in hide_set) for f, lbl in fields])
            for grp, fields in _model_hide_options()
        ]
        ctrl_set = set(meta.get('controllers', []))
        imp_set = set(meta.get('important', []))
        imp_groups = [
            (grp, [(f, lbl, f in imp_set) for f, lbl in fields])
            for grp, fields in _model_hide_options()
        ]
        return {
            'type':        category,
            'hide_groups': hide_groups,
            'controllers': [(c, c in ctrl_set) for c in _CARD_CONTROLLERS],
            'imp_groups':  imp_groups,
        }
    elif category == 'chemistry':
        return {'type': 'chemistry', 'volt': meta.get('volt', 3.7)}
    elif category == 'activitytype':
        return {'type': 'activitytype', 'color': meta.get('color', '')}
    return None


def _usage_count(category, name):
    """Return the total number of data rows that carry this name."""
    return sum(
        db(tbl[field] == name).count()
        for tbl, field in LOOKUP_FIELD_MAP.get(category, [])
    )


def _cascade_rename(category, old_name, new_name):
    """Bulk-update all data rows from old_name → new_name for this category."""
    for tbl, field in LOOKUP_FIELD_MAP.get(category, []):
        db(tbl[field] == old_name).update(**{field: new_name})


def index():
    session.ReturnHere = URL(args=request.args, vars=request.get_vars, host=True)

    # Value counts per category from DB
    count_rows = db(db.lookup.id > 0).select(
        db.lookup.category,
        db.lookup.id.count().with_alias('value_count'),
        groupby=db.lookup.category,
    )
    counts = {r.lookup.category: r['value_count'] for r in count_rows}

    # Group categories by their primary table
    table_groups = {}
    for cat, tables in LOOKUP_FIELD_MAP.items():
        if not tables:
            continue
        tablename = tables[0][0]._tablename
        if tablename not in table_groups:
            table_groups[tablename] = []
        _priority = cat in ('modeltype', 'modelcategory')
        table_groups[tablename].append(dict(
            cat=cat,
            label=CATEGORY_LABELS.get(cat, cat),
            comment=CATEGORY_COMMENTS.get(cat, ''),
            count=counts.get(cat, 0),
            priority=_priority,
        ))

    # Sort categories within each table: priority first, then alphabetical
    for cats in table_groups.values():
        cats.sort(key=lambda x: (not x['priority'], x['label']))
    groups = sorted(
        [(_table_display_name(t), cats) for t, cats in table_groups.items()],
        key=lambda x: x[0]
    )

    ct_count   = db(db.componenttype.id > 0).count()
    de_count   = db(db.diagramedge.id > 0).count()
    chem_count = db(db.chemistry.id > 0).count()
    return dict(groups=groups, ct_count=ct_count, de_count=de_count, chem_count=chem_count)


def category():
    cat = request.args(0) or redirect(URL('admin', 'index'))
    session.ReturnHere = URL(args=request.args, vars=request.get_vars, host=True)

    rows = db(db.lookup.category == cat).select(
        orderby=db.lookup.sort_order | db.lookup.name
    )
    label = CATEGORY_LABELS.get(cat, cat)
    cat_comment = CATEGORY_COMMENTS.get(cat, '')
    tables = LOOKUP_FIELD_MAP.get(cat, [])
    table_name = _table_display_name(tables[0][0]._tablename) if tables else ''
    rows_with_counts = [(row, _usage_count(cat, row.name)) for row in rows]
    return dict(category=cat, label=label, cat_comment=cat_comment,
                table_name=table_name, rows_with_counts=rows_with_counts)


def update():
    lookup_id = VerifyTableID('lookup', request.args(0)) if request.args(0) else None
    old_row = db.lookup(lookup_id) if lookup_id else None
    old_name = old_row.name if old_row else None
    old_category = old_row.category if old_row else request.vars.category

    # Block renaming a system value
    if (old_row and old_row.is_system
            and request.vars.name
            and request.vars.name != old_name):
        response.flash = "Cannot rename a system value"
        form = SQLFORM(db.lookup, old_row, showid=False, deletable=False,
                       fields=['name', 'sort_order', 'is_system'])
        disable_autocomplete(form)
        meta_config = _build_meta_config(old_category, _parse_metadata(old_row.metadata))
        return dict(form=form, old_row=old_row, meta_config=meta_config)

    # Auto sort_order and category default for new rows
    if not lookup_id and old_category:
        max_order = db(db.lookup.category == old_category).select(
            db.lookup.sort_order.max()).first()[db.lookup.sort_order.max()] or 0
        db.lookup.sort_order.default = max_order + 1
        db.lookup.category.default = old_category

    # Pre-build metadata JSON from custom POST vars
    metadata_json = None
    if request.post_vars and old_category in _METADATA_CATEGORIES:
        metadata_json = _build_metadata_json(old_category, request.post_vars)

    form = SQLFORM(db.lookup, old_row, showid=False, deletable=False,
                   fields=['name', 'sort_order', 'is_system'])
    disable_autocomplete(form)

    if form.process().accepted:
        new_name = form.vars.name
        if old_name and new_name and old_name != new_name:
            _cascade_rename(old_category, old_name, new_name)
        if metadata_json is not None:
            db(db.lookup.id == (lookup_id or form.vars.id)).update(metadata=metadata_json)
        session.flash = "Saved"
        redirect(URL('admin', 'category', args=[old_category]))
    elif form.errors:
        response.flash = "Please correct the errors below"

    existing_meta = _parse_metadata(old_row.metadata if old_row else None)
    meta_config = _build_meta_config(old_category, existing_meta)

    return dict(form=form, old_row=old_row, meta_config=meta_config)


def delete():
    lookup_id = VerifyTableID('lookup', request.args(0))
    if not lookup_id:
        session.flash = "Invalid lookup entry"
        redirect(URL('admin', 'index'))

    row = db.lookup(lookup_id)
    if not row:
        session.flash = "Lookup entry not found"
        redirect(URL('admin', 'index'))

    if row.is_system:
        session.flash = "Cannot delete a system value"
        redirect(URL('admin', 'category', args=[row.category]))

    count = _usage_count(row.category, row.name)
    if count > 0:
        session.flash = "Value '%s' is in use (%d record%s). Use Replace to reassign first." % (
            row.name, count, 's' if count != 1 else '')
        redirect(URL('admin', 'replace', args=[lookup_id]))

    db(db.lookup.id == lookup_id).delete()
    session.flash = "Deleted '%s'" % row.name
    redirect(URL('admin', 'category', args=[row.category]))


def replace():
    lookup_id = VerifyTableID('lookup', request.args(0))
    if not lookup_id:
        session.flash = "Invalid lookup entry"
        redirect(URL('admin', 'index'))

    row = db.lookup(lookup_id)
    if not row:
        session.flash = "Lookup entry not found"
        redirect(URL('admin', 'index'))

    if row.is_system:
        session.flash = "Cannot delete a system value"
        redirect(URL('admin', 'category', args=[row.category]))

    # Other names in the same category
    others = db((db.lookup.category == row.category) &
                (db.lookup.id != lookup_id)).select(
        orderby=db.lookup.sort_order | db.lookup.name)
    other_names = [r.name for r in others]

    if not other_names:
        session.flash = "No replacement values available — add another value first"
        redirect(URL('admin', 'category', args=[row.category]))

    replace_form = SQLFORM.factory(
        Field('replacement', type='string', label='Replace with',
              requires=IS_IN_SET(other_names, zero='-- choose --')),
        submit_button='Replace & Delete',
    )

    add_form = SQLFORM.factory(
        Field('new_name', type='string', label='New value',
              requires=IS_NOT_EMPTY()),
        submit_button='Add',
    )

    count = _usage_count(row.category, row.name)

    if replace_form.process(session=None, formname='replace').accepted:
        _cascade_rename(row.category, row.name, replace_form.vars.replacement)
        db(db.lookup.id == lookup_id).delete()
        session.flash = "Replaced '%s' → '%s' and deleted" % (row.name, replace_form.vars.replacement)
        redirect(URL('admin', 'category', args=[row.category]))
    elif replace_form.errors:
        response.flash = "Please select a replacement value"

    if add_form.process(session=None, formname='add_new').accepted:
        next_order = (db(db.lookup.category == row.category).select(
            db.lookup.sort_order.max()).first()[db.lookup.sort_order.max()] or 0) + 1
        db.lookup.insert(category=row.category, name=add_form.vars.new_name,
                         sort_order=next_order, is_system=False)
        session.flash = "Added '%s' — now select it as the replacement" % add_form.vars.new_name
        redirect(URL('admin', 'replace', args=[lookup_id]))

    return dict(row=row, replace_form=replace_form, add_form=add_form, count=count)


# ---------------------------------------------------------------------------
# Component Type admin (dedicated table — not lookup-based)
# ---------------------------------------------------------------------------

def componenttype_list():
    session.ReturnHere = URL(args=request.args, vars=request.get_vars, host=True)
    rows = db(db.componenttype.id > 0).select(
        orderby=db.componenttype.sort_order | db.componenttype.name)
    rows_with_counts = [
        (row, db(db.component.componenttype == row.name).count())
        for row in rows
    ]
    return dict(rows_with_counts=rows_with_counts)


def componenttype_update():
    ct_id = VerifyTableID('componenttype', request.args(0)) if request.args(0) else None
    old_row = db.componenttype(ct_id) if ct_id else None

    # Auto sort_order for new rows
    if not ct_id:
        _max = db(db.componenttype.id > 0).select(
            db.componenttype.sort_order.max()
        ).first()[db.componenttype.sort_order.max()] or 0
        db.componenttype.sort_order.default = _max + 1

    # Block renaming system values
    if old_row and old_row.is_system and request.vars.name and request.vars.name != old_row.name:
        response.flash = "Cannot rename a system value"

    else:
        # Collect custom POST vars (attrs + diagram fields handled outside SQLFORM)
        extra = None
        if request.post_vars:
            extra = dict(
                attrs              = request.post_vars.getlist('meta_attrs') or [],
                diagram_shape      = (request.post_vars.get('meta_diagram_shape') or '').strip(),
                diagram_color      = (request.post_vars.get('meta_diagram_color') or '#efefef').strip(),
                diagram_edgeattrib = (request.post_vars.get('meta_diagram_edgeattrib') or 'default').strip(),
            )

        form = SQLFORM(db.componenttype, old_row, showid=False, deletable=False,
                       fields=['name', 'sort_order', 'is_system'])
        disable_autocomplete(form)

        if form.process().accepted:
            if old_row and old_row.name != form.vars.name:
                db(db.component.componenttype == old_row.name).update(
                    componenttype=form.vars.name)
            if extra is not None:
                db(db.componenttype.id == (ct_id or form.vars.id)).update(**extra)
            session.flash = "Saved"
            redirect(URL('admin', 'componenttype_list'))
        elif form.errors:
            response.flash = "Please correct the errors below"

    form = SQLFORM(db.componenttype, old_row, showid=False, deletable=False,
                   fields=['name', 'sort_order', 'is_system'])
    disable_autocomplete(form)

    _attrs_set = set(old_row.attrs or []) if old_row else set()
    attr_groups = [
        (grp, [(f, lbl, f in _attrs_set) for f, lbl in flds])
        for grp, flds in _component_attr_options()
    ]
    _opts = _edge_options()
    _ea = {r.name: r.dot_attribs for r in db(db.diagramedge.id > 0).select()}
    return dict(
        form=form,
        old_row=old_row,
        attr_groups=attr_groups,
        physical_attrs=_physical_attr_options(),
        edge_options=_opts,
        edge_attribs_json=json.dumps(_ea),
        diagram_shape=old_row.diagram_shape if old_row else '',
        diagram_color=old_row.diagram_color if old_row else '#efefef',
        diagram_edgeattrib=old_row.diagram_edgeattrib if old_row else 'default',
    )


def componenttype_delete():
    ct_id = VerifyTableID('componenttype', request.args(0))
    if not ct_id:
        session.flash = "Invalid component type"
        redirect(URL('admin', 'componenttype_list'))

    row = db.componenttype(ct_id)
    if not row:
        session.flash = "Component type not found"
        redirect(URL('admin', 'componenttype_list'))

    if row.is_system:
        session.flash = "Cannot delete a system value"
        redirect(URL('admin', 'componenttype_list'))

    count = db(db.component.componenttype == row.name).count()
    if count > 0:
        session.flash = "Type '%s' is in use (%d component%s). Reassign first." % (
            row.name, count, 's' if count != 1 else '')
        redirect(URL('admin', 'componenttype_list'))

    db(db.componenttype.id == ct_id).delete()
    session.flash = "Deleted '%s'" % row.name
    redirect(URL('admin', 'componenttype_list'))


# ---------------------------------------------------------------------------
# Diagram Edge Types
# ---------------------------------------------------------------------------

def diagramedge_list():
    rows = db(db.diagramedge.id > 0).select(orderby=db.diagramedge.sort_order | db.diagramedge.name)
    return dict(rows=rows)


def diagramedge_update():
    de_id = VerifyTableID('diagramedge', request.args(0)) if request.args(0) else None
    old_row = db.diagramedge(de_id) if de_id else None

    if not de_id:
        _max = db(db.diagramedge.id > 0).select(
            db.diagramedge.sort_order.max()
        ).first()[db.diagramedge.sort_order.max()] or 0
        db.diagramedge.sort_order.default = _max + 1

    form = SQLFORM(db.diagramedge, old_row, showid=False, deletable=False,
                   fields=['name', 'dot_attribs', 'sort_order'])
    disable_autocomplete(form)

    if form.process().accepted:
        session.flash = "Saved"
        redirect(URL('admin', 'diagramedge_list'))
    elif form.errors:
        response.flash = "Please correct the errors below"

    return dict(form=form, old_row=old_row)


def diagramedge_delete():
    de_id = VerifyTableID('diagramedge', request.args(0))
    if not de_id:
        session.flash = "Invalid edge type"
        redirect(URL('admin', 'diagramedge_list'))

    row = db.diagramedge(de_id)
    if not row:
        session.flash = "Edge type not found"
        redirect(URL('admin', 'diagramedge_list'))

    in_use = db(db.componenttype.diagram_edgeattrib == row.name).count()
    if in_use > 0:
        session.flash = "Edge type '%s' is used by %d component type%s. Reassign first." % (
            row.name, in_use, 's' if in_use != 1 else '')
        redirect(URL('admin', 'diagramedge_list'))

    db(db.diagramedge.id == de_id).delete()
    session.flash = "Deleted '%s'" % row.name
    redirect(URL('admin', 'diagramedge_list'))


# ---------------------------------------------------------------------------
# Battery Chemistries
# ---------------------------------------------------------------------------

def chemistry_list():
    rows = db(db.chemistry.id > 0).select(orderby=db.chemistry.sort_order | db.chemistry.name)
    return dict(rows=rows)


def chemistry_update():
    chem_id = VerifyTableID('chemistry', request.args(0)) if request.args(0) else None
    old_row = db.chemistry(chem_id) if chem_id else None

    if not chem_id:
        _max = db(db.chemistry.id > 0).select(
            db.chemistry.sort_order.max()
        ).first()[db.chemistry.sort_order.max()] or 0
        db.chemistry.sort_order.default = _max + 1

    form = SQLFORM(db.chemistry, old_row, showid=False, deletable=False,
                   fields=['name', 'volt', 'sort_order'])
    disable_autocomplete(form)

    if form.process().accepted:
        if old_row and form.vars.name != old_row.name:
            db(db.battery.chemistry == old_row.name).update(chemistry=form.vars.name)
        session.flash = "Saved"
        redirect(URL('admin', 'chemistry_list'))
    elif form.errors:
        response.flash = "Please correct the errors below"

    return dict(form=form, old_row=old_row)


def chemistry_delete():
    chem_id = VerifyTableID('chemistry', request.args(0))
    if not chem_id:
        session.flash = "Invalid chemistry"
        redirect(URL('admin', 'chemistry_list'))

    row = db.chemistry(chem_id)
    if not row:
        session.flash = "Chemistry not found"
        redirect(URL('admin', 'chemistry_list'))

    count = db(db.battery.chemistry == row.name).count()
    if count > 0:
        session.flash = "Chemistry '%s' is used by %d batter%s. Reassign first." % (
            row.name, count, 'ies' if count != 1 else 'y')
        redirect(URL('admin', 'chemistry_list'))

    db(db.chemistry.id == chem_id).delete()
    session.flash = "Deleted '%s'" % row.name
    redirect(URL('admin', 'chemistry_list'))


# ---------------------------------------------------------------------------
# Controller Matrix (read-only reference view)
# ---------------------------------------------------------------------------

def controller_matrix():
    mt_rows = db(db.lookup.category == 'modeltype').select(
        orderby=db.lookup.sort_order | db.lookup.name)
    cat_rows = db(db.lookup.category == 'modelcategory').select(
        orderby=db.lookup.sort_order | db.lookup.name)

    # Flat field → label lookup from grouped model field definitions.
    field_labels = {
        f: db.model[f].label
        for group_name, fields in _MODEL_FIELD_GROUPS
        for f in fields
        if f in db.model.fields
    }

    categories = []
    for r in cat_rows:
        m = _parse_metadata(r.metadata)
        categories.append({
            'name':        r.name,
            'controllers': set(m.get('controllers', [])),
            'hide':        set(m.get('hide', [])),
            'important':   set(m.get('important', [])),
        })

    rows = []
    for r in mt_rows:
        m = _parse_metadata(r.metadata)
        mt_ctrl      = set(m.get('controllers', [])) or _ALL_CONTROLLERS
        mt_hide      = set(m.get('hide', []))
        mt_important = set(m.get('important', []))
        cells = []
        for cat in categories:
            cat_hide = cat['hide']
            all_hide = mt_hide | cat_hide
            hidden = []
            for f in sorted(all_hide):
                if f in mt_hide and f in cat_hide:
                    src = 'both'
                elif f in mt_hide:
                    src = 'type'
                else:
                    src = 'cat'
                hidden.append((f, field_labels.get(f, f), src))
            # Important = intersection of type important and category important
            important = sorted(
                mt_important & cat['important'],
                key=lambda f: field_labels.get(f, f)
            )
            important_labeled = [(f, field_labels.get(f, f)) for f in important]
            cells.append({
                'controllers': sorted(mt_ctrl & cat['controllers']),
                'hidden':      hidden,
                'important':   important_labeled,
            })
        rows.append({'name': r.name, 'cells': cells})

    return dict(rows=rows, categories=categories,
                all_controllers=sorted(_ALL_CONTROLLERS))


# ---------------------------------------------------------------------------
# Component Attributes Matrix (read-only reference view)
# ---------------------------------------------------------------------------

def component_matrix():
    ct_rows = db(db.componenttype.id > 0).select(
        orderby=db.componenttype.sort_order | db.componenttype.name)

    # Build flat ordered list of (fieldname, label) for all non-physical attrs.
    all_attrs = []
    seen = set()
    for _grp, _fields in _COMPONENT_ATTR_GROUPS:
        for f in _fields:
            if f not in seen and f in db.component.fields:
                all_attrs.append((f, db.component[f].label))
                seen.add(f)

    physical = _physical_attr_options()

    rows = []
    for r in ct_rows:
        attrs_set = set(r.attrs or [])
        cells = [(f, f in attrs_set) for f, _lbl in all_attrs]
        rows.append({'name': r.name, 'is_system': r.is_system, 'cells': cells})

    return dict(rows=rows, all_attrs=all_attrs, physical_attrs=physical)


# ---------------------------------------------------------------------------
# Data Integrity Report
# ---------------------------------------------------------------------------

def integrity_report():
    # Build field label lookup
    field_labels = {
        f: db.model[f].label
        for grp, fields in _MODEL_FIELD_GROUPS
        for f in fields
        if f in db.model.fields
    }

    # Gather important field sets per modeltype and modelcategory.
    # Effective important fields = modeltype.important ∩ modelcategory.important
    mt_important = {}
    for r in db(db.lookup.category == 'modeltype').select():
        m = _parse_metadata(r.metadata)
        mt_important[r.name] = set(m.get('important', []))

    cat_important = {}
    for r in db(db.lookup.category == 'modelcategory').select():
        m = _parse_metadata(r.metadata)
        cat_important[r.name] = set(m.get('important', []))

    models = db(db.model).select(orderby=db.model.name)
    flagged = []
    for model in models:
        mt_imp = mt_important.get(model.modeltype, set())
        cat_imp = cat_important.get(model.modelcategory, set())
        # Only flag if both type AND category mark the field as important
        eff_important = mt_imp & cat_imp
        if not eff_important:
            continue
        missing = [
            (f, field_labels.get(f, f))
            for f in sorted(eff_important)
            if not model[f]
        ]
        if missing:
            flagged.append({'model': model, 'missing': missing})

    return dict(flagged=flagged, total=len(models))
