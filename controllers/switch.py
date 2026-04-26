
def add():
    model_id = VerifyTableID('model', request.args(0))

    if not model_id:
        redirect(session.ReturnHere or URL('default','index'))

    fields = ['switch', 'switchtype', 'purpose']
    
    form = SQLFORM(db.switch, fields=fields, showid=False, deletable=True)
    form.vars.model = model_id
    if form.process().accepted:
        session.flash = "Switch Added"
        redirect(session.ReturnHere or URL('default','index'))
    elif form.errors:
        response.flash = "Error Adding Switch"

    return dict(form=form)

def renderswitches():
    session.forget(response)
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate this model', 'model', 'Models')
    render_card = request.args(1)

    switchList = {}
    x = 0

    new_switches = db(db.model_switch.model == model_id).select(orderby=db.model_switch.id)

    if new_switches:
        all_ms_ids = [s.id for s in new_switches]
        pos_rows = db(db.model_switch_position.model_switch.belongs(all_ms_ids)).select(
            orderby=db.model_switch_position.id)
        pos_map = {}
        for p in pos_rows:
            pos_map.setdefault(p.model_switch, {})[p.pos] = p.func

        for s in new_switches:
            x += 1
            ts = db.transmitter_switch[s.transmitter_switch] if s.transmitter_switch else None
            switchList[x] = {
                'id':       s.id,
                'mid':      s.model,
                'switch':   ts.name if ts else (s.name or ''),
                'type':     ts.switchtype if ts else (s.switchtype or ''),
                'purpose':  s.purpose or '',
                'positions': pos_map.get(s.id, {}),
            }
    else:
        switches = db(db.switch.model == model_id).select()
        for s in switches:
            x += 1
            switchPos = {}
            for p in db(db.switch_position.switch == s.id).select():
                switchPos[p.pos] = p.func
            switchList[x] = {
                'id':       s.id,
                'mid':      s.model.id,
                'switch':   s.switch,
                'type':     s.switchtype,
                'purpose':  s.purpose,
                'positions': switchPos,
            }

    return dict(switchList=switchList, switch_count=x, model_id=model_id, render_card=render_card)

def renderswitchtable():
    session.forget(response)
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate this model', 'model', 'Models')

    switchList = {}
    x = 0

    new_switches = db(db.model_switch.model == model_id).select(
        orderby=db.model_switch.id)

    if new_switches:
        all_ms_ids = [s.id for s in new_switches]
        pos_rows = db(db.model_switch_position.model_switch.belongs(all_ms_ids)).select(
            orderby=db.model_switch_position.id)
        pos_map = {}
        for p in pos_rows:
            pos_map.setdefault(p.model_switch, {})[p.pos] = p.func

        for s in new_switches:
            x += 1
            ts = db.transmitter_switch[s.transmitter_switch] if s.transmitter_switch else None
            switchList[x] = {
                'id':       s.id,
                'mid':      s.model,
                'switch':   ts.name if ts else (s.name or ''),
                'type':     ts.switchtype if ts else (s.switchtype or ''),
                'purpose':  s.purpose or '',
                'positions': pos_map.get(s.id, {}),
            }
    else:
        switches = db(db.switch.model == model_id).select()
        for s in switches:
            x += 1
            switchPos = {}
            for p in db(db.switch_position.switch == s.id).select():
                switchPos[p.pos] = p.func
            switchList[x] = {
                'id':       s.id,
                'mid':      s.model.id,
                'switch':   s.switch,
                'type':     s.switchtype,
                'purpose':  s.purpose,
                'positions': switchPos,
            }

    return dict(switchList=switchList, switch_count=x, model_id=model_id, options=request.args(1))

def update():

    switch_id = request.args(0) or None

    fields = ['model','switch','switchtype','purpose']

    form = SQLFORM(db.switch, switch_id, upload=URL(
        'default', 'download'), fields=fields,showid=False, deletable=True)
    if form.process().accepted:
        response.flash = "Switch Updated"
    elif form.errors:
        response.flash = "Error Updating Switch"

    return dict(form=form, switch_id=switch_id)

