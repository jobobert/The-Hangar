

def select():

    response.title = 'Choose the Models'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    # Load itemtype rows: system types (Standard) are always included, others get checkboxes.
    _itemtypes = db(db.lookup.category == 'itemtype').select(orderby=db.lookup.sort_order)
    _optional_types = [r for r in _itemtypes if not r.is_system]
    _opt_names = [r.name for r in _optional_types]  # capture for lambda closure

    fields = [db.model.id, db.model.img, db.model.name, db.model.powerplant]
    query = db(db.model.modelstate.belongs((4, 5)))

    models = SQLFORM.grid(
        query,
        fields=fields,
        selectable=lambda ids, _opt=_opt_names: redirect(URL('packinglist', 'thelist', vars=dict(
            id=ids,
            **{n: request.vars.get(n) for n in _opt}
        ))),
        selectable_submit_button='Choose', csv=False, _class='packinglist_select',
        paginate=200, orderby=db.model.modeltype | db.model.name
    )

    # Build JS checkbox injections (reversed so prependTo builds correct top-to-bottom order)
    _chk_tpl = (
        "$('<div style=\"display: inline-block; margin-right: 1rem;\">"
        "<label for=\"{n}\"><input style=\"padding-left: .5rem\" type=\"checkbox\" "
        "id=\"{n}\" name=\"{n}\"/>{name}</label></div>').prependTo(formstart);"
    )
    _chk_js = '\n    '.join(
        _chk_tpl.format(n=r.name, name=r.name)
        for r in reversed(_optional_types)
    )

    js = """
    <script>
    var formstart = $(".web2py_htmltable");
    $('<h2>Models</h2>').prependTo(formstart);
    {chk_js}
    $('<h2>Trip Extras</h2>').prependTo(formstart);
    </script>
    """.format(chk_js=_chk_js)

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
    
    # System types (e.g. Standard) are always included; optional types load if checked.
    _itemtypes = db(db.lookup.category == 'itemtype').select(orderby=db.lookup.sort_order)
    for _itype in _itemtypes:
        if _itype.is_system or request.vars.get(_itype.name) == 'on':
            for _item in db(db.packingitems.itemtype == _itype.name).select():
                if _item.name not in si_list:
                    si_list.append(_item.name)

    if len(si_list) > 0:
        si_list = sorted([item for item in si_list if item is not None])


    # return dict(content = request.vars)
    return dict(
        models=model_list, tools=tool_list, supportitems=si_list, batteries=battery_list, propellers=propeller_list, rocketmotors=rm_list, transmitters=transmitter_list, todos=todo_list, model_ids=model_ids
    )

def listview():

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)
        
    packingitems = db(db.packingitems).select(orderby=db.packingitems.itemtype | db.packingitems.name)
    return dict(packingitems=packingitems)

def update():
    response.title = 'Update Packing Item'

    form = SQLFORM(db.packingitems, request.args(0), upload=URL('default', 'download'), deletable=True, showid=False).process(
        message_onsuccess='Packing Item %s' % ('updated' if request.args else 'added'),
        next=(URL('packingitems', 'allitems', extension="html"))
    )
    disable_autocomplete(form)

    return dict(form=form)

def delete():
    item_id = VerifyTableID('packingitems', request.args(0)) or redirect(URL('default', 'index'))

    db(db.packingitems.id == item_id).delete()
    return redirect(session.ReturnHere or URL('packingitems', 'listview'))