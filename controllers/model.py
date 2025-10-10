
from gluon.contrib.user_agent_parser import mobilize
# -*- coding: utf-8 -*-


def index(): 
    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('model', 'listview'))


    model = db.model(model_id) 

    details_form = SQLFORM(db.model, model.id, fields=[
                           'notes'], showid=False, formstyle='divs')

    if details_form.process().accepted:
        session.flash = "Model Updated"
        redirect(URL('model', 'index', args=details_form.vars.id, extension="html"))
    elif details_form.errors:
        response.flash = "Error Adding New Model"


    response.title = 'Model: ' + model.name
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    session.index = "index ready"
    return dict(model=model, details_form=details_form)

def wishlist():
    
    addform = SQLFORM(db.wishlist, formstyle='bootstrap4_inline', submit_button='Add')
    for s in addform.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    if addform.process(session=None, formname='wishlistadd').accepted:
        response.flash = "Added"
    elif addform.errors:
        response.flash = "Failed to add"

    convertform = SQLFORM.factory()
    if convertform.process(session=None, formname='convertform').accepted:
        for y, z in request.vars.items():
            if z == 'found':
                item = db(db.wishlist.id == y).select().first()
                
                # create a model
                new_id = db.model.insert(
                    name=item.item, 
                    modeltype='Airplane', 
                    havekit=True
                )
                
                # remove the item
                db(db.wishlist.id == item.id).delete()

                redirect(URL('model', 'update', args=new_id))
            if z == 'remove':
                del_id = y
                db(db.wishlist.id == del_id).delete()
                response.flash = "Item Deleted"
    elif convertform.errors:
        response.flash = "An error occurred"

    list = db(db.wishlist).select()

    return dict(list=list, addform=addform, convertform=convertform)

def export():

    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('model', 'listview'))

    model = db.model(model_id) 

    todos = db((db.todo.model == model_id) &
               (db.todo.complete == False)).select()
    components = models_and_components(db.model.id == model_id).select()
    tools = db(db.model_tool.model == model_id).select()
    batteries = db(db.model_battery.model == model_id).select()
    propellers = db(db.propeller.model == model_id).select()
    supportitems = db(db.supportitem.model == model_id).select()
    flighttimes = db(db.eflite_time.model == model_id).select()
    attachments = db(db.attachment.model == model_id).select()
    activities = db(db.activity.model == model_id).select()
    wtcs = models_and_wtcs(db.model.id == model_id).select()
    hardware = db(db.hardware.model == model_id).select()

    c = {}
    for comp in components:
        if len(c) > 0 and comp.component.name in c:
            # add the purpose/channel
            c[comp.component.name]['uses'].append(
                {'purpose': comp.model_component.purpose, 'channel': comp.model_component.channel})
        else:
            c[comp.component.name] = {
                'img': comp.component.img,
                'type': comp.component.componenttype,
                'subtype': comp.component.componentsubtype,
                'significantdetail': comp.component.significantdetail,
                'ownedcount': comp.component.ownedcount,
                'attachment': comp.component.attachment,
                'notes': comp.component.notes,
                'uses': [{'purpose': comp.model_component.purpose, 'channel': comp.model_component.channel}]
            }
            #c[comp.component.name] = {'type':'type', 'subtype': 'sub'}

    response.title = 'Export Model: ' + model.name

    return dict(model=model, todos=todos, components=c, tools=tools, batteries=batteries, propellers=propellers, supportitems=supportitems, flighttimes=flighttimes, attachments=attachments, activities=activities, wtcs=wtcs, hardware=hardware)

