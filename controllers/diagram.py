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

    return dict(dot=model.diagram, model_id=model.id, options=request.args(1),
                is_mobile=is_mobile)

def rendermodelexport():
    session.forget(response)

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
    key:i1:e -> key2:i1:w [{edge_attribs['5v Servo']}];
    key:i2:e -> key2:i2:w [{edge_attribs['5v Signal']}];
    key:i3:e -> key2:i3:w [{edge_attribs['12v 12gauge']}];
    key:i4:e -> key2:i4:w [{edge_attribs['12v 20gauge']}];
}}
    """

###############################################
## DOT DOCUMENT ASSEMBLY
## Generated diagrams are `digraph`s using `->` edges, not the undirected
## `graph`/`--` form used before wire types gained arrowheads: Graphviz
## silently ignores dir/arrowhead/arrowtail inside an undirected graph, so
## arrowheads are only expressible on a directed one. Hand-written legacy
## documents still using `graph`/`--` keep rendering untouched — the read-only
## views pass saved text straight to Viz.js — and the editor's Connections
## table sniffs the current document's directedness before emitting an edge,
## since mixing `->` and `--` in one document is a hard Graphviz parse error.

def _dot_escape_label(text):
    """Escape a label for a plain (non-HTML, non-record) Graphviz label."""
    if text is None:
        text = ''
    return str(text).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def _dot_record_escape(text):
    """Escape a label fragment destined for a record-shaped node, where
    Graphviz additionally treats | < > { } as structural characters."""
    out = _dot_escape_label(text)
    for ch in '|<>{}':
        out = out.replace(ch, '\\' + ch)
    return out

def _dot_label(compname, purpose=None, note=None):
    """Node label with each populated extra on its own line. `purpose` is the
    model_component's role; `note` is its optional diagram comment."""
    parts = [str(compname)]
    if purpose:
        parts.append(str(purpose))
    if note:
        parts.append(str(note))
    return _dot_escape_label('\n'.join(parts))

def _dot_click_attribs(component_id):
    """Make a component's node a link to its own detail page, opening in a new
    tab so the diagram/editor isn't navigated away from. Viz.js renders these
    as real <a xlink:href> elements in the output SVG."""
    return f' URL="{URL("component", "index.html", args=[component_id])}"; target="_blank";'

###############################################
## PORT RECORDS
## A Graphviz `record` node carries named sub-fields (ports) that edges anchor
## to individually — "mc12":f3. Whether a component is one resolves through a
## hierarchy, highest priority first:
##
##   1. the node already written in model.diagram   -> defines the record
##   2. component.customdot                         -> defines the record
##   3. component.diagram_is_record ('yes'/'no')    -> decides only
##   4. componenttype.diagram_is_record             -> decides only
##   5. neither set                                 -> plain node
##
## Levels 1-2 supply a complete record label, so their ports and labels are read
## back out of the text — that extraction lives in the editor's getAllNodeIds()
## (views/diagram/editmodeldiagram.html), the only place that sees the live
## document. Levels 3-4 only decide, so the ports are generated here from
## attr_channel_count plus the telemetry/SBUS/power flags.
##
## _resolves_to_record() covers levels 3-4 only; levels 1-2 short-circuit before
## it is ever consulted, because the generator emits customdot verbatim and the
## saved text is whatever the user last wrote.

def _resolves_to_record(comp):
    """Levels 3-4 of the hierarchy: does this component render as a port record?

    The component's own tri-state setting wins when set ('yes'/'no'); '' means
    inherit from its componenttype. Deliberately independent of diagram_shape —
    see the note on componenttype.diagram_is_record in models/db.py."""
    if not comp:
        return False
    own = (comp.diagram_is_record or '').strip().lower()
    if own == 'yes':
        return True
    if own == 'no':
        return False
    return bool(componenttype_is_record.get(comp.componenttype))

