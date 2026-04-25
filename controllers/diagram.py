def rendermodeldiagram():

    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('model', 'listview'))

    if len(request.args) == 2:
        is_mobile = request.args[1]
    else:
        is_mobile = False 

    model = db.model(model_id) 

    return dict(dot=model.diagram, model_id=model.id,options=request.args(1),is_mobile=is_mobile)

def rendermodelexport():

    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('model', 'listview'))

    model = db.model(model_id) 

    return dict(dot=model.diagram)

# This list must be kept in sync with the component.componenttype(s) in the database,
# Plus battery and connector
# The "edgeattrib" has to be in the edge_attribs dict
components_to_ignore = [
    'Battery Charger'
    , 'Tire'
    , 'Shock'
]
components = {
    'Engine': 
        {'id': 'eng', 'shape': 'invhouse', 'attribs': 'style="filled"; fillcolor="#efefef"', 'edgeattrib': '5v Servo'}
    , 'Servo': 
        {'id': 'servo', 'shape': 'trapezium', 'attribs': 'style="filled"; fillcolor="#efefef"', 'edgeattrib': '5v Servo'}
    , 'Receiver': 
        {'id': 'receiver', 'shape': 'record', 'attribs': 'style="filled"; fillcolor="#ffffff"', 'edgeattrib': '5v Servo'}
    , 'Motor': 
        {'id': 'motor', 'shape': 'cylinder', 'attribs': 'style="filled"; fillcolor="#cc33ff"', 'edgeattrib': '12v 12gauge'}
    , 'ESC': 
        {'id': 'esc', 'shape': 'polygon', 'attribs': 'style="filled"; fillcolor="#336600"', 'edgeattrib': '5v Servo'}
    , 'BEC': 
        {'id': 'bec', 'shape': 'box3d', 'attribs': 'style="filled"; fillcolor="#668cff"', 'edgeattrib': '5v Servo'}
    , 'Regulator': 
        {'id': 'reg', 'shape': 'box3d', 'attribs': 'style="filled"; fillcolor="#efefef"', 'edgeattrib': '5v Servo'}
    , 'Flight Controller':     
        {'id': 'fc', 'shape': 'Msquare', 'attribs': 'style="filled"; fillcolor="#df80ff"', 'edgeattrib': '5v Servo'}
    , 'Gyro':                  
        {'id': 'gyro', 'shape': 'Mcircle', 'attribs': 'style="filled"; fillcolor="#ff0066"', 'edgeattrib': '5v Servo'}
    #, 'Battery Charger':       
    #    {'id': 'battchar', 'shape': 'rect', 'attribs': 'style="filled"; fillcolor="#efefef"', 'edgeattrib': '12v 12gauge'}
    , 'Flybarless Controller': 
        {'id': 'fblcont', 'shape': 'tripleoctagon', 'attribs': 'style="filled"; fillcolor="#9900cc"', 'edgeattrib': '5v Servo'}
    , 'Electrical':            
        {'id': 'elec', 'shape': 'cds', 'attribs': 'style="filled"; fillcolor="#efefef"', 'edgeattrib': 'default'}
    , 'Switch':                
        {'id': 'sw', 'shape': 'septagon', 'attribs': 'style="filled"; fillcolor="#efefef"', 'edgeattrib': '5v Servo'}
    , 'Winch':                 
        {'id': 'winch', 'shape': 'component', 'attribs': 'style="filled"; fillcolor="#efefef"', 'edgeattrib': '5v Servo'}
    , 'Other':                 
        {'id': 'other', 'shape': 'component', 'attribs': 'style="filled"; fillcolor="#efefef"', 'edgeattrib': 'default'}
    , 'Retracts':              
        {'id': 'retract', 'shape': 'parallelogram', 'attribs': 'style="filled"; fillcolor="#666699"', 'edgeattrib': '5v Servo'}
    
    , 'Battery': 
        {'id': 'batt', 'shape': 'circle', 'attribs': 'style="filled"; fillcolor="#ffcc00"', 'edgeattrib': '12v 12gauge'}
    , 'Connector': 
        {'id': 'conn', 'shape': 'house', 'attribs': 'style="filled"; fillcolor="#806600"', 'edgeattrib': '12v 12gauge'}

    , 'Pump':
        {'id': 'pump', 'shape': 'hexagon', 'attribs': 'style="filled"; fillcolor="#efefef"', 'edgeattrib': '12v 12gauge'}

    , 'Sensor':
        {'id': 'sensor', 'shape': 'cds', 'attribs': 'style="filled"; fillcolor="#797979"', 'edgeattrib': '5v Servo'}
}