def exportminimal():

    model = db.model(request.args(0)) or redirect(URL('model', 'listview'))

    model_id = request.args(0)
    todos = db((db.todo.model == model_id) &
               (db.todo.complete == False)).select()
    components = models_and_components(db.model.id == model_id).select()
    tools = db(db.model_tool.model == model_id).select()
    batteries = db(db.model_battery.model == model_id).select()
    propellers = db(db.propeller.model == model_id).select()
    supportitems = db(db.supportitem.model == model_id).select()
    flighttimes = db(db.eflite_time.model == request.args(0)).select()
    attachments = db(db.attachment.model == model_id).select()

    c = {}
    for comp in components:
        if len(c) > 0 and comp.component.name in c:
            # add the purpose/channel
            c[comp.component.name]['uses'].append(
                {'purpose': comp.model_component.purpose, 'channel': comp.model_component.channel})
        else:
            c[comp.component.name] = {
                'img': comp.component.img,
                'type': comp.component.componenttype,
                'notes': comp.component.notes,
                'uses': [{'purpose': comp.model_component.purpose, 'channel': comp.model_component.channel}]
            }
            #c[comp.component.name] = {'type':'type', 'subtype': 'sub'}

    response.title = 'Export Model (minimal): ' + model.name

    return dict(model=model, todos=todos, components=c, tools=tools, batteries=batteries, propellers=propellers, supportitems=supportitems, flighttimes=flighttimes, attachments=attachments)

def rendercard():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate this model', controller='model', title='Models')

    model = db.model(model_id) or None

    return dict(model=model)

def renderurlcard():
    model_id = VerifyTableID('model', request.args(0))

    if not model_id:
        response.view = 'rendercarderror.load'
        return redirect(content='Unable to locate associated model', controller='model', title='URLs')

    addform = SQLFORM(db.url, fields=['url', 'notes'], formstyle='bootstrap4_inline', submit_button='Add')
    addform.vars.model = model_id
    if addform.process(session=None, formname='addurlform').accepted:
        response.flash = 'URL added to model'
    elif addform.errors:
        response.flash = 'Error adding URL to model'

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='urldeleteform').accepted:
        for y, z in request.vars.items():
            if z == "remove":
                del_id = y
                db(db.url.id == del_id).delete()
                response.flash = "URL removed"
    elif deleteform.errors:
        response.flash = 'Unable to remove URL'

    urlquery = db(db.url.model == model_id)
    urlcount = urlquery.count()
    urls = urlquery.select()

    return dict(urls=urls, urlcount=urlcount, addform=addform, deleteform=deleteform)


def printcard():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate this model', controller='model', title='Models')

    return dict(model_id=model_id)

def renderpackinglistcard():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate this model', controller='model', title='Models')
    
    model = db.model(model_id)
    batteries = db(db.model_battery.model == model_id).select()
    hardware = db(db.hardware.model == model_id).select()
    tools = db(db.model_tool.model == model_id).select()
    support_items = db(db.supportitem.model == model_id).select()
    propellers = db(db.propeller.model == model_id).select()
    rigs = model.get_sailrig_list()

    return dict(model=model, batteries=batteries, hardware=hardware, tools=tools, support_items=support_items, propellers=propellers, rigs=rigs)

def renderhass():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate this model', controller='model', title='Models')

    model = db.model(model_id)

    if (not model):
        return HTML(BODY(H1("No Model Found")))

    todos = db((db.todo.model == request.args(0)) &
               (db.todo.complete == False)).select()

    return HTML(
        BODY(
            DIV(
                DIV(
                    DIV(model_type_icon(model, 48),
                        _style="display:inline-block;"),
                    H4(model.name, _style="display:inline-block; vertical-align: middle; overflow: hidden; text-align: center; min-width: 75%"),
                    _style="margin: 0px 0px 0px 0px; height: 50px; "
                ),
                DIV(
                    model.modelstate.name,
                    _class="modelstate_bg_" + str(model.modelstate.id),
                    _style="margin: 0px 0px 5px 0px; padding-left: 5px;"
                ),
                DIV(
                    IMG(_src=URL('default', 'download', args=model.img),
                        _style="max-height: 190px; max-width: 50%; margin-right: 10px; margin-bottom: 10px; float:left; box-shadow: 3px 3px 10px rgb(0, 0, 0, 0.6);"),
                    P(model.description),
                    _style="overflow: auto;"
                ),
                DIV(
                    H6(model.open_todos_count(), " Todos | ", model.activity_count(), " Activities",
                       _style="color: #789f8a; background-color: #0a373a; padding-left: 1em;"),
                    UL(*[LI(x.todo) for x in todos]),
                    _style="display:block; float:clear; "
                ),
                _style="display:block; float:clear;  "
            ),
            _style="background-color: #789f8a;"
        )
    )

    # return dict(model=model)

