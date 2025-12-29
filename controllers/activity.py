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

    get_activitycount = activity_query.count()

    activities = activity_query.select(
        orderby=~db.activity.activitydate | ~db.activity.id)

    return dict(activities=activities, model_id=model_id, get_activitycount=get_activitycount, form=form)


def calendar():
    model_id = VerifyTableID('model', request.args(0))

    return dict(model_id=model_id)

def listrecentflights():

    #model_id = VerifyTableID('model', request.args(0)) or redirect(URL('activity', 'calendar'))

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

    activity_id = VerifyTableID('activity', request.args(0)) or redirect(URL('activity', 'calendar'))
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
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)
    
    activities = db(db.activity).select(orderby=db.activity.activitydate)
    return dict(activities=activities)

def update():

    response.title = "Update/Add Activity"

    form = SQLFORM(db.activity, request.args(0), upload=URL(
        'default', 'download'), deletable=True, showid=False)
    if form.process().accepted:
        session.flash = "Activity Updated"
        #print(form.vars.model)
        redirect(session.ReturnHere or URL('model', 'index', args=form.vars.model))
    
    elif form.errors:
        response.flash = "Error Adding New Activity "

    return dict(form=form)


def modelactivities():

    response.title = "Model Activities"

    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('model', 'listview'))

    activity_query = db(db.activity.model == model_id)

    activities = activity_query.select(orderby=~db.activity.activitydate)

    return dict(
        activities=activities, model_name=db.model(model_id).name, model_id=model_id)


def renderactivities():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='activity', title='Activity')


    activity_query = db(db.activity.model == model_id)

    activities = activity_query.select(orderby=~db.activity.activitydate)

    return dict(activities=activities)

def rendernotes():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='activity', title='Notes')

    activity_query = db((db.activity.model == model_id) &
                        (db.activity.activitytype == 'Note'))

    fields = (db.activity.notes)

    form = SQLFORM(db.activity, submit_button='Add')
    for s in form.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    form.vars.model = model_id
    form.vars.activitytype = "Note"
    form.vars.activitydate = request.now
    if form.process(session=None, formname='noteform').accepted:
        response.flash = "New Note Added"
    elif form.errors:
        response.flash = "Error Adding New Note " + str(form.errors)

    activities = activity_query.select(orderby=~db.activity.activitydate)

    return dict(notes=activities, model_id=model_id, options=request.args(1))


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
        
        model_id = VerifyTableID('model', request.args(0)) 
        if not model_id:
            return redirect(session.ReturnHere or URL('component', 'listview'))

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

def renderexport():

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'            
        return dict(content='Unable to locate the associated model', controller='activity', title='Activities')
    
    activities = db(db.activity.model == model_id).select(orderby=~db.activity.activitydate | ~db.activity.id)
    torender = {
        'title': 'Activities',
        'items': None,
        'emptymsg': 'No activities are associated with this model',
        'controller': 'activity',
        'header': None,
    }

    table = TABLE(_class="table export-table")
    header = [
        TH(getattr(db.activity,'activitydate').label, _class="col export-field_name"),
        TH(getattr(db.activity,'activitytype').label, _class="col export-field_name"),
        TH(getattr(db.activity,'duration').label, _class="col export-field_name"),
        TH(getattr(db.activity,'activitylocation').label, _class="col export-field_name"),
        TH(getattr(db.activity,'notes').label, _class="col export-field_name"),
    ]
    table.append(TR(*header, _class="row export-row"))
    for activity in activities or []:
        row = [
            TD(activity.activitydate, _class="col export-field_value"),
            TD(activity.activitytype, _class="col export-field_value"),
            TD(activity.duration, _class="col export-field_value"),
            TD(activity.activitylocation, _class="col export-field_value"),
            TD(MARKMIN(activity.notes) if activity.notes else "", _class="col export-field_value"),
        ]
        table.append(TR(*row, _class="row export-row"))

    torender['items'] = table

    response.view = 'renderexport.load'
    return dict(content=torender)