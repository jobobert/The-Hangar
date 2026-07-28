def rendercard():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'model_model', 'Related Models')

    addform = SQLFORM(db.model_model, fields=['model_b', 'notes'],
                     formstyle='bootstrap4_inline', submit_button='Add')
    addform.vars.model_a = model_id
    if addform.process(session=None, formname='modelmodelform').accepted:
        if addform.vars.model_b == model_id:
            db(db.model_model.id == addform.vars.id).delete()
            response.flash = 'A model cannot be related to itself'
        else:
            response.flash = 'Related model added'
    elif addform.errors:
        response.flash = 'Error adding related model'

    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='modelmodeldeleteform').accepted:
        for y, z in request.vars.items():
            if z == 'Remove':
                db(db.model_model.id == y).delete()
                response.flash = 'Relationship removed'
    elif deleteform.errors:
        response.flash = 'Removal failed'

    rel_query = db(
        (db.model_model.model_a == model_id) | (db.model_model.model_b == model_id)
    )
    related   = rel_query.select()
    rel_count = rel_query.count()

    return dict(related=related, rel_count=rel_count, model_id=model_id,
                addform=addform, deleteform=deleteform)


def update():
    response.title = 'Edit Relationship Notes'

    rel_id = VerifyTableID('model_model', request.args(0))
    if not rel_id:
        session.flash = 'Invalid relationship ID'
        redirect(URL('default', 'index'))

    form = SQLFORM(db.model_model, rel_id, fields=['notes'], showid=False).process()
    if form.accepted:
        rel = db.model_model(rel_id)
        model_id = rel.model_a if rel else None
        redirect(URL('model', 'index', args=model_id, extension='html'))

    disable_autocomplete(form)
    return dict(form=form)


def delete():
    rel_id = VerifyTableID('model_model', request.args(0))
    if rel_id:
        rel = db.model_model(rel_id)
        model_id = rel.model_a if rel else None
        db(db.model_model.id == rel_id).delete()
        session.flash = 'Relationship removed'
        redirect(URL('model', 'index', args=model_id, extension='html'))
    else:
        session.flash = 'Invalid relationship ID'
        redirect(URL('default', 'index'))