def _record_shape(resolved_shape):
    """A record label only renders inside a record shape, so the flag overrides
    whatever shape was resolved — preserving Mrecord (the rounded variant) if
    that is what was asked for."""
    return 'Mrecord' if resolved_shape == 'Mrecord' else 'record'

def _record_node(node_id, title, comp, attribs, click, shape=None):
    """Build a record node whose ports come from the component's port
    attributes. `title` becomes the <f0> field (this app's convention — see
    default_components['Receiver'] and the f0 skip in the editor's port
    extraction); numbered channels become <f1>..<fN>, and the three optional
    ports become <t1>/<t2>/<t3>.

    Every channel is emitted, used or not: record fields are sub-fields of one
    node, so unlike separate per-port nodes they cost almost nothing."""
    count = comp.attr_channel_count or 4
    parts = [f'"{node_id}" [label = "<f0>{_dot_record_escape(title)}']
    for x in range(1, count + 1):
        parts.append(f'| <f{x}>Port {x} ')
    if comp.attr_telemetry_port:
        parts.append(' | <t1>Telemetry ')
    if comp.attr_sbus_port:
        parts.append(' | <t2>SBUS ')
    if comp.attr_pwr_port:
        parts.append(' | <t3>Power ')
    parts.append(f'"; shape = "{_record_shape(shape)}"; {attribs};{click}];')
    return ''.join(parts)

def record_port_options(comp, label):
    """The ports _record_node() will emit, as (port, label) pairs, for the
    editor's connection dropdowns. Shares its channel/flag reading with the
    generator so the two cannot drift."""
    ports = []
    count = comp.attr_channel_count or 4
    for x in range(1, count + 1):
        ports.append((f'f{x}', f'{label} — Port {x}'))
    if comp.attr_telemetry_port:
        ports.append(('t1', f'{label} — Telemetry'))
    if comp.attr_sbus_port:
        ports.append(('t2', f'{label} — SBUS'))
    if comp.attr_pwr_port:
        ports.append(('t3', f'{label} — Power'))
    return ports

def dot_title(model_name):
    return f"""
// Title
fontsize = 30;
label = "{_dot_escape_label(model_name)} Wiring Diagram";
labelloc = "t";
    """

def _wrap_dot(body, model_name):
    """Assemble a complete Graphviz document: header, legend, component body,
    and title."""
    return f"""digraph model {{
rankdir = LR;
fontsize="10"
{legend}
{body}
{dot_title(model_name)}
}}
"""

def default_dot_body():
    """Canned Receiver+Servo example body for the 'Use default diagram'
    button, using the same // Nodes / // Edges markers as
    creatediagramfromcomponents() so it round-trips through the same
    Connections-table parsing."""
    body = '// Nodes\n'
    body += default_components['Receiver'] + '\n'
    body += default_components['Servo']
    body += '\n// End Nodes\n\n// Edges\n'
    body += f'"receiver":f1 -> "servo" [{edge_attribs["5v Servo"]}];'
    body += '\n// End Edges'
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
        # Generated server-side from the structured columns above so the
        # editor's findEdgeTypeName() reverse match is exact by construction —
        # it compares against the same string creatediagramfromcomponents()
        # emits, rather than re-deriving DOT in JS.
        'dot_attribs': _style_to_dot_attribs(r),
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
        # Full node-attribute fragment generated from the structured columns —
        # the editor inserts this verbatim rather than rebuilding it in JS.
        'dot_attribs': _component_style_to_dot_attribs(r),
        'sort_order': r.sort_order,
    } for r in rows])


