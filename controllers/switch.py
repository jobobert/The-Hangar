
def add():
    model_id = request.args(0) or None

    if not model_id:
        redirect(session.ReturnHere or URL('default','index'))
    
    form = SQLFORM(db.switch, showid=False, deletable=True)
    form.vars.model = model_id
    if form.process().accepted:
        session.flash = "Switch Added"
        redirect(session.ReturnHere or URL('default','index'))
    elif form.errors:
        response.flash = "Error Adding Switch"

    return dict(form=form)

def renderswitches():
    model_id = request.args(0) or None
    render_card = request.args(1) #or True

    switchList = {}
    x  = 0

    switches = db(db.switch.model == model_id).select()

    for s in switches:
        x = x + 1
        switchDetails = {}
        switchPos = {}
        switchDetails['id'] = s.id
        switchDetails['mid'] = s.model.id
        switchDetails['switch'] = s.switch
        switchDetails['type'] = s.switchtype
        switchDetails['purpose'] = s.purpose

        switchPositions = db(db.switch_position.switch == s.id).select()
        for p in switchPositions:
            switchPos[p.pos] = p.func

        switchDetails['positions'] = switchPos
        switchList[x] = switchDetails
        
    return dict(switchList=switchList, switch_count=x, model_id=model_id, render_card=render_card )

def renderswitchtable(): 
    model_id = request.args(0) or None

    switchList = {}
    x  = 0

    switches = db(db.switch.model == model_id).select()

    for s in switches:
        x = x + 1
        switchDetails = {}
        switchPos = {}
        switchDetails['id'] = s.id
        switchDetails['mid'] = s.model.id
        switchDetails['switch'] = s.switch
        switchDetails['type'] = s.switchtype
        switchDetails['purpose'] = s.purpose

        switchPositions = db(db.switch_position.switch == s.id).select()
        for p in switchPositions:
            switchPos[p.pos] = p.func

        switchDetails['positions'] = switchPos
        switchList[x] = switchDetails
        
    return dict(switchList=switchList, switch_count=x, model_id=model_id,options=request.args(1) )

def update():

    switch_id = request.args(0) or None

    fields = ['model','switch','switchtype','purpose']

    form = SQLFORM(db.switch, switch_id, fields=fields,showid=False, deletable=True)
    if form.process().accepted:
        session.flash = "Switch Updated"
    elif form.errors:
        response.flash = "Error Updating Switch"

    return dict(form=form, switch_id=switch_id)

def renderpositions():
    switch_id = request.args[0] or None
    newpos = ""

    fields = ['pos', 'func']

    addform = SQLFORM(db.switch_position,fields=fields)
    addform.vars.switch = switch_id
    if addform.process(session=None, formname='addposition').accepted:
        response.flash = "New Position Added"
    elif addform.errors:
        response.flash = "Error Adding Position"

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='positiondeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.switch_position.id == del_id).delete()
                response.flash = "Removal Success"
                #response.flash = str(del_id) + " Removal Success"
    elif deleteform.errors:
        response.flash = "Removal Failure"

    position_count = db(db.switch_position.switch == switch_id).count()
    positions = db(db.switch_position.switch == switch_id).iterselect() #or None

    return dict(position_count=position_count, positions=positions, addform=addform,deleteform=deleteform)

def listswitches_old():
    transmitter_id = int(request.args(0))

    switches = db(db.switch.model).select()
    trans_switches = switches.exclude(lambda row: row.model.transmitter.id == transmitter_id)

    x = []

    for switch in trans_switches:
        
        x.append(dict(
            trans=switch.model.transmitter.name, 
            tid = switch.model.transmitter.id,
            switch=switch.switch,
            model=switch.model.name,
            type=switch.switchtype,
            purpose=switch.purpose
            )
        )

    #response.view = 'content.html'
    return dict(content=x, m=transmitter_id)
# http://127.0.0.1:8000/init/switch/listswitches/2

def listswitches():

    transmitter_id = int(request.args(0))

    # Get the switches excluding those not associated with the specified transmitter
    switches = db(db.switch.model).select().exclude(lambda row: row.model.transmitter.id == transmitter_id)

    # Prepare the content for the view
    switch_names = sorted(set(s.switch for s in switches))
    model_names = sorted(set(s.model.name for s in switches))

    # Build a lookup: {(model_name, switch_name): purpose}
    table_data = {}
    for s in switches:
        key = (s.model.name, s.switch)
        table_data[key] = s.purpose

    # Prepare rows for the table
    rows = []
    for model in model_names:
        
        row = [model]
        for switch in switch_names:
            row.append(table_data.get((model, switch), ""))
        rows.append(row)
    
    # Pass headers and rows to the view
    headers = ["Model"] + switch_names
    
    return dict(headers=headers, rows=rows)