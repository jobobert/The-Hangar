
import json

def index():
    component_id = VerifyTableID('component', request.args(0)) or redirect(URL('component', 'listview'))

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    addform = SQLFORM(db.model_component, fields=["model", "purpose", "channel"], showid=False, comments=False)
    addform.vars.component = component_id
    if addform.process(session=None, formname="addtomodel").accepted:
        response.flash = "Added to Model"
    elif addform.errors:
        response.flash = "Error Adding to Model"

    component = db(db.component.id == component_id).select() or redirect(URL('component', 'listview'))
    models = models_and_components( db.component.id == component_id).select(db.model.id, db.model.name, db.model.img)
    flitetimes = db(db.eflite_time.motor == component_id).select()

    modelCount = dict()
    for m in models:
        if m.name in modelCount:
            modelCount[m.name] += 1
        else:
            modelCount[m.name] = 1
    modelIDs = dict()
    for m in models:
        modelIDs[m.name] = m.id

    

    response.title = "Component: " + component[0].name

    return dict(component=component, flitetimes=flitetimes, modelCount=modelCount, modelIDs=modelIDs, addform=addform)

def listview():

    response.title = 'Component List'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    types = []
    for x, y in db.component.componenttype.requires.options():
        if y != '':
            types.append(y)

    components = DIV('Choose the Component Type Above...',
                     _class='componentlist_choose')
    requestedtype = ''
    active = ''
    available = False

    if request.vars['a']:
        available = True

    if request.vars['c'] in types:
        requestedtype = request.vars['c']
        active = request.vars['c']
        fields = [db.component.img, db.component.name,
                  db.component.significantdetail]

        for attrib in component_attribs[requestedtype]:
            fields.append(db.component[attrib])

        fields.append(db.component.ownedcount)

        links = [
            dict(header='In Use', body=lambda row: DIV(row.get_usedcount(), _class='text-center')), 
            dict(header='Remaining', body=lambda row: DIV(B(row.get_remainingcount()), _class='text-center')), 
            lambda row: viewButton('component', 'index', [row.id]),
            lambda row: editButton('component', 'update', [row.id]),
            lambda row: plusButton('component', 'addcount', [row.id]),
            lambda row: minusButton('component', 'subtractcount', [row.id]),
        ]

        comp = db(db.component.componenttype == request.vars['c'])

        if available:
            available_ids = [r.id for r in comp.select() if r.get_remainingcount() > 0]
            comp = db(db.component.id.belongs(available_ids))

        components = SQLFORM.grid(
            comp, orderby=db.component.componenttype | db.component.name, args=request.args[:1], user_signature=False, editable=False, deletable=False, details=False, maxtextlength=255, create=False, links=links, fields=fields, _class='itemlist-grid', searchable=False
        )

    #response.view = 'content.html'
    return dict(components=components, types=types, requestedtype=requestedtype, active=active, available=available)