def renderpositions():
    session.forget(response)
    switch_id = request.args[0] or None
    newpos = ""

    fields = ['pos', 'func']

    addform = SQLFORM(db.switch_position,fields=fields)
    addform.vars.switch = switch_id
    if addform.process(session=None, formname='addposition').accepted:
        response.flash = "New Position Added"
    elif addform.errors:
        response.flash = "Error Adding Position"

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='positiondeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                del_id = y
                db(db.switch_position.id == del_id).delete()
                response.flash = "Removal Success"
                #response.flash = str(del_id) + " Removal Success"
    elif deleteform.errors:
        response.flash = "Removal Failure"

    position_count = db(db.switch_position.switch == switch_id).count()
    positions = db(db.switch_position.switch == switch_id).iterselect() #or None

    return dict(position_count=position_count, positions=positions, addform=addform,deleteform=deleteform)

###############################################
## TRANSMITTER SWITCH CRUD

def transmitter_switch_move():
    """AJAX endpoint: update x/y position of a transmitter_switch by drag-and-drop."""
    switch_id = VerifyTableID('transmitter_switch', request.vars.switch_id)
    if not switch_id:
        return response.json({'ok': False, 'error': 'Invalid switch'})
    try:
        x = round(max(0.0, min(100.0, float(request.vars.x))), 1)
        y = round(max(0.0, min(100.0, float(request.vars.y))), 1)
    except (TypeError, ValueError):
        return response.json({'ok': False, 'error': 'Invalid coordinates'})
    db(db.transmitter_switch.id == switch_id).update(x=x, y=y)
    return response.json({'ok': True, 'x': x, 'y': y})

def transmitter_layout_canvas():
    session.forget(response)
    transmitter_id = VerifyTableID('transmitter', request.args(0))
    if not transmitter_id:
        return render_card_error('Unable to locate this transmitter', 'transmitter', 'Transmitters')

    switches = db(db.transmitter_switch.transmitter == transmitter_id).select(
        orderby=db.transmitter_switch.sort_order | db.transmitter_switch.name)

    add_form = SQLFORM(db.transmitter_switch,
                       fields=['name', 'switchtype', 'x', 'y', 'sort_order'],
                       showid=False)
    add_form.vars.transmitter = transmitter_id
    if add_form.process(session=None, formname='addswitch').accepted:
        response.flash = 'Switch added'
        switches = db(db.transmitter_switch.transmitter == transmitter_id).select(
            orderby=db.transmitter_switch.sort_order | db.transmitter_switch.name)
    elif add_form.errors:
        response.flash = 'Error adding switch'

    edit_forms = {}
    for sw in switches:
        eform = SQLFORM(db.transmitter_switch, sw.id,
                        fields=['name', 'switchtype', 'x', 'y', 'sort_order'],
                        showid=False, deletable=True)
        if eform.process(session=None, formname=f'editswitch_{sw.id}').accepted:
            response.flash = 'Switch updated'
            switches = db(db.transmitter_switch.transmitter == transmitter_id).select(
                orderby=db.transmitter_switch.sort_order | db.transmitter_switch.name)
        elif eform.errors:
            response.flash = 'Error updating switch'
        edit_forms[sw.id] = eform

    return dict(switches=switches, add_form=add_form, edit_forms=edit_forms,
                transmitter_id=transmitter_id)


def transmitter_switch_delete():
    switch_id = VerifyTableID('transmitter_switch', request.args(0))
    if not switch_id:
        response.flash = 'Invalid switch'
        return dict()
    if db(db.model_switch.transmitter_switch == switch_id).count() > 0:
        session.flash = 'Cannot delete: switch is used by one or more models'
        redirect(session.ReturnHere or URL('transmitter', 'index'))
    transmitter_id = db.transmitter_switch[switch_id].transmitter
    db(db.transmitter_switch.id == switch_id).delete()
    session.flash = 'Switch deleted'
    redirect(URL('transmitter', 'index', args=[transmitter_id], extension='html'))


###############################################
## MODEL SWITCH CRUD