def creatediagramfromcomponents(model_id):
    """Build a Graphviz DOT graph body string for the given model.

    Returns a partial DOT body with section markers (// Nodes / // End Nodes /
    // Edges / // End Edges) for use in the diagram editor. Node IDs use the
    stable scheme mc{model_component.id} so connections survive component
    additions and removals.

    A receiver is one `record`-shaped node whose channels are addressable
    sub-fields (<f1>..<fN>, plus <t1>/<t2>/<t3> for telemetry/SBUS/power), so a
    channel wire anchors to the exact port it belongs to via "mc12":f3. Every
    port is emitted, used or not — unlike separate per-port nodes, record
    fields cost almost nothing.

    Edges use `->` because wire types can carry arrowheads; see the DOT
    DOCUMENT ASSEMBLY note above.
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
        label = _dot_label(compname, row.purpose, row.note)
        click = _dot_click_attribs(row.component.id)
        # None means no receiver channel — component floats as unconnected node.
        # The node_id guard matters now that a record component reaches an
        # edge-emitting branch: the receiver used to be handled by a case that
        # emitted no edge at all, so a channel set on the receiver itself would
        # now produce a self-loop.
        from_ref = (f'"{receiver_node_id}":f{row.channel}'
                    if (receiver_node_id and row.channel and node_id != receiver_node_id)
                    else None)

        is_record = _resolves_to_record(row.component)

        if comptype not in components:
            _diag = componenttype_diagram.get(comptype)
            # A record-flagged type needs no explicit shape — the flag implies
            # one — but a non-record type with no shape has nothing to draw.
            if not _diag or not (_diag.get('shape') or is_record):
                continue
            _attribs = f'style="filled"; fillcolor="{_diag["color"] if _diag else "#efefef"}"'
            if is_record:
                nodes.append(_record_node(
                    node_id, _dot_label(compname, None, row.note), row.component,
                    _attribs, click, _diag.get('shape') if _diag else None))
            else:
                nodes.append(
                    f'"{node_id}" [label="{label}"; '
                    f'shape="{_diag["shape"]}"; {_attribs};{click}];'
                )
            if from_ref:
                edges.append(f'{from_ref} -> "{node_id}" [{edge_attribs[_diag["edge"]]}];')
            continue

        if row.component.customdot:
            customReplacement = row.component.customdot.replace('{id}', node_id).replace('{name}', compname).replace('{purpose}', row.purpose if row.purpose else '')
            nodes.append(f'"{node_id}" {customReplacement}')
            if from_ref:
                edges.append(f'{from_ref} -> "{node_id}" [{edge_attribs[components[comptype]["edgeattrib"]]}];')
        else:
            match comptype:
                case 'ESC':
                    nodes.append(f'"{node_id}" [label="{label}"; {components[comptype]["attribs"]}; shape="{components[comptype]["shape"]}";{click}];')
                    if from_ref:
                        edges.append(f'{from_ref} -> "{node_id}" [{edge_attribs[components[comptype]["edgeattrib"]]}];')
                    esc_node_id = node_id
                case 'Motor':
                    nodes.append(f'"{node_id}" [label="{_dot_label(compname, None, row.note)}"; {components[comptype]["attribs"]}; shape="{components[comptype]["shape"]}";{click}];')
                    if esc_node_id:
                        edges.append(f'"{esc_node_id}" -> "{node_id}" [{edge_attribs[components[comptype]["edgeattrib"]]}];')
                case 'Battery':
                    pass
                case _ if is_record:
                    # Replaces what used to be a hardcoded `case 'Receiver':`.
                    # Receiver is now simply the one built-in type seeded with
                    # the record flag; Flight Controller, Flybarless Controller
                    # or an admin-added type behave identically once flagged.
                    #
                    # Placed after ESC/Motor/Battery deliberately: those three
                    # carry bespoke wiring (esc_node_id tracking, and batteries
                    # being emitted by the battery loop below instead), which a
                    # record node would break. Flagging one of them is a no-op.
                    nodes.append(_record_node(
                        node_id, _dot_label(compname, None, row.note), row.component,
                        components[comptype]["attribs"], click,
                        components[comptype]["shape"]))
                    if from_ref:
                        edges.append(f'{from_ref} -> "{node_id}" [{edge_attribs[components[comptype]["edgeattrib"]]}];')
                case _:
                    nodes.append(f'"{node_id}" [label="{label}"; {components[comptype]["attribs"]}; shape="{components[comptype]["shape"]}";{click}];')
                    if from_ref:
                        edges.append(f'{from_ref} -> "{node_id}" [{edge_attribs[components[comptype]["edgeattrib"]]}];')

    for batt_row in model_battery.render():
        batt_count = batt_row.quantity if batt_row.quantity else 1
        if batt_count == 0:
            continue
        for x in range(1, batt_count + 1):
            batt_id = f'batt{batt_row.id}_{x}' if batt_count > 1 else f'batt{batt_row.id}'
            nodes.append(f'"{batt_id}" [label = "{_dot_escape_label(batt_row.battery)}"; {components["Battery"]["attribs"]}; shape="{components["Battery"]["shape"]}";];')
            if esc_node_id:
                edges.append(f'"{esc_node_id}" -> "{batt_id}" [{edge_attribs[components["Battery"]["edgeattrib"]]}];')

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
    model_id = VerifyTableID('model', request.args(0)) or redirect(URL('model', 'listview'))

    model = db.model(model_id)

    details_form = SQLFORM(db.model, model.id, fields=[
                           'diagram'], showid=False, formstyle='divs')

    default_dot = _wrap_dot(default_dot_body(), model.name)

    components_body = creatediagramfromcomponents(model.id)
    model_components_dot = _wrap_dot(components_body, model.name)

    # Full document for "Rebuild from Components" — a full-text replace of the
    # textarea rather than splicing a new body between the // Nodes and
    # // End Edges markers. Splicing would leave a generated `->` body inside a
    # legacy `graph`/`--` document, which Graphviz rejects outright; a whole
    # replace is also exactly what the button's own confirm dialog promises
    # ("replace all nodes and connections... custom wiring lost").
    model_nodes_dot = model_components_dot

    # Build node options for the connections manager dropdowns. An option id is
    # the DOT reference itself, unquoted: "mc12" for a whole node, "mc12:f3" for
    # one of its ports. That mapping is lossless, so any port name round-trips —
    # unlike the old mc12_p3/_tlm/_sbus/_pwr suffix scheme, which could only
    # express f<n>/t1/t2/t3 and silently dropped edges to anything else.
    #
    # These cover the components this model already knows about, with good
    # labels. The editor's getAllNodeIds() adds any further ports it finds by
    # parsing the live document (customdot records, connector terminals,
    # hand-written nodes); its Map de-dupes by id, so these labels win.
    model_comps = db(db.model_component.model == model_id).select()
    node_options = []
    for mc in model_comps:
        comp = mc.component
        if not comp or comp.componenttype in components_to_ignore:
            continue
        label = comp.diagramname if comp.diagramname else comp.name
        node_options.append({'id': 'mc' + str(mc.id), 'label': label})
        if _resolves_to_record(comp):
            for port, port_label in record_port_options(comp, label):
                node_options.append({'id': f'mc{mc.id}:{port}', 'label': port_label})

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

    # LEGACY MERMAID SCAFFOLDING — temporary, read-only reference so diagrams
    # drawn during the Mermaid period aren't just lost from view while they get
    # re-drawn in Graphviz. Remove this along with model.diagram_mermaid,
    # diagram_comment_mermaid_legacy (models/db.py), and the matching card +
    # mermaid.min.js include in editmodeldiagram.html once every model has a
    # model.diagram again.
    legacy_mermaid = model.diagram_mermaid or ''
    legacy_mermaid_json = json.dumps(legacy_mermaid)
    mermaid_edge_styles_json = json.dumps(mermaid_edge_styles)

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
        legacy_mermaid=legacy_mermaid,
        legacy_mermaid_json=legacy_mermaid_json,
        mermaid_edge_styles_json=mermaid_edge_styles_json,
    )