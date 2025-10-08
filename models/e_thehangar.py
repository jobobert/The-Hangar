from collections import deque
import os, random, math
from typing import Literal
from enum import Enum

class FormFieldType(Enum):
    COLUMNS = 1
    ROWS = 2

def class_isrequired(form, fieldname:str):
    table = form.table
    
    field = db[table][fieldname]

    if (field.required or field.requires and 'IS_NOT_EMPTY' in str(field.requires)):
        return "font-weight-bold"
    else:
        return ""

def splitColumn(size:int):
    if size % 2 == 0:
        half = size // 2
        return (int(half), int(half))
    else:
        half = size // 2
        return (half + 1, half)

def makeFormField(form, fieldname:str, fieldType:FormFieldType, columns:int = 0, fieldid:str = "", divClass:str = ""):
    table = form.table
    field = db[table][fieldname]
    isCheckbox = False
    theLabel = None
    theInput = None
    theComment = None
    hasConverter = False
    theConverterLabel = None
    theConverterInput = None
    theConverterComment = None
    originalText = ""
    conversionText = ""
    labelClass = ""
    inputType = None
    inputID = f'{table}_{fieldname}'

    if columns < 0:
        columns = 0
    if columns > 12:
        columns = 12
    
    print(f'{fieldname} @ {field.required} or {field.requires}')

    if (field.required or
        (field.requires and (
            ('IS_NOT_EMPTY' in str(field.requires)) 
            or 
            ('IS_EMPTY_OR' not in str(field.requires)))
        )):
        labelClass = "font-weight-bold"

    #print(field.type)
    if field.type == 'boolean':
        isCheckbox = True

    if hasattr(field, 'extra'):
        if 'measurement' in field.extra:
            hasConverter = True
            func = None # the func javascript function must be declared in layout.html!!
            match field.extra['measurement']:
                case 'mm':
                    func = 'inchToMm'
                    originalText = 'mm'
                    conversionText = 'Inch'
                case 'dm2':
                    func = 'dm2ToSqin'
                    originalText = 'dm2'
                    conversionText = 'sqin'
                case 'oz':
                    func = 'gramToOz'
                    originalText = "oz"
                    conversionText = 'Gram'
                case 'sqin':
                    func = None
                    originalText = 'sqin'
                case 'cc':
                    func = None
                    originalText = 'cc'
                case _:
                    hasConverter = False

            if hasConverter and func == None:
                theConverterInput = f"No Converter Available '{field.extra['measurement']}'"
            elif hasConverter:
                theConverterInput = INPUT(
                        _placeholder = conversionText,
                        _class = 'double form-control th_form_field_calc',
                        _type = 'number',
                        _step = '0.01',
                        _autocomplete = "off",
                        _id = f'c_{fieldname}',
                        _onchange = f'{func}("c_{fieldname}", "{inputID}");'
                    )
                theConverterLabel = XML(f'<label class="form-text {"col-sm-2 col-form-label" if fieldType == FormFieldType.ROWS else ""}" for="c_{fieldname}">{field.label or field.name} ({conversionText})</label>') 
                theConverterComment = XML(f'<small class="form-text text-muted d-none d-sm-block">Convert from {conversionText}</small>')
        if 'input' in field.extra:
            #print(field.extra['input'])
            match field.extra['input']:
                case 'color':
                    inputType = 'color'
    
    col1 = col2 = columns
    if hasConverter:
        col1, col2 = splitColumn(columns)

    theLabel = XML(f'<label class="form-text {"col-sm-2 col-form-label" if fieldType == FormFieldType.ROWS else ""} {labelClass}" for="{inputID}">{field.label or field.name} {"(" + originalText + ")" if originalText else ""}</label>')
    theInput = form.custom.widget[fieldname]
    theComment = XML(f'<small class="form-text text-muted d-none d-sm-block">{field.comment or ""}</small>')

    if inputType:
        theInput.attributes['_type'] = inputType
    
    if '_type' in theInput.attributes:
        #print(theInput.attributes['_type'] )

        if theInput.attributes['_type'] == 'text':
            theInput.attributes['_placeholder'] = field.label or field.name
    
    output = None

    if fieldType == FormFieldType.COLUMNS:
        output = DIV(
            theComment if isCheckbox else theLabel,
            theInput,
            theLabel if isCheckbox else theComment,
            _class=f'{"col" if col1 == 0 else f"col-sm-{col1}"} {divClass}'
        ) + (DIV(
            theConverterLabel if theConverterLabel else "",
            theConverterInput,
            theConverterComment if theConverterComment else "",
            _class=f'{"col" if col2 == 0 else f"col-sm-{col2}"} {divClass}'
        ) if hasConverter else "")

    if fieldType == FormFieldType.ROWS:
        output = DIV(
            theLabel, 
            DIV(
                theInput,
                theComment,
                _class='col-sm-10'),
            _class=f'{divClass} form-group row'
        ) + (DIV(
            theConverterLabel,
            DIV(
                theConverterInput,
                theConverterComment,
                _class=f'col-sm-10'),
            _class=f'{divClass} form-group row'
            ) if hasConverter else ""
        )

    if fieldid:
        output = DIV(output, _id=fieldid, _class=f'col-sm-{columns}')

    return output

