
import json

def index():

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    addform = SQLFORM(db.model_component, fields=["model", "purpose", "channel"], showid=False, comments=False)
    addform.vars.component = request.args[0]
    if addform.process(session=None, formname="addtomodel").accepted:
        response.flash = "Added to Model"
    elif addform.errors:
        response.flash = "Error Adding to Model"

    component = db(db.component.id == request.args(
        0)).select() or redirect(URL('component', 'listview'))
    models = models_and_components(
        db.component.id == request.args[0]).select(db.model.id, db.model.name, db.model.img)
    flitetimes = db(db.eflite_time.motor == request.args(0)).select()

    modelCount = dict()
    for m in models:
        if m.name in modelCount:
            modelCount[m.name] += 1
        else:
            modelCount[m.name] = 1
    modelIDs = dict()
    for m in models:
        modelIDs[m.name] = m.id

    

    response.title = "Component: " + component[0].name

    return dict(component=component, flitetimes=flitetimes, modelCount=modelCount, modelIDs=modelIDs, addform=addform)

def listview():
    
    other = ""

    response.title = 'Component List'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    types = []
    for x, y in db.component.componenttype.requires.options():
        if y != '':
            types.append(y)

    components = DIV('Choose the Component Type Above...',
                     _class='componentlist_choose')
    requestedtype = ''
    active = ''
    available = False

    if request.vars['a']:
        available = True

    if request.vars['c'] in types:
        requestedtype = request.vars['c']
        active = request.vars['c']
        fields = [db.component.img, db.component.name,
                  db.component.significantdetail]

        for attrib in component_attribs[requestedtype]:
            fields.append(db.component[attrib])

        fields.append(db.component.ownedcount)

        links = [
            dict(header='In Use', body=lambda row: DIV(row.get_usedcount(), _class='text-center')), 
            dict(header='Remaining', body=lambda row: DIV(B(row.get_remainingcount()), _class='text-center')), 
            lambda row: viewButton('component', 'index', [row.id]),
            lambda row: editButton('component', 'update', [row.id]),
            lambda row: plusButton('component', 'addcount', [row.id]),
            lambda row: minusButton('component', 'subtractcount', [row.id]),
        ]

        comp = db(db.component.componenttype == request.vars['c'])

        if available:
            other = "available!"
            comp = comp.select().find(lambda row: row.get_remainingcount() > 0)

        components = SQLFORM.grid(
            comp, orderby=db.component.componenttype | db.component.name, args=request.args[:1], user_signature=False, editable=False, deletable=False, details=False, maxtextlength=255, create=False, links=links, fields=fields, _class='itemlist-grid'
        )

    #response.view = 'content.html'
    return dict(components=components, types=types, requestedtype=requestedtype, active=active,other=other)


def addcount():

    # session.forget(response)

    if request.args(0):
        row = db(db.component.id == request.args(0)).select().first()
        if row.ownedcount == None:
            row.update_record(ownedcount=(1))
        else:
            row.update_record(ownedcount=(row.ownedcount + 1))

    return redirect(session.ReturnHere or URL('component', 'listview'))

def subtractcount():

    if request.args(0):
        row = db(db.component.id == request.args(0)).select().first()
        if row.ownedcount > 0:
            row.update_record(ownedcount=(row.ownedcount - 1))
    return redirect(session.ReturnHere or URL('component', 'listview'))

def update():

    response.title = 'Add/Update Component'

    # form = SQLFORM(db.component, request.args(0), deletable=True, showid=False).process(
    #    message_onsuccess='Document %s' % (
    #        'updated' if request.args else 'added'), next=(URL('component', 'index', args=request.vars.id, extension="html")))

    form = SQLFORM(db.component, request.args(0), upload=URL(
        'default', 'download'), deletable=True, showid=False).process(
        message_onsuccess='Document %s' % ('updated' if request.args else 'added')) 

    if form.accepted:
        redirect(URL('component', 'index', args=form.vars.id,
                 extension="html") or session.ReturnHere)

    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    return dict(form=form, component_attribs=json.dumps(component_attribs))

