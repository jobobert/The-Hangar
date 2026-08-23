
import os, random, math

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

def makeFormSubmitbutton(form):
    if form.custom.submit:
        return(DIV(form.custom.submit, _class='d-inline-block ml-2'))
    else:
        return ''

def makeFormDeleteButton(form):
    if form.custom.delete:
        form.custom.delete['_class'] = 'th-delete-checkbox-button'
        btn = BUTTON(
            'Delete',
            _type='button',
            _class='btn th-delete-checkbox-button-label',
            _onclick=(
                "if(confirm('Are you sure you want to delete this object?'))"
                "{document.getElementById('delete_record').checked=true;"
                "this.closest('form').submit();}"
            )
        )
        return DIV(btn, form.custom.delete, _class='d-inline-block ml-2')
    else:
        return ''

def disable_autocomplete(form):
    for s in form.elements('input', _type='text'):
        s['_autocomplete'] = 'off'

def makeFormField(form, fieldname:str, fieldType:FormFieldType, columns:int = 0, fieldid:str = "", divClass:str = ""):
    """Render a single form field as a Bootstrap grid row.

    Returns a DIV containing a label column (col1) and an input column (col2).
    Pass columns=0 to auto-size based on field type; otherwise the value sets
    the Bootstrap column width of the input half.
    """
    isSubmit = False
    field = None
    inputID = ""
    helpText = None

    if not form:
        return DIV("No form provided")

    table = form.table
    if fieldname.lower() == 'submit':
        isSubmit = True
    else:
        try:
            field = db[table][fieldname]
            inputID = f'{table}_{fieldname}'
            helpText = getDatabaseHelp(field)
        except KeyError:
            field = None
    
    isCheckbox = False
    theHelp = None
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
    

    if columns < 0:
        columns = 0
    if columns > 12:
        columns = 12

    # If the field is required then bold the label
    if field:
        if (field.required or
            (field.requires and (
                ('IS_NOT_EMPTY' in str(field.requires)) 
                or 
                ('IS_EMPTY_OR' not in str(field.requires)))
            )):
            labelClass = "font-weight-bold"

        # check for special field types
        #print(field.type)
        if field.type == 'boolean':
            isCheckbox = True

        # Process field extra attributes
        if hasattr(field, 'extra'):
            if 'measurement' in field.extra:
                # Values are stored in metric (mm, g, dm²) but shown with a live
                # JS converter button so the user can toggle to imperial units.
                hasConverter = True
                func = None # the func javascript function must be declared in layout.html!!
                match field.extra['measurement']:
                    case 'mm':
                        func = 'inchToMm'
                        originalText = 'mm'
                        conversionText = 'Inch'
                    case 'dm2':
                        func = None
                        originalText = 'dm2'
                        conversionText = 'sqin'
                    case 'oz':
                        func = 'gramToOz'
                        originalText = "oz"
                        conversionText = 'Gram'
                    case 'sqin':
                        func = 'dm2ToSqin'
                        originalText = 'sqin'
                        conversionText = 'dm2'
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

        if helpText:
            #theHelp = DIV(f'{helpText}', _id=f'{inputID}_help', _popover)
            theHelp = XML(f'<div id="{inputID}_help" popover class="help_popover">{MARKMIN(helpText)}</div>')
            theHelpIcon = XML(f'<button type="button" class="btn btn-link" style="margin-top: -0.5rem" popovertarget="{inputID}_help">{action_icon("help", 15)}</button>')
  
        theLabel = XML(f'<label class="form-text {"col-sm-2 col-form-label" if fieldType == FormFieldType.ROWS else ""} {labelClass}" for="{inputID}">{field.label or field.name} {"(" + originalText + ")" if originalText else ""} {theHelpIcon if helpText else ""}</label>')
        theInput = form.custom.widget[fieldname]
        if isinstance(theInput, SELECT):
            first = theInput.components[0] if theInput.components else None
            if not (isinstance(first, OPTION) and str(first['_value'] or '') == ''):
                theInput.insert(0, OPTION('', _value=''))
        if isinstance(theInput, str):
            theInput = XML(theInput)
        theComment = XML(f'<small class="form-text text-muted d-none d-sm-block">{field.comment or ""}</small>')

        if inputType and hasattr(theInput, 'attributes'):
            theInput.attributes['_type'] = inputType

        if hasattr(theInput, 'attributes') and '_type' in theInput.attributes:
            #print(theInput.attributes['_type'] )

            if theInput.attributes['_type'] == 'text':
                theInput.attributes['_placeholder'] = field.label or field.name
        
        output = None
    elif isSubmit:
        col1 = col2 = columns
        theComment = XML('&nbsp;')
        theLabel = XML(f'<label class="form-text {"col-sm-2 col-form-label" if fieldType == FormFieldType.ROWS else ""} {labelClass}" for="{inputID}">&nbsp;</label>')
        theInput = form.custom.submit
    else:
        col1 = col2 = columns
        theComment = XML('&nbsp;')
        theLabel = XML(f'<label class="form-text {"col-sm-2 col-form-label" if fieldType == FormFieldType.ROWS else ""} {labelClass}" for="{inputID}">&nbsp;</label>')
        theInput = SPAN(f'Unknown field: {fieldname}')

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
        ) if hasConverter else ""
        ) + (theHelp if theHelp else "") 

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
        ) + (theHelp if theHelp else "")

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
    if switchitem:
        row = db((db.lookup.category == 'switchtype') & (db.lookup.name == switchitem)).select(db.lookup.metadata).first()
        svg = ((row.metadata or {}).get('svg') if row else None)
        if svg:
            return XML(f'<span class="switch-icon" style="width:{size}px;height:{size}px;display:inline-block;vertical-align:middle">{svg}</span>')
    return show_icon('switch/' + (switchitem or 'nopicture') + '.png', size)