default_components = {
    'Servo': f'"servo" [label="Servo"; shape="{components["Servo"]["shape"]}"; {components["Servo"]["attribs"]};];',
    'Receiver': f'"receiver" [label = "<f0>Receiver | <f1>Port 1 | <f2>Port 2 | <f3>Port 3 | <f4>Port 4";shape = "{components["Receiver"]["shape"]}"; {components["Receiver"]["attribs"]};];',
    'Connector': f'"connector" [label="Connector"; shape="{components["Connector"]["shape"]}"; {components["Connector"]["attribs"]};]',
    'Battery': f'"batt" [label = "3s2200"; shape="{components["Battery"]["shape"]}" {components["Battery"]["attribs"]};];',
    'Motor': f'"motor" [label="Motor"; shape="{components["Motor"]["shape"]}" {components["Motor"]["attribs"]};];',
    'ESC': f'"esc" [label="ESC"; shape="{components["ESC"]["shape"]}" {components["ESC"]["attribs"]};];',   
    'Switch': f'"switch" [label="Switch"; shape="{components["Switch"]["shape"]}" {components["Switch"]["attribs"]};];',
}

edge_attribs = diagram_edge_attribs

legend = f"""
// Legend
subgraph cluster_legend {{
    label = "Legend";
    fontsize = "14"
    node [shape = plaintext; fontsize="10"];
    key [label = <<table border="0" cellpadding="2" cellspacing="0" cellborder="0">
        <tr><td align="right" port="i1">5v Servo</td></tr>
        <tr><td align="right" port="i2">5v Signal</td></tr>
        <tr><td align="right" port="i3">12v 12 Gauge</td></tr>
        <tr><td align="right" port="i4">12v 20 Gauge</td></tr>
        </table>>;];
    key2 [label = <<table border="0" cellpadding="2" cellspacing="0" cellborder="0">
        <tr><td port="i1">&nbsp;</td></tr>
        <tr><td port="i2">&nbsp;</td></tr>
        <tr><td port="i3">&nbsp;</td></tr>
        <tr><td port="i4">&nbsp;</td></tr>
        </table>>;];
    key:i1:e -- key2:i1:w [{edge_attribs['5v Servo']}];
    key:i2:e -- key2:i2:w [{edge_attribs['5v Signal']}];
    key:i3:e -- key2:i3:w [{edge_attribs['12v 12gauge']}];
    key:i4:e -- key2:i4:w [{edge_attribs['12v 20gauge']}];
}}
    """