def model_switch_card():
    session.forget(response)
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate this model', 'model', 'Models')

    model = db.model[model_id]
    transmitter_id = model.transmitter if model else None

    transmitter_switches = []
    assigned_map = {}

    if transmitter_id:
        transmitter_switches = db(db.transmitter_switch.transmitter == transmitter_id).select(
            orderby=db.transmitter_switch.sort_order | db.transmitter_switch.name)
        assigned = db(db.model_switch.model == model_id).select()
        assigned_map = {ms.transmitter_switch: ms for ms in assigned if ms.transmitter_switch}

    freeform_switches = db((db.model_switch.model == model_id) &
                           (db.model_switch.transmitter_switch == None)).select()

    add_freeform_form = SQLFORM(db.model_switch,
                                fields=['name', 'switchtype', 'purpose', 'notes'],
                                showid=False)
    add_freeform_form.vars.model = model_id
    if add_freeform_form.process(session=None, formname='addfreeform').accepted:
        response.flash = 'Switch added'
        freeform_switches = db((db.model_switch.model == model_id) &
                               (db.model_switch.transmitter_switch == None)).select()
    elif add_freeform_form.errors:
        response.flash = 'Error adding switch'

    assign_forms = {}
    for ts in transmitter_switches:
        if ts.id not in assigned_map:
            aform = SQLFORM(db.model_switch,
                            fields=['purpose', 'notes'],
                            showid=False)
            aform.vars.model = model_id
            aform.vars.transmitter_switch = ts.id
            if aform.process(session=None, formname=f'assign_{ts.id}').accepted:
                response.flash = f'{ts.name} assigned'
                assigned_map[ts.id] = db.model_switch[aform.vars.id]
            elif aform.errors:
                response.flash = 'Error assigning switch'
            assign_forms[ts.id] = aform

    edit_forms = {}
    for ts_id, ms in assigned_map.items():
        eform = SQLFORM(db.model_switch, ms.id,
                        fields=['purpose', 'notes'],
                        showid=False, deletable=True)
        if eform.process(session=None, formname=f'editms_{ms.id}').accepted:
            response.flash = 'Switch updated'
            if eform.vars.delete_this_record:
                assigned_map.pop(ts_id, None)
            else:
                assigned_map[ts_id] = db.model_switch[ms.id]
        elif eform.errors:
            response.flash = 'Error updating switch'
        edit_forms[ms.id] = eform

    freeform_edit_forms = {}
    for ms in freeform_switches:
        eform = SQLFORM(db.model_switch, ms.id,
                        fields=['name', 'switchtype', 'purpose', 'notes'],
                        showid=False, deletable=True)
        if eform.process(session=None, formname=f'editff_{ms.id}').accepted:
            response.flash = 'Switch updated'
            freeform_switches = db((db.model_switch.model == model_id) &
                                   (db.model_switch.transmitter_switch == None)).select()
        elif eform.errors:
            response.flash = 'Error updating switch'
        freeform_edit_forms[ms.id] = eform

    # Pre-load positions for all model_switches on this model
    all_ms_ids = [ms.id for ms in list(assigned_map.values()) + list(freeform_switches)]
    positions_map = {}
    if all_ms_ids:
        for p in db(db.model_switch_position.model_switch.belongs(all_ms_ids)).select(
                orderby=db.model_switch_position.id):
            positions_map.setdefault(p.model_switch, []).append(p)

    position_forms = {}
    for ms_id in all_ms_ids:
        positions = positions_map.get(ms_id, [])

        addform = SQLFORM(db.model_switch_position, fields=['pos', 'func'], showid=False)
        addform.vars.model_switch = ms_id
        if addform.process(session=None, formname=f'addpos_{ms_id}').accepted:
            response.flash = 'Position added'
            positions = list(db(db.model_switch_position.model_switch == ms_id).select(
                              orderby=db.model_switch_position.id))
            positions_map[ms_id] = positions
        elif addform.errors:
            response.flash = 'Error adding position'

        delform = SQLFORM.factory()
        if delform.process(session=None, formname=f'delpos_{ms_id}').accepted:
            for k, v in request.vars.items():
                if v == 'Remove':
                    db(db.model_switch_position.id == k).delete()
                    positions = [p for p in positions if str(p.id) != str(k)]
                    positions_map[ms_id] = positions
                    response.flash = 'Position removed'

        pos_edit_forms = {}
        for p in list(positions):
            eform = SQLFORM(db.model_switch_position, p.id, fields=['pos', 'func'], showid=False)
            if eform.process(session=None, formname=f'editpos_{p.id}').accepted:
                response.flash = 'Position updated'
                positions = list(db(db.model_switch_position.model_switch == ms_id).select(
                                  orderby=db.model_switch_position.id))
                positions_map[ms_id] = positions
            elif eform.errors:
                response.flash = 'Error updating position'
            pos_edit_forms[p.id] = eform

        position_forms[ms_id] = dict(positions=positions, addform=addform, delform=delform,
                                     pos_edit_forms=pos_edit_forms)

    switch_count = len(assigned_map) + len(freeform_switches)

    return dict(
        model_id=model_id,
        model=model,
        transmitter_id=transmitter_id,
        transmitter_switches=transmitter_switches,
        assigned_map=assigned_map,
        freeform_switches=freeform_switches,
        add_freeform_form=add_freeform_form,
        assign_forms=assign_forms,
        edit_forms=edit_forms,
        freeform_edit_forms=freeform_edit_forms,
        positions_map=positions_map,
        position_forms=position_forms,
        switch_count=switch_count,
    )


