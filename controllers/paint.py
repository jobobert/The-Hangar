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
    
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    return dict(form=form)

def listview():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    response.title = "List Paint Types"

    paints = db(db.paint).select( orderby=db.paint.color)

    return dict(paints=paints)

def delete():
    paint_id = request.args(0)

    db(db.paint.id == paint_id).delete()
    resposne.flash = 'Paint Deleted'
    return redirect(session.ReturnHere or URL('paint', 'listview'))

def removefrommodel():
    model_id = request.args(0)
    relationship_id = request.args(1)
    db(db.model_paint.id == relationship_id).delete()

    return redirect(URL('model', 'index.html', args=model_id))

def rendercard():
    model_id = request.args(0)

    new_id = 0
    newform = SQLFORM(db.paint, showid=False, formstyle='bootstrap4_inline')
    for s in newform.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    if newform.process(session=None, formname='newpaintform').accepted:
        new_id = newform.vars.id
        
        redirect(request.env.http_web2py_component_location, client_side=True)
    elif newform.errors:
        response.flash = 'Error creating new paint'


    addfields = ['paint', 'purpose']
    addform = SQLFORM(db.model_paint, fields=addfields, formstyle='bootstrap4_inline', submit_button='Add')
    addform.vars.model = model_id
    if new_id:
        addform.vars.paint = new_id
    if addform.process(session=None, formname='addpaintform').accepted:
        response.flash = 'Paint added to model'
    elif addform.errors:
        response.flash = 'Error adding paint to model'

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='deletepaintform').accepted:
        for y, z in request.vars.items():
            if z ==  'Remove':
                del_id = y
                db(db.model_paint.id == del_id).delete()
                response.flash = 'Removal Sucess'
    elif deleteform.errors:
        response.flash = "Removal Failure"

    paint_query = db(db.model_paint.model == model_id)
    paint_count = paint_query.count()
    model_paints = paint_query.select()

    return dict(model_paints=model_paints, model_id=model_id, addform=addform, newform=newform, deleteform=deleteform, paint_count=paint_count)
