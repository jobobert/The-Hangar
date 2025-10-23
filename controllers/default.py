# -*- coding: utf-8 -*-

import random
import urllib
import os
# try:
#    import response
#    import request
#    import session
# except:
#    pass

def find_unreferenced_uploads():
    ## make form, use random int to identify file, show pic/download in view (don't use the "delete" above)
    message=""
    app_path = os.path.join(request.folder, 'uploads')

    all_uploaded_files = set()
    uploaded_files_fullpath = {}
    for root, dirs, filenames in os.walk(app_path):
        for filename in filenames:
            all_uploaded_files.add(filename)
            #print(f'-- {os.path.join(root, filename)}')
            uploaded_files_fullpath[filename] = os.path.join(root, filename)

    referenced_files = set()

    # Iterate through all tables in your database
    for table_name in db.tables:
        table = db[table_name]
        # Check each field in the table
        for field_name in table.fields:
            field = table[field_name]
            # If the field is of type 'upload'
            if field.type == 'upload':
                # Fetch all filenames stored in this upload field
                records = db(table).select(field)
                for record in records:
                    filename = record[field_name]
                    if filename: # Ensure filename is not None or empty
                        referenced_files.add(filename)

    # Calculate the difference to find unreferenced files
    unreferenced_files = {}
    for file in all_uploaded_files:
        found = False
        for rfile in referenced_files:
            if file == rfile:
                found = True
                break
        if not found:
            unreferenced_files[hash(file)] = file

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='deleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = int(y)
                #message=del_id
                fname = unreferenced_files.get(del_id)
                if fname is not None:
                    fullfilename = uploaded_files_fullpath[fname]
                    try:
                        os.remove(fullfilename)
                        del unreferenced_files[del_id]
                        response.flash = "Removal Success"
                    except (OSError, PermissionError) as e:
                        response.flash = f'Failed to remove file: {str(e)}'
                else:
                    response.flash = "Unknown File Requested"
    elif deleteform.errors:
        response.flash = "Removal Failure"

    return dict(unreferenced_files=unreferenced_files, deleteform=deleteform, message=message)

