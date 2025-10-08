
def rendercard():
    
    model_id = request.args[0]

    fields = ["name", "attachmenttype", "attachment"]

    form = SQLFORM(db.attachment, model=model_id, fields=fields, comments=False)
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'
    form.vars.model = model_id
    if form.process(formname='attachmentform').accepted:
        response.flash = "New Attachment Added"
    elif form.errors:
        response.flash = "Error Adding New Attachment"
 
    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='attachmentdeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.attachment.id == del_id).delete()
                response.flash = "Removal Success"
                #response.flash = str(del_id) + " Removal Success"
    elif deleteform.errors:
        response.flash = "Removal Failure"

    attachment_query = db(db.attachment.model == model_id)
    attachment_count = attachment_query.count()
    attachments = attachment_query.select()

    return dict(attachments=attachments, model_id=model_id, attachment_count=attachment_count, options=request.args(1), form=form, deleteform=deleteform)


def new():
    model_id = request.args[0]

    form = SQLFORM(db.attachment, model=model_id)
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'
    form.vars.model = model_id
    if form.process(formname='attachmentform').accepted:
        response.flash = "New Attachment Added"

        #redirect(URL('default', 'breadcrumb_back'))
        redirect(session.ReturnHere or URL('model', 'index', args=model_id))

    elif form.errors:
        response.flash = "Error Adding New Attachment"

    response.view = 'content.html'

    return dict(content=form)


def update():

    response.title = "Add/Update Attachment"

    form = SQLFORM(db.attachment, request.args(0), upload=URL(
        'default', 'download'), deletable=True, showid=False).process(
        message_onsuccess='Document %s' % (
            'updated' if request.args else 'added'), next=(URL('attachment', 'index', args=request.vars.id, extension="html"))
    )
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    response.view = 'content.html'
    return dict(content=form)


def remove():
    # try to do this via ajax sometime...

    #session.forget(response)

    model_id = request.args[0]
    attachment_id = request.args[1]

    db(db.attachment.id == attachment_id).delete()

    #breadcrumb_back()
    #redirect(URL('default', 'breadcrumb_back'))
    #redirect(URL('model', 'index', args=model_id))
    return redirect(session.ReturnHere or URL('model', 'index', args=model_id))
