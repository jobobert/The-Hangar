def rendercard():

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='propeller', title='Propellers')

    si_query = db(db.propeller.model == model_id)

    si_count = si_query.count() 

    fields = ['item']
    addform = SQLFORM(db.propeller, fields=fields, formstyle='bootstrap4_inline', submit_button='Add')
    for s in addform.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    addform.vars.model = model_id
    if addform.process(session=None, formname='propelleraddform').accepted:
        response.flash = "New Propeller Added"
    elif addform.errors:
        response.flash = "Error Adding New Propeller"

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='propellerdeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.propeller.id == del_id).delete()
                response.flash = "Removal Success"
                #response.flash = str(del_id) + " Removal Success"
    elif deleteform.errors:
        response.flash = "Removal Failure"

    items = si_query.select()

    return dict(items=items, model_id=model_id, item_count=si_count, addform=addform, deleteform=deleteform)

def listview():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    activemodels = db(db.model.modelstate > 1)._select(db.model._id)

    propellers = db(db.propeller.model.belongs(activemodels)).select(orderby=db.propeller.item | db.propeller.model)
    return dict(propellers=propellers)

def delete():
    
    item_id = VerifyTableID('propeller', request.args(0)) or redirect(URL('default', 'index'))
    response.flash = item_id
    
    if item_id:
        db(db.propeller.id == item_id).delete()
        
        redirect(URL('propeller', 'index', args=item_id, extension="html"))

def renderexport():

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='propeller', title='Propellers')

    propellers = db(db.propeller.model == model_id).select()

    torender = {
        'title': 'Propellers',
        'items': [],
        'emptymsg': 'No propellers associated with this model',
        'controller': 'propeller',
        'header': None,
    }

    for propeller in propellers or []:
        torender['items'].append((propeller.item, ""))

    response.view = 'renderexport.load'
    return dict(content=torender)