def renderstatecounts():
    # (response)

    counts = db(db.model).select(db.model.modelstate,
                                 db.model.id.count(), groupby=db.model.modelstate)

    return dict(counts=counts, options=request.args(0))

def renderdashboard():
    model_id = VerifyTableID('model', request.args(0))
    
    model = db.model(model_id) if model_id else DIV("No Such Model Found")
    
    todo_count = db((db.todo.model == model.id) &
                    (db.todo.complete == False)).count()
    note_count = db((db.activity.model == model.id) & (
        db.activity.activitytype == 'Note')).count()
    component_count = db((db.model_component.model == model.id)).count()
    tool_count = db((db.model_tool.model == model.id)).count()
    attachment_count = db((db.attachment.model == model.id)).count()
    switch_count = db((db.switch.model == model.id)).count()

    opts = {
        "todo": todo_count,
        "note": note_count,
        "component": component_count,
        "tool": tool_count,
        "attachment": attachment_count,
        "switch": switch_count
    }

    note_form = SQLFORM.factory(Field(
        'note', type='text', label='Note'), formstyle='divs', table_name='note_form')
    if note_form.process().accepted:
        db.activity.insert(
            activitydate=request.now.today(), model=model, activitytype='Note', notes=note_form.vars.note
        )
        session.flash = "Note Added"
        redirect(URL('default', 'index', args=note_form.vars.id, extension="html"))
    elif note_form.errors:
        response.flash = "Error Adding Note"

    details_form = SQLFORM(db.model, model.id, fields=[
                           'notes'], showid=False, formstyle='divs')
    if details_form.process().accepted:
        session.flash = "Details Updated"
        redirect(URL('default', 'index',
                     args=details_form.vars.id, extension="html"))
    elif details_form.errors:
        response.flash = "Error Updating Details"

    return dict(model=model, details_form=details_form, note_form=note_form, options=opts)

def listview():
    response.title = 'Model List'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    query = db.model
    active = ''
    if request.args:
        if request.args[0] == 'plans':
            query = db.model.haveplans == True
            active = 'plans'
        elif request.args[0] == 'kits':
            query = db.model.havekit == True
            active = 'kits'

    fields = (db.model.img, db.model.name, db.model.modeltype, db.model.modelstate, db.model.controltype
              # , db.model.haveplans
              # , db.model.havekit
              )

    links = [ 
        dict(header='Major Dim', body=lambda row: row.get_major_dimension()),
        lambda row: viewButton('model', 'index', [row.id]),
        lambda row: editButton('model', 'update', [row.id]),
        lambda row: LOAD('model', 'selected.load', args=[row.id], ajax=True, content='...')
    ]

    # model = SQLFORM.grid(
    #     query  # db.model  # , groupby=db.component.componenttype
    #     , args=request.args[:1], orderby=db.model.name, editable=False, deletable=False, details=False, maxtextlength=255, create=False, fields=fields, links=links, _class='itemlist-grid', user_signature=False
    # )
    models = db(query).select(db.model.id, db.model.name, db.model.img, db.model.modeltype, db.model.modelstate, db.model.controltype, orderby=db.model.name)

    return dict(models=models, active=active)

def update():

    response.title = 'Add/Update Model'

    form = SQLFORM(db.model, request.args(0), upload=URL(
        'default', 'download'), _id='modelform')
    form.custom.widget.attr_covering['_class'] = "form-control"
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'
    if form.process().accepted:
        response.flash = 'Model %s' % ('Updated' if request.args else 'Added')
        if (not request.args):
            db.activity.insert(
                activitydate=request.now.today(), model=form.vars.id, activitytype='Other', notes="Model Created"
            )

        redirect(URL( 'model', 'index', args=form.vars.id, extension="html") or session.ReturnHere)
    elif form.errors:
        response.flash = "Error Adding New Model"
    else:
        pass
        #response.flash = "something happened"

    #response.view = 'content.html'

    return dict(form=form)

