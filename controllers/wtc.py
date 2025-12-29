#import urllib.parse

def index():

    response.title = "Water Tight Cylinder Details"
    
    wtc_id = request.args(0, cast=int) or redirect(URL('default', 'index'))
    wtc = db.wtc(wtc_id) or redirect(URL('default', 'index'))
    models = db(db.model_wtc.wtc == wtc_id).select()
    
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
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='wtc', title='Water Tight Cylinder')
    
    addform = SQLFORM(db.model_wtc, fields=["wtc", "notes"], comments=False)
    addform.vars.model = model_id
    if addform.process(session=None, formname='addwtc').accepted:
        response.flash = "WTC Added"
    elif addform.errors:
        response.flash = "Error Adding WTC"


    newform = SQLFORM(db.wtc, showid=False,
                      formstyle='bootstrap4_inline')
    for s in newform.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
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

    form = SQLFORM(db.wtc, request.args(0), upload=URL('default', 'download'), deletable=True, showid=False).process(
        message_onsuccess='WTC %s' % ('updated' if request.args else 'added')
    )

    if form.accepted:
        redirect(URL('wtc', 'index', args=form.vars.id, extension="html") or session.ReturnHere)

    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    return dict(form=form)

def listview():

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    wtcs = db(db.wtc).select(orderby=db.wtc.name)

    return dict(wtcs=wtcs)

def delete():
    wtc_id = VerifyTableID('wtc', request.args(0)) or redirect(URL('wtc', 'listview'))

    if db(db.model_wtc.wtc == wtc_id).select(db.model_wtc.id, limitby=(0,1)).first():
        response.flash = "Cannot delete: WTC is assigned to models!"        
        redirect(session.ReturnHere or URL('wtc', 'listview'))

    db(db.wtc.id == wtc_id).delete()
    response.flash = "Deleted"
    redirect(session.ReturnHere or URL('wtc', 'listview'))

def renderexport():
    """
    Render WTC export for a given model
    """

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='wtc', title='Water Tight Cylinder Export')
    
    wtcs = models_and_wtcs(db.model.id == model_id).select() or None

    torender = {
        'title': 'Water Tight Cylinders',
        'items': [],
        'emptymsg': 'No Water Tight Cylinders associated with this model',
        'controller': 'wtc',
        'header': None,
    }

    for wtc in wtcs or []:
        cylinder = wtc.wtc
        content = {
            'name': cylinder.name,
            'img': cylinder.img,
            'attachment': None, 
            'details': []
        }

        content['details'] = [
            (getattr(db.wtc,'make').label, cylinder.make),
            (getattr(db.wtc,'model').label, cylinder.model),
            (getattr(db.wtc,'notes').label, MARKMIN(cylinder.notes) if cylinder.notes else ''),
            (getattr(db.wtc,'attr_ballast_capacity').label, cylinder.attr_ballast_capacity),
        ]

        torender['items'].append(content)

    response.view = 'renderexport.load'
    return dict(content=torender)