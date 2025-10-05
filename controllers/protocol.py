
def index():
    response.title = 'Protocol'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)
    
    protocol = db.protocol(request.args(0)) or redirect(URL('default', 'index'))

    models = db(db.model.protocol == request.args(0)).select()
    transmitters = db(db.transmitter.protocol.contains(request.args(0))).select()

    #response.view = 'content.html'
    
    return dict(protocol=protocol, models=models, transmitters=transmitters)

def listview():
    response.title = 'Protocols'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)
    
    links = [
        lambda row: viewButton('protocol', 'index', [row.id]),
        lambda row: editButton('protocol', 'update', [row.id]),
    ]

    grid = SQLFORM.grid(db.protocol, links=links, create=True, editable=False, deletable=False, details=False, csv=False, user_signature=False)
    
    response.view = 'content.html'
    
    return dict(content=grid, header=response.title)

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