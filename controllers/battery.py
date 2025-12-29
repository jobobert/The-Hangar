def index():

    battery_id = VerifyTableID('battery', request.args(0)) or redirect(URL('battery', 'listview'))

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    #battery_id = request.args(0)
    battery = db(db.battery.id == battery_id).select().first() or redirect(URL('battery', 'listview'))

    response.title = "Battery: " + battery.name

    models = models_and_batteries(
        db.battery.id == battery_id).select(db.model.id, db.model.name, db.model.img)

    return dict(battery=battery, models=models)


def listview():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    batteries = db(db.battery).select(orderby=db.battery.chemistry | db.battery.cellcount | db.battery.mah | db.battery.crating)
    return dict(batteries=batteries)


def addcount():

    if request.args(0):
        row = db(db.battery.id == request.args(0)).select().first()
        if row.ownedcount == None:
            row.update_record(ownedcount=(1))
        else:
            row.update_record(ownedcount=(row.ownedcount + 1))

    return redirect(session.ReturnHere or URL('battery', 'listview'))

 
def subtractcount():

    if request.args(0):
        row = db(db.battery.id == request.args(0)).select().first()
        if row.ownedcount > 0:
            row.update_record(ownedcount=(row.ownedcount - 1))

    return redirect(session.ReturnHere or URL('battery', 'listview'))


def update():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    response.title = "Add/Update Battery"

    form = SQLFORM(db.battery, request.args(0), upload=URL('default', 'download'), deletable=True, showid=False, submit_button='Submit')
    form.process(
        message_onsuccess='Document %s' % ('updated' if request.args else 'added'),
        next=(URL('battery', 'index', args=form.vars.id, extension="html"))
    )
    
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    return dict(form=form)


def rendercard():
   
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='battery', title='Batteries')

    fields = ['battery', 'quantity']
    addform = SQLFORM(db.model_battery, fields=fields,
                      formstyle='bootstrap4_inline', submit_button='Add')
    addform.vars.model = model_id
    if addform.process(session=None, formname='batteryform').accepted:
        response.flash = "Battery added to model"
    elif addform.errors:
        response.flash = "Error adding battery to model"

    newform = SQLFORM(db.battery, showid=False, formstyle='bootstrap4_inline')
    for s in newform.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    if newform.process(session=None, formname='newbattery').accepted:
        db.model_battery.insert(model=model_id, battery=newform.vars.id)
        redirect(request.env.http_web2py_component_location, client_side=True)
    elif newform.errors:
        response.flash = "Error Creating New Battery"

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='batterydeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.model_battery.id == del_id).delete()
                response.flash = "Removal Success"

    elif deleteform.errors:
        response.flash = "Removal Failure"

    battery_query = db(db.model_battery.model == model_id)
    battery_count = battery_query.count()
    model_batteries = battery_query.select()

    return dict(model_batteries=model_batteries, model_id=model_id, addform=addform, newform=newform, deleteform=deleteform, battery_count=battery_count)
 
def delete():

    battery_id = VerifyTableID('battery', request.args(0)) or redirect(URL('battery', 'listview'))

    #if db(db.model_battery.battery == battery_id).count() > 0:
    if db(db.model_battery.battery == battery_id).select(db.model_battery.id, limitby=(0,1)).first():
        response.flash = "Cannot delete: battery is assigned to models!"
        redirect(session.ReturnHere or URL('battery', 'listview'))

    #if db(db.eflite_time.battery == battery_id).count() > 0:
    if db(db.eflite_time.battery == battery_id).select(db.model_battery.id, limitby=(0,1)).first():
        response.flash = "Cannot delete: battery is assigned to flight time record!"
        redirect(session.ReturnHere or URL('battery', 'listview'))

    db(db.battery.id == battery_id).delete()
    response.flash = "Deleted"
    redirect(session.ReturnHere or URL('battery', 'listview'))

def removefrommodel():
    # try to do this via ajax sometime...

    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('default', 'index'))
    relationship_id = VerifyTableID('model_battery', request.args(1)) or redirect(URL('default', 'index'))
    db(db.model_battery.id == relationship_id).delete()

    return redirect(URL('model', 'index.html', args=model_id))

def renderexport():
    
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='battery', title='Batteries')

    batteries = db(db.model_battery.model == model_id).select() or None

    torender = {
        'title': 'Batteries',
        'items': [],
        'emptymsg': 'No Batteries assigned to this model',
        'controller': 'battery',
        'header': None,
    }
    for battery in batteries or []:
        torender['items'].append((battery.battery.name or "Unknown", f"{battery.quantity} needed"))
            
    response.view = 'renderexport.load'
    return dict(content=torender)