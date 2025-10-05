

def select():

    response.title = 'Choose the Models'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    fields = [db.model.id, db.model.img, db.model.name, db.model.powerplant]
    query = db(db.model.modelstate.belongs((4, 5)))

    models = SQLFORM.grid(
        # db.model
        query,
        fields=fields,
        selectable=lambda ids: redirect(URL('packinglist', 'thelist', vars=dict(
            id=ids,
            event=request.vars.chk_event,
            overnight=request.vars.chk_overnight,
            nightevent=request.vars.chk_nightevent,
            planeevent=request.vars.chk_planeevent,
            boatevent=request.vars.chk_boatevent,
            helievent=request.vars.chk_helievent,
            subevent=request.vars.chk_subevent))),
        selectable_submit_button='Choose', csv=False, _class='packinglist_select', paginate=200, orderby=db.model.modeltype | db.model.name
    )

    js = """
    <script>
    var formstart = $(".web2py_htmltable");
    $('<h2>Models</h2>').prependTo(formstart);
    $('<div style="display: inline-block; margin-right: 1rem;"><label for="chk_subevent"><input style="padding-left: .5rem" type="checkbox" id="chk_subevent" name="chk_subevent"/>Sub Event</label></div>').prependTo(formstart);
    $('<div style="display: inline-block; margin-right: 1rem;"><label for="chk_boatevent"><input style="padding-left: .5rem" type="checkbox" id="chk_boatevent" name="chk_boatevent"/>Boat Event</label></div>').prependTo(formstart);
    $('<div style="display: inline-block; margin-right: 1rem;"><label for="chk_helievent"><input style="padding-left: .5rem" type="checkbox" id="chk_helievent" name="chk_helievent"/>Heli Event</label></div>').prependTo(formstart);
    $('<div style="display: inline-block; margin-right: 1rem;"><label for="chk_planeevent"><input style="padding-left: .5rem" type="checkbox" id="chk_planeevent" name="chk_planeevent"/>Plane Event</label></div>').prependTo(formstart);
    $('<div style="display: inline-block; margin-right: 1rem;"><label for="chk_nightevent"><input style="padding-left: .5rem" type="checkbox" id="chk_nightevent" name="chk_nightevent"/>Night Event</label></div>').prependTo(formstart);
    $('<div style="display: inline-block; margin-right: 1rem;"><label for="chk_overnight"><input style="padding-left: .5rem" type="checkbox" id="chk_overnight" name="chk_overnight"/>Overnight</label></div>').prependTo(formstart);
    //$('<div style="display: inline-block; margin-right: 1rem;"><label for="chk_event"><input style="padding-left: .5rem" type="checkbox" id="chk_event" name="chk_event"/>Event</label></div>').prependTo(formstart);
    $('<h2>Trip Extras</h2>').prependTo(formstart);
    </script>
    """

    return dict(content=models, extra=XML(js))


