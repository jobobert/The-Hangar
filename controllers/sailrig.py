def index():
    rig_id = VerifyTableID('sailrig', request.args(0)) or redirect(URL('sailrig', 'listview'))
    rig = db(db.sailrig.id == rig_id).select(
    ).first() or redirect(URL('sailrig', 'listview'))

    response.title = "Sail Rig " + rig.rigname

    model = db(db.sailrig.id == rig_id).select(
        db.sailrig.model).first()

    return dict(rig=rig, model=model)


def listview():
    response.title = 'Sail Rig List'

    fields = (db.sailrig.rigname, db.sailrig.img,
              db.sailrig.notes, db.sailrig.model)

    links = [
        lambda row: viewButton('sailrig', 'index', [row.id]),
        lambda row: editButton('sailrig', 'update', [row.id]),
    ]

    sailrigs = SQLFORM.grid(
        db.sailrig, orderby=db.sailrig.model | db.sailrig.rigname, editable=False, details=False, maxtextlength=255, user_signature=False, create=False, deletable=False, links=links, fields=fields, _class='itemlist-grid'
    )

    response.view = 'content.html'

    return dict(content=sailrigs, header=response.title)


def update():
    response.title = "Add/Update Sail Rig"

    form = SQLFORM(db.sailrig, request.args(0), upload=URL('default', 'download'), deletable=True, showid=False).process(
        formname='updateform',
        message_onsuccess='Rig %s' % ('updated' if request.args else 'added'),
        next=(URL('sailrig', 'index', args=request.vars.id, extension='html'))
    )
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    return dict(form=form)


def delete():
    sailrig_id = VerifyTableID('sailrig', request.args(0)) or redirect(URL('sailrig', 'listview'))

    db(db.sailrig.id == sailrig_id).delete()
    response.flash = "Deleted"
    return redirect(session.ReturnHere or URL('sailrig', 'listview'))


def rendercard():
    modelid = request.args(0)
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='sailrig', title='Sail Rigs')

    newFields = ['rigname', 'notes']
    newform = SQLFORM(db.sailrig, fields=newFields,
                      showid=False, formstyle='bootstrap4_inline')
    newform.vars.model = model_id
    if newform.process(session=None, formname='newform').accepted:
        response.flash = 'Rig Added'
    elif newform.errors:
        response.flash = newform.errors

    delid = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='deleteform').accepted:
        response.flash = 'Removal Success'
    elif deleteform.errors:
        response.flash = 'Removal Failure'

    rig_query = db(db.sailrig.model == model_id)
    rig_count = rig_query.count()
    model_rigs = rig_query.select()

    return dict(model_rigs=model_rigs, modelid=model_id, newform=newform, deleteform=deleteform, rig_count=rig_count)