########################################
## ICON HANDLING

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
    
    return show_icon(folder + activity.lower() + '.png', size, activity)

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

    test = ""
    if type(article) == str:
        test = article
    if hasattr(article, 'articletype'):
        test = article.articletype

    iconname = ''
    match test:
        case 'Article': iconname = 'scroll.png'
        case 'Book': iconname = 'books.png'
        case 'Idea': iconname = 'light-bulb.png'

    return show_icon(folder + iconname, size=32, alt=test)

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
        thename = 'icons/nopicture.png'
        #return iconname

    if size > 0:
        return IMG(_src=URL('static', thename), _alt=alt, _width=str(size) + 'px', _height=str(size) + 'px')
    
    return IMG(_src=URL('static', thename), _alt=alt)
    
############################################
## UTILITIES

def TwoDecimal(number):
    if number is None:
        return 0.00
    return "{:.2f}".format(number)


def ZeroDecimal(number):
    if number is None:
        return 0
    return "{:.0f}".format(number)

def AttachPopup2(attachment):
    # This doesn't work, it doesn't start with the dialog hidden
    rnd = random.randint(0, 100)
    
    if isimage(attachment):
        attach = attachment
        if hasattr(attachment, "attachment"):
            attach = attachment.attachment
        x = XML(f'<button popovertarget="img_{rnd}">{action_icon("OpenTab", 16)}</button><dialog id="img_{rnd}" popover="manual"><button popovertarget="img_{rnd}" popovertargetaction="hide">X</button><img class="" src="{URL("default", "download", args=attach)}"/></dialog>')
    else:
        return ""

    return x

def AttachPopup(attachment, useicon = False):
    if isimage(attachment):
        attach = attachment
        if hasattr(attachment, "attachment"):
            attach = attachment.attachment
        attributes = {
            '_data-toggle': 'modal',
            '_data-target': '#mainModal',
            '_data-whatever': '<img class="card-img-top" src=' + URL("default", "download", args=attach) + '>',
            '_class': 'btn'
        }
        if useicon:
            return A(filetype_icon(attach, 32), **attributes)
        else:    
            return A(action_icon("OpenTab", 16), **attributes)
    else:
        return ""

def ConvertMeasurementField(table, row, FieldName, seperator=" | "):
    if not hasattr(db[table][FieldName], "extra"):
        return ""

    match getattr(db[table], FieldName).extra['measurement']:
        case 'mm':
            return seperator + str(TwoDecimal((row[FieldName] or 0) / 25.4)) + " in"
        case 'oz':
            if (row[FieldName] or 0) >= 16:
                return seperator + str(TwoDecimal((row[FieldName] or 0) / 16)) + " lbs"
            else:
                return seperator + str(TwoDecimal((row[FieldName] or 0) * 28.35)) + " g"
        case 'dm2':
            return seperator + str(TwoDecimal((row[FieldName] or 0) * 15.5)) + " sqin"
        case 'sqin':
            return seperator + str(TwoDecimal((row[FieldName] or 0) / 15.5)) + "dm2"
        case 'cc':
            return seperator + str(TwoDecimal((row[FieldName] or 0) / 1000)) + " liters"
        case _:
            return ""

def isimage(attachment):

    if hasattr(attachment, "attachment"):
        ext = attachment.attachment.split('.')[-1]
    elif hasattr(attachment, "split"):
        ext = attachment.split('.')[-1]
    elif isinstance(attachment, str):
        ext = attachment.split('.')[-1]
    else:        return False

    imageExtensions = {
        'jpeg': True,
        'jpg': True,
        'gif': True,
        'png': True
    }
    
    return imageExtensions.get(ext, False)

def ispdf(attachment):
    
    if hasattr(attachment, "attachment"):
        ext = attachment.attachment.split('.')[-1]
    elif hasattr(attachment, "split"):
        ext = attachment.split('.')[-1]
    elif type(attachment) == 'str':
        ext = attachment.split('.')[-1]
    else:
        return False

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

def makeTagList(tags, divClass=""): 
    if not tags:
        return ""
    return DIV([SPAN(t.name, _class="ml-2 badge badge-primary") for t in tags], _class=divClass)
    
        

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

######################################################
## LIST ITEM CREATION
def _makeListItem(controller:str, action:str, args, img:str=None, icon:str=None, label:str='', detail:str=None):
    parts = []
    imgsize = '48px'

    if img:
        parts.append(IMG(_src=URL('default', 'download', args=img), _width=imgsize, _height=imgsize) if img else '')
    if icon:
        parts.append(icon)
    if detail:
        parts.append(DIV(XML(f'<small class="text-muted">{detail}</small>')))
    parts.append(' ' + label)

    return LI(A(DIV(parts), _href=URL(controller, action, args=args)), _class='list-group-item')

def modelListItem(model, img:bool, label:str = None, idOverride:int = None, detail:str = None):

    if isinstance(model, int):
        model = db(db.model.id == model).select(db.model.id, db.model.img, db.model.name).first()
       
    #print(model)
    modelID = model.id

    if idOverride:
        modelID = idOverride

    if img and model.img:
        return _makeListItem('model', 'index', modelID, model.img, label or model.name, detail=detail)

    return _makeListItem('model', 'index', modelID, None, label or model.name, detail=detail)

def transmitterListItem(transmitter, img:bool, label:str = None, idOverride:int = None):
    if idOverride:
        transID = idOverride
    else:
        transID = transmitter.id
        
    if img and transmitter.img:
        return _makeListItem('transmitter', 'index', transID, transmitter.img, label or transmitter.name)

    return _makeListItem('transmitter', 'index', transID, None, label or transmitter.name)

def attachmentListItem(attachment, img:bool, label:str):
    #print(filetype_icon(attachment, 32))

    return _makeListItem('default', 'download', attachment, icon=filetype_icon(attachment, 32), label=label)

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
