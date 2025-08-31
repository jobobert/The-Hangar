
def index():
    response.title = 'Protocol'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)
    
    protocol = db.protocol(request.args(0)) or redirect(URL('default', 'index'))

    #response.view = 'content.html'
    
    return dict(protocol=protocol)

def listview():
    response.title = 'Protocols'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)
    
    links = [
        lambda row: A('Details', _href=URL('protocol', 'index', args=[row.id]), _class='btn btn-primary'),
        lambda row: A('Edit', _href=URL('protocol', 'update', args=[row.id]), _class='btn btn-secondary'), 
    ]

    grid = SQLFORM.grid(db.protocol, links=links, create=True, editable=False, deletable=False, details=False, csv=False, user_signature=False)
    
    response.view = 'content.html'
    
    return dict(content=grid)

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
    
    response.view = 'content.html'
    
    return dict(content=form)