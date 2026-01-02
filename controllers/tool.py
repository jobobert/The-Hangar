

def index():
    response.title = 'Tools'

    tool_id = VerifyTableID('tool', request.args(0)) or redirect(URL('tool', 'listview'))

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    tools = db(db.tool.id == tool_id).select() 

    models = models_and_tools(
        db.tool.id == tool_id).select(db.model.id, db.model.name, db.model.img)

    return dict(tools=tools, models=models)


def listview():

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    tools = db(db.tool).select(orderby=db.tool.tooltype | db.tool.name)
    return dict(tools=tools)


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

    return dict(form=form)

def rendercard():

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='tool', title='Tools')

    addfields = ['tool', 'purpose']
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

def renderexport():

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        response.view = 'rendercarderror.load'
        return dict(content='Unable to locate the associated model', controller='tool', title='Tools')
    
    tools = db(db.model_tool.model == model_id).select() or None

    torender = {
        'title': 'Tools',
        'items': [],
        'emptymsg': 'No tools assigned to this model',
        'controller': 'tool',
        'header': None,
    }
    for tool in tools or []:
        t = tool.tool
        content = {
            'name': t.name,
            'img': t.img,
            'attachment': t.attachment,
            'details': []
        }
        content['details'] = [
            (getattr(db.tool,'tooltype').label, t.tooltype),
            (getattr(db.tool,'notes').label, t.purpose or 'No purpose specified'),
        ]

        torender['items'].append(content)

    response.view = 'renderexport.load'
    return dict(content=torender)


def removefrommodel():
    # try to do this via ajax sometime...

    VerifyTableID('model', request.args(0)) or redirect(URL('default', 'index'))
    relationship_id = VerifyTableID('model_tool', request.args(1))  or redirect(URL('default', 'index'))

    if relationship_id:
        db(db.model_tool.id == relationship_id).delete()

    redirect(URL('model', 'index.html', args=model_id))

def delete():
    tool_id = VerifyTableID('tool', request.args(0)) or redirect(URL('tool', 'listview'))

    #if db(db.model_tool.tool == tool_id).count() > 0:
    if db(db.model_tool.tool == tool_id).select(db.model_tool.id, limitby=(0,1)).first():
        response.flash = "Cannot delete: tool is assigned to models!"
        redirect(session.ReturnHere or URL('tool', 'listview'))

    db(db.tool.id == tool_id).delete()
    response.flash = "Deleted"
    redirect(session.ReturnHere or URL('tool', 'listview'))