def usage():
    session.ReturnHere = URL(args=request.args, vars=request.get_vars, host=True)

    types = [y for x, y in db.component.componenttype.requires.options() if y != '']
    requestedtype = request.vars.get('c', '') if request.vars.get('c', '') in types else ''
    groupby = 'model' if request.vars.get('g') == 'model' else 'component'

    filter_specs = []
    filter_active = False

    if requestedtype:
        for attrname in component_attribs.get(requestedtype, []):
            field = db.component[attrname]
            ftype = field.type
            label = field.label

            if ftype == 'boolean':
                val = request.vars.get('f_' + attrname, '') or ''
                filter_specs.append({'name': attrname, 'label': label, 'kind': 'boolean', 'value': val})
                if val:
                    filter_active = True

            elif ftype in ('double', 'integer'):
                vmin = request.vars.get('f_' + attrname + '_min', '') or ''
                vmax = request.vars.get('f_' + attrname + '_max', '') or ''
                filter_specs.append({'name': attrname, 'label': label, 'kind': 'range',
                                     'step': 'any' if ftype == 'double' else '1',
                                     'min': vmin, 'max': vmax})
                if vmin or vmax:
                    filter_active = True

            elif ftype.startswith('reference '):
                ref_table = ftype.split(' ')[1]
                options = [(str(r.id), r.name) for r in db(db[ref_table]).select()]
                val = request.vars.get('f_' + attrname, '') or ''
                filter_specs.append({'name': attrname, 'label': label, 'kind': 'select',
                                     'options': options, 'value': val})
                if val:
                    filter_active = True

            else:  # string
                req = field.requires
                if isinstance(req, (list, tuple)) and req:
                    req = req[0]
                if isinstance(req, IS_EMPTY_OR):
                    req = req.other
                options = list(req.theset) if isinstance(req, IS_IN_SET) else None
                val = request.vars.get('f_' + attrname, '') or ''
                if options is None:
                    rows_d = db(
                        (db.component.componenttype == requestedtype) &
                        (db.component[attrname] != None) &
                        (db.component[attrname] != '')
                    ).select(db.component[attrname], distinct=True, orderby=db.component[attrname])
                    options = [r[attrname] for r in rows_d]
                filter_specs.append({'name': attrname, 'label': label, 'kind': 'select',
                                     'options': [(o, o) for o in options], 'value': val})
                if val:
                    filter_active = True

    groups = []
    if requestedtype:
        q = models_and_components(db.component.componenttype == requestedtype)

        for spec in filter_specs:
            fname = spec['name']
            kind = spec['kind']
            if kind == 'range':
                if spec['min']:
                    try: q = q(db.component[fname] >= float(spec['min']))
                    except (ValueError, TypeError): pass
                if spec['max']:
                    try: q = q(db.component[fname] <= float(spec['max']))
                    except (ValueError, TypeError): pass
            elif kind == 'boolean':
                if spec['value'] == 'yes':
                    q = q(db.component[fname] == True)
                elif spec['value'] == 'no':
                    q = q((db.component[fname] == False) | (db.component[fname] == None))
            elif kind == 'select' and spec.get('value'):
                if db.component[fname].type.startswith('reference '):
                    try: q = q(db.component[fname] == int(spec['value']))
                    except (ValueError, TypeError): pass
                else:
                    q = q(db.component[fname] == spec['value'])
            elif kind == 'text' and spec.get('value'):
                q = q(db.component[fname].contains(spec['value']))

        rows = q.select(
            db.component.id, db.component.name, db.component.significantdetail, db.component.img,
            db.model.id, db.model.name, db.model.img, db.model.modelstate,
            db.model_component.purpose, db.model_component.channel,
            orderby=db.component.name | db.model.name
        )

        if groupby == 'model':
            seen = {}
            for row in rows:
                mid = row.model.id
                if mid not in seen:
                    seen[mid] = {'model': row.model, 'entries': []}
                seen[mid]['entries'].append({'component': row.component, 'mc': row.model_component})
            groups = list(seen.values())
        else:
            seen = {}
            for row in rows:
                cid = row.component.id
                if cid not in seen:
                    seen[cid] = {'component': row.component, 'entries': []}
                seen[cid]['entries'].append({'model': row.model, 'mc': row.model_component})
            groups = list(seen.values())

    return dict(types=types, requestedtype=requestedtype, groupby=groupby, groups=groups,
                filter_specs=filter_specs, filter_active=filter_active)


def addcount():

    component_id = VerifyTableID('component', request.args(0)) or redirect(session.ReturnHere or URL('component', 'listview'))
    row = db.component(component_id)
    if row.ownedcount == None:
        row.update_record(ownedcount=(1))
    else:
        row.update_record(ownedcount=(row.ownedcount + 1))

    return redirect(session.ReturnHere or URL('component', 'listview'))

def subtractcount():

    component_id = VerifyTableID('component', request.args(0)) or redirect(session.ReturnHere or URL('component', 'listview'))
    row = db.component(component_id)
    if row.ownedcount > 0:
        row.update_record(ownedcount=(row.ownedcount - 1))
    return redirect(session.ReturnHere or URL('component', 'listview'))

def update():

    response.title = 'Add/Update Component'
    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    form = SQLFORM(db.component, request.args(0), upload=URL(
        'default', 'download'), deletable=True, showid=False).process(
        message_onsuccess='Document %s' % ('updated' if request.args else 'added')) 

    if form.accepted:
        redirect(URL('component', 'index', args=form.vars.id,
                 extension="html") or session.ReturnHere)

    disable_autocomplete(form)

    return dict(form=form, component_attribs=json.dumps(component_attribs))

