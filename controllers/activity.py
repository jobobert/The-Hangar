#from gluon.contrib.user_agent_parser import mobilize

# @mobilize
def rendercard():

    model_id = request.args[0]
    fields = ['activitydate', 'activitytype',
                  'duration', 'activitylocation', 'notes']
    

    form = SQLFORM(db.activity, fields=fields, formstyle="divs")
    form.vars.model = model_id
    if form.process().accepted:
        session.flash = "Activity Updated"
    elif form.errors:
        response.flash = "Error Adding New Activity "
    activity_query = db(db.activity.model == model_id)

    activity_count = activity_query.count()

    activities = activity_query.select(
        orderby=~db.activity.activitydate | ~db.activity.id)

    return dict(activities=activities, model_id=model_id, activity_count=activity_count, form=form)


def calendar():
    model_id = request.args(0)

    return dict(model_id=model_id)

def listrecentflights():

    model_id = request.args(0)

    flights = db((db.activity.activitytype == 'Flight') | (
        db.activity.activitytype == 'Crash')).select(limitby=(0, 10), orderby=~db.activity.activitydate)

    return dict(flights=flights)

def events():

    theList = []

    activity_query = db(db.activity)

    activities = activity_query.select(
        orderby=~db.activity.activitydate | ~db.activity.id)

    for activity in activities:
        if activity.activitytype not in ['StateChange', 'Note']:
            theList.append({
                'title': activity.model.name,
                'start': activity.activitydate,
                'url': URL('activity', 'index.html', args=[activity.id]),
                'classNames': 'activitytype_' + activity.activitytype,
                'extendedProps': {
                    'location': activity.activitylocation,
                    'notes': activity.notes,
                    'model': activity.model.name,
                    'model_id': activity.model.id,
                    'activitytype': activity.activitytype
                }
            })

    return dict(content=theList)


def index():

    activity_id = request.args[0]
    activity = db.activity(activity_id)
    response.title = "Activity"

    return dict(activity=activity)

def addactivity():
    form = SQLFORM(db.activity)
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    if len(request.args) == 0:
        fields = ['activitydate', 'model', 'activitytype',
                  'duration', 'activitylocation', 'notes']
    else:
        fields = ['activitydate', 'activitytype',
                  'duration', 'activitylocation', 'notes']
        model_id = request.args[0]
        form.vars.model = model_id

    form.fields = fields
    if form.process().accepted:
        session.flash = "New Activity Added"

        redirect(session.ReturnHere or URL('model', 'index', args=model_id))
    elif form.errors:
        response.flash = "Error Adding New Activity"
    # else:
        #response.flash = "Please Add a New Model"

    response.view = 'content.html'

    return dict(content=form)


def listview():

    response.title = 'Activity List'

    fields = (db.activity.activitydate, db.activity.model, db.activity.activitytype, db.activity.duration, db.activity.activitylocation
              )

    links = [
        lambda row: viewButton('activity', 'index', [row.id]),
        lambda row: editButton('activity', 'update', [row.id]),
    ]

    activities = SQLFORM.grid(
        db.activity, orderby=db.activity.activitydate, editable=False, details=False, deletable=False, user_signature=False, maxtextlength=255, create=True, links=links, fields=fields
    )

    response.view = 'content.html'

    return dict(content=activities, header=response.title)


def update():

    response.title = "Update/Add Activity"

    form = SQLFORM(db.activity, request.args(0), upload=URL(
        'default', 'download'), deletable=True, showid=False)
    if form.process().accepted:
        session.flash = "Activity Updated"
        redirect(session.ReturnHere or URL('model', 'index', args=model_id))
        # breadcrumb_back()
        #redirect(URL('default', 'breadcrumb_back'))
        # turned off breakcrumbs - if need to redirect, do it here
    elif form.errors:
        response.flash = "Error Adding New Activity "
    # else:
        #response.flash = "Please Add a New Model"

    response.view = 'content.html'

    return dict(content=form)


def modelactivities():

    response.title = "Model Activities"

    model_id = request.args[0]

    activity_query = db(db.activity.model == model_id)

    activities = activity_query.select(orderby=~db.activity.activitydate)

    return dict(
        activities=activities, model_name=db.model(request.args[0]).name, model_id=model_id)


def renderactivities():
    model_id = request.args[0]

    activity_query = db(db.activity.model == model_id)

    activities = activity_query.select(orderby=~db.activity.activitydate)

    return dict(
        activities=activities)


def rendernotes():
    model_id = request.args[0]

    activity_query = db((db.activity.model == model_id) &
                        (db.activity.activitytype == 'Note'))

    fields = (db.activity.notes)

    form = SQLFORM(db.activity, submit_button='Add')  # , fields=fields)
    form.vars.model = model_id
    form.vars.activitytype = 'Note'
    form.vars.activitydate = request.now
    if form.process(session=None, formname='noteform').accepted:
        response.flash = "New Note Added"
    elif form.errors:
        response.flash = "Error Adding New Note " + form.errors

    activities = activity_query.select(orderby=~db.activity.activitydate)

    return dict(form=form, notes=activities, model_id=model_id, options=request.args(1))


def addflight():

    if request.args(0):
        activitydate = request.now
        activitytype = 'Flight'
        modelid = request.args(0)

        db.activity.insert(activitydate=activitydate,
                           activitytype=activitytype, model=modelid)
        response.flash = "Flight Logged"

    return redirect(session.ReturnHere or URL('component', 'listview'))


def addcrash():

    if request.args(0):
        activitydate = request.now
        activitytype = 'Crash'
        model_id = request.args(0)

        db.activity.insert(activitydate=activitydate,
                           activitytype=activitytype, model=model_id)
        response.flash = "Crash Logged"

        model = db.model(model_id)
        new_modelstate = db.modelstate(6)

        db(db.model.id == model_id).update(modelstate=new_modelstate)

        notes = "State changed to **{}**".format(
            new_modelstate.name)

        # Add ModelState Activity into the Activity table
        db.activity.insert(
            activitydate=request.now.today(), model=model  # db(db.model.id == model_id)
            , activitytype='StateChange', notes=notes
        )

    return redirect(session.ReturnHere or URL('component', 'listview'))
