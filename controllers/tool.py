

def index():
    response.title = 'Tools'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    tool_id = request.args(0)
    tools = db(db.tool.id == tool_id).select(
    ) or redirect(URL('tool', 'listview'))

    models = models_and_tools(
        db.tool.id == tool_id).select(db.model.id, db.model.name, db.model.img)

    return dict(tools=tools, models=models)


def listview():
    response.title = 'Tool List'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    # db.tool.img
    fields = (db.tool.img, db.tool.tooltype, db.tool.name
              )

    links = [
        lambda row: viewButton('tool', 'index', [row.id]),
        lambda row: editButton('tool', 'update', [row.id]),
    ]

    tools = SQLFORM.grid(
        db.tool, orderby=db.tool.tooltype, user_signature=False, editable=False, details=False, maxtextlength=255, create=False, deletable=False, links=links, fields=fields, _class='itemlist-grid'
    )

    response.view = 'content.html'

    return dict(content=tools, header=response.title)


def update():

    response.title = 'Add/Update Tool'

    form = SQLFORM(db.tool, request.args(0), upload=URL(
        'default', 'download'), deletable=True, showid=False).process(
        message_onsuccess='Tool %s' % (
            'updated' if request.args else 'added'))

    if form.accepted:
        redirect(URL('tool', 'index', args=form.vars.id,
                 extension="html") or session.ReturnHere)

    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    response.view = 'content.html'

    return dict(content=form)


def rendercard():
    # session.forget(response)
    model_id = request.args[0]

    addfields = ['tool']
    addform = SQLFORM(db.model_tool, fields=addfields,
                      formstyle='bootstrap4_inline', submit_button='Add')
    addform.vars.model = model_id
    if addform.process(session=None, formname='addtool').accepted:
        response.flash = "Tool added to model"
    elif addform.errors:
        response.flash = "Error adding tool to model"

    newform = SQLFORM(db.tool, showid=False, formstyle='bootstrap4_inline')
    inputs = newform.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'
    if newform.process(session=None, formname='newtool').accepted:
        # add to model_tool
        db.model_tool.insert(model=model_id, tool=newform.vars.id)
        redirect(request.env.http_web2py_component_location, client_side=True)
    elif newform.errors:
        response.flash = "Error Creating New Tool"

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='tooldeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.model_tool.id == del_id).delete()
                response.flash = "Removal Success"
                #response.flash = str(del_id) + " Removal Success"

    elif deleteform.errors:
        response.flash = "Removal Failure"

    tool_query = db(db.model_tool.model == model_id)
    tool_count = tool_query.count()
    model_tools = tool_query.select()

    # ,other=other)
    return dict(model_tools=model_tools, model_id=model_id, addform=addform, newform=newform, deleteform=deleteform, tool_count=tool_count, options=request.args(1))


def removefrommodel():
    # try to do this via ajax sometime...
    # session.forget(response)

    model_id = request.args[0]
    relationship_id = request.args[1]
    db(db.model_tool.id == relationship_id).delete()

    return redirect(URL('model', 'index.html', args=model_id))
