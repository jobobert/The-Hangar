import re
import json

def rendermodeldiagram():
    session.forget(response)

    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('model', 'listview'))

    if len(request.args) == 2:
        is_mobile = request.args[1]
    else:
        is_mobile = False

    model = db.model(model_id)

    return dict(mermaid=model.diagram_mermaid, model_id=model.id, options=request.args(1),
                is_mobile=is_mobile, edge_styles_json=json.dumps(mermaid_edge_styles))

def rendermodelexport():
    session.forget(response)

    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('model', 'listview'))

    model = db.model(model_id)

    return dict(mermaid=model.diagram_mermaid, edge_styles_json=json.dumps(mermaid_edge_styles))

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

###############################################
## MERMAID GENERATION
## Parallel to the Graphviz generation above — reads the same
## model_component/model_battery source of truth, but Mermaid flowcharts
## have no port-anchored edges like Graphviz record shapes, so receiver
## ports and connector terminals are represented as separate small nodes.

MERMAID_SHAPES = {
    'Engine':                 {'open': '[/', 'close': '\\]', 'class': 'ctEngine'},
    'Servo':                  {'open': '[\\', 'close': '/]', 'class': 'ctServo'},
    'Receiver':               {'open': '[',  'close': ']',   'class': 'ctReceiver'},
    'Motor':                  {'open': '[(', 'close': ')]',  'class': 'ctMotor'},
    'ESC':                    {'open': '{{', 'close': '}}',  'class': 'ctEsc'},
    'BEC':                    {'open': '[[', 'close': ']]',  'class': 'ctBec'},
    'Regulator':              {'open': '[[', 'close': ']]',  'class': 'ctRegulator'},
    'Flight Controller':      {'open': '[',  'close': ']',   'class': 'ctFc'},
    'Gyro':                   {'open': '((', 'close': '))',  'class': 'ctGyro'},
    'Flybarless Controller':  {'open': '{{', 'close': '}}',  'class': 'ctFbl'},
    'Electrical':             {'open': '[',  'close': ']',   'class': 'ctElec'},
    'Switch':                 {'open': '{',  'close': '}',   'class': 'ctSwitch'},
    'Winch':                  {'open': '[[', 'close': ']]',  'class': 'ctWinch'},
    'Other':                  {'open': '[',  'close': ']',   'class': 'ctOther'},
    'Retracts':               {'open': '[/', 'close': '/]',  'class': 'ctRetract'},
    'Battery':                {'open': '((', 'close': '))',  'class': 'ctBattery'},
    'Connector':               {'open': '[/', 'close': '\\]', 'class': 'ctConnector'},
    'Pump':                   {'open': '{{', 'close': '}}',  'class': 'ctPump'},
    'Sensor':                 {'open': '[',  'close': ']',   'class': 'ctSensor'},
}

# Fallback for shape names coming from componenttype_diagram (admin-defined
# custom component types) or diagram_component.shape — every Graphviz shape
# previously offered in the editor's shape picker maps to one of Mermaid's
# real tokens, with plain rect as the universal fallback.
GRAPHVIZ_SHAPE_TO_MERMAID = {
    'box': ('[', ']'), 'rect': ('[', ']'), 'square': ('[', ']'),
    'circle': ('((', '))'), 'doublecircle': ('((', '))'),
    'ellipse': ('(', ')'), 'oval': ('(', ')'), 'egg': ('(', ')'),
    'diamond': ('{', '}'), 'Mdiamond': ('{', '}'),
    'triangle': ('[/', '\\]'), 'invtriangle': ('[\\', '/]'),
    'trapezium': ('[\\', '/]'), 'invtrapezium': ('[/', '\\]'),
    'parallelogram': ('[/', '/]'),
    'house': ('[/', '\\]'), 'invhouse': ('[/', '\\]'),
    'pentagon': ('{{', '}}'), 'hexagon': ('{{', '}}'), 'septagon': ('{{', '}}'),
    'octagon': ('{{', '}}'), 'doubleoctagon': ('{{', '}}'), 'tripleoctagon': ('{{', '}}'),
    'star': ('{{', '}}'), 'polygon': ('{{', '}}'),
    'box3d': ('[(', ')]'), 'component': ('[(', ')]'), 'cylinder': ('[(', ')]'),
    'Msquare': ('[', ']'), 'Mcircle': ('((', '))'),
    'plaintext': ('[', ']'), 'none': ('[', ']'), 'note': ('[', ']'),
    'tab': ('[', ']'), 'folder': ('[', ']'),
    'cds': ('[', ']'), 'promoter': ('[', ']'), 'rpromoter': ('[', ']'),
    'terminator': ('[', ']'), 'utr': ('[', ']'),
    'larrow': ('[', ']'), 'rarrow': ('[', ']'),
    'point': ('((', '))'),
}