def diagram_connector_json():
    """JSON endpoint for wire connector type CRUD used by the diagram editor."""
    import json
    response.headers['Content-Type'] = 'application/json'

    if request.env.request_method == 'POST':
        action = (request.post_vars.get('action') or '').strip()

        if action == 'save':
            dc_id = VerifyTableID('diagram_connector', request.post_vars.get('id')) if request.post_vars.get('id') else None
            name = (request.post_vars.get('name') or '').strip()
            if not name:
                return json.dumps({'error': 'Name is required'})
            left_count  = int(request.post_vars.get('left_count')  or 1)
            right_count = int(request.post_vars.get('right_count') or 1)
            left_label  = (request.post_vars.get('left_label')  or '').strip()
            right_label = (request.post_vars.get('right_label') or '').strip()
            fillcolor   = (request.post_vars.get('fillcolor')   or '#d4c07a').strip()
            custom_dot  = (request.post_vars.get('custom_dot')  or '').strip()
            sort_order  = int(request.post_vars.get('sort_order') or 0)
            fields = dict(name=name, left_count=left_count, right_count=right_count,
                          left_label=left_label, right_label=right_label,
                          fillcolor=fillcolor, custom_dot=custom_dot, sort_order=sort_order)
            if dc_id:
                db(db.diagram_connector.id == dc_id).update(**fields)
            else:
                dc_id = db.diagram_connector.insert(**fields)
            return json.dumps({'ok': True, 'id': int(dc_id)})

        if action == 'delete':
            dc_id = VerifyTableID('diagram_connector', request.post_vars.get('id'))
            if not dc_id:
                return json.dumps({'error': 'Invalid ID'})
            db(db.diagram_connector.id == dc_id).delete()
            return json.dumps({'ok': True})

        return json.dumps({'error': 'Unknown action'})

    rows = db(db.diagram_connector.id > 0).select(orderby=db.diagram_connector.sort_order | db.diagram_connector.name)
    return json.dumps([{
        'id': r.id, 'name': r.name,
        'left_count': r.left_count, 'right_count': r.right_count,
        'left_label': r.left_label or '', 'right_label': r.right_label or '',
        'fillcolor': r.fillcolor or '#d4c07a',
        'custom_dot': r.custom_dot or '',
        'sort_order': r.sort_order,
    } for r in rows])


def diagramedge_json():
    """JSON endpoint for wire type (diagramedge) CRUD used by the diagram editor."""
    import json
    response.headers['Content-Type'] = 'application/json'

    if request.env.request_method == 'POST':
        action = (request.post_vars.get('action') or '').strip()

        if action == 'save':
            de_id = VerifyTableID('diagramedge', request.post_vars.get('id')) if request.post_vars.get('id') else None
            name = (request.post_vars.get('name') or '').strip()
            dot_attribs = (request.post_vars.get('dot_attribs') or '').strip()
            sort_order = int(request.post_vars.get('sort_order') or 0)
            if not name:
                return json.dumps({'error': 'Name is required'})
            dup = db((db.diagramedge.name == name) & (db.diagramedge.id != de_id)).count()
            if dup:
                return json.dumps({'error': f'Wire type "{name}" already exists'})
            if de_id:
                db(db.diagramedge.id == de_id).update(name=name, dot_attribs=dot_attribs, sort_order=sort_order)
            else:
                de_id = db.diagramedge.insert(name=name, dot_attribs=dot_attribs, sort_order=sort_order)
            return json.dumps({'ok': True, 'id': int(de_id)})

        if action == 'delete':
            de_id = VerifyTableID('diagramedge', request.post_vars.get('id'))
            if not de_id:
                return json.dumps({'error': 'Invalid ID'})
            row = db.diagramedge(de_id)
            if not row:
                return json.dumps({'error': 'Not found'})
            in_use = db(db.componenttype.diagram_edgeattrib == row.name).count()
            if in_use:
                return json.dumps({'error': f'"{row.name}" is used by {in_use} component type(s) — reassign first'})
            db(db.diagramedge.id == de_id).delete()
            return json.dumps({'ok': True})

        return json.dumps({'error': 'Unknown action'})

    rows = db(db.diagramedge.id > 0).select(orderby=db.diagramedge.sort_order | db.diagramedge.name)
    return json.dumps([{'id': r.id, 'name': r.name, 'dot_attribs': r.dot_attribs, 'sort_order': r.sort_order} for r in rows])


