def index():
    rigId = request.args(0)
    rig = db(db.sailrig.id == rigId).select(
    ).first() or redirect(URL('sailrig', 'listview'))

    response.title = "Sail Rig " + rig.rigname

    model = db(db.sailrig.id == rigId).select(
        db.sailrig.model).first()

    return dict(rig=rig, model=model)


def listview():
    response.title = 'Sail Rig List'

    fields = (db.sailrig.rigname, db.sailrig.img,
              db.sailrig.notes, db.sailrig.model)

    links = [
        lambda row: A('Details', _href=URL('sailrig', 'index',
                      args=[row.id]), _class="btn btn-primary"),
        lambda row: A('Edit', _href=URL('sailrig', 'update',
                      args=[row.id]), _class="btn btn-secondary")
    ]

    sailrigs = SQLFORM.grid(
        db.sailrig, orderby=db.sailrig.model | db.sailrig.rigname, editable=False, details=False, maxtextlength=255, user_signature=False, create=False, deletable=False, links=links, fields=fields, _class='itemlist-grid'
    )

    response.view = 'content.html'

    return dict(content=sailrigs)


def update():
    response.title = "Add/Update Sail Rig"

    form = SQLFORM(db.sailrig, request.args(0), deletable=True, showid=False).process(
        message_onsuccess='Rig %s' % ('updated' if request.args else 'added'),
        next=(URL('sailrig', 'index', args=request.vars.id, extension='html'))
    )
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    response.view = 'content.html'

    return dict(content=form)


def rendercard():
    modelid = request.args(0)

    newFields = ['rigname', 'notes']
    newform = SQLFORM(db.sailrig, fields=newFields,
                      showid=False, formstyle='bootstrap4_inline')
    newform.vars.model = modelid
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

    rig_query = db(db.sailrig.model == modelid)
    rig_count = rig_query.count()
    model_rigs = rig_query.select()

    return dict(model_rigs=model_rigs, modelid=modelid, newform=newform, deleteform=deleteform, rig_count=rig_count)