def rendercard_grid():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'component', 'Components')
    
    newcomponentname = ""

    newform = SQLFORM(db.component, showid=False,
                      formstyle='bootstrap4_inline')
    disable_autocomplete(newform)
    if newform.process(session=None, formname='newcomponent').accepted:
        newcomponentname = newform.vars.name
    elif newform.errors:
        response.flash = "Error Creating New Component"

    query = db(db.model_component.model == model_id)
    left = db.component.on(db.component.id == db.model_component.component)
    fields = [db.component.name, db.model_component.purpose,
              db.model_component.channel, db.component.img, db.component.attachment]
    links = [dict(header=T('Img'),
                  body=lambda row: A(IMG(_src=URL('default', 'download', args=row.component.img), _width=75, _height=75)))]
    db.component.img.represent = None
    db.component.img.readable = db.component.img.writable = False

    grid = SQLFORM.grid(
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

    component_count = db(db.model_component.model == model_id).count() or None
    components = models_and_components(
        db.model.id == model_id).iterselect() or None

    return dict(components=components, component_count=component_count, grid=grid, newform=newform, options=request.args(1))

def rendercard():
    session.forget(response)
    if len(request.args) == 2:
        is_mobile = request.args[1]
    else:
        is_mobile = False 

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'component', 'Components')
    
    addform = SQLFORM(db.model_component, fields=[
                      "component", "purpose", "channel"], comments=False)
    addform.vars.model = request.args(0)
    disable_autocomplete(addform)
    if addform.process(session=None, formname='addcomponent').accepted:
        response.flash = "New Component Added"
    elif addform.errors:
        response.flash = "Error Adding Component"

    newform = SQLFORM(db.component, fields=[
        'name', 'componenttype', 'componentsubtype', 'significantdetail', 'serial',
        'manufacturer', 'ownedcount', 'storedat',
        'attr_length', 'attr_width', 'attr_height', 'attr_weight_oz',
        'attr_channel_count', 'attr_telemetry_port', 'attr_sbus_port', 'attr_pwr_port',
        'attr_protocol', 'attr_gear_type', 'attr_amps_in', 'attr_amps_out',
        'attr_torque', 'attr_switch_type', 'attr_displacement_cc', 'attr_motor_kv',
        'attr_voltage_in', 'attr_voltage_out', 'attr_num_turns', 'attr_watts_in',
        'attr_watts_out', 'attr_pump_type', 'attr_travel', 'attr_model_scale',
        'attr_firmware_version',
    ], showid=False, formstyle='divs')
    disable_autocomplete(newform)
    if newform.process(session=None, formname='newcomponent').accepted:
        try:
            channel = int(request.vars.newcomponent_channel) if request.vars.newcomponent_channel else None
        except (ValueError, TypeError):
            channel = None
        db.model_component.insert(
            model=model_id,
            component=newform.vars.id,
            purpose=request.vars.newcomponent_purpose or '',
            channel=channel,
        )
        response.flash = "Component added to model"
    elif newform.errors:
        response.flash = "Error Creating New Component"

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='componentdeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.model_component.id == del_id).delete()
                response.flash = "Removal Success"
    elif deleteform.errors:
        response.flash = "Removal Failure"

    component_count = db(db.model_component.model == model_id).count()
    components = models_and_components(db.model.id == model_id).iterselect()

    return dict(components=components, model_id=model_id, component_count=component_count,
                options=request.args(1), addform=addform, newform=newform, deleteform=deleteform,
                component_attribs=json.dumps(component_attribs), is_mobile=is_mobile)