def _mermaid_escape_label(text):
    """Wrap in quotes and strip characters Mermaid labels can't contain
    unquoted. Real newlines are collapsed to spaces — customdot-driven
    multi-line labels are exactly the case that forces manual review (see
    mermaid_migration_status), so the generator never needs a literal
    newline. A visual second line (e.g. a component's diagram comment) is
    instead added as an explicit <br/> by the caller before this function
    ever sees the text — see _mermaid_label_with_comment()."""
    if text is None:
        text = ''
    text = str(text).replace('\n', ' ').replace('"', "'")
    return f'"{text}"'

def _mermaid_label_with_comment(main_text, comment):
    """Append a component's optional diagram comment as an italicized
    second line on its node label, using <br/> (a real Mermaid line-break
    the renderer supports) rather than a newline, which
    _mermaid_escape_label() would otherwise collapse to a space."""
    text = str(main_text)
    if comment:
        text += '<br/><i>' + str(comment).replace('\n', ' ') + '</i>'
    return text

def _mermaid_click_line(node_id, component_id):
    """Make a component's diagram node a clickable link to its own detail
    page, opening in a new tab so the diagram/editor isn't navigated away
    from."""
    return f'  click {node_id} href "{URL("component", "index.html", args=[component_id])}" _blank'

def _extract_fillcolor(attribs_str, default='#efefef'):
    m = re.search(r'fillcolor\s*=\s*"?(#[0-9a-fA-F]{3,8})"?', attribs_str or '')
    return m.group(1) if m else default

def _mermaid_node_line(node_id, label, comptype):
    shape = MERMAID_SHAPES.get(comptype)
    if shape:
        return f'    {node_id}{shape["open"]}{_mermaid_escape_label(label)}{shape["close"]}:::{shape["class"]}'
    _diag = componenttype_diagram.get(comptype, {})
    gv_shape = _diag.get('shape', 'box')
    open_, close_ = GRAPHVIZ_SHAPE_TO_MERMAID.get(gv_shape, ('[', ']'))
    cls = 'ct_' + re.sub(r'[^A-Za-z0-9]', '', comptype)
    return f'    {node_id}{open_}{_mermaid_escape_label(label)}{close_}:::{cls}'

def _mermaid_classdefs():
    lines = []
    for comptype, shape in MERMAID_SHAPES.items():
        color = _extract_fillcolor(components.get(comptype, {}).get('attribs', ''))
        lines.append(f'  classDef {shape["class"]} fill:{color},stroke:#333,stroke-width:1px')
    for name, info in componenttype_diagram.items():
        if name in MERMAID_SHAPES:
            continue  # _mermaid_node_line() checks MERMAID_SHAPES first, so these names never hit the componenttype_diagram fallback
        cls = 'ct_' + re.sub(r'[^A-Za-z0-9]', '', name)
        lines.append(f'  classDef {cls} fill:{info.get("color") or "#efefef"},stroke:#333,stroke-width:1px')
    lines.append('  classDef ctPort fill:#ffffff,stroke:#999,stroke-width:1px')
    lines.append('  classDef legendLabel fill:none,stroke:none')
    lines.append('  classDef legendSwatch fill:none,stroke:none')
    return '\n'.join(lines)

def _legend_row_selection():
    preferred = ['5v Servo', '5v Signal', '12v 12gauge', '12v 20gauge']
    rows = [n for n in preferred if n in mermaid_edge_styles]
    if len(rows) < 4:
        rows += [n for n in mermaid_edge_styles if n not in rows][: 4 - len(rows)]
    return rows[:4]

