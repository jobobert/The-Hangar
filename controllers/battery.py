def index():
    battery_id = request.args(0)
    battery = db(db.battery.id == battery_id).select(
    ).first() or redirect(URL('battery', 'listview'))

    response.title = "Battery: " + battery.name

    models = models_and_batteries(
        db.battery.id == battery_id).select(db.model.id, db.model.name, db.model.img)

    return dict(battery=battery, models=models)


def listview():

    response.title = 'Battery List'

    fields = (db.battery.chemistry, db.battery.cellcount, db.battery.mah, db.battery.crating, db.battery.voltage, db.battery.ownedcount
              )

    links = [
        lambda row: viewButton('battery', 'index', [row.id]),
        lambda row: editButton('battery', 'update', [row.id]),
        lambda row: plusButton('battery', 'addcount', [row.id]),
        lambda row: minusButton('battery', 'subtractcount', [row.id]),
    ]

    batteries = SQLFORM.grid(
        db.battery, orderby=db.battery.chemistry | db.battery.cellcount | db.battery.mah | db.battery.crating, editable=False, details=False, maxtextlength=255, user_signature=False, create=False, deletable=False, links=links, fields=fields, _class='itemlist-grid'
    )

    response.view = 'content.html'

    return dict(content=batteries, header=response.title)


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

    response.title = "Add/Update Battery"

    form = SQLFORM(db.battery, request.args(0), upload=URL(
        'default', 'download'), deletable=True, showid=False, submit_button='Add').process(
        message_onsuccess='Document %s' % (
            'updated' if request.args else 'added'),
        next=(URL('battery', 'index', args=request.vars.id, extension="html")))
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    response.view = 'content.html'

    return dict(content=form)


def rendercard():
    # session.forget(response)
    model_id = request.args[0]

    fields = ['battery']
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


def removefrommodel():
    # try to do this via ajax sometime...

    model_id = request.args[0]
    relationship_id = request.args[1]
    db(db.model_battery.id == relationship_id).delete()

    return redirect(URL('model', 'index.html', args=model_id))