def diagram_component_json():
    """JSON endpoint for custom diagram component CRUD used by the diagram editor."""
    import json
    response.headers['Content-Type'] = 'application/json'

    if request.env.request_method == 'POST':
        action = (request.post_vars.get('action') or '').strip()

        if action == 'save':
            dc_id = VerifyTableID('diagram_component', request.post_vars.get('id')) if request.post_vars.get('id') else None
            name = (request.post_vars.get('name') or '').strip()
            if not name:
                return json.dumps({'error': 'Name is required'})
            shape      = (request.post_vars.get('shape')       or 'box').strip()
            fillcolor  = (request.post_vars.get('fillcolor')   or '#efefef').strip()
            dot_attribs = (request.post_vars.get('dot_attribs') or '').strip()
            sort_order = int(request.post_vars.get('sort_order') or 0)
            fields = dict(name=name, shape=shape, fillcolor=fillcolor, dot_attribs=dot_attribs, sort_order=sort_order)
            if dc_id:
                db(db.diagram_component.id == dc_id).update(**fields)
            else:
                dc_id = db.diagram_component.insert(**fields)
            return json.dumps({'ok': True, 'id': int(dc_id)})

        if action == 'delete':
            dc_id = VerifyTableID('diagram_component', request.post_vars.get('id'))
            if not dc_id:
                return json.dumps({'error': 'Invalid ID'})
            db(db.diagram_component.id == dc_id).delete()
            return json.dumps({'ok': True})

        return json.dumps({'error': 'Unknown action'})

    rows = db(db.diagram_component.id > 0).select(orderby=db.diagram_component.sort_order | db.diagram_component.name)
    return json.dumps([{
        'id': r.id, 'name': r.name, 'shape': r.shape or 'box',
        'fillcolor': r.fillcolor or '#efefef',
        'dot_attribs': r.dot_attribs or '',
        'sort_order': r.sort_order,
    } for r in rows])


