def index():

    response.title = 'Library'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    includeComponents = True
    query = db.article
    tagname = ""
    if request.vars.t:
         query = (db.article.tags.contains(request.vars.t))
         tagname = db(db.tag.id == request.vars.t).select().first().name
         includeComponents = False
    if request.vars.b:
        query = (db.article.articletype == 'Book')
        tagname = 'book'
        includeComponents = False
    
    results = []

    #articles = db(query).iterselect(db.article.id, db.article.name, db.article.articletype, db.article.img, db.article.summary, db.article.attachment,orderby=db.article.name)
    articles = db(query).iterselect(orderby=db.article.name)
    for a in articles:
        results.append({
            "id" : a.id,
            "name" : a.name,
            "articletype" : a.articletype,
            "img" : a.img,
            "summary" : a.summary,
            "attachment" : a.attachment,
            "tags": a.tags,
            "controller": "library"
        })
    
    if includeComponents:
        components = db(db.component).select(orderby=db.component.name)
        for ca in components:
            if ispdf(ca.attachment):
                results.append({
                    "id" : ca.id,
                    "name" : ca.name,
                    "articletype" : 'attachment',
                    "img" : ca.img,
                    "summary" : ca.componenttype,
                    "attachment" : ca.attachment,
                    "tags": [],
                    "controller": "component"
                })
        transmitters = db(db.transmitter).select(orderby=db.transmitter.name)
        for ca in transmitters:
            if ispdf(ca.attachment):
                results.append({
                    "id" : ca.id,
                    "name" : ca.name,
                    "articletype" : 'attachment',
                    "img" : ca.img,
                    "summary" : "",
                    "attachment" : ca.attachment,
                    "tags": [],
                    "controller": "transmitter"
                })

        tools = db(db.tool).select(orderby=db.tool.name)
        for ca in tools:
            if ispdf(ca.attachment):
                results.append({
                    "id" : ca.id,
                    "name" : ca.name,
                    "articletype" : 'attachment',
                    "img" : ca.img,
                    "summary" : ca.tooltype,
                    "attachment" : ca.attachment,
                    "tags": [],
                    "controller": "tool"
                })
            
    tags = db(db.tag).select(orderby=db.tag.name)

    return dict(articles=sorted(results, key=lambda x: x['name']), tags=tags, tagname=tagname)


def index_old():

    response.title = 'Library'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    query = db.article
    tagname = ""
    if request.vars.t:
         query = (db.article.tags.contains(request.vars.t))
         tagname = db(db.tag.id == request.vars.t).select().first().name

    articles = db(query).iterselect(db.article.id, db.article.name, db.article.articletype, db.article.img, db.article.summary, db.article.attachment,orderby=db.article.name)
    tags = db(db.tag).select(orderby=db.tag.name)
    
    componentsWithPDFs = db(db.component.hasPDFAttachment == True).select(orderby=db.component.name)

    temp_db = DAL('sqlite://:memory:')
    temp_db.define_table('compTable', Field('name'), Field('articletype'), Field('img', type='upload'), Field('summary'), Field('attachment', type='upload'), migrate=True)
    for ca in componentsWithPDFs:
        temp_db.compTable.insert(name=ca.name, articletype='Component', img=ca.img, summary=ca.componenttype, attachment=ca.attachment)

    compTable = temp_db(temp_db.compTable).select()
    union = articles.union(compTable)

    return dict(articles=union, tags=tags, tagname=tagname)


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
