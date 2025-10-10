def listview():

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    response.title = 'Tag List'

    fields=[db.tag.name]
    
    links = [
        lambda row: editButton('tag', 'update', [row.id]),
        lambda row: deleteButton('tag', 'delete', [row.id])
    ]
    grid = SQLFORM.grid(db.tag, links=links, fields=fields, create=True, editable=False, deletable=False, details=False, csv=False, user_signature=False)

    response.view = 'content.html'
    return dict(content=grid, header=response.title)

def update():
    response.title = 'Add/Update Tag'

    form = SQLFORM(db.tag, request.args(0), upload=URL('default', 'download'), _id='tagform', showid=False, deletable=True)
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'
    if form.process().accepted:
        session.flash = "Tag Added/Updated"
        redirect(URL('tag', 'listview', extension="html"))
    elif form.errors:
        response.flash = "Error Adding/Updating Tag"
    else:
        pass
    
    return dict(form=form)

def delete():
    tag_id = VerifyTableID('tag', request.args(0))

    if tag_id:
        response.flash = "Tag deleted"
        db(db.tag.id == tag_id).delete()
    else:
        response.flash = "Could not delete: tag not found"
    
    redirect(session.ReturnHere or URL('tag', 'listview'))

def rendertags():
    pass