def thelist():
    response.title = 'The List'
    if type(request.vars.id) is not list:
        model_ids = [request.vars.id]
    else:
        model_ids = request.vars.id

    model_list = []
    transmitter_list = []

    models = db(db.model.id.belongs(model_ids)).select()
    for model in models:
        rig_list = model.get_sailrig_list()
        if model.transmitter:
            if model.transmitter.name not in transmitter_list:
                transmitter_list.append(model.transmitter.name)

        model_list.append((model.name, model.attr_plane_rem_wings or False, model.attr_plane_rem_wing_tube or False,
                           model.attr_plane_rem_struts or False, rig_list))
    if len(model_list) > 0:
        model_list = sorted([item for item in model_list if item is not None])
    if len(transmitter_list) > 0:
        transmitter_list = sorted([item for item in transmitter_list if item is not None])

    tool_list = []
    tools = db(db.model_tool.model.belongs(
        model_ids)).select()
    for tool in tools:
        if tool.tool.name not in tool_list:
            tool_list.append(tool.tool.name)
    if len(tool_list) > 0:
        tool_list = sorted([item for item in tool_list if item is not None])

    battery_list = []
    batteries = db(db.model_battery.model.belongs(
        model_ids)).select()
    for battery in batteries:
        if battery.battery.get_name() not in battery_list:
            battery_list.append(battery.battery.get_name())
    if len(battery_list) > 0:
        battery_list = sorted([item for item in battery_list if item is not None])

    propeller_list = []
    propellers = db(db.propeller.model.belongs(
        model_ids)).select()
    for propeller in propellers:
        if propeller.item not in propeller_list:
            propeller_list.append(propeller.item)
    if len(propeller_list) > 0:
        propeller_list = sorted([item for item in propeller_list if item is not None])

    rm_list = []
    for model in models:
        rocket_motors = model.attr_rocket_motors
        if rocket_motors:
            for rocket_motor in rocket_motors:
                if rocket_motor not in rm_list:
                    rm_list.append(rocket_motor)
    if len(rm_list) > 0:
        rm_list = sorted([item for item in rm_list if item is not None])

    todo_list = []
    todos = db((db.todo.model.belongs(model_ids)) & (
        db.todo.complete == False) & (db.todo.critical == True)).select()
    for todo in todos:
        todo_list.append([todo.model.name, todo.todo])
    if len(todo_list) > 0:
        todo_list = sorted([item for item in todo_list if item is not None])

    si_list = []
    sis = db(db.supportitem.model.belongs(
        model_ids)).select()
    for si in sis:
        if si.item not in si_list:
            si_list.append(si.item)
    
    items = db(db.packingitems.itemtype == 'Standard').select()
    for item in items:
        if item not in si_list:
            si_list.append(item.name)

    if request.vars.overnight == 'on':
        items = db(db.packingitems.itemtype == 'Overnight').select()
        for item in items:
            if item not in si_list:
                si_list.append(item.name)

    is_event = False

    if request.vars.nightevent == 'on':
        is_event = True
        items = db(db.packingitems.itemtype == 'Night Event').select()
        for item in items:
            if item not in si_list:
                si_list.append(item.name)

    if request.vars.planeevent == 'on':
        is_event = True
        items = db(db.packingitems.itemtype == 'Plane Event').select()
        for item in items:
            if item not in si_list:
                si_list.append(item.name)

    if request.vars.boatevent == 'on':
        is_event = True
        items = db(db.packingitems.itemtype == 'Boat Event').select()
        for item in items:
            if item not in si_list:
                si_list.append(item.name)

    if request.vars.helievent == 'on':
        is_event = True
        items = db(db.packingitems.itemtype == 'Heli Event').select()
        for item in items:
            if item not in si_list:
                si_list.append(item.name)

    if request.vars.subevent == 'on':
        is_event = True
        items = db(db.packingitems.itemtype == 'Sub Event').select()
        for item in items:
            if item not in si_list:
                si_list.append(item.name)

    if is_event == True:  # request.vars.event == 'on':
        items = db(db.packingitems.itemtype == 'Event').select()
        for item in items:
            if item not in si_list:
                si_list.append(item.name)

    if len(si_list) > 0:
        si_list = sorted([item for item in si_list if item is not None])


    # return dict(content = request.vars)
    return dict(
        models=model_list, tools=tool_list, supportitems=si_list, batteries=battery_list, propellers=propeller_list, rocketmotors=rm_list, transmitters=transmitter_list, todos=todo_list, model_ids=model_ids
    )


def allitems():

    response.title = 'Packing Items'

    links = [
        lambda row: editButton('packinglist', 'update', [row.id])
    ]

    form = SQLFORM.grid(
        db.packingitems, links=links, details=False, editable=False, csv=False, create=True, _class='itemlist-grid', user_signature=False)

    response.view = 'content.html'

    return dict(content=form, header=response.title)


def update():
    response.title = 'Update Packing Item'

    # form = SQLFORM(db.packingitems, request.args(0), upload=URL('default', 'download'), deletable=True, showid=False).process(
    #     message_onsuccess='Item %s' % ('updated' if request.args else 'added'))

    # if form.process().accepted:
    #     redirect(URL('packinglist', 'allitems', args=form.vars.id, extension="html") or session.ReturnHere)
    form = SQLFORM(db.packingitems, request.args(0), upload=URL('default', 'download'), deletable=True, showid=False).process(
        message_onsuccess='Packing Item %s' % ('updated' if request.args else 'added'),
        next=(URL('packinglist', 'allitems', extension="html"))
    )
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    #response.view = 'content.html'
    #return dict(content=form)
    return dict(form=form)