def export():
    component_id = VerifyTableID('component', request.args(0))

    comp = db(db.component.id == component_id).select().first() or redirect(URL('component', 'listview'))

    torender = {
        'title': comp.name,
        'items': [],
        'emptymsg': 'Component Not Found',
        'controller': 'component',
        'header': None,
    }

    content = {
        'name': comp.name,
        'img': comp.img,
        'attachment': comp.attachment, 
        'details': []
    }
    

    content['details'] = [
        (getattr(db.component,'serial').label, comp.serial),
        (getattr(db.component,'componenttype').label, comp.componenttype),
        (getattr(db.component,'componentsubtype').label, comp.componentsubtype),
        (getattr(db.component,'significantdetail').label, comp.significantdetail),
        (getattr(db.component,'notes').label, MARKMIN(comp.notes) if comp.notes else  ''),
        (getattr(db.component,'ownedcount').label, comp.ownedcount),
        (getattr(db.component,'storedat').label, comp.storedat),
    ]
    # Append any populated type-specific attribute fields (stored as attr_* columns)
    for key in comp.__dict__:
        if key.startswith('attr_') and comp[key]:
            name = getattr(db.component, key).label
            value = None
            if getattr(db.component, key).type == 'double':
                value = TwoDecimal(comp[key])
            else:
                value = comp[key]
            content['details'].append((name, value))


    torender['items'].append(content)
    
    return dict(content=torender)

def renderexport_formodel():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'component', 'Components')
    
    components = models_and_components(
        db.model.id == model_id).select() or None

    torender = {
        'title': 'Components',
        'items': [],
        'emptymsg': 'No Components',
        'controller': 'component',
        'header': None,
    }
    for component in components or []:
        comp = component.component
        content = {
            'name': comp.name,
            'img': comp.img,
            'attachment': comp.attachment, 
            'details': []
        }
        function = ''
        if component.model_component.purpose:
            function = component.model_component.purpose
        else:
            function = "General Purpose"
        if component.model_component.channel:
            function += " on channel " + str(component.model_component.channel)

        content['details'] = [
            (getattr(db.component,'componenttype').label, comp.componenttype),
            (getattr(db.component,'componentsubtype').label, comp.componentsubtype),
            ('function', function),
        ]
        if comp.serial:
            content['details'].append((getattr(db.component,'serial').label, comp.serial))
        
        torender['items'].append(content)
    
    response.view = 'renderexport.load'
    return dict(content=torender)
    
def addtomodel():

    response.title = 'Add Component to Model'

    form = SQLFORM(db.model_component)
    form.vars.model = request.args(0)

    disable_autocomplete(form)
    if form.process(next=(URL('default', 'index', extension="html"))).accepted:
        response.flash = "New Component Added"
    elif form.errors:
        response.flash = "Error Adding New Component"

    response.view = 'content.html'

    return dict(content=form)

def removefrommodel():
    # try to do this via ajax sometime...
    # session.forget(response)

    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('default', 'index'))
    relationship_id = VerifyTableID('model_component', request.args(1)) or redirect(URL('default', 'index'))
    db(db.model_component.id == relationship_id).delete()

    return redirect(URL('model', 'index.html', args=model_id))

def updatemodelrelation():

    relationship_id = request.args[0]

    rel = db(db.model_component.model == relationship_id).select().first()

    fields = ['purpose', 'channel']

    form = SQLFORM(db.model_component, relationship_id, fields=fields, showid=False)

    disable_autocomplete(form)
    if form.process().accepted:
        session.flash = "Relationship Updated"
        redirect(session.ReturnHere or URL(
            'default', 'index', extension="html"))
    elif form.errors:
        response.flash = "Error Updating Component Relationship"

    response.view = 'content.html'

    header = ''
    if rel:
        header = rel.component.name + ' on ' + rel.model.name

    return dict(content=form, header=header)

def delete():
    component_id = VerifyTableID('component', request.args(0)) or redirect(URL('component', 'listview'))

    #if db(db.model_component.component == component_id).count() > 0:
    if db(db.model_component.component == component_id).select(db.model_component.id, limitby=(0,1)).first():
        session.flash = "Cannot delete: component is assigned to models!"
        redirect(session.ReturnHere or URL('component', 'listview'))

    #if db(db.eflite_time.motor == component_id).count() > 0:
    if db(db.eflite_time.motor == component_id).select(db.eflite_time.id, limitby=(0,1)).first():
        session.flash = "Cannot delete: component is assigned to a flight time!"
        redirect(session.ReturnHere or URL('component', 'listview'))

    if component_id:
        db(db.component.id == component_id).delete()
        session.flash = "Deleted"
        
    return redirect(session.ReturnHere or URL('component', 'listview'))