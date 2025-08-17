from collections import deque

def breadcrumb_set(text):
    return
    if (not session.breadcrumb) or (len(session.breadcrumb) == 0):
        session.breadcrumb = deque()
        session.breadcrumb.append((text, request.env.request_uri))
        return
    else:
        if session.breadcrumb[-1][1] != request.env.request_uri:
            session.breadcrumb.append((text, request.env.request_uri))

def breadcrumb_show():
    return
    if session.breadcrumb and len(session.breadcrumb) > 1:
        if session.breadcrumb[-1][1] != request.env.request_uri:
                return A( "Return to  "
                ,B(session.breadcrumb[-1][0]),#,  " (" ,len(session.breadcrumb) - 2 ,")",
                    _href=URL('default', 'breadcrumb_back'))
        else:
            return A( "Return to  "
                ,B(session.breadcrumb[-2][0]),#,  " (" ,len(session.breadcrumb) - 2 ,")",
                _href=URL('default', 'breadcrumb_back')  )
    else:
        return ""



def model_type_icon(model, size):
    if size == 32:
        size = 32
    elif size == 48:
        size = 48
    else:
        size = 32
    icon_name = 'icons/' + model.modeltype.lower() + '-' + str(size) + '.svg'
    return IMG(_src=URL('static', icon_name), _alt=model.modeltype, _width=str(size), _height=str(size))

def model_powerplant_icon(model, size):
    if size == 32:
        size = 32
    elif size == 48:
        size = 48
    else:
        size = 32

    icon_name = 'icons/'

    if model.powerplant == 'Electric':
        icon_name = icon_name + 'th-m_electric-' + str(size) + '.svg'
    elif model.powerplant == 'Internal Combustion':
        icon_name = icon_name + 'th-m_ic-' + str(size) + '.svg'
    elif model.powerplant == 'Rocket':
        icon_name = icon_name + 'th-m_rocket-' + str(size) + '.svg'
    elif model.powerplant == 'Rubber':
        icon_name = icon_name + 'th-m_rubber-' + str(size) + '.svg'
    elif model.powerplant == 'Sail':
        icon_name = icon_name + 'th-m_sail-' + str(size) + '.svg'
    else:
        icon_name = icon_name + 'th-m_other-' + str(size) + '.svg'

    return IMG(_src=URL('static', icon_name), _alt=model.powerplant)

def model_control_icon(model, size):
    if size == 32:
        size = 32
    elif size == 48:
        size = 48
    else:
        size = 32

    icon_name = 'icons/'

    ('Radio Control', 'Free Flight', 'Control Line', 'Other')

    if model.controltype == 'Radio Control':
        icon_name = icon_name + 'th-c_rc-' + str(size) + '.svg'
    if model.controltype == 'Free Flight':
        icon_name = icon_name + 'th-c_freeflight-' + str(size) + '.svg'
    if model.controltype == 'Control Line':
        icon_name = icon_name + 'th-c_controlline-' + str(size) + '.svg'
    if model.controltype == 'Other':
        icon_name = icon_name + 'th-c_other-' + str(size) + '.svg'

    return IMG(_src=URL('static', icon_name), _alt=model.controltype)

def library_type_icon(article, size):
    if size == 32:
        size = 32
    elif size == 48:
        size = 32
    else:
        size = 32

    if article.articletype == 'Article':
        return IMG(_src=URL('static', 'icons/scroll.png'), _alt=article.articletype)
    elif article.articletype == 'Book':
        return IMG(_src=URL('static', 'icons/books.png'), _alt=article.articletype)
    if article.articletype == 'Idea':
        return IMG(_src=URL('static', 'icons/light-bulb.png'), _alt=article.articletype)
    else:
        return IMG(_src=URL('static', 'icons/help.png'), _alt=article.articletype)

def model_flowchart(model):
    return DIV('flowchart')

def filetype_icon(attachment, size):
    try:
        ext = attachment.attachment.split('.')[-1].lower()
    except:
        ext = attachment.split('.')[-1].lower()

    icon_name = 'icons/' + ext + '.png'
    return IMG(_src=URL('static', icon_name), _alt=ext, _width=str(size) + 'px', _height=str(size) + 'px')