def mermaid_legend():
    """4-row wire-type legend as a Mermaid subgraph — no ports/anchors,
    each row is two invisible nodes joined by a real edge carrying the wire
    type's name as its label (id -- "Wire Type" --- id), same convention as
    creatediagramfrommermaid()'s body edges.

    Commented out (every line prefixed with %%): wires already carry their
    type as an inline edge label, so a separate legend is redundant screen
    space. The generation logic is kept intact rather than deleted so this
    is a one-line change to re-enable (drop the '%% ' prefix below) if
    inline labels are ever turned off for a decluttered view instead.
    Since commented lines aren't real Mermaid edges, they don't consume
    positional linkStyle/edge-index slots — mermaid-helpers.js's
    injectMermaidLinkStyles() skips them the same way Mermaid itself does,
    so the two stay in sync without any special-casing there."""
    legend_rows = _legend_row_selection()
    lines = ['  subgraph legend ["Legend"]', '    direction TB']
    for i, edge_name in enumerate(legend_rows, 1):
        lines.append(f'    lg{i}_a[" "]:::legendLabel')
        lines.append(f'    lg{i}_b[" "]:::legendSwatch')
        lines.append(f'    lg{i}_a -- "{edge_name}" --- lg{i}_b')
    lines.append('  end')
    return '\n'.join('%% ' + line for line in lines)

def _wrap_mermaid(body, model_name):
    """Assemble a complete Mermaid flowchart document: title comment,
    header, classDefs, legend, and component body. Edge styling is
    intentionally NOT baked in here — see mermaid_legend()'s docstring."""
    parts = [
        f'%% {model_name} Wiring Diagram',
        'flowchart LR',
        _mermaid_classdefs(),
        mermaid_legend(),
        body,
    ]
    return '\n\n'.join(p for p in parts if p and p.strip())

def default_mermaid_body():
    """Canned Receiver+Servo example body, mirroring default_components'
    role for the 'Use default diagram' button. Uses the same %% Nodes/%%
    Edges marker convention and labeled-edge format as
    creatediagramfrommermaid() so it round-trips through the same
    Connections-table parsing."""
    node_lines = [
        _mermaid_node_line('receiver', 'Receiver', 'Receiver'),
        '  receiver_p1(["Port 1"]):::ctPort',
        '  receiver --- receiver_p1',
        _mermaid_node_line('servo1', 'Servo', 'Servo'),
    ]
    edge_lines = ['  receiver_p1 -- "5v Servo" --- servo1']

    body = '%% Nodes\n'
    body += '\n'.join(node_lines)
    body += '\n%% End Nodes\n\n%% Edges\n'
    body += '\n'.join(edge_lines)
    body += '\n%% End Edges'

    return body

def diagram_connector_json():
    session.forget(response)
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
    session.forget(response)
    """JSON endpoint for wire type (diagramedge) CRUD used by the diagram editor."""
    import json
    response.headers['Content-Type'] = 'application/json'

    if request.env.request_method == 'POST':
        action = (request.post_vars.get('action') or '').strip()

        if action == 'save':
            de_id = VerifyTableID('diagramedge', request.post_vars.get('id')) if request.post_vars.get('id') else None
            name = (request.post_vars.get('name') or '').strip()
            stroke_color = (request.post_vars.get('stroke_color') or '#000000').strip()
            stroke_width = int(request.post_vars.get('stroke_width') or 1)
            stroke_style = (request.post_vars.get('stroke_style') or 'solid').strip()
            arrow_start = (request.post_vars.get('arrow_start') or 'none').strip()
            arrow_end = (request.post_vars.get('arrow_end') or 'none').strip()
            sort_order = int(request.post_vars.get('sort_order') or 0)
            if not name:
                return json.dumps({'error': 'Name is required'})
            if stroke_style not in ('solid', 'dashed', 'dotted'):
                return json.dumps({'error': 'Invalid style'})
            if arrow_start not in ('none', 'arrow', 'circle', 'cross') or arrow_end not in ('none', 'arrow', 'circle', 'cross'):
                return json.dumps({'error': 'Invalid arrowhead'})
            dup = db((db.diagramedge.name == name) & (db.diagramedge.id != de_id)).count()
            if dup:
                return json.dumps({'error': f'Wire type "{name}" already exists'})
            fields = dict(name=name, stroke_color=stroke_color, stroke_width=stroke_width,
                          stroke_style=stroke_style, arrow_start=arrow_start, arrow_end=arrow_end,
                          sort_order=sort_order)
            if de_id:
                db(db.diagramedge.id == de_id).update(**fields)
            else:
                de_id = db.diagramedge.insert(**fields)
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
    return json.dumps([{
        'id': r.id, 'name': r.name,
        'stroke_color': r.stroke_color, 'stroke_width': r.stroke_width, 'stroke_style': r.stroke_style,
        'arrow_start': r.arrow_start, 'arrow_end': r.arrow_end,
        'sort_order': r.sort_order,
    } for r in rows])