def addnote():
    # Add the note and return. Use GET for the text
    pass

def deleteconfig():
    # Delete the radio config
    model_id = request.args(0)

    # Confirmation is done in the front end
    row = db(db.model.id == model_id).select().first()
    delete_file(row, 'configbackup')

    return redirect(session.ReturnHere or URL('model', 'index.html', args=model_id))

def updatestate():
    # session.forget(response)
    model_id = request.args[0]
    state_id = request.args[1]

    model = db.model(model_id)

    old_modelstate = model.modelstate
    new_modelstate = db.modelstate(state_id)

    db(db.model.id == model_id).update(modelstate=new_modelstate)

    notes = "State changed from **{}** to **{}**".format(
        old_modelstate.name, new_modelstate.name)

    # Add ModelState Activity into the Activity table
    db.activity.insert(
        activitydate=request.now.today(), model=model  # db(db.model.id == model_id)
        , activitytype='StateChange', notes=notes
    )

    return redirect(session.ReturnHere or URL('model', 'index.html', args=model_id))

@mobilize
def flowchart():
    session.point = "flowchart"
    model_id = request.args[0]
    model = db.model(model_id)

    states = {'idea': '', 'board': '', 'maiden': '',
              'service': '', 'oos': '', 'repair': '', 'retired': ''}
    links = {'idea': '', 'board': '', 'maiden': '',
             'service': '', 'oos': '', 'repair': '', 'retired': ''}

    if model.modelstate == 1:  # retired
        states['service'] = '|past'
        links['service'] = URL('model', 'updatestate', args=(model_id, 5))
        states['retired'] = '|current'
    elif model.modelstate == 2:  # idea
        states['idea'] = '|current'
        states['board'] = '|future'
        links['board'] = URL('model', 'updatestate', args=(model_id, 3))
    elif model.modelstate == 3:  # board
        states['idea'] = '|past'
        links['idea'] = URL('model', 'updatestate', args=(model_id, 2))
        states['board'] = '|current'
        states['maiden'] = '|future'
        links['maiden'] = URL('model', 'updatestate', args=(model_id, 4))
    elif model.modelstate == 4:  # maiden
        states['board'] = '|past'
        links['board'] = URL('model', 'updatestate', args=(model_id, 3))
        states['maiden'] = '|current'
        states['service'] = '|future'
        links['service'] = URL('model', 'updatestate', args=(model_id, 5))
    elif model.modelstate == 5:  # service
        states['maiden'] = '|past'
        links['maiden'] = URL('model', 'updatestate', args=(model_id, 4))
        states['service'] = '|current'
        states['oos'] = '|future'
        links['oos'] = URL('model', 'updatestate', args=(model_id, 6))
        states['retired'] = '|future'
        links['retired'] = URL('model', 'updatestate', args=(model_id, 1))
    elif model.modelstate == 6:  # out of service
        states['service'] = '|past'
        links['service'] = URL('model', 'updatestate', args=(model_id, 5))
        states['oos'] = '|current'
        states['repair'] = '|future'
        links['repair'] = URL('model', 'updatestate', args=(model_id, 7))
    elif model.modelstate == 7:  # repair
        states['oos'] = '|past'
        links['oos'] = URL('model', 'updatestate', args=(model_id, 6))
        states['repair'] = '|current'
        states['service'] = '|future'
        links['service'] = URL('model', 'updatestate', args=(model_id, 5))
    else:
        pass

    if 'ui' in request.cookies:
        if request.cookies['ui'].value == 'dashboard':
            response.view = 'model/flowchartdashboard.load'
        elif request.cookies['ui'].value == 'list':
            pass

    return dict(states=states, links=links, thestate=model.modelstate, model_id=model_id)