def rendercard_grid():
    model_id = request.args[0]
    newcomponentname = ""

    newform = SQLFORM(db.component, showid=False,
                      formstyle='bootstrap4_inline')
    for s in newform.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    if newform.process(session=None, formname='newcomponent').accepted:
        newcomponentname = newform.vars.name
    elif newform.errors:
        response.flash = "Error Creating New Component"

    query = db(db.model_component.model == model_id)
    left = db.component.on(db.component.id == db.model_component.component)
    fields = [db.component.name, db.model_component.purpose,
              db.model_component.channel, db.component.img, db.component.attachment]
    links = [dict(header=T('Img'),
                  body=lambda row: A(IMG(_src=URL('default', 'download', args=row.component.img), _width=75, _height=75)))]
    db.component.img.represent = None
    db.component.img.readable = db.component.img.writable = False

    grid = SQLFORM.grid(
        query,
        left=left,
        fields=fields,
        links=links,
        showbuttontext=False,
        details=False,
        deletable=True,
        editable=True,
        searchable=False,
        create=False,
        upload=URL('default', 'download'),
        links_placement='left',
        csv=False,
        exportclasses=None,
        user_signature=False,
        _class='itemlist-grid')

    component_count = db(db.model_component.model == model_id).count() or None
    components = models_and_components(
        db.model.id == model_id).iterselect() or None

    return dict(components=components, component_count=component_count, grid=grid, newform=newform, options=request.args(1))

def rendercard():
    # session.forget(response)
    if len(request.args) == 2:
        is_mobile = request.args[1]
    else:
        is_mobile = False 

    model_id = request.args[0]
    
    newcomponentname = ""


    addform = SQLFORM(db.model_component, fields=[
                      "component", "purpose", "channel"], comments=False)
    addform.vars.model = request.args(0)
    for s in addform.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    if addform.process(session=None, formname='addcomponent').accepted:
        response.flash = "New Component Added"
    elif addform.errors:
        response.flash = "Error Adding Component"


    newform = SQLFORM(db.component, showid=False,
                      formstyle='bootstrap4_inline')
    for s in newform.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    if newform.process(session=None, formname='newcomponent').accepted:
        newcomponentname = newform.vars.name
        db.model_component.insert(
            model=model_id, component=newform.vars.id
        )
        redirect(request.env.http_web2py_component_location, client_side=True)
    elif newform.errors:
        response.flash = "Error Creating New Component"


    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='componentdeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.model_component.id == del_id).delete()
                response.flash = "Removal Success"
    elif deleteform.errors:
        response.flash = "Removal Failure"

    component_count = db(db.model_component.model == model_id).count()
    components = models_and_components(db.model.id == model_id).iterselect()

    return dict(components=components, model_id=model_id, component_count=component_count, options=request.args(1), addform=addform, newform=newform, deleteform=deleteform, newcomponentname=newcomponentname, is_mobile= is_mobile)

def addtomodel():

    response.title = 'Add Component to Model'

    form = SQLFORM(db.model_component)
    form.vars.model = request.args(0)

    for s in form.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    if form.process(next=(URL('default', 'index', extension="html"))).accepted:
        response.flash = "New Component Added"
    elif form.errors:
        response.flash = "Error Adding New Component"

    response.view = 'content.html'

    return dict(content=form)

def removefrommodel():
    # try to do this via ajax sometime...
    # session.forget(response)

    model_id = request.args[0]
    relationship_id = request.args[1]
    db(db.model_component.id == relationship_id).delete()

    return redirect(URL('model', 'index.html', args=model_id))

def updatemodelrelation():

    relationship_id = request.args[0]

    rel = db(db.model_component.model == relationship_id).select().first()

    fields = ['purpose', 'channel']

    form = SQLFORM(db.model_component, relationship_id, fields=fields, showid=False)

    for s in form.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    if form.process().accepted:
        response.flash = "Relationship Updated"
        redirect(session.ReturnHere or URL(
            'default', 'index', extension="html"))
    elif form.errors:
        response.flash = "Error Updating Component Relationship"

    response.view = 'content.html'

    header = ''
    if rel:
        header = rel.component.name + ' on ' + rel.model.name

    return dict(content=form, header=header)

def inventory():

    response.title = 'Component Inventory'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    components = db(db.component).select(orderby=db.component.componenttype | db.component.name)

    return dict(components=components)