def diagram_component_json():
    session.forget(response)
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
            shape        = (request.post_vars.get('shape')        or 'box').strip()
            fillcolor    = (request.post_vars.get('fillcolor')    or '#efefef').strip()
            stroke_color = (request.post_vars.get('stroke_color') or '').strip()
            stroke_width = int(request.post_vars.get('stroke_width') or 1)
            stroke_style = (request.post_vars.get('stroke_style') or 'solid').strip()
            sort_order   = int(request.post_vars.get('sort_order') or 0)
            if stroke_style not in ('solid', 'dashed', 'dotted'):
                return json.dumps({'error': 'Invalid style'})
            fields = dict(name=name, shape=shape, fillcolor=fillcolor,
                          stroke_color=stroke_color, stroke_width=stroke_width, stroke_style=stroke_style,
                          sort_order=sort_order)
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
        'stroke_color': r.stroke_color or '', 'stroke_width': r.stroke_width or 1, 'stroke_style': r.stroke_style or 'solid',
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

def creatediagramfrommermaid(model_id):
    """Build a Mermaid flowchart body for the given model, from the same
    structured source of truth (model_component / model_battery rows) used
    by creatediagramfromcomponents() above — mirrors its exact branching
    order (ignore-list/Receiver -> componenttype_diagram fallback ->
    customdot -> hardcoded match/case) so the two generators stay in sync
    for the "safe to auto-migrate" comparison in mermaid_migration_status().

    Returns a partial Mermaid body with section markers (%% Nodes / %% End
    Nodes / %% Edges / %% End Edges), mirroring creatediagramfromcomponents()'s
    // Nodes / // Edges convention so the editor's Connections-table JS can
    scope its parsing to genuine cross-component connections only (a
    receiver's own port-wiring lives in the Nodes section as part of its
    subgraph, not the Edges section). Every edge line carries its wire-type
    name as an inline Mermaid edge label (id -- "Wire Type" --- id) rather
    than relying on positional linkStyle indices, since those don't survive
    live add/remove/reorder edits in the browser. Edge color/width/dash is
    never baked into the returned text — every render call site computes it
    live from these labels via mermaid-helpers.js's injectMermaidLinkStyles().

    Returns (body_text, warnings). warnings is a list of human-readable
    strings describing anything that couldn't be represented (non-empty
    means this model needs manual review — see mermaid_migration_status()).
    """
    model_components = db(db.model_component.model == model_id).select()
    model_battery = db(db.model_battery.model == model_id).select()

    node_lines = []
    edge_lines = []
    warnings = []
    esc_node_id = None

    receiver_row = next((r for r in model_components if r.component.componenttype == 'Receiver'), None)
    receiver_node_id = ('mc' + str(receiver_row.id)) if receiver_row else None
    receiver_port_nodes = {}
    # Channels actually assigned to some component — a receiver's unused
    # ports (e.g. channels 6-16 on a 16ch receiver when only 5 are wired)
    # would otherwise add a node+edge per port for nothing anyone connects
    # to, which is most of the size cost on a fully-populated receiver.
    used_channels = {r.channel for r in model_components if r.channel}

    def edge_line(from_id, to_id, edgeattrib_name):
        edge_lines.append(f'  {from_id} -- "{edgeattrib_name}" --- {to_id}')

    if receiver_row:
        comp = receiver_row.component
        compname = comp.diagramname if comp.diagramname else comp.name
        count = comp.attr_channel_count or 4
        # Deliberately NOT wrapped in a subgraph: Mermaid bundles edges that
        # cross a subgraph boundary at the boundary itself rather than at
        # the specific internal node, which defeats the whole point of
        # per-port nodes (a viewer couldn't tell which port a wire actually
        # went to). Plain sibling nodes + --- edges render each connection
        # precisely from the port it belongs to.
        node_lines.append(_mermaid_node_line(receiver_node_id, _mermaid_label_with_comment(compname, receiver_row.note), 'Receiver'))
        node_lines.append(_mermaid_click_line(receiver_node_id, comp.id))
        for x in range(1, count + 1):
            if x not in used_channels:
                continue
            port_id = f'{receiver_node_id}_p{x}'
            node_lines.append(f'  {port_id}(["Port {x}"]):::ctPort')
            node_lines.append(f'  {receiver_node_id} --- {port_id}')
            receiver_port_nodes[x] = port_id
        if comp.attr_telemetry_port:
            node_lines.append(f'  {receiver_node_id}_tlm(["Telemetry"]):::ctPort')
            node_lines.append(f'  {receiver_node_id} --- {receiver_node_id}_tlm')
        if comp.attr_sbus_port:
            node_lines.append(f'  {receiver_node_id}_sbus(["SBUS"]):::ctPort')
            node_lines.append(f'  {receiver_node_id} --- {receiver_node_id}_sbus')
        if comp.attr_pwr_port:
            node_lines.append(f'  {receiver_node_id}_pwr(["Power"]):::ctPort')
            node_lines.append(f'  {receiver_node_id} --- {receiver_node_id}_pwr')

    for row in sorted(model_components, key=lambda r: r.component.componenttype):
        comp = row.component
        comptype = comp.componenttype
        if comptype in components_to_ignore or comptype == 'Receiver':
            continue

        node_id = 'mc' + str(row.id)
        compname = comp.diagramname if comp.diagramname else comp.name
        from_port_id = receiver_port_nodes.get(row.channel) if row.channel else None

        if comptype not in components:
            _diag = componenttype_diagram.get(comptype)
            if not _diag or not _diag.get('shape'):
                continue
            label = f'{compname} {row.purpose}' if row.purpose else compname
            label = _mermaid_label_with_comment(label, row.note)
            node_lines.append(_mermaid_node_line(node_id, label, comptype))
            node_lines.append(_mermaid_click_line(node_id, comp.id))
            if from_port_id:
                edge_line(from_port_id, node_id, _diag['edge'])
            continue

        if comp.customdot:
            warnings.append(f'Component "{compname}" (mc{row.id}) uses Custom .dot Code — cannot auto-convert.')
            node_lines.append(_mermaid_node_line(node_id, _mermaid_label_with_comment(compname, row.note), comptype))
            node_lines.append(_mermaid_click_line(node_id, comp.id))
            if from_port_id:
                edge_line(from_port_id, node_id, components[comptype]['edgeattrib'])
            continue

        match comptype:
            case 'ESC':
                label = f'{compname} {row.purpose}' if row.purpose else compname
                label = _mermaid_label_with_comment(label, row.note)
                node_lines.append(_mermaid_node_line(node_id, label, comptype))
                node_lines.append(_mermaid_click_line(node_id, comp.id))
                if from_port_id:
                    edge_line(from_port_id, node_id, components[comptype]['edgeattrib'])
                esc_node_id = node_id
            case 'Motor':
                node_lines.append(_mermaid_node_line(node_id, _mermaid_label_with_comment(compname, row.note), comptype))
                node_lines.append(_mermaid_click_line(node_id, comp.id))
                if esc_node_id:
                    edge_line(esc_node_id, node_id, components[comptype]['edgeattrib'])
            case 'Battery':
                pass
            case _:
                label = f'{compname} {row.purpose}' if row.purpose else compname
                label = _mermaid_label_with_comment(label, row.note)
                node_lines.append(_mermaid_node_line(node_id, label, comptype))
                node_lines.append(_mermaid_click_line(node_id, comp.id))
                if from_port_id:
                    edge_line(from_port_id, node_id, components[comptype]['edgeattrib'])

    for batt_row in model_battery.render():
        batt_count = batt_row.quantity if batt_row.quantity else 1
        if batt_count == 0:
            continue
        for x in range(1, batt_count + 1):
            batt_id = f'batt{batt_row.id}_{x}' if batt_count > 1 else f'batt{batt_row.id}'
            node_lines.append(_mermaid_node_line(batt_id, str(batt_row.battery), 'Battery'))
            if esc_node_id:
                edge_line(esc_node_id, batt_id, components['Battery']['edgeattrib'])

    body = '%% Nodes\n'
    body += '\n'.join(node_lines)
    body += '\n%% End Nodes\n\n%% Edges\n'
    body += '\n'.join(edge_lines)
    body += '\n%% End Edges'

    return body, warnings

