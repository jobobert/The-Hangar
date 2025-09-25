def index():

    response.title = 'Library'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    query = db.article
    tagname = ""
    if request.vars.t:
         query = (db.article.tags.contains(request.vars.t))
         tagname = db(db.tag.id == request.vars.t).select().first().name

    #fields = []
    #fields.append(Field('tags', label=db.model.modeltype.label, requires=IS_EMPTY_OR(db.model.modeltype.requires), required=False))

    articles = db(query).iterselect(orderby=db.article.name)
    tags = db(db.tag).select(orderby=db.tag.name)

    return dict(articles=articles, tags=tags, tagname=tagname)


def update():

    response.title = 'Add/Update Article'

    buttons=[DIV(INPUT(_type='submit', _value='Submit'), _class='pl-5 p-2 fixed-bottom')]

    form = SQLFORM(db.article, request.args(0), upload=URL(
        'default', 'download'), deletable=True, showid=False, buttons=buttons, _id='articleform')
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'

    if form.process().accepted:
        response.flash = 'Article %s' % (
            'updated' if request.args else 'added')
        redirect(URL('library', 'read', args=form.vars.id,
                 extension="html") or session.ReturnHere)
    elif form.errors:
        response.flash = "Error Adding Article"
    else:
        pass  # response.flash = "somethign happened"

    print(form.errors)

    response.view = 'content.html'

    return dict(content=form)


def read():
    response.title = 'Read Article'

    article = db.article(request.args(0)) or redirect(URL('library', 'index'))

    return dict(article=article)

def search():
    finalresults = []

    # Library Query
    query = (db.article.name.like('%' + request.vars.s + '%')
             | db.article.summary.like('%' + request.vars.s + '%')
             | db.article.notes.like('%' + request.vars.s + '%')
             )

    results = db(query).select(db.article.id, db.article.img, db.article.name,
                               db.article.summary, db.article.articletype, db.article.tags, orderby=db.article.name)

    for res in results:
        finalresults.append({
            #"type": "article", "name": res.name, "url": URL('library', 'read', args=res.id), "img": IMG(_src=URL('default', 'download', args=res.img), _alt='Image', _width='65px', _onerror="this.src = '" + URL('static', 'icons/nopicture.png') + "'"), "desc": "" if res.summary == None else " ".join(res.summary.split()[:30]), "state": "", "tag": res.articletype
            "type": res.articletype, 
            "name": res.name, 
            "url": URL('library', 'read', args=res.id), 
            "img": library_type_icon(res, 24), 
            "desc": "" if res.summary == None else " ".join(res.summary.split()[:30]), 
            "state": "", 
            "tags": res.tags
        })

    # response.view = 'content.html'
    if len(finalresults) == 1:  # Auto redirect if there is only 1 result
        redirect(finalresults[0]['url'])
    else:
        return dict(searchtext=request.vars.s, finalresults=finalresults)
