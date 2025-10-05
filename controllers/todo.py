

def renderlist():
    
    activemodels = db(db.model.modelstate > 1)._select(db.model._id)

    if request.args(0) == 'dashboard':
        todo_query = db((db.todo.complete == False)
                        & (db.todo.critical == True)
                        & (db.todo.model.belongs(activemodels))
                        )
    else:
        todo_query = db((db.todo.complete == False)
                        & (db.todo.model.belongs(activemodels))
                        )

    todo_count = todo_query.count()
    todos = todo_query.select(orderby=db.todo.model.name)

    return dict(todos=todos, todo_count=todo_count, options=request.args(0))


def rendercard():
    
    if request.args:
        model_id = request.args[0]
        todo_query = db((db.todo.model == model_id) &
                        (db.todo.complete == False))
    else:
        model_id = -1
        todo_query = db(db.todo.complete == False)

    todo_count = todo_query.count()

    form = SQLFORM(db.todo, submit_button='Add')
    for s in form.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    form.vars.model = model_id
    if form.process(session=None, formname='todoform').accepted:
        response.flash = "New Todo Added"
    elif form.errors:
        response.flash = "Error Adding New Todo"

    del_id = 0
    completeform = SQLFORM.factory()
    if completeform.process(session=None, formname='todocompleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.todo.id == del_id).update(complete=True)
                response.flash = "Todo Completed"
                #response.flash = str(del_id) + " Removal Success"
    elif completeform.errors:
        response.flash = "Todo Completion Failure"

    todos = todo_query.select()

    return dict(todos=todos, model_id=model_id, todo_count=todo_count, options=request.args(1), completeform=completeform)


def complete():
    # try to do this via ajax sometime...
    # session.forget(response)

    model_id = request.args[0]
    todo_id = request.args[1]
    #response.flash = todo_id
    db(db.todo.id == todo_id).update(complete=True)

    # return redirect(URL('todo', 'index', args=todo_id, extension="html"))
    redirect(session.ReturnHere or URL('todo', 'index', args=model_id))


def listview():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    response.title = 'Todo List'

    activemodels = db(db.model.modelstate > 1)._select(db.model._id)

    todo_query = db((db.todo.complete == False)
                    & (db.todo.model.belongs(activemodels))
                    )
    fields = (
        db.todo.model, db.todo.todo, db.todo.critical, db.todo.notes
    )

    links = [
        lambda row: completeButton('todo', 'complete', [None, row.id]),
        lambda row: editButton('todo', 'update', [row.id]),
    ]
    todos = SQLFORM.grid(
        todo_query, user_signature=False, editable=False, deletable=False, details=False, create=False, fields=fields, links=links, maxtextlength=255
    )

    response.view = 'content.html'

    return dict(content=todos, header=response.title)


def update():
 
    response.title = 'Add/Update Todo'

    form = SQLFORM(db.todo, request.args(0), upload=URL('default', 'download'), deletable=True, showid=False).process(
        message_onsuccess='Document %s' % ('updated' if request.args else 'added'),
        next=(URL('todo', 'listview', args=request.vars.id, extension="html"))
    )

    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    return dict(form=form)

def newmodal():
    # This is the controller to create a new todo in a modal...
    #return dict(content="Need to make this happen...")

    fields = ["todo", "model", "critical", "notes"]

    form = SQLFORM(db.todo, deletable=False, showid=False, fields=fields).process(
        message_onsuccess='Document %s' % (
            'updated' if request.args else 'added')
        #,next=(URL('todo', 'listview', args=request.vars.id, extension="html"))
    )

    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    return dict(content=form)