def addflighttime():
    model_id = request.args(0)
    model = db.model(model_id)
    motor = model.get_motor()

    response.title = 'Add Flight Time'

    response.view = 'content.html'

    form = SQLFORM(db.eflite_time)
    if model_id:
        form.vars.model = model_id
    if motor:
        form.vars.motor = motor.id  # model.get_motor().id

    if form.process().accepted:
        session.flash = "New Flight Time Added"
        redirect(session.ReturnHere or URL('model', 'index', args=model_id))
    elif form.errors:
        response.flash = "Error Adding Flight Time"

    return dict(content=form)


def removeflighttime():
    flitetime_id = VerifyTableID('eflite_time', request.args(0)) or redirect(URL('default', 'index'))
    model_id = db(db.eflite_time.id == flitetime_id).select().first().model

    db(db.eflite_time.id == flitetime_id).delete()

    return redirect(URL('model', 'index.html', args=model_id))


def updateflighttime():
    flitetime_id = VerifyTableID('eflite_time', request.args(0)) or redirect(URL('default', 'index'))
    model_id = db(db.eflite_time.id == flitetime_id).select().first().model

    form = SQLFORM(db.eflite_time, flitetime_id, deletable=False, showid=False).process(
        message_onsuccess='Flight Time %s' % (
            'updated' if request.args else 'added'),
        # `next=(URL('model', 'updateflighttime', args=request.vars.id, extension="html"))
        next=(URL('model', 'index.html', args=model_id)))

    response.view = 'content.html'

    return dict(content=form)


def renderflighttimes():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate this model', controller='model', title='Models')
    
    model = db.model(model_id)
    motor = model.get_motor() or None
    message = None
    newform = None
    flighttimes = db(db.eflite_time.model == model_id).select()

    return dict(flighttimes=flighttimes, modelid=model_id, newform=newform, message=message)


def selected():
    session.point = "selected"
    model_id = request.args(0)
    options = request.args(1) or None

    model = db(db.model.id == model_id).select(db.model.id, db.model.selected)

    form = SQLFORM.factory(formname='selected', table_name='selected_form')

    if form.process().accepted:
        db(db.model.id == model_id).update(selected=not (model[0].selected))

    model = db(db.model.id == model_id).select(db.model.id, db.model.selected)

    return dict(model=model, form=form, options=options)


def retire():
    content = []
    model_id = VerifyTableID('model', request.args(0))

    model = db.model(request.args(0)) or redirect(URL('model', 'listview'))

    components = db(db.model_component.model == request.args[0]).select()

    form = SQLFORM.factory(table_name='retire_form')
    form.element(_type='submit')['_value'] = "Retire"

    if form.process().accepted:
        # for each component see if it is keep/dispose
        # if keep, remove the model_component entry
        # if dispose, subtract 1 from the count, remove the model_component entry
        #     if current count = 0, then ignore?
        # Add a note to the history of the removal of the component
        reason = ""
        for var in request.vars:
            if var == "reason":
                reason = request.vars[var]

                db.activity.insert(
                    activitydate=request.now.today(), model=model_id  # db(db.model.id == model_id)
                    , activitytype='Retirement', notes=reason
                )

                db(db.model.id == model_id).update(modelstate=1)

            if "disposition" in var:
                model_component_id = int(var.split("_")[0])
                component_id = int(
                    db(db.model_component.id == model_component_id).select()[0].component)

                if request.vars[var] == 'keep':
                    pass
                else:  # Dispose
                    content.append(component_id)
                    row = db(db.component.id ==
                             component_id).select().first()
                    if row.ownedcount > 0:
                        row.update_record(ownedcount=(row.ownedcount - 1))
                db(db.model_component.id == model_component_id).delete()
            else:
                pass

        redirect(URL('model', 'index', args=model_id))

    return dict(model=model, components=components, form=form, content=content)