def creatediagramfromcomponents(model_id):
    """Build a Graphviz DOT graph body string for the given model.

    Returns a partial DOT body with section markers (// Nodes / // End Nodes /
    // Edges / // End Edges) for use in the diagram editor. Node IDs use the
    stable scheme mc{model_component.id} so connections survive component
    additions and removals.
    """
    model_components = db(db.model_component.model == model_id).select()
    model_battery = db(db.model_battery.model == model_id).select()

    nodes = []
    edges = []
    esc_node_id = None

    # Pre-scan for receiver so its node ID is available when generating edges
    # for other components (sorted order puts Receiver after ESC and Motor).
    receiver_row = next((r for r in model_components if r.component.componenttype == 'Receiver'), None)
    receiver_node_id = ('mc' + str(receiver_row.id)) if receiver_row else None

    for row in sorted(model_components, key=lambda r: r.component.componenttype):
        if row.component.componenttype in components_to_ignore:
            continue

        node_id = 'mc' + str(row.id)
        comptype = row.component.componenttype
        compname = row.component.diagramname if row.component.diagramname else row.component.name
        # None means no receiver channel — component floats as unconnected node
        from_ref = f'"{receiver_node_id}":f{row.channel}' if (receiver_node_id and row.channel) else None

        if comptype not in components:
            _diag = componenttype_diagram.get(comptype)
            if not _diag or not _diag.get('shape'):
                continue
            nodes.append(
                f'"{node_id}" [label="{compname}\\n{row.purpose or ""}"; '
                f'shape="{_diag["shape"]}"; style="filled"; fillcolor="{_diag["color"]}";];'
            )
            if from_ref:
                edges.append(f'{from_ref} -- "{node_id}" [{edge_attribs[_diag["edge"]]}];')
            continue

        if row.component.customdot:
            customReplacement = row.component.customdot.replace('{id}', node_id).replace('{name}', compname).replace('{purpose}', row.purpose if row.purpose else '')
            nodes.append(f'"{node_id}" {customReplacement}')
            if from_ref:
                edges.append(f'{from_ref} -- "{node_id}" [{edge_attribs[components[comptype]["edgeattrib"]]}];')
        else:
            match comptype:
                case 'ESC':
                    nodes.append(f'"{node_id}" [label="{compname}\n{row.purpose}"; {components[comptype]["attribs"]}; shape="{components[comptype]["shape"]}"];')
                    if from_ref:
                        edges.append(f'{from_ref} -- "{node_id}" [{edge_attribs[components[comptype]["edgeattrib"]]}];')
                    esc_node_id = node_id
                case 'Motor':
                    nodes.append(f'"{node_id}" [label="{compname}"; {components[comptype]["attribs"]}; shape="{components[comptype]["shape"]}"];')
                    if esc_node_id:
                        edges.append(f'"{esc_node_id}" -- "{node_id}" [{edge_attribs[components[comptype]["edgeattrib"]]}];')
                case 'Receiver':
                    count = 4
                    ports = []
                    if row.component.attr_channel_count:
                        count = row.component.attr_channel_count
                    ports.append(f'"{node_id}" [label = "<f0>{compname}')
                    for x in range(1, count + 1):
                        ports.append(f'| <f{x}>Port {x} ')
                    if row.component.attr_telemetry_port:
                        ports.append(' | <t1>Telemetry ')
                    if row.component.attr_sbus_port:
                        ports.append(' | <t2>SBUS ')
                    if row.component.attr_pwr_port:
                        ports.append(' | <t3>Power ')
                    ports.append('";shape = "record";];')
                    nodes.append(''.join(ports))
                case 'Battery':
                    pass
                case _:
                    nodes.append(f'"{node_id}" [label="{compname}\n{row.purpose if row.purpose else ""}"; {components[comptype]["attribs"]}; shape="{components[comptype]["shape"]}"];')
                    if from_ref:
                        edges.append(f'{from_ref} -- "{node_id}" [{edge_attribs[components[comptype]["edgeattrib"]]}];')

    for batt_row in model_battery.render():
        batt_count = batt_row.quantity if batt_row.quantity else 1
        if batt_count == 0:
            continue
        for x in range(1, batt_count + 1):
            batt_id = f'batt{batt_row.id}_{x}' if batt_count > 1 else f'batt{batt_row.id}'
            nodes.append(f'"{batt_id}" [label = "{batt_row.battery}"; {components["Battery"]["attribs"]}];')
            if esc_node_id:
                edges.append(f'"{esc_node_id}" -- "{batt_id}" [{edge_attribs[components["Battery"]["edgeattrib"]]}];')

    ret = '// Nodes\n'
    ret += "\n".join(nodes)
    ret += '\n// End Nodes\n\n// Edges\n'
    ret += "\n".join(edges)
    ret += '\n// End Edges'

    return ret

def createcomponentexamples():
    comps = []
    for name, details in components.items():
        comps.append((name, f'"{details["id"]}" [label="{name}"; shape="{details["shape"]}"; {details["attribs"]}];'))

    return comps

def migrate_model_diagram():
    """Remap legacy node IDs in an existing DOT diagram to the mc{id} scheme."""
    import re, json as _json
    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('model', 'listview'))
    model = db.model(model_id)

    already_migrated = _migration_applied(f'model_diagram_migrated_{model_id}')

    if request.post_vars.get('action') == 'save':
        dot_to_save = request.post_vars.get('dot', '').strip()
        if dot_to_save:
            db(db.model.id == model_id).update(diagram=dot_to_save)
        _mark_migration(f'model_diagram_migrated_{model_id}')
        session.flash = 'Diagram migrated'
        redirect(URL('model', 'index', args=[model_id], extension='html'))

    if request.post_vars.get('action') == 'skip':
        _mark_migration(f'model_diagram_migrated_{model_id}')
        session.flash = 'Skipped'
        redirect(URL('admin', 'integrity_report'))

    # Parse node definition IDs from the existing DOT, preserving order
    node_ids = []
    if model.diagram:
        seen = set()
        for nid in re.findall(r'"([^"]+)"\s*\[', model.diagram):
            if nid not in seen:
                seen.add(nid)
                node_ids.append(nid)

    # Build new-ID options from model_component records (mc{id} scheme)
    comp_options = []
    for mc in db(db.model_component.model == model_id).select():
        comp = mc.component
        if not comp:
            continue
        label = comp.diagramname if comp.diagramname else comp.name
        if mc.purpose:
            label += f' — {mc.purpose}'
        comp_options.append({
            'new_id': f'mc{mc.id}',
            'label': f'[{comp.componenttype}] {label}',
        })

    existing_dot = model.diagram or ''
    return dict(
        model=model,
        model_id=model_id,
        existing_dot=existing_dot,
        existing_dot_json=_json.dumps(existing_dot),
        already_migrated=already_migrated,
        node_ids=node_ids,
        comp_options_json=_json.dumps(comp_options),
    )