def index():

    response.title = 'The Hangar: Models'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    parse_success = False
    state_number = 4
    state_plus = True
    the_filters = {
                 'modeltype': ''
                , 'controltype': ''
                , 'powerplant': ''
                , 'plankit': ''
                , 'transmitter': ''
                , 'subjecttype': ''
                , 'selected': ''
                }
    filter_text = {
                 'modeltype': ''
                , 'controltype': ''
                , 'powerplant': ''
                , 'plankit': ''
                , 'transmitter': ''
                , 'subjecttype': ''
                , 'selected': ''}

    states = db(db.modelstate).select(db.modelstate.id, db.modelstate.name)
    filterstatelist = []
    log = []
    queries = []

    wasFormUsed = False
    modelCategory = None
    if request.cookies['ui'].value != 'dashboard':
        # Setting up the model category.
        # Step 1: set default
        # Step 2: check the URL
        # Step 3: check the session
        # Step 4: verify or set to known state
        # Step 5: do the filtering
        viableOptions = [o[1] for o in db.model.modelcategory.requires.options()]
        modelCategory = viableOptions[2]

        if session.modelcategory:
            modelCategory = session.modelcategory

        if request.vars['c']:
            modelCategory = request.vars['c'] 

        if modelCategory not in viableOptions:
            modelCategory = viableOptions[2]

        session.modelcategory = modelCategory
        queries.append(db.model.modelcategory == modelCategory)

    for s in states:
        the_filters[s.name] = ''
        filter_text[s.name] = ''

    if 's' in request.vars:
        state = request.vars['s']
        if len(str(state)) == 2:
            if isinstance(int(state[0]), int) and state[1] == '*':
                state_number = int(state[0])
                state_plus = True
                parse_success = True
        elif isinstance(int(state), int):
            state_number = int(state)
            state_plus = False
            parse_success = True

    if parse_success:
        session.state = state_number
        session.stateplus = state_plus
    else:
        if not session.state:
            session.state = state_number
            session.stateplus = state_plus

    if session.filters:
        filters = session.filters
    else:
        filters = the_filters

    fields = []

    fields.append(Field('modeltype', label=db.model.modeltype.label,
                        requires=IS_EMPTY_OR(db.model.modeltype.requires), required=False))
    fields.append(Field('controltype', label=db.model.controltype.label,
                        requires=IS_EMPTY_OR(db.model.controltype.requires), required=False))
    fields.append(Field('powerplant', label=db.model.powerplant.label,
                        requires=IS_EMPTY_OR(db.model.powerplant.requires), required=False))
    fields.append(Field('plankit', label='Plan or Kit',
                        requires=IS_EMPTY_OR(IS_IN_SET(['Plan', 'Kit', 'Both', 'Neither'])), required=False))
    fields.append(Field('transmitter', label=db.model.transmitter.label,
                        requires=IS_EMPTY_OR(db.model.transmitter.requires), required=False))
    fields.append(Field('subjecttype', label=db.model.subjecttype.label,
                        requires=IS_EMPTY_OR(db.model.subjecttype.requires), required=False))
    fields.append(Field('isselected', 'boolean',
                        label='Is Selected', required=False))

    for s in states:
        selected = True
        if s.id <= 2:
            selected = False
        fields.append(Field('s' + str(s.id), 'boolean',
                            label=s.name, default=selected, required=False))

    selectform = SQLFORM.factory(
        *fields, formstyle='divs', keepvalues=True, _class='filterform', table_name='filter_form')

    if selectform.process(message_onsuccess=None).accepted:
        wasFormUsed = True

        response.flash = ''

        filters['modeltype'] = selectform.vars.modeltype

        filters['controltype'] = selectform.vars.controltype

        filters['powerplant'] = selectform.vars.powerplant

        filters['plankit'] = selectform.vars.plankit

        filters['transmitter'] = selectform.vars.transmitter

        filters['subjecttype'] = selectform.vars.subjecttype

        filters['isselected'] = selectform.vars.selected

        for s in states:
            filters['s' + str(s.id)] = selectform.vars['s' + str(s.id)]
            if filters['s' + str(s.id)]:
                filterstatelist.append(s.id)

        session.filters = filters

    if request.vars['clear']:
        session.filters = filters = the_filters
        wasFormUsed = False
        redirect(URL(args=request.args, host=True))

    if filters['modeltype']:
        queries.append(db.model.modeltype == filters['modeltype'])
        filter_text['modeltype'] = filters['modeltype']

    if filters['controltype']:
        queries.append(db.model.controltype == filters['controltype'])
        filter_text['controltype'] = filters['controltype']

    if filters['powerplant']:
        queries.append(db.model.powerplant == filters['powerplant'])
        filter_text['powerplant'] = filters['powerplant']

    if filters['subjecttype']:
        queries.append(db.model.subjecttype == filters['subjecttype'])
        filter_text['subjecttype'] = filters['subjecttype']

    if filters['plankit']:

        if filters['plankit'] == 'Plan':
            queries.append(db.model.haveplans == True)
        if filters['plankit'] == 'Kit':
            queries.append(db.model.havekit == True)
        if filters['plankit'] == 'Both':
            queries.append((db.model.haveplans == True)
                           & (db.model.havekit == True))
        if filters['plankit'] == 'Neither':
            queries.append((db.model.haveplans == False)
                           & (db.model.havekit == False))
        filter_text['plankit'] = filters['plankit']

    if filters['transmitter']:
        queries.append(db.model.transmitter == filters['transmitter'])
        filter_text['transmitter'] = db.transmitter[filters['transmitter']].name

    if filters['selected'] == True:
        queries.append(db.model.selected == filters['selected'])
        filter_text['selected'] = "Selected"

    if len(filterstatelist) > 0:
        queries.append(db.model.modelstate.belongs(filterstatelist))

        for s in states:
            for f in filterstatelist:
                if s.id == f:
                    filter_text[s.name] = s.name

    if not wasFormUsed:
        if 'ui' in request.cookies:
            if request.cookies['ui'].value == 'dashboard':
                queries.append((db.model.selected == True) & (db.model.modelstate > 1))
        if 'ui' not in request.cookies or request.cookies['ui'].value != 'dashboard':
            if session.stateplus:
                queries.append(db.model.modelstate >= session.state)
            else:
                queries.append(db.model.modelstate == session.state)

    query = reduce(lambda a, b: (a & b), queries)

    models = db(query).select(db.model.ALL, orderby=db.model.name)

    selected = None
    if request.args:
        selected = VerifyTableID('model', request.args(0))
    if selected == None:
        selected = -1

    #print(f'selected = {selected}')

    if 'ui' in request.cookies:
        if request.cookies['ui'].value == 'dashboard':
            response.view = 'default/dashboard.html'
        elif request.cookies['ui'].value == 'list':
            pass

    session.ft = filter_text
    return dict(models=models, form=selectform, filters=filter_text, selected=selected, log=log, modelCategory=modelCategory)


