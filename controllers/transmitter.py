

def index():

    transmitter_id = VerifyTableID('transmitter', request.args(0), URL('transmitter', 'listview'), prefer_referer=True)
    response.title = 'Transmitters'

    transmitters = db(db.transmitter.id == transmitter_id).select(
    ) or redirect(URL('transmitter', 'listview'))

    models = db((db.model.transmitter == transmitter_id)
                & (db.model.modelstate > 1)).select()

    return dict(transmitters=transmitters, models=models)


def listview():

    transmitters = db(db.transmitter).select(orderby=db.transmitter.name)
    return dict(transmitters=transmitters)


def update():

    response.title = 'Add/Update Transmitter'

    form = SQLFORM(db.transmitter, request.args(0), upload=URL(
        'default', 'download'), showid=False).process(
        message_onsuccess='Transmitter %s' % (
            'updated' if request.args else 'added'))

    if form.accepted:
        transmitter_id = VerifyTableID('transmitter', request.args(0), URL('transmitter', 'listview'), prefer_referer=False)
        redirect(URL('transmitter', 'index', args=form.vars.id, extension="html"))

    disable_autocomplete(form)

    return dict(form=form)
