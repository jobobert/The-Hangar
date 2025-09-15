from collections import deque
import os
from typing import Literal

########################################
## ICON HANDLING
# app_table_metadata = {
#     'model': {'icon': 'plane.png', 'title': 'Model', 
#         'listaction': 'listview', 'newaction': 'update', 'updateaction': 'update'},
#     'component': {'icon': 'icons8-gearbox-64.png', 'title': 'Component', 
#         'listaction': 'listview', 'newaction': 'update', 'updateaction': 'update'}
        
#         }
# metatypes = Literal['iconname', 'title', 'icon', 'listurl', 'newurl', 'updateurl']
# def get_table_meta(tablename: str, meta: metatypes, size: int =0) -> str:
#     if meta not in metatypes: return None
#     if tablename not in app_table_metadata: return None
#     if meta not in app_table_metadata[tablename]: return None
#     if meta == 'icon' and size == 0: return None
    
#     size = str(size) + 'px'
#     info = app_table_meta[tablename]
    
#     if meta.endswith('url'):
#         return URL(tablename, info[meta])

#     match meta:
#         case 'iconname' | 'title':
#             return info[meta]
#         case 'icon':
#             return IMG(_src=URL('static', f'icons/{info["icon"]}'), _width=size, _height=size)

def controller_icon(controller:str, size: int):
    folder = 'controller/'
    #if size not in [32, 48]: size = 32

    return show_icon(folder + controller.replace(" ", "").lower() + '.png', size, controller)

def switch_icon(switchitem: str, size: int):
    folder = 'switch/'

    return show_icon(folder + switchitem + '.png', 32)

def action_icon(action: str, size:int):
    folder = 'action/'

    return show_icon(folder + action.lower() + '.png', size, action)

def activity_icon(activity:str, size:int):
    folder = 'activity/'
    
    return show_icon(folder + activity.lower() + '-' + str(size) + '.svg', size, activity)

def attribute_icon(attribute:str, size:int):
    folder = 'attribute/'

    return show_icon(folder + attribute.lower() + '.png', size, attribute)

def model_type_icon(model, size:int):
    folder = 'model_type/'
    if size not in [32, 48]: size = 32
    
    return show_icon(folder + model.modeltype.lower() + '-' + str(size) + '.svg', size, model.modeltype)

def model_powerplant_icon(model, size:int):
    folder = 'model_powerplant/'
    if size not in [32, 48]: size = 32

    iconname = ''
    match model.powerplant:
        case 'Electric': iconname = 'th-m_electric-'
        case 'Internal Combustion': iconname = 'th-m_ic-'
        case 'Rocket': iconname = 'th-m_rocket-'
        case 'Rubber': iconname = 'th-m_rubber-'
        case 'Sail': iconname = 'th-m_sail-'
        case _: iconname = 'th-m_other-'

    iconname = iconname + str(size) + '.svg'

    return show_icon(folder + iconname, size, alt=model.powerplant)

def model_control_icon(model, size):
    folder = 'model_control/'
    if size not in [32, 48]: size = 32

    iconname = ''
    match model.controltype:
        case 'Radio Control': iconname = 'th-c_rc-'
        case 'Free Flight': iconname = 'th-c_freeflight-'
        case 'Control Line': iconname = 'th-c_controlline-'
        case 'Other': iconname = 'th-c_other-'

    iconname = iconname + str(size) + '.svg'

    return show_icon(folder + iconname, size, alt=model.controltype)

def library_type_icon(article, size):
    folder = 'library_type/'
    size = 32

    iconname = ''
    match article.articletype:
        case 'Article': iconname = 'scroll.png'
        case 'Book': iconname = 'books.png'
        case 'Idea': iconname = 'light-bulb.png'

    return show_icon(folder + iconname, size=32, alt=article.articletype)

def model_flowchart(model):
    return DIV('flowchart')

def filetype_icon(attachment, size):
    folder = 'attachment_filetype/'
    try:
        ext = attachment.attachment.split('.')[-1].lower()
    except:
        ext = attachment.split('.')[-1].lower()

    return show_icon(folder + ext + '.png', size, ext)

def show_icon(iconname:str, size:int=0, alt:str="icon"):
    thename = 'icons/' + iconname

    if not os.path.exists(os.path.join(request.folder, 'static', thename)):
        thename = 'icons/default.png'
        return iconname

    if size > 0:
        return IMG(_src=URL('static', thename), _alt=alt, _width=str(size) + 'px', _height=str(size) + 'px')
    
    return IMG(_src=URL('static', thename), _alt=alt)
    
############################################
## UTILITIES

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


#################################################
## ACTION BUTTON CREATION

def _makeButton(label, controller, action, args, classes = ''):
    return A(label, _href=URL(controller, action, args=args), _class=classes)

def editButton(controller, action, args, size=24):
    return _makeButton(action_icon('edit', size), controller, action, args, 'btn btn-warning')

def viewButton(controller, action, args, size=24):
    return _makeButton(action_icon('details', size), controller, action, args, 'btn btn-info')

def plusButton(controller, action, args, size=24):
    return _makeButton(action_icon('add', size), controller, action, args, 'btn btn-success')

def minusButton(controller, action, args, size=24):
    return _makeButton(action_icon('subtract', size), controller, action, args, 'btn btn-danger')

def completeButton(controller, action, args, size=24):
    return _makeButton(action_icon('unchecked', size), controller, action, args, 'btn btn-success')

def deleteButton(controller, action, args, size=24 ):
    return _makeButton(action_icon('delete', size), controller, action ,args, 'btn btn-danger')

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