def createcomponentexamples():
    comps = []
    for name, details in components.items():
        comps.append((name, f'"{details["id"]}" [label="{name}"; shape="{details["shape"]}"; {details["attribs"]}];'))

    return comps

def createmermaidcomponentexamples():
    comps = []
    for name, shape in MERMAID_SHAPES.items():
        details = components.get(name)
        if not details:
            continue
        comps.append((name, f'{details["id"]}{shape["open"]}"{name}"{shape["close"]}:::{shape["class"]}'))
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
    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('model', 'listview'))

    model = db.model(model_id)

    details_form = SQLFORM(db.model, model.id, fields=[
                           'diagram_mermaid'], showid=False, formstyle='divs')

    default_mermaid = _wrap_mermaid(default_mermaid_body(), model.name)

    components_body, mermaid_warnings = creatediagramfrommermaid(model.id)
    model_mermaid = _wrap_mermaid(components_body, model.name)

    # Full node body for "Rebuild from Components" — a full-text replace of
    # the textarea (matches what the button's own confirm dialog already
    # promises: "replace all nodes and connections... custom wiring lost").
    model_nodes_mermaid = model_mermaid

    # Build node options for the connections manager dropdowns (mc{id}
    # scheme), including one option per receiver port sub-node — Mermaid
    # has no port-anchored edges, so a "connection to Receiver Port 2" is
    # just an edge to that port's own node id.
    model_comps = db(db.model_component.model == model_id).select()
    node_options = []
    for mc in model_comps:
        comp = mc.component
        if not comp or comp.componenttype in components_to_ignore:
            continue
        label = comp.diagramname if comp.diagramname else comp.name
        node_options.append({'id': 'mc' + str(mc.id), 'label': label})
        if comp.componenttype == 'Receiver':
            count = comp.attr_channel_count or 4
            for x in range(1, count + 1):
                node_options.append({'id': f'mc{mc.id}_p{x}', 'label': f'{label} — Port {x}'})
            if comp.attr_telemetry_port:
                node_options.append({'id': f'mc{mc.id}_tlm', 'label': f'{label} — Telemetry'})
            if comp.attr_sbus_port:
                node_options.append({'id': f'mc{mc.id}_sbus', 'label': f'{label} — SBUS'})
            if comp.attr_pwr_port:
                node_options.append({'id': f'mc{mc.id}_pwr', 'label': f'{label} — Power'})

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

    edge_styles_json = json.dumps(mermaid_edge_styles)
    node_options_json = json.dumps(node_options)
    model_nodes_mermaid_json = json.dumps(model_nodes_mermaid)
    componenttype_nodes_json = json.dumps(sorted(componenttype_nodes, key=lambda x: x['name']))

    # LEGACY GRAPHVIZ SCAFFOLDING — temporary, read-only reference so old
    # diagrams that never got auto-migrated to Mermaid aren't just lost from
    # view. Remove this along with model.diagram, diagram_comment_legacy
    # (models/db.py), and the matching accordion + viz-global.js include in
    # editmodeldiagram.html once every model is off the legacy field.
    legacy_dot = model.diagram or ''
    legacy_dot_json = json.dumps(legacy_dot)

    if details_form.process().accepted:
        session.flash = "Model Updated"
        redirect(URL('model', 'index', args=details_form.vars.id, extension="html"))
    elif details_form.errors:
        response.flash = "Error Adding New Model"

    return dict(
        mermaid=model.diagram_mermaid,
        model_name=model.name,
        form=details_form,
        default_mermaid=default_mermaid,
        edge_styles=mermaid_edge_styles,
        components=createmermaidcomponentexamples(),
        model_mermaid=model_mermaid,
        edge_styles_json=edge_styles_json,
        node_options_json=node_options_json,
        model_nodes_mermaid_json=model_nodes_mermaid_json,
        componenttype_nodes_json=componenttype_nodes_json,
        legacy_dot=legacy_dot,
        legacy_dot_json=legacy_dot_json,
    )