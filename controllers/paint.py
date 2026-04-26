def index():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    paint_id = request.args(0)
    paint = db(db.paint.id == paint_id).select().first() or redirect(URL('paint', 'listview'))

    response.title = "Paint"

    models = models_and_paints(
        db.paint.id == paint_id).select(db.model.id, db.model.name, db.model.img)
    
    return dict(paint=paint, models=models)


def update():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    response.title = "Add/Update Paint Type"

    form = SQLFORM(db.paint, request.args(0), upload=URL('default', 'download'), deletable=True, showid=False, submit_button='Submit').process(
        message_onsuccess='Document %s' % ('updated' if request.args else 'added'),
        next=(URL('paint', 'index', args=request.vars.id, extension="html"))
    )
    
    disable_autocomplete(form)

    return dict(form=form)

def listview():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    response.title = "List Paint Types"

    paints = db(db.paint).select( orderby=db.paint.color)

    return dict(paints=paints)

def delete():
    paint_id = VerifyTableID('paint', request.args(0)) or redirect(URL('paint', 'listview'))

    if db(db.model_paint.paint == paint_id).count() > 0:
        session.flash = "Cannot delete: paint is assigned to models!"
        return redirect(session.ReturnHere or URL('paint', 'listview'))
    
    if paint_id:
        db(db.paint.id == paint_id).delete()
        response.flash = 'Paint Deleted'    
    else:
        session.flash = "Cannot delete: paint not found"
        
    return redirect(session.ReturnHere or URL('paint', 'listview'))

def removefrommodel():
    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('default', 'index'))
    relationship_id = VerifyTableID('model_paint', request.args(1)) or redirect(URL('default', 'index'))
    db(db.model_paint.id == relationship_id).delete()

    return redirect(URL('model', 'index.html', args=model_id))

def rendercard():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'paint', 'Paint')

    newform = SQLFORM.factory(
        db.paint.manufacturer, db.paint.brand, db.paint.color,
        db.paint.colorid, db.paint.colorhex, db.paint.notes, db.paint.img,
        db.model_paint.purpose,
        formstyle='divs'
    )
    disable_autocomplete(newform)
    if newform.process(session=None, formname='newpaintform').accepted:
        new_id = db.paint.insert(
            manufacturer=newform.vars.manufacturer, brand=newform.vars.brand,
            color=newform.vars.color, colorid=newform.vars.colorid,
            colorhex=newform.vars.colorhex, notes=newform.vars.notes,
            img=newform.vars.img
        )
        db.model_paint.insert(model=model_id, paint=new_id, purpose=newform.vars.purpose)
        response.flash = 'Paint added to model'
    elif newform.errors:
        response.flash = 'Error creating new paint'

    addfields = ['paint', 'purpose']
    addform = SQLFORM(db.model_paint, fields=addfields, formstyle='bootstrap4_inline', submit_button='Add')
    addform.vars.model = model_id
    if addform.process(session=None, formname='addpaintform').accepted:
        response.flash = 'Paint added to model'
    elif addform.errors:
        response.flash = 'Error adding paint to model'

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='deletepaintform').accepted:
        for y, z in request.vars.items():
            if z ==  'Remove':
                del_id = VerifyTableID('model_paint', y)
                if del_id and db.model_paint[del_id].model == model_id:
                    db(db.model_paint.id == del_id).delete()
                    response.flash = 'Removal Success'
    elif deleteform.errors:
        response.flash = "Removal Failure"

    paint_query = db(db.model_paint.model == model_id)
    paint_count = paint_query.count()
    model_paints = paint_query.select()

    return dict(model_paints=model_paints, model_id=model_id, addform=addform, newform=newform, deleteform=deleteform, paint_count=paint_count)

def renderexport():
    session.forget(response)
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'paint', 'Paint')

    paints = db(db.model_paint.model == model_id).select() or None

    torender = {
        'title': 'Paints',
        'items': [],
        'emptymsg': 'No paints are associated with this model',
        'controller': 'paint',
        'header': None,
    }

    for paint in paints or []:
        torender['items'].append((paint.paint.color, paint.purpose))

    response.view = 'renderexport.load'
    return dict(content=torender)