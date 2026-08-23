# -*- coding: utf-8 -*-
"""Generic guarded delete for non-model inventory items.

One action instead of a near-identical delete() in fourteen controllers.
The rules, the impact report and the cleanup all live in models/m_delete.py;
DELETABLE is the whitelist of what may be deleted here.
"""


def delete():
    """item/delete/<table>/<id> — confirm on GET, delete on POST."""

    table = request.args(0)
    if table not in DELETABLE:
        session.flash = "That kind of item cannot be deleted."
        redirect(URL('default', 'index'))

    row_id = VerifyTableID(table, request.args(1),
                           URL(*DELETABLE[table]), prefer_referer=True)

    response.title = 'Delete %s' % table_label(table).rstrip('s').title()

    impact = delete_impact(table, row_id)

    # Full page (not a .load), so the form key is stored normally and CSRF
    # applies. POST-only deletion also keeps link prefetchers from firing it.
    confirmform = SQLFORM.factory(formstyle='divs', table_name='confirm_delete',
                                  submit_button='Delete permanently')
    submit = confirmform.element('input[type=submit]')
    if submit:
        submit['_class'] = 'btn btn-danger'
    if confirmform.process(formname='confirm_delete_%s_%s' % (table, row_id),
                           message_onsuccess=None).accepted:
        result = perform_delete(table, row_id)
        session.flash = 'Deleted "%s"%s' % (
            result['label'],
            ' and %d related record(s)' % result['total'] if result['total'] else ''
        )
        redirect(URL(*DELETABLE[table]))

    return dict(table=table, table_label=table_label(table), row_id=row_id,
                impact=impact, form=confirmform,
                cancel_url=RefererOrDefault(URL(*DELETABLE[table])))
