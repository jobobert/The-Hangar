
def index():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    response.title = 'Protocol'

    protocol_id = VerifyTableID('protocol', request.args(0)) or redirect(URL('protocol', 'listview'))
    
    protocol = db.protocol(protocol_id) or redirect(URL('default', 'index'))

    models = db(db.model.protocol == protocol_id).select()
    transmitters = db(db.transmitter.protocol.contains(protocol_id)).select()
    
    return dict(protocol=protocol, models=models, transmitters=transmitters)

def listview():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    protocols = db(db.protocol).select()
    return dict(protocols=protocols)


def update():
    response.title = 'Add/Update Protocol'

    form = SQLFORM(db.protocol, request.args(0), upload=URL('default', 'download'), _id='protocolform', showid=False, deletable=True)
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'
    if form.process().accepted:
        session.flash = "Protocol Added/Updated"
        redirect(URL('protocol', 'index', extension="html"))
    elif form.errors:
        response.flash = "Error Adding/Updating Protocol"
    else:
        pass
    
    return dict(form=form)