def model_switch_positions():
    model_switch_id = VerifyTableID('model_switch', request.args(0))
    if not model_switch_id:
        return render_card_error('Unable to locate this switch', 'model', 'Models')

    fields = ['pos', 'func']

    addform = SQLFORM(db.model_switch_position, fields=fields)
    addform.vars.model_switch = model_switch_id
    if addform.process(session=None, formname='addposition').accepted:
        response.flash = 'Position added'
    elif addform.errors:
        response.flash = 'Error adding position'

    del_id = 0
    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='positiondeleteform').accepted:
        for y, z in request.vars.items():
            if z == 'Remove':
                del_id = y
                db(db.model_switch_position.id == del_id).delete()
                response.flash = 'Position removed'
    elif deleteform.errors:
        response.flash = 'Remove failed'

    position_count = db(db.model_switch_position.model_switch == model_switch_id).count()
    positions = db(db.model_switch_position.model_switch == model_switch_id).iterselect()

    return dict(position_count=position_count, positions=positions,
                addform=addform, deleteform=deleteform,
                model_switch_id=model_switch_id)


def change_transmitter():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        redirect(URL('model', 'listview'))
    model = db.model[model_id]

    # Phase 2: apply choices
    if request.post_vars.get('confirm') == '1':
        new_transmitter_id = int(request.post_vars.new_transmitter_id)
        linked = db((db.model_switch.model == model_id) &
                    (db.model_switch.transmitter_switch != None)).select()
        for ms in linked:
            old_ts = db.transmitter_switch[ms.transmitter_switch]
            choice = int(request.post_vars.get(f'map_{ms.id}', 0))
            if choice == -1:
                db(db.model_switch_position.model_switch == ms.id).delete()
                ms.delete_record()
            elif choice == 0:
                ms.update_record(transmitter_switch=None,
                                 name=old_ts.name, switchtype=old_ts.switchtype)
            else:
                ms.update_record(transmitter_switch=choice, name=None, switchtype=None)
        db.model[model_id].update_record(transmitter=new_transmitter_id)
        session.flash = 'Transmitter changed'
        redirect(URL('model', 'index', args=[model_id], extension='html'))

    # Phase 1 POST: compute pre-selections, show resolution form
    if request.post_vars.get('new_transmitter_id'):
        new_transmitter_id = int(request.post_vars.new_transmitter_id)
        new_ts_list = db(db.transmitter_switch.transmitter == new_transmitter_id).select(
            orderby=db.transmitter_switch.sort_order | db.transmitter_switch.name)
        new_ts_by_key = {(ts.name, ts.switchtype): ts for ts in new_ts_list}

        linked = db((db.model_switch.model == model_id) &
                    (db.model_switch.transmitter_switch != None)).select()
        rows = []
        for ms in linked:
            old_ts = db.transmitter_switch[ms.transmitter_switch]
            match = new_ts_by_key.get((old_ts.name, old_ts.switchtype))
            rows.append((ms, old_ts, match.id if match else 0))

        new_transmitter = db.transmitter[new_transmitter_id]
        new_ts_opts = [(0, '-- Keep as freeform --'), (-1, '-- Discard --')]
        for ts in new_ts_list:
            new_ts_opts.append((ts.id, f'{ts.name} ({ts.switchtype})'))

        return dict(phase=2, model=model, model_id=model_id,
                    new_transmitter=new_transmitter,
                    new_transmitter_id=new_transmitter_id,
                    rows=rows,
                    new_ts_opts=new_ts_opts)

    # GET: show transmitter selector
    transmitters = db(db.transmitter.id != model.transmitter).select(
        orderby=db.transmitter.name)
    return dict(phase=1, model=model, model_id=model_id, transmitters=transmitters)


###############################################
## PER-MODEL MIGRATION TOOL

