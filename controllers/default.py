# -*- coding: utf-8 -*-

import random
import urllib
import os
import json as _json


def quick_search():
    """Simple text search across model, component, article, and tag names."""
    s = (request.vars.get('s') or '').strip()
    results = []
    if s:
        pat = '%' + s + '%'

        # Models by name
        for row in db(db.model.name.like(pat)).select(
                db.model.id, db.model.name, db.model.img,
                db.model.modeltype, orderby=db.model.name):
            results.append({'controller': 'model', 'name': row.name,
                            'img': row.img, 'sub': row.modeltype or '',
                            'url': URL('model', 'index', args=row.id)})

        # Components by name + models that use each matching component
        seen_models = set(r['url'] for r in results)
        for crow in db(db.component.name.like(pat)).select(
                db.component.id, db.component.name, db.component.img,
                db.component.componenttype, orderby=db.component.name):
            results.append({'controller': 'component', 'name': crow.name,
                            'img': crow.img, 'sub': crow.componenttype or '',
                            'url': URL('component', 'index', args=crow.id)})
            for mc in db(db.model_component.component == crow.id).select(db.model_component.model):
                mrow = db.model(mc.model)
                if mrow:
                    mu = URL('model', 'index', args=mrow.id)
                    if mu not in seen_models:
                        seen_models.add(mu)
                        results.append({'controller': 'model',
                                        'name': mrow.name,
                                        'img': mrow.img,
                                        'sub': 'has: ' + crow.name,
                                        'url': mu})

        # Articles by name
        for row in db(db.article.name.like(pat)).select(
                db.article.id, db.article.name, db.article.img,
                db.article.articletype, orderby=db.article.name):
            results.append({'controller': 'article', 'name': row.name,
                            'img': row.img, 'sub': row.articletype or '',
                            'url': URL('library', 'read', args=row.id)})

        # Tags by name + articles that have each matching tag
        seen_articles = set()
        for trow in db(db.tag.name.like(pat)).select(
                db.tag.id, db.tag.name, orderby=db.tag.name):
            results.append({'controller': 'tag', 'name': trow.name,
                            'img': None, 'sub': '',
                            'url': URL('tag', 'listview')})
            for arow in db(db.article.tags.contains(trow.id)).select(
                    db.article.id, db.article.name, db.article.img,
                    db.article.articletype, orderby=db.article.name):
                au = URL('library', 'read', args=arow.id)
                if au not in seen_articles:
                    seen_articles.add(au)
                    results.append({'controller': 'article',
                                    'name': arow.name,
                                    'img': arow.img,
                                    'sub': 'tagged: ' + trow.name,
                                    'url': au})
        if len(results) == 1:
            redirect(results[0]['url'])
    return dict(s=s, results=results)