def setui():
    if request.args(0) == 'dashboard':
        response.cookies['ui'] = 'dashboard'
    elif request.args(0) == 'list':
        response.cookies['ui'] = 'list'
    else:
        response.cookies['ui'] = ''

    response.cookies['ui']['path'] = '/'

    return redirect(URL('default', 'index'))

# ---- action to server uploaded static content (required) ---


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def test():
    query = db(db.model_component.model == 12)
    left = db.component.on(db.component.id == db.model_component.component)
    fields = [db.component.name, db.model_component.purpose,
              db.model_component.channel, db.component.img, db.component.attachment]
    links = [dict(header=T('Img'),
                  body=lambda row: A(IMG(_src=URL('default', 'download', args=row.component.img), _width=75, _height=75)))]
    db.component.img.represent = None
    db.component.img.readable = db.component.img.writable = False

    form = SQLFORM.grid(
        query,
        left=left,
        fields=fields,
        links=links,
        showbuttontext=False,
        details=False,
        deletable=True,
        editable=True,
        searchable=False,
        create=False,
        upload=URL('default', 'download'),
        links_placement='left',
        csv=False,
        exportclasses=None,
        user_signature=False,
        _class='itemlist-grid')

    return dict(form=form)


def search():

    finalresults = []

    # Model Query
    query = (db.model.name.like('%' + request.vars.s + '%')
             | db.model.description.like('%' + request.vars.s + '%')
             | db.model.notes.like('%' + request.vars.s + '%')
             )

    results = db(query).select(db.model.id, db.model.img, db.model.name,
                               db.model.description, db.model.modelstate, orderby=db.model.name)

    for res in results:
        finalresults.append({
            # , "img": IMG(_src=URL('default', 'download', args=res.img), _alt='Image', _width='65px', _onerror="this.src = '" + URL('static', 'icons/nopicture.png') + "'")
            # , "desc": " ".join(res.description.split()[:30])
            "type": "model", "name": res.name, "url": URL('model', 'index', args=res.id), "img": IMG(_src=URL('default', 'download', args=res.img), _alt='Image', _width='65px'), "desc": "" if res.description is None else " ".join(res.description.split()[:30]), "state": res.modelstate, "tag": ""
        })

    # Component Query
    query = (db.component.name.like('%' + request.vars.s + '%')
             | db.component.notes.like('%' + request.vars.s + '%')
             )

    results = db(query).select(db.component.id, db.component.img, db.component.name,
                               db.component.notes, db.component.componenttype, orderby=db.component.name)

    for res in results:
        finalresults.append({
            "type": "component", "name": res.name, "url": URL('component', 'index', args=res.id), "img": IMG(_src=URL('default', 'download', args=res.img), _alt='Image', _width='65px', _onerror="this.src = '" + URL('static', 'icons/nopicture.png') + "'"), "desc": "" if res.notes == None else " ".join(res.notes.split()[:30]), "state": "", "tag": res.componenttype
        })

    # Library Query
    query = (db.article.name.like('%' + request.vars.s + '%')
             | db.article.summary.like('%' + request.vars.s + '%')
             | db.article.notes.like('%' + request.vars.s + '%')
             )

    results = db(query).select(db.article.id, db.article.img, db.article.name,
                               db.article.summary, db.article.articletype, orderby=db.article.name)

    for res in results:
        finalresults.append({
            "type": "article", "name": res.name, "url": URL('library', 'read', args=res.id), "img": IMG(_src=URL('default', 'download', args=res.img), _alt='Image', _width='65px', _onerror="this.src = '" + URL('static', 'icons/nopicture.png') + "'"), "desc": "" if res.summary == None else " ".join(res.summary.split()[:30]), "state": "", "tag": res.articletype
        })

    # response.view = 'content.html'
    if len(finalresults) == 1:  # Auto redirect if there is only 1 result
        redirect(finalresults[0]['url'])
    else:
        return dict(searchtext=request.vars.s, finalresults=finalresults)


