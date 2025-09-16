

def index():
    response.title = 'Transmitters'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    transmitter_id = request.args(0)
    transmitters = db(db.transmitter.id == transmitter_id).select(
    ) or redirect(URL('transmitter', 'listview'))

    models = db((db.model.transmitter == transmitter_id)
                & (db.model.modelstate > 1)).select()

    return dict(transmitters=transmitters, models=models)


def listview():
    response.title = 'Transmitter List'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    fields = (db.transmitter.img, db.transmitter.name, db.transmitter.os, db.transmitter.serial
              )

    links = [
        lambda row: viewButton('transmitter', 'index', [row.id]),
        lambda row: editButton('transmitter', 'update', [row.id]),
    ]

    transmitters = SQLFORM.grid(
        db.transmitter, orderby=db.transmitter.name, user_signature=False, editable=False, details=False, maxtextlength=255, create=True, deletable=False, links=links, fields=fields, _class='itemlist-grid'
    )

    response.view = 'content.html'

    return dict(content=transmitters, header=response.title)


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

    response.view = 'content.html'

    return dict(content=form)