def migrate_model_switches():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        redirect(URL('model', 'listview'))

    model = db.model[model_id]
    transmitter_id = model.transmitter if model else None

    old_switches = db(db.switch.model == model_id).select()
    transmitter_switch_opts = [(0, '-- Keep as freeform --'), (-1, '-- Skip / discard --')]
    if transmitter_id:
        for ts in db(db.transmitter_switch.transmitter == transmitter_id).select(
                orderby=db.transmitter_switch.sort_order | db.transmitter_switch.name):
            transmitter_switch_opts.append((ts.id, f'{ts.name} ({ts.switchtype})' if ts.switchtype else ts.name))

    if request.post_vars:
        for s in old_switches:
            choice = int(request.post_vars.get(f'map_{s.id}', 0))
            if choice == -1:
                continue
            ms_id = db.model_switch.insert(
                model=model_id,
                transmitter_switch=choice if choice > 0 else None,
                name=s.switch if choice == 0 else None,
                switchtype=s.switchtype if choice == 0 else None,
                purpose=s.purpose,
            )
            for p in db(db.switch_position.switch == s.id).select():
                db.model_switch_position.insert(
                    model_switch=ms_id,
                    pos=p.pos,
                    func=p.func,
                )
        _mark_migration(f'model_switch_migrated_{model_id}')
        session.flash = 'Migration complete'
        redirect(URL('model', 'index', args=[model_id], extension='html'))

    already_migrated = _migration_applied(f'model_switch_migrated_{model_id}')
    old_with_positions = []
    for s in old_switches:
        positions = db(db.switch_position.switch == s.id).select()
        old_with_positions.append((s, list(positions)))

    return dict(model=model, model_id=model_id,
                old_with_positions=old_with_positions,
                transmitter_switch_opts=transmitter_switch_opts,
                already_migrated=already_migrated)


def listswitches():
    session.forget(response)
    transmitter_id = VerifyTableID('transmitter', request.args(0))

    try:
        if not transmitter_id:
            return render_card_error('Unable to locate this transmitter')

        # Models using this transmitter (active only)
        model_ids = [r.id for r in db((db.model.transmitter == transmitter_id) &
                                      (db.model.modelstate > 1)).select(db.model.id)]

        # Try new model_switch table first
        new_switches = db((db.model_switch.model.belongs(model_ids))).select(
            db.model_switch.ALL, db.model.name, db.model.id, db.model.protocol,
            left=db.model.on(db.model_switch.model == db.model.id))

        old_switches = db((db.switch.model.belongs(model_ids))).select(
            db.switch.ALL, db.model.name, db.model.id, db.model.protocol,
            left=db.model.on(db.switch.model == db.model.id))

        # If a model has new records use those; otherwise fall back to old
        migrated_models = set(ms['model_switch.model'] for ms in new_switches)

        rows_source = []
        for s in new_switches:
            name = (db.transmitter_switch[s['model_switch.transmitter_switch']].name
                    if s['model_switch.transmitter_switch'] else s['model_switch.name'])
            rows_source.append({
                'model_name': s['model.name'],
                'model_id': s['model.id'],
                'switch_name': name or '',
                'purpose': s['model_switch.purpose'] or '',
                'protocol': s['model.protocol'],
                'legacy': False,
            })
        for s in old_switches:
            if s['switch.model'] in migrated_models:
                continue
            rows_source.append({
                'model_name': s['model.name'],
                'model_id': s['model.id'],
                'switch_name': s['switch.switch'] or '',
                'purpose': s['switch.purpose'] or '',
                'protocol': s['model.protocol'],
                'legacy': True,
            })

        switch_names = sorted(set(r['switch_name'] for r in rows_source if r['switch_name']))
        model_names = sorted(set(r['model_name'] for r in rows_source))

        table_data = {}
        model_data = {}
        for r in rows_source:
            table_data[(r['model_name'], r['switch_name'])] = r['purpose']
            try:
                proto = r['protocol'].name if r['protocol'] else 'No Protocol'
            except Exception:
                proto = 'No Protocol'
            model_data[(r['model_name'], 'protocol')] = proto
            model_data[(r['model_name'], 'actions')] = A(
                'Go', _href=URL('model', 'index', args=[r['model_id']], extension='html'),
                _class='btn btn-primary btn-sm')
            if r['legacy']:
                model_data[(r['model_name'], 'legacy')] = True

        rows = []
        for model_name in model_names:
            row = [model_name]
            for switch in switch_names:
                row.append(table_data.get((model_name, switch), ''))
            row.append(model_data.get((model_name, 'protocol'), 'No Protocol'))
            row.append(model_data.get((model_name, 'actions'), ''))
            rows.append(row)

        headers = ['Model'] + switch_names + ['Protocol', 'Actions']
        legacy_models = {r['model_name'] for r in rows_source if r['legacy']}

    except Exception as e:
        return render_card_error('An error occurred while fetching switches: ' + str(e))

    return dict(headers=headers, rows=rows, legacy_models=legacy_models)


