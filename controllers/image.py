def index():

    response.title = 'Images'
    
    fields = []
    fields.append(Field('text', labels={'text':''}))#, widget=widget))

    form = SQLFORM.factory(*fields, formstyle='ul', keepvalues=True, _class='form-inline')#, table_name='tag-filter')
    disable_autocomplete(form)

    queries = []

    if form.process(message_onsuccess=None).accepted:
        if form.vars.text:
            queries.append(db.images.tags.contains(form.vars.text))
        else:
            queries.append(db.images)
    else:
        queries.append(db.images)

    query = reduce(lambda a, b: (a & b), queries)

    images = db(query).select()

    return dict(images=images, form=form)

def update():

    response.title = 'Add/Update Image'

    form = SQLFORM(db.images, request.args(0), upload=URL('default', 'download'), _id='imageform')
    disable_autocomplete(form)
    if form.process().accepted:
        session.flash = "Image Added/Updated"
        redirect(URL('image', 'index', extension="html"))
    elif form.errors:
        response.flash = "Error Adding/Updating Image"
    else:
        pass
    
    response.view = 'content.html'
    
    return dict(content=form)
