def listview():

    tags = db(db.tag).select()
    return dict(tags=tags)

def update():
    response.title = 'Add/Update Tag'

    form = SQLFORM(db.tag, request.args(0), upload=URL('default', 'download'), _id='tagform', showid=False)
    disable_autocomplete(form)
    if form.process().accepted:
        session.flash = "Tag Added/Updated"
        redirect(URL('tag', 'listview', extension="html"))
    elif form.errors:
        response.flash = "Error Adding/Updating Tag"
    else:
        pass
    
    return dict(form=form)