@request.restful()
def api():
    response.view = 'api.json'

    def GET1(*args, **vars):
        return dict()

    def GET(theRequest):
        #activeModels = activeModels()
        if theRequest == 'active':
            return dict(header="Active Models", models=activeModels())
        elif theRequest == 'selected':
            return dict(header="Selected Models", models=selectedModels())
        elif theRequest == 'stats':
            return dict(header="The Hangar", stats=theHangarStats())
        else:
            return dict()

    return locals()


def hass():
    a = activeModels()
    a += underConstructionModels()
    return dict(header="Active Models", models=a, rand=random.choice(a))


def final():
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    query = db((db.model.modelstate > 3) | (
        (db.model.modelstate == 2) & (db.model.havekit == True)))

    fields = (db.model.img, db.model.name, db.model.modeltype,
              db.model.final_disposition, db.model.final_value)

    links = [
        lambda row: A('Print Details', _href=URL('model', 'export',
                      args=[row.id]), _class='btn btn-secondary'),
        lambda row: A('Mark Gone', _href=URL('model', 'retire',
                      args=[row.id]), _class='btn btn-primary')
    ]

    models = SQLFORM.grid(
        query  # db.model  # , groupby=db.component.componenttype
        , args=request.args[:1], orderby=db.model.name, editable=False, deletable=False, details=False, maxtextlength=255, create=False, fields=fields, links=links, _class='itemlist-grid', user_signature=False
    )

    #response.view = 'content.html'
    return dict(models=models)


def editfinal():
    models = query = db((db.model.modelstate > 3) | (
        (db.model.modelstate == 2) & (db.model.havekit == True))).select()

    #response.view = 'content.html'
    return dict(models=models)


def editfinal_render():
    model = db.model(request.args(0)) or None

    form = SQLFORM(db.model
                   , model.id
                   , fields=["final_disposition", "final_value"]
                   , buttons=[BUTTON('Submit', _type='submit', _id='btn_' + str(model.id), _class="btn btn-outline-primary")]
                   , comments=False)
    inputs = form.elements('input', _type='text')
    for s in inputs:
        s['_autocomplete'] = 'off'
        s['_onkeypress'] = "enableButton('" + 'btn_' + str(model.id) + "');"
    if form.process(formname='m_' + str(model.id)).accepted:
        response.flash = "Disposition Set"
    elif form.errors:
        response.flash = "Error Setting Disposition"

    return dict(form=form, model=model)

def inventory():

    response.title = 'Component Inventory'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    components = db(db.component).select(orderby=db.component.componenttype | db.component.name)
    propellers = db(db.propeller).select(orderby=db.propeller.item, distinct=True)

    hardware = db(db.hardware).select(orderby=db.hardware.hardwaretype | db.hardware.diameter | db.hardware.length_mm)
    unique_formatted_values = set()
    unique_hardware = []
    for row in hardware:
        value = f'{row.hardwaretype}_{row.diameter}_{row.length_mm}'
        if value not in unique_formatted_values:
            unique_formatted_values.add(value)
            unique_hardware.append(row)

    batteries = db(db.battery).select(orderby=db.battery.chemistry | db.battery.cellcount | db.battery.mah | db.battery.crating)

    return dict(components=components, propellers=propellers, hardware=unique_hardware, batteries=batteries)