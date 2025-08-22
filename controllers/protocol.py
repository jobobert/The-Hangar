
def index():
    response.title = 'Protocols'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    grid = SQLFORM.grid(db.protocol, create=True, editable=True, deletable=True, details=False, csv=False, user_signature=False)
    
    response.view = 'content.html'
    
    return dict(content=grid)

def update():
    response.title = 'Add/Update Protocol'

    form = SQLFORM(db.protocol, request.args(0), upload=URL('default', 'download'), _id='protocolform')
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