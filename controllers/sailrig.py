def index():
    rig_id = VerifyTableID('sailrig', request.args(0)) or redirect(URL('sailrig', 'listview'))
    rig = db(db.sailrig.id == rig_id).select(
    ).first() or redirect(URL('sailrig', 'listview'))

    response.title = "Sail Rig " + rig.rigname

    model = db(db.sailrig.id == rig_id).select(
        db.sailrig.model).first()

    return dict(rig=rig, model=model)


def listview():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    activemodels = db(db.model.modelstate > 1)._select(db.model._id)

    sailrigs = db(db.sailrig.model.belongs(activemodels)).select(orderby=db.sailrig.model | db.sailrig.rigname)
    return dict(sailrigs=sailrigs)


def update():
    response.title = "Add/Update Sail Rig"

    form = SQLFORM(db.sailrig, request.args(0), upload=URL('default', 'download'), deletable=True, showid=False).process(
        formname='updateform',
        message_onsuccess='Rig %s' % ('updated' if request.args else 'added'),
        next=(URL('sailrig', 'index', args=request.vars.id, extension='html'))
    )
    disable_autocomplete(form)

    return dict(form=form)


def delete():
    sailrig_id = VerifyTableID('sailrig', request.args(0)) or redirect(URL('sailrig', 'listview'))

    db(db.sailrig.id == sailrig_id).delete()
    session.flash = "Deleted"
    return redirect(session.ReturnHere or URL('sailrig', 'listview'))


def rendercard():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'sailrig', 'Sail Rigs')

    newFields = ['rigname', 'notes']
    newform = SQLFORM(db.sailrig, fields=newFields,
                      showid=False, formstyle='bootstrap4_inline')
    newform.vars.model = model_id
    if newform.process(session=None, formname='newform').accepted:
        response.flash = 'Rig Added'
    elif newform.errors:
        response.flash = newform.errors

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='deleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.sailrig.id == del_id).delete()
        response.flash = 'Removal Success'
    elif deleteform.errors:
        response.flash = 'Removal Failure'

    rig_query = db(db.sailrig.model == model_id)
    rig_count = rig_query.count()
    model_rigs = rig_query.select()

    return dict(model_rigs=model_rigs, modelid=model_id, newform=newform, deleteform=deleteform, rig_count=rig_count)

def renderexport():
    session.forget(response)
    """
    Render Sail Rig export for a given model
    """

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'sailrig', 'Sail Rig Export')

    sailrigs = db(db.sailrig.model == model_id).select() or None

    torender = {
        'title': 'Sail Rig',
        'items': [],
        'emptymsg': 'No sails are associated with this model',
        'controller': 'sailrig',
        'header': None,
    }
    for rig in sailrigs or []:
        content = {
            'name': rig.rigname,
            'img': rig.img,
            'attachment': None,
            'details': []
        }
        content['details'] = [
            (getattr(db.sailrig,'notes').label, MARKMIN(rig.notes) if rig.notes else '')
        ]

        torender['items'].append(content)

    response.view = 'renderexport.load'
    return dict(content=torender)