def switchreport():
    session.forget(response)
    response.title = 'Switch Report'

    all_transmitters = db(db.transmitter).select(orderby=db.transmitter.name)

    selected_ids = request.vars.getlist('transmitter') or []
    selected_ids = [int(x) for x in selected_ids if str(x).isdigit()]

    active_tx_ids = [t.id for t in all_transmitters
                     if not selected_ids or t.id in selected_ids]

    tx_name_map = {t.id: t.name for t in all_transmitters}

    model_rows = db(
        (db.model.transmitter.belongs(active_tx_ids)) &
        (db.model.modelstate > 1)
    ).select(db.model.id, db.model.name, db.model.transmitter, db.model.protocol,
             orderby=db.model.name)

    model_ids = [r.id for r in model_rows]
    model_tx_map = {r.id: r.transmitter for r in model_rows}

    rows_source = []

    if model_ids:
        new_switches = db(db.model_switch.model.belongs(model_ids)).select(
            db.model_switch.ALL, db.model.name, db.model.id, db.model.protocol,
            left=db.model.on(db.model_switch.model == db.model.id))

        old_switches = db(db.switch.model.belongs(model_ids)).select(
            db.switch.ALL, db.model.name, db.model.id, db.model.protocol,
            left=db.model.on(db.switch.model == db.model.id))

        migrated_models = set(ms['model_switch.model'] for ms in new_switches)

        for s in new_switches:
            ts_id = s['model_switch.transmitter_switch']
            name = (db.transmitter_switch[ts_id].name if ts_id else s['model_switch.name'])
            mid = s['model.id']
            rows_source.append({
                'model_name':      s['model.name'],
                'model_id':        mid,
                'transmitter_name': tx_name_map.get(model_tx_map.get(mid), ''),
                'switch_name':     name or '',
                'purpose':         s['model_switch.purpose'] or '',
                'protocol':        s['model.protocol'],
                'legacy':          False,
            })
        for s in old_switches:
            if s['switch.model'] in migrated_models:
                continue
            mid = s['switch.model']
            rows_source.append({
                'model_name':      s['model.name'],
                'model_id':        mid,
                'transmitter_name': tx_name_map.get(model_tx_map.get(mid), ''),
                'switch_name':     s['switch.switch'] or '',
                'purpose':         s['switch.purpose'] or '',
                'protocol':        s['model.protocol'],
                'legacy':          True,
            })

    switch_names = sorted(set(r['switch_name'] for r in rows_source if r['switch_name']))
    model_keys = sorted(set((r['transmitter_name'], r['model_name'], r['model_id'])
                            for r in rows_source))

    # Also include models with no switches at all
    for mr in model_rows:
        tx_name = tx_name_map.get(mr.transmitter, '')
        key = (tx_name, mr.name, mr.id)
        if key not in model_keys:
            model_keys.append(key)
    model_keys = sorted(model_keys)

    table_data = {}
    model_data = {}
    legacy_models = set()
    for r in rows_source:
        key = (r['transmitter_name'], r['model_name'])
        table_data[(key, r['switch_name'])] = r['purpose']
        try:
            proto = r['protocol'].name if r['protocol'] else 'No Protocol'
        except Exception:
            proto = 'No Protocol'
        model_data[(key, 'protocol')] = proto
        model_data[(key, 'actions')] = A(
            'Go', _href=URL('model', 'index', args=[r['model_id']]),
            _class='btn btn-primary btn-sm')
        if r['legacy']:
            legacy_models.add(r['model_name'])

    rows = []
    for tx_name, model_name, model_id in model_keys:
        key = (tx_name, model_name)
        row = [model_name, tx_name]
        for switch in switch_names:
            row.append(table_data.get((key, switch), ''))
        row.append(model_data.get((key, 'protocol'), 'No Protocol'))
        row.append(model_data.get((key, 'actions'),
                                  A('Go', _href=URL('model', 'index', args=[model_id]),
                                    _class='btn btn-primary btn-sm')))
        rows.append((row, model_name in legacy_models))

    headers = ['Model', 'Transmitter'] + switch_names + ['Protocol', 'Actions']

    return dict(headers=headers, rows=rows, all_transmitters=all_transmitters,
                selected_ids=selected_ids)