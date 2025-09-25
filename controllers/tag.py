def listview():

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    response.title = 'Tag List'

    fields=[db.tag.name]

    tags = SQLFORM.grid(db.tag, user_signature=False, fields=fields, editable=True, deletable=True, details=False, create=True, csv=False)


    response.view = 'content.html'

    return dict(content=tags, header=response.title)

def rendertags():
    pass