

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

    disable_autocomplete(form)

    return dict(form=form)

def renderexport():
    session.forget(response)
    transmitter_id = VerifyTableID('transmitter', request.args(0))

    if not transmitter_id:
            return render_card_error('Unable to locate the associated transmitter', 'transmitter', 'Transmitter')

    if transmitter_id:
        transmitter = db(db.transmitter.id == transmitter_id).select().first() or None

    if not transmitter:
        return render_card_error('Unable to locate the associated transmitter', 'transmitter', 'Transmitter')

    torender = {
        'title': 'Transmitter',
        'items': [],
        'emptymsg': 'No Transmitter',
        'controller': 'transmitter',
        'header': None,
    }

    content = {
            'name': f"{transmitter.name} {'(' + transmitter.nickname + ')' if transmitter.nickname else ''}",
            'img': transmitter.img,
            'attachment': transmitter.attachment, 
            'details': [
                (getattr(db.transmitter,'manufacturer').label, transmitter.manufacturer),
                (getattr(db.transmitter,'model').label, transmitter.model),
                (getattr(db.transmitter,'serial').label, transmitter.serial),
                (getattr(db.transmitter,'protocol').label, transmitter.get_protocollist()),
                (getattr(db.transmitter,'processor').label, transmitter.processor),
                (getattr(db.transmitter,'os').label, transmitter.os),
                (getattr(db.transmitter,'os_version').label, transmitter.os_version),
                (getattr(db.transmitter,'radio_firmware').label, transmitter.radio_firmware),
                (getattr(db.transmitter,'firmware_version').label, transmitter.firmware_version),
                #(getattr(db.transmitter,'notes').label, MARKMIN(transmitter.notes)),
            ]
        }

    torender['items'].append(content)

    response.view = 'renderexport.load'
    return dict(content=torender)