def search():
    """Advanced QueryBuilder search across models and related tables."""
    session.ReturnHere = URL(args=request.args, vars=request.get_vars, host=True)

    rules_json   = request.vars.get('q', '')
    results      = []
    result_count = 0
    search_error = None
    search_sql   = None

    # Pre-build modelstate name lookup so the view doesn't need extra queries
    state_names = {r.id: r.name for r in db().select(db.modelstate.id, db.modelstate.name)}

    if rules_json:
        try:
            rules     = _json.loads(rules_json)
            condition = parse_search_query(rules)
            if condition is not None:
                results      = db(condition).select(
                    db.model.id, db.model.name, db.model.img,
                    db.model.modeltype, db.model.modelstate, db.model.modelcategory,
                    orderby=db.model.name)
                result_count = len(results)
                search_sql   = db._lastsql
        except Exception as e:
            import traceback
            search_error = str(e) + '\n' + traceback.format_exc()

    fields_config = get_qb_field_config()

    return dict(
        fields_config = fields_config,
        results       = results,
        result_count  = result_count,
        rules_json    = rules_json,
        search_error  = search_error,
        search_sql    = search_sql,
        state_names   = state_names,
    )
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
    session.ReturnHere = URL(args=request.args, vars=request.get_vars, host=True)

    if 'ui' not in request.cookies:
        request.cookies['ui'] = 'list'

    state_number = 4
    state_plus = True
    filter_text = {
        'modeltype': '', 'controltype': '', 'powerplant': '',
        'plankit': '', 'transmitter': '', 'subjecttype': '', 'selected': ''
    }

    states = db(db.modelstate).select(db.modelstate.id, db.modelstate.name)
    filterstatelist = []
    log = []
    queries = []

    wasFormUsed = False
    modelCategory = None
    if 'ui' in request.cookies and request.cookies['ui'].value != 'dashboard':
        viableOptions = [o[1] for o in db.model.modelcategory.requires.options()]
        modelCategory = viableOptions[2]
        if request.vars.get('c') in viableOptions:
            modelCategory = request.vars['c']
        queries.append(db.model.modelcategory == modelCategory)

    for s in states:
        filter_text[s.name] = ''

    if 's' in request.vars:
        state = request.vars['s']
        try:
            if len(str(state)) == 2 and state[1] == '*':
                state_number = int(state[0])
                state_plus = True
            else:
                state_number = int(state)
                state_plus = False
        except (ValueError, IndexError):
            pass

    state_param = str(state_number) + ('*' if state_plus else '')

    # Read filter values from GET params
    filters = {
        'modeltype':   request.vars.get('modeltype',   '') or '',
        'controltype': request.vars.get('controltype', '') or '',
        'powerplant':  request.vars.get('powerplant',  '') or '',
        'plankit':     request.vars.get('plankit',     '') or '',
        'transmitter': request.vars.get('transmitter', '') or '',
        'subjecttype': request.vars.get('subjecttype', '') or '',
        'isselected':  request.vars.get('isselected',  '') or '',
    }
    fstates_param = request.vars.get('fstates', '') or ''

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
    fields.append(Field('isselected', 'boolean', label='Is Selected', required=False))
    for s in states:
        fields.append(Field('s' + str(s.id), 'boolean',
                            label=s.name, default=(s.id > 2), required=False))

    selectform = SQLFORM.factory(
        *fields, formstyle='divs', keepvalues=True, _class='filterform', table_name='filter_form')

    if selectform.process(message_onsuccess=None).accepted:
        # POST-redirect-GET: encode form values as URL params and redirect
        rvars = {}
        if modelCategory: rvars['c'] = modelCategory
        if request.vars.get('s'): rvars['s'] = request.vars['s']
        for key in ['modeltype', 'controltype', 'powerplant', 'plankit', 'transmitter', 'subjecttype']:
            if selectform.vars.get(key): rvars[key] = selectform.vars[key]
        if selectform.vars.get('isselected'): rvars['isselected'] = 'on'
        checked = [str(s.id) for s in states if selectform.vars.get('s' + str(s.id))]
        if checked: rvars['fstates'] = ','.join(checked)
        redirect(URL('default', 'index', vars=rvars))

    # Pre-populate form display from GET params
    for key in ['modeltype', 'controltype', 'powerplant', 'plankit', 'transmitter', 'subjecttype', 'isselected']:
        selectform.vars[key] = filters.get(key, '')
    if fstates_param:
        fstates_set = set(fstates_param.split(','))
        for s in states:
            selectform.vars['s' + str(s.id)] = str(s.id) in fstates_set

    if request.vars.get('clear'):
        rvars = {}
        if modelCategory: rvars['c'] = modelCategory
        rvars['s'] = state_param
        redirect(URL('default', 'index', vars=rvars))

    # Apply filter queries from GET params
    wasFormUsed = bool(
        any(filters.get(k) for k in ['modeltype', 'controltype', 'powerplant', 'plankit', 'transmitter', 'subjecttype', 'isselected'])
        or fstates_param
    )

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
        pk = filters['plankit']
        if pk == 'Plan':
            queries.append(db.model.haveplans == True)
        elif pk == 'Kit':
            queries.append(db.model.havekit == True)
        elif pk == 'Both':
            queries.append((db.model.haveplans == True) & (db.model.havekit == True))
        elif pk == 'Neither':
            queries.append((db.model.haveplans == False) & (db.model.havekit == False))
        filter_text['plankit'] = pk

    if filters['transmitter']:
        queries.append(db.model.transmitter == filters['transmitter'])
        filter_text['transmitter'] = db.transmitter[filters['transmitter']].name

    if filters['isselected'] == 'on':
        queries.append(db.model.selected == True)
        filter_text['selected'] = 'Selected'

    if fstates_param:
        filterstatelist = [int(x) for x in fstates_param.split(',') if x.strip().isdigit()]
        if filterstatelist:
            queries.append(db.model.modelstate.belongs(filterstatelist))
            for s in states:
                if s.id in filterstatelist:
                    filter_text[s.name] = s.name

    if not wasFormUsed:
        if 'ui' in request.cookies and request.cookies['ui'].value == 'dashboard':
            queries.append((db.model.selected == True) & (db.model.modelstate > 1))
        else:
            if state_plus:
                queries.append(db.model.modelstate >= state_number)
            else:
                queries.append(db.model.modelstate == state_number)

    # Combine all active filter conditions with AND into a single DAL query
    query = reduce(lambda a, b: (a & b), queries)
    models = db(query).select(db.model.ALL, orderby=db.model.name)

    selected = None
    selectedmodel = None
    if request.args:
        selected = VerifyTableID('model', request.args(0))
        if selected:
            selectedmodel = db(db.model.id == selected).select().first()
    if selected is None:
        selected = -1
        selectedmodel = None

    if 'ui' in request.cookies and request.cookies['ui'].value == 'dashboard':
        response.view = 'default/dashboard.html'

    return dict(models=models, form=selectform, filters=filter_text, selected=selected,
                selectedmodel=selectedmodel, log=log, modelCategory=modelCategory,
                state_number=state_number, state_plus=state_plus, state_param=state_param)


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


def inline():
    """serves uploaded files inline (for browser-native PDF/image viewing)"""
    return response.download(request, db, attachment=False)


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
    propellers = db(db.propeller).select(orderby=db.propeller.item, groupby=db.propeller.item)

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