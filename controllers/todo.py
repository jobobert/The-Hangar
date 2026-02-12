

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
    model_id = None
    todo_query = db(db.todo.complete == False)
    
    if request.args:
        model_id = VerifyTableID('model', request.args(0))
        if model_id:
            todo_query = db((db.todo.model == model_id) &
                        (db.todo.complete == False))
    
    todo_count = todo_query.count()

    form = SQLFORM(db.todo, submit_button='Add')
    for s in form.elements('input', _type='text'):
        s['_autocomplete'] = 'off'
    form.vars.model = model_id
    if form.process(session=None, formname='todoform').accepted:
        response.flash = "New Todo Added"
    elif form.errors:
        response.flash = "Error Adding New Todo " + str(form.errors)

    del_id = 0
    completeform = SQLFORM.factory()
    if completeform.process(session=None, formname='todocompleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.todo.id == del_id).update(complete=True)
                response.flash = "Todo Completed"
    elif completeform.errors:
        response.flash = "Todo Completion Failure " + str(completeform.errors)

    todos = todo_query.select()

    return dict(todos=todos, model_id=model_id, todo_count=todo_count, options=request.args(1), completeform=completeform)

 
def complete():
    # try to do this via ajax sometime...

    model_id = VerifyTableID('model', request.args(0)) 
    if not model_id:
        return redirect(session.ReturnHere or URL('todo', 'listview'))
    todo_id = VerifyTableID('todo', request.args(1)) 

    if todo_id:
        db(db.todo.id == todo_id).update(complete=True)

    redirect(session.ReturnHere or URL('todo', 'index', args=model_id))


def listview():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    activemodels = db(db.model.modelstate > 1)._select(db.model._id)

    todo_query = db((db.todo.complete == False)
                    & (db.todo.model.belongs(activemodels))
                   )

    todos = todo_query.select(orderby=db.todo.model | db.todo.todo)
    return dict(todos=todos)

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

def renderexport():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
            response.view = 'rendercarderror.load'
            return dict(content='Unable to locate the associated model', controller='todo', title='Todos')

    todos = db((db.todo.model == model_id) &
            (db.todo.complete == False)).select() or None

    torender = {
        'title': 'Todos',
        'items': [],
        'emptymsg': 'No todos assigned to this model',
        'controller': 'todo',
        'header': None,
    }
    for todo in todos or []:
        torender['items'].append((
            f"{todo.todo}{' (Critical)' if todo.critical else ''}", 
            MARKMIN(todo.notes) if todo.notes else 'No Notes'
        ))

    response.view = 'renderexport.load'
    return dict(content=torender)