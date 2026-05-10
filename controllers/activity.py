#from gluon.contrib.user_agent_parser import mobilize

# @mobilize
def rendercard():

    model_id = request.args[0]
    fields = ['activitydate', 'activitytype',
                  'duration', 'activitylocation', 'notes']
    

    form = SQLFORM(db.activity, fields=fields, formstyle="divs")
    form.vars.model = model_id
    if form.process().accepted:
        response.flash = "Activity Updated"
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
    session.forget(response)

    #model_id = VerifyTableID('model', request.args(0)) or redirect(URL('activity', 'calendar'))

    flights = db((db.activity.activitytype == 'Flight') | (
        db.activity.activitytype == 'Crash')).select(limitby=(0, 10), orderby=~db.activity.activitydate)

    return dict(flights=flights)

def events():
    session.forget(response)

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

    activity_id = VerifyTableID('activity', request.args(0), URL('activity', 'calendar'), prefer_referer=True)
    activity = db.activity(activity_id) 
    response.title = "Activity"

    return dict(activity=activity)

def addactivity():
    form = SQLFORM(db.activity)
    disable_autocomplete(form)

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

        redirect(URL('model', 'index', args=form.vars.model))
    elif form.errors:
        response.flash = "Error Adding New Activity"
    # else:
        #response.flash = "Please Add a New Model"

    response.view = 'content.html'

    return dict(content=form)

def listview():
    activities = db(db.activity).select(orderby=db.activity.activitydate)
    return dict(activities=activities)

def update():

    response.title = "Update/Add Activity"

    activity_id = VerifyTableID('activity', request.args(0), URL('activity', 'listview'), prefer_referer=True)

    existing = db.activity(activity_id)
    model_id = existing.model if existing else None

    form = SQLFORM(db.activity, activity_id, upload=URL(
        'default', 'download'), deletable=True, showid=False)
    if form.process().accepted:
        if form.deleted:
            session.flash = "Activity Deleted"
            redirect(URL('model', 'index', args=model_id))
        else:
            session.flash = "Activity Updated"
            redirect(URL('model', 'index', args=form.vars.model))

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
        return render_card_error('Unable to locate the associated model', 'activity', 'Activity')


    activity_query = db(db.activity.model == model_id)

    activities = activity_query.select(orderby=~db.activity.activitydate)

    return dict(activities=activities)

def rendernotes():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'activity', 'Notes')

    activity_query = db((db.activity.model == model_id) &
                        (db.activity.activitytype == 'Note'))

    fields = (db.activity.notes)

    form = SQLFORM(db.activity, submit_button='Add')
    disable_autocomplete(form)
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
        modelid = request.args(0)
        log_activity(modelid, 'Flight')
        session.flash = "Flight Logged"
        return redirect(URL('model', 'index', args=modelid))

    return redirect(URL('default', 'index'))


def addcrash():

    if request.args(0):
        model_id = VerifyTableID('model', request.args(0))
        if not model_id:
            return redirect(URL('model', 'listview'))

        log_activity(model_id, 'Crash')
        response.flash = "Crash Logged"

        new_modelstate = db.modelstate(6)
        db(db.model.id == model_id).update(modelstate=new_modelstate)

        notes = "State changed to **{}**".format(new_modelstate.name)
        log_activity(model_id, 'StateChange', notes)

        return redirect(URL('model', 'index', args=model_id))

    return redirect(URL('default', 'index'))

def renderexport():

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'activity', 'Activities')
    
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