def show_icon(iconname, size):
    thename = 'icons/' + iconname
    return IMG(_src=URL('static', thename), _alt='icon', _width=str(size) + 'px', _height=str(size) + 'px')

def isimage(attachment):
    try:
        ext = attachment.attachment.split('.')[-1]
    except:
        ext = attachment.split('.')[-1]
        
    imageExtensions = {
        'jpeg': True,
        'jpg': True,
        'gif': True,
        'png': True
    }
    return imageExtensions.get(ext, False)

def ispdf(attachment):
    try:
        ext = attachment.attachment.split('.')[-1]
    except:
        ext = attachment.split('.')[-1]

    return (ext == 'pdf')
        

def underConstructionModels():
    models = db((db.model.modelstate == 3) | (db.model.modelstate == 6)).select(
        db.model.id, db.model.name, db.model.img, db.model.description).as_list()

    m = []
    for i, model in enumerate(models):
        model['img'] = IMG(_src=URL('default', 'download', args=model['img'], scheme=True, host=True))

    return models

def activeModels():
    models = db((db.model.modelstate == 4) | (db.model.modelstate == 5)).select(
        db.model.id, db.model.name, db.model.img, db.model.description).as_list()

    m = []
    for i, model in enumerate(models):
        model['img'] = IMG(_src=URL('default', 'download', args=model['img'], scheme=True, host=True))
        #m = m + [model['img']]

    return models

def selectedModels():
    models = db(db.model.selected == True).select(
        db.model.name, db.model.img, db.model.description).as_list()

    m = []
    for i, model in enumerate(models):
        model['img'] = IMG(_src=URL('default', 'download', args=model['img'], scheme=True, host=True))
    
    return models

def theHangarStats():
    stats = {}

    # Get the States
    states = db(db.model).select(db.model.modelstate,
                                 db.model.id.count(), groupby=db.model.modelstate)
    for i, state in enumerate(states):
        state['stateid'] = state['model'].modelstate
        state['statename'] = state['model'].modelstate.name
        del state['model']
        state['count'] = state['_extra']['COUNT("model"."id")']
        del state['_extra']

    stats['states'] = states

    # Get todos
    critical_todos = db(
        (db.todo.complete == False) &
        (db.todo.critical == True)
        ).select(
        db.todo.model, db.todo.todo
    ).exclude(lambda row: row.model.modelstate != 1)

    for i, todo in enumerate(critical_todos):

        m = todo['model']
        todo['m'] = m.img

        todo['model'] = m.name
        todo['modelstate'] = m.modelstate.name
        todo['img'] = "<img src='" + URL('default', 'download', args=m.img, scheme=True, host=True) + "' />"
        
        
    total_todo_count = db(db.todo.complete == False).count()

    stats['todo_count'] = total_todo_count
    stats['todo_list'] = critical_todos

    return stats



def delete_file(row, uploadfield):
    # https://groups.google.com/g/web2py/c/hNYpxTsgk0E
    import os
    file = row(uploadfield)
    table, field, subfolder = file.split('.')[0:3]
    subfolder = subfolder[:2]
    upf = db[table][field].uploadfolder
    if not upf:
        upf = os.path.join(request.folder, 'uploads')
    os.remove(os.path.join(upf, '%s.%s' % (table, field), subfolder, file))
    row.update_record(**{uploadfield: None})


# def markmin_syntax():
#     html = DIV(
#         TABLE(
#             THEAD(
#                 TR(TH('Source'), TH('Output'))
#             ),
#             TBODY(
#                 TR(TD('# title'), TD(B('title'))),
#                 TR(TD('## secion'), TD(B('section'))),
#                 TR(TD('### subsection'), TD(B('subsection'))),
#                 TR(TD('**bold**'), TD()),
#                 TR(TD("''italic''"), TD(I('italic'))),
#                 TR(TD('~~strikout~~~'), TD(TAG.del ('strikeout'))),
#                 TR(TD('``verbatim``'), TD('verbatim')),
#                 TR(TD('``color with **bold **``:red'), TD(SPAN('color with', B('bold')))),
#                 TR(TD('``many colors``:color[blue:#ffff00]'), TD('many colors')),
#                 TR(TD('http://google.com'), TD(A('http://google.com', _href='http://google.com'))),

#             )
#         )
#     )
