

def index():

    transmitter_id = VerifyTableID('transmitter', request.args(0)) or redirect(URL('transmitter', 'listview'))
    response.title = 'Transmitters'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    transmitters = db(db.transmitter.id == transmitter_id).select(
    ) or redirect(URL('transmitter', 'listview'))

    models = db((db.model.transmitter == transmitter_id)
                & (db.model.modelstate > 1)).select()

    return dict(transmitters=transmitters, models=models)


def listview():

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    transmitters = db(db.transmitter).select(orderby=db.transmitter.name)
    return dict(transmitters=transmitters)


def update():

    response.title = 'Add/Update Transmitter'

    form = SQLFORM(db.transmitter, request.args(0), upload=URL(
        'default', 'download'), deletable=True, showid=False).process(
        message_onsuccess='Transmitter %s' % (
            'updated' if request.args else 'added'))

    if form.accepted:
        redirect(URL('transmitter', 'index', args=form.vars.id,
                 extension="html") or session.ReturnHere)

    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    return dict(form=form)