def editmodeldiagram():
    import json
    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('model', 'listview'))

    model = db.model(model_id)

    details_form = SQLFORM(db.model, model.id, fields=[
                           'diagram'], showid=False, formstyle='divs')
    title = f"""
// Title
fontsize = 30;
label = "{model.name} Wiring Diagram";
labelloc = "t";
    """

    default_dot = f"""
graph model {{
rankdir = LR;
fontsize="10"
{legend}

// Nodes
{default_components['Receiver']}
{default_components['Servo']}
// End Nodes

// Edges
"receiver":f1 -- "servo" [{edge_attribs['5v Servo']}];
// End Edges

{title}
}}
    """

    components_body = creatediagramfromcomponents(model.id)

    model_components_dot = f"""
graph model {{
rankdir = LR;
fontsize="10"
{legend}

{components_body}

{title}
}}
    """

    # Full nodes+edges block for "Refresh from Components" — replaces both sections
    model_nodes_dot = components_body

    # Build node options for the connections manager dropdowns (mc{id} scheme)
    model_comps = db(db.model_component.model == model_id).select()
    node_options = []
    for mc in model_comps:
        comp = mc.component
        if not comp or comp.componenttype in components_to_ignore:
            continue
        label = comp.diagramname if comp.diagramname else comp.name
        node_options.append({'id': 'mc' + str(mc.id), 'label': label})

    for batt_row in db(db.model_battery.model == model_id).select().render():
        batt_count = batt_row.quantity if batt_row.quantity else 1
        if batt_count == 0:
            continue
        for x in range(1, batt_count + 1):
            batt_id = f'batt{batt_row.id}_{x}' if batt_count > 1 else f'batt{batt_row.id}'
            batt_label = str(batt_row.battery) + (f' ({x})' if batt_count > 1 else '')
            node_options.append({'id': batt_id, 'label': batt_label})

    componenttype_nodes = [
        {'name': name, 'shape': info['shape'], 'color': info['color'], 'edge': info['edge']}
        for name, info in componenttype_diagram.items()
        if info.get('shape')
    ]

    edge_attribs_json = json.dumps(edge_attribs)
    node_options_json = json.dumps(node_options)
    model_nodes_dot_json = json.dumps(model_nodes_dot)
    componenttype_nodes_json = json.dumps(sorted(componenttype_nodes, key=lambda x: x['name']))

    if details_form.process().accepted:
        session.flash = "Model Updated"
        redirect(URL('model', 'index', args=details_form.vars.id, extension="html"))
    elif details_form.errors:
        response.flash = "Error Adding New Model"

    return dict(
        dot=model.diagram,
        model_name=model.name,
        form=details_form,
        default_dot=default_dot,
        edge_attribs=edge_attribs,
        components=createcomponentexamples(),
        model_components_dot=model_components_dot,
        edge_attribs_json=edge_attribs_json,
        node_options_json=node_options_json,
        model_nodes_dot_json=model_nodes_dot_json,
        componenttype_nodes_json=componenttype_nodes_json,
    )