def action_icon(action: str, size:int, alt:str=None):
    folder = 'action/'
    
    return show_icon(folder + action.lower() + '.png', size, alt if alt else action)

def activity_icon(activity:str, size:int):
    folder = 'activity/'
    
    return show_icon(folder + activity.lower() + '.png', size, activity)

def attribute_icon(attribute:str, size:int):
    folder = 'attribute/'

    return show_icon(folder + attribute.lower() + '.png', size, attribute)

def model_type_icon(model, size:int):
    folder = 'model_type/'
    if size not in [32, 48]: size = 32

    if model.modeltype:
        _slug = model.modeltype.lower().replace(' ', '-')
        return show_icon(folder + _slug + '-' + str(size) + '.svg', size, model.modeltype)
    else:
        return show_icon('noicon.svg', size, f"unknown modeltype for {model.name}")

def text_model_type_icon(modeltype:str, size:int):
    folder = 'model_type/'
    if size not in [32, 48]: size = 32

    try:
        _slug = modeltype.lower().replace(' ', '-')
        return show_icon(folder + _slug + '-' + str(size) + '.svg', size, modeltype)
    except:
        return show_icon('noicon.svg', size, f"unknown modeltype for {modeltype}")

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


def _file_ext(attachment):
    try:
        if hasattr(attachment, 'attachment'):
            return attachment.attachment.split('.')[-1].lower()
        return attachment.split('.')[-1].lower()
    except (AttributeError, TypeError, IndexError):
        return None

def filetype_icon(attachment, size):
    ext = _file_ext(attachment) or 'nopicture'
    return show_icon('attachment_filetype/' + ext + '.png', size, ext)

def filename_filetype_icon(filename:str, size:int):
    ext = _file_ext(filename) or 'nopicture'
    return show_icon('attachment_filetype/' + ext + '.png', size, ext)

def show_icon(iconname:str, size:int=0, alt:str="icon"):
    thename = 'icons/' + iconname

    if not os.path.exists(os.path.join(request.folder, 'static', thename)):
        thename = 'icons/nopicture.png'
        #return iconname

    if size > 0:
        return IMG(_src=URL('static', thename), _alt=alt, _title=alt, _width=str(size) + 'px', _height=str(size) + 'px')
    
    return IMG(_src=URL('static', thename), _alt=alt, _title=alt)
    
############################################
## UTILITIES
import inspect
def static_cachebust(relpath):
    """Query-string cache-buster (file mtime) for a static asset, e.g.
    URL('static', 'js/x.js', vars=dict(v=static_cachebust('js/x.js'))) —
    for files under active development, so browsers don't need a hard
    refresh to pick up each edit."""
    try:
        return int(os.path.getmtime(os.path.join(request.folder, 'static', relpath)))
    except OSError:
        return 0

def render_card_error(content, controller=None, title=None):
    response.view = 'rendercarderror.load'
    return dict(content=content, controller=controller, title=title)

def VerifyTableID(table:str, rowID:int|str, redirect_url=None, prefer_referer=False):
    #print(f'{table} -- {rowID}:  {type(rowID)}')

    def _fail():
        if redirect_url:
            session.flash = "Record not found."
            target = RefererOrDefault(redirect_url) if prefer_referer else redirect_url
            redirect(target)
        response.flash = "Record not found!"
        return None

    if rowID is None:
        print(f"VerifyTableID: Error: Received Null ID (table '{table}').")
        return _fail()

    try:
        integer_value = int(rowID)
    except (ValueError, TypeError):
        print(f"VerifyTableID: Error: Could not convert '{rowID}' (table '{table}').")
        print(inspect.stack()[1][3])
        return _fail()

    if (db(db[table].id == integer_value)).count() == 0:
        return _fail()

    return integer_value