def atthefield():
    response.title = 'At The Field'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    #query = db((db.model.modelstate == 4) | (db.model.modelstate == 5))
    queries = []
    queries.append((db.model.modelstate == 4) | (db.model.modelstate == 5))

    fq = None

    if request.vars['f']:
        # Then adjust the query accordingly...
        # 
        match request.vars['f']:
            case 'f':
                fq = ( 'Airplane', 'Rocket' )
            case 'r':
                fq = ( 'Multirotor', 'Helicopter', 'Autogyro' )
            case 'b': 
                fq = ( 'Boat', 'Submarine' )
            case 'd':
                fq = ( 'Car' )
            case 'o':
                fq = ( 'Robot', 'Experimental' )
        

    if fq:
        queries.append(db.model.modeltype.belongs(fq))

    query = reduce(lambda a, b: (a & b), queries)
    fields = (db.model.img, db.model.name)

    links = [
        dict(header='Count', body=lambda row: row.activity_flightcount()),
        lambda row: A('+1', _href=URL('activity', 'addflight', args=[row.id]), _class='btn btn-primary'),
        lambda row: A(activity_icon('crash', 20), _href=URL('activity', 'addcrash', args=[row.id]), _class='btn btn-outline-danger'),
        lambda row: A(controller_icon('model', 20), _href=URL('model', 'index', args=[ row.id]), _class="btn btn-outline-secondary")
    ]

    models = SQLFORM.grid(
        query, args=request.args[:1], searchable=False, orderby=db.model.name, csv=False, editable=False, deletable=False, paginate=100,
        details=False, maxtextlength=255, create=False, fields=fields, links=links, links_placement='right', buttons_placement='both', _class='itemlist-grid', user_signature=False
    )

    filters = {
        'Fixed':  'f',
        'Rotary': 'r',
        'Boating': 'b',
        'Driving': 'd',
        'Other': 'o'
    }
  
    # mark the active filter, if there is one...
    filter = DIV()
    for x,y in filters.items():
        _class = 'btn '
        if request.vars['f'] == y:
            _class += 'btn-primary'
        else:
            _class += 'btn-outline-primary'
        filter.append(A(x, _href=URL('model', 'atthefield', args=request.args, vars=dict(f=y)), _class=_class))
        
    #DIV(A("Flying", _href="", _class="btn btn-secondary"), A("Boating", _href="", _class="btn btn-secondary"))

    return dict(content=models, filter=filter)

#@mobilize
def renderhardware():

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='model', title='Hardware')

    fields = ['hardwaretype', 'diameter', 'length_mm', 'purpose', 'quantity']
    addform = SQLFORM(db.hardware, fields=fields, formstyle='bootstrap4_inline', submit_button='Submit')
    for s in addform.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    addform.vars.model = model_id
    if addform.process(session=None, formname='hwform').accepted:
        response.flash = "New Hardware Added"
    elif addform.errors:
        response.flash = "Error Adding New Hardware"

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='hwdeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.hardware.id == del_id).delete()
                response.flash = "Removal Success"
                
    elif deleteform.errors:
        response.flash = "Removal Failure"

    hardware = db(db.hardware.model == model_id).select()

    return dict(hardware=hardware, addform=addform, deleteform=deleteform)


def updatemodelbattery():
    response.title = "Update Model/Battery"

    model_battery_id = request.args(0)

    form = SQLFORM(db.model_battery, model_battery_id, formstyle='bootstrap4_inline', showid=False, submit_button='Submit')

    if form.process(session=None).accepted:
        session.flash = "Model/Battery Updated"
        redirect(session.ReturnHere or URL('default', 'index'))

    response.view = 'content.html'

    return dict(content=form, header=response.title)

def updatemodelpaint():
    response.title = "Update Model/Paint"

    model_paint_id = request.args(0)

    form = SQLFORM(db.model_paint, model_paint_id, formstyle='bootstrap4_inline', showid=False, submit_button='Submit')

    if form.process(session=None).accepted:
        session.flash = "Model/Paint Updated"
        redirect(session.ReturnHere or URL('default', 'index'))

    response.view = 'content.html'

    return dict(content=form, header=response.title)