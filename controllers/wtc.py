#import urllib.parse

def index():

    response.title = "Water Tight Cylinder Details"
    
    wtc_id = request.args(0, cast=int) or redirect(URL('default', 'index'))
    wtc = db.wtc(wtc_id) or redirect(URL('default', 'index'))
    activemodels = db(db.model.modelstate > 1)._select(db.model._id)
    models = db((db.model_wtc.wtc == wtc_id)
                & (db.model_wtc.model.belongs(activemodels))).select()
    
    # Fetch associated WTCs
    
    return dict(wtc=wtc, models=models)

def rendercard():
    """
    Render WTC card for a given model
    """
    if len(request.args) == 2:
        is_mobile = request.args[1]
    else:
        is_mobile = False 

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'wtc', 'Water Tight Cylinder')
    
    addform = SQLFORM(db.model_wtc, fields=["wtc", "notes"], comments=False)
    addform.vars.model = model_id
    if addform.process(session=None, formname='addwtc').accepted:
        response.flash = "WTC Added"
    elif addform.errors:
        response.flash = "Error Adding WTC"


    newform = SQLFORM(db.wtc, showid=False,
                      formstyle='bootstrap4_inline')
    disable_autocomplete(newform)
    if newform.process(session=None, formname='newwtc').accepted:
        pass
        #newwtcname = newform.vars.name
        #db.model_wtc.insert(
        #    model=model_id, wtc=newform.vars.id
        #)
        #redirect(request.env.http_web2py_component_location, client_side=True)
    elif newform.errors:
        response.flash = "Error Creating New WTC"


    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='wtcdeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.model_wtc.id == del_id).delete()
                response.flash = "Removal Success"
    elif deleteform.errors:
        response.flash = "Removal Failure"

    # Fetch associated WTCs
    wtcs = db(db.model_wtc.model == model_id).select()

    return dict(wtcs=wtcs, addform=addform, deleteform=deleteform, newform=newform)

def update():
    response.title = 'Add/Update WTC'

    form = SQLFORM(db.wtc, request.args(0), upload=URL('default', 'download'), showid=False).process(
        message_onsuccess='WTC %s' % ('updated' if request.args else 'added')
    )

    if form.accepted:
        redirect(URL('wtc', 'index', args=form.vars.id, extension="html"))

    disable_autocomplete(form)

    return dict(form=form)

def listview():

    wtcs = db(db.wtc).select(orderby=db.wtc.name)

    return dict(wtcs=wtcs)