def RefererOrDefault(default_url):
    referer = request.env.http_referer or ''
    same_action = URL(request.controller, request.function, host=True)
    if referer and not referer.startswith(same_action):
        return referer
    return default_url

def TwoDecimal(number):
    if number is None:
        return 0.00
    return "{:.2f}".format(number)

def ZeroDecimal(number):
    if number is None:
        return 0
    return "{:.0f}".format(number)

def AttachPopup(attachment):
    rnd = random.randint(0, 999999)  # unique suffix so multiple popups on the same page don't share DOM IDs
    attach = attachment
    if hasattr(attachment, "attachment"):
        attach = attachment.attachment

    if isimage(attach):
        return XML(
            f'<button type="button" popovertarget="img_{rnd}">{action_icon("OpenTab", 16)}</button>'
            f'<div id="img_{rnd}" popover="manual" style="padding:1rem;background:white;border:1px solid #ccc;border-radius:4px;">'
            f'<button type="button" popovertarget="img_{rnd}" popovertargetaction="hide" style="display:block;margin-bottom:.5rem;">&#x2715; Close</button>'
            f'<img src="{URL("default","download",args=attach)}" style="max-width:90vw;max-height:80vh;"/>'
            f'</div>'
        )
    elif ispdf(attach):
        inline_url = URL("default", "inline", args=attach)
        download_url = URL("default", "download", args=attach)
        return XML(
            # mobile: open in new tab
            f'<a href="{inline_url}" target="_blank" class="btn btn-sm btn-outline-primary ml-1 d-md-none">'
            f'{action_icon("OpenTab", 16)} View</a>'
            # desktop: open in popover
            f'<button type="button" popovertarget="pdf_{rnd}" class="btn btn-sm btn-outline-primary ml-1 d-none d-md-inline-block">'
            f'{action_icon("OpenTab", 16)} View</button>'
            f'<div id="pdf_{rnd}" popover="manual" style="position:fixed;top:2vh;left:2vw;width:96vw;height:96vh;'
            f'background:white;border:1px solid #ccc;border-radius:4px;overflow:hidden;">'
            f'<div style="display:flex;flex-direction:column;height:100%;padding:0.75rem 1rem;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;flex-shrink:0;">'
            f'<a href="{download_url}" class="btn btn-sm btn-outline-secondary">&#x2B07; Download</a>'
            f'<button type="button" popovertarget="pdf_{rnd}" popovertargetaction="hide" class="btn btn-sm btn-outline-secondary">&#x2715; Close</button>'
            f'</div>'
            f'<embed src="{inline_url}" type="application/pdf" style="flex:1;width:100%;min-height:0;"/>'
            f'</div>'
            f'</div>'
        )
    return ""

def renderModal(modal_id, title, form, label='New'):
    style = (
        'position:fixed;top:5vh;left:50%;transform:translateX(-50%);'
        'padding:1rem;background:white;border:1px solid #ccc;border-radius:4px;'
        'min-width:40vw;max-height:90vh;overflow-y:auto;'
    )
    return XML(
        f'<button type="button" class="card-link th-new-link btn btn-link"'
        f' popovertarget="{modal_id}">{label}</button>'
        f'<div id="{modal_id}" popover="manual" style="{style}">'
        f'<button type="button" popovertarget="{modal_id}" popovertargetaction="hide"'
        f' style="display:block;margin-bottom:.5rem;">&#x2715; Close</button>'
        f'<h5>{title}</h5>{str(form)}</div>'
    )

def ConvertMeasurementField(table, row, FieldName, separator=" | "):
    if not hasattr(db[table][FieldName], "extra"):
        return ""

    match getattr(db[table], FieldName).extra['measurement']:
        case 'mm':
            return separator + str(TwoDecimal((row[FieldName] or 0) / 25.4)) + " in"
        case 'oz':
            if (row[FieldName] or 0) >= 16:
                return separator + str(TwoDecimal((row[FieldName] or 0) / 16)) + " lbs"
            else:
                return separator + str(TwoDecimal((row[FieldName] or 0) * 28.35)) + " g"
        case 'dm2':
            return separator + str(TwoDecimal((row[FieldName] or 0) * 15.5)) + " sqin"
        case 'sqin':
            return separator + str(TwoDecimal((row[FieldName] or 0) / 15.5)) + " dm2"
        case 'cc':
            return separator + str(TwoDecimal((row[FieldName] or 0) / 1000)) + " liters"
        case _:
            return ""

def isimage(attachment):
    return _file_ext(attachment) in {'jpeg', 'jpg', 'gif', 'png', 'bmp'}

def ispdf(attachment):
    return _file_ext(attachment) == 'pdf'
        
def log_activity(model_id, activitytype, notes=''):
    model_id = VerifyTableID('model', model_id)
    if not model_id:
        return
    db.activity.insert(
        activitydate=request.now.date(),
        model=model_id,
        activitytype=activitytype,
        notes=notes
    )

def fleetQuery():
    """DAL condition for the selected fleet — the dashboard's scope.
    modelstate 1 is Retired/Disposed (see db.py:145-152)."""
    return (db.model.selected == True) & (db.model.modelstate != 1)

def underConstructionModels():
    models = db((db.model.modelstate == 3) | (db.model.modelstate == 6)).select(
        db.model.id, db.model.name, db.model.img, db.model.description).as_list()

    for model in models:
        model['img'] = IMG(_src=URL('default', 'download', args=model['img'], scheme=True, host=True))

    return models

def activeModels():
    models = db((db.model.modelstate == 4) | (db.model.modelstate == 5)).select(
        db.model.id, db.model.name, db.model.img, db.model.description).as_list()

    for model in models:
        model['img'] = IMG(_src=URL('default', 'download', args=model['img'], scheme=True, host=True))

    return models

def selectedModels():
    models = db(db.model.selected == True).select(
        db.model.name, db.model.img, db.model.description).as_list()

    for model in models:
        model['img'] = IMG(_src=URL('default', 'download', args=model['img'], scheme=True, host=True))
    
    return models

def theHangarStats():
    stats = {}

    # Get the States
    states = db(db.model).select(db.model.modelstate,
                                 db.model.id.count(), groupby=db.model.modelstate)
    for state in states:
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

    for todo in critical_todos:

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
    """Clear an upload column and remove its file from disk.

    Removal is best-effort and goes through _safe_upload_delete (models/db.py),
    which validates the name and skips anything that is not a web2py upload
    name. The old inline version did `table, field, subfolder = file.split('.')[0:3]`
    and raised ValueError on a short value, plus os.remove raised on an already
    missing file — either way the column was then never cleared.
    """
    name = row(uploadfield)
    m = re.match(REGEX_UPLOAD_PATTERN, name or '')
    if m:
        # The upload name encodes its own table.field, which is also what
        # determines where the file sits on disk. Same source response.download
        # uses, so it stays correct even if called with a row from a join.
        _safe_upload_delete(db[m.group('table')][m.group('field')])(name)
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

def deleteItemButton(table, row_id, size=24):
    """Delete an inventory item through the guarded flow in controllers/item.py.

    No JS confirm() here on purpose — item/delete shows what the delete would
    affect and takes the confirmation itself. See models/m_delete.py.
    """
    return _makeButton(action_icon('delete', size), 'item', 'delete',
                       [table, row_id], 'btn btn-danger')

def newButton(controller, action, args, size=24):
    return _makeButton('Create', controller, action, args, 'btn btn-success')

######################################################
## THUMBNAILS

def thumbIMG(value, size=48, _class='mr-2 rounded'):
    """Fixed-size square thumbnail, falling back to the neutral placeholder.

    Deliberately NOT default/download()'s fallback: that serves the 240x130
    branded defaultUpload.png, which suits a large reserved slot but squashes
    in a square box. Small avatar slots get icons/nopicture.png instead, the
    same choice views/default/search.html already makes. _onerror covers the
    other case download() would answer with the wide image — a name that looks
    valid but whose file is gone.
    """
    nopicture = URL('static', 'icons/nopicture.png')
    return IMG(_src=URL('default', 'download', args=value) if value else nopicture,
               _width=size, _height=size, _alt='', _class=_class,
               _onerror="this.src='%s'" % nopicture)

######################################################
## LIST ITEM CREATION
def _makeListItem(controller:str, action:str, args, img:str=None, icon:str=None, label:str='', detail:str=None):
    parts = []

    # None means "no thumbnail on this item"; '' means "thumbnail slot, but this
    # row has no picture" — which still renders, as the placeholder.
    if img is not None:
        parts.append(thumbIMG(img, 48, _class=''))
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

    return _makeListItem('model', 'index', modelID,
                         (model.img or '') if img else None,
                         label or model.name, detail=detail)

def transmitterListItem(transmitter, img:bool, label:str = None, idOverride:int = None):
    if idOverride:
        transID = idOverride
    else:
        transID = transmitter.id
        
    return _makeListItem('transmitter', 'index', transID,
                         (transmitter.img or '') if img else None,
                         label or transmitter.name)

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
