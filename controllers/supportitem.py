def rendercard():
    
    #session.forget(response)
    model_id = request.args[0]
    si_query = db(db.supportitem.model == model_id)

    si_count = si_query.count()

    fields = ['item']
    form = SQLFORM(db.supportitem, fields=fields, formstyle='bootstrap4_inline', submit_button='Add')
    for s in form.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    form.vars.model = model_id
    if form.process(session=None, formname='siform').accepted:
        response.flash = "New Support Item Added"
    elif form.errors:
        response.flash = "Error Adding New Support Item"

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='supportdeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.supportitem.id == del_id).delete()
                response.flash = "Removal Success"
                #response.flash = str(del_id) + " Removal Success"
    elif deleteform.errors:
        response.flash = "Removal Failure"

    items = si_query.select()

    return dict(items=items, model_id=model_id, item_count=si_count, form=form, deleteform=deleteform)

def remove():
    #session.forget(response)
    
    item_id = request.args(0)
    response.flash = item_id
    if item_id:
        db(db.supportitem.id == item_id).delete()

        return redirect(URL('supportitem', 'index', args=item_id, extension="html"))
