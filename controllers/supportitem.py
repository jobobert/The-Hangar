def rendercard():
    
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'supportitem', 'Support Items')

    si_query = db(db.supportitem.model == model_id)

    si_count = si_query.count()

    fields = ['item']
    addform = SQLFORM(db.supportitem, fields=fields, formstyle='bootstrap4_inline', submit_button='Add')
    disable_autocomplete(addform)
    addform.vars.model = model_id
    if addform.process(session=None, formname='siform').accepted:
        response.flash = "New Support Item Added"
    elif addform.errors:
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

    return dict(items=items, model_id=model_id, item_count=si_count, addform=addform, deleteform=deleteform)

def remove():
    
    item_id = VerifyTableID('supportitem', request.args(0))
    
    if item_id:
        db(db.supportitem.id == item_id).delete()
        response.flash = "Support item removed successfully"

    else:
        session.flash = "Invalid support item ID"      
        
    redirect(session.ReturnHere or URL('supportitem', 'index', args=item_id, extension="html"))

def renderexport():
    
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'supportitem', 'Support Items')

    supportitems = db(db.supportitem.model == model_id).select()

    torender = {
        'title': 'Support Items',
        'items': [],
        'emptymsg': 'No supporting items necessary',
        'controller': 'supportitem',
        'header': None,
    }
    for item in supportitems or []:
        torender['items'].append((item.item, MARKMIN(item.notes or '')))

    response.view = 'renderexport.load'
    return dict(content=torender)