def rendermodeldiagram():
    if len(request.args) == 2:
        is_mobile = request.args[1]
    else:
        is_mobile = False 

    model = db.model(request.args(0)) 

    return dict(dot=model.diagram, model_id=model.id,options=request.args(1),is_mobile=is_mobile)

def rendermodelexport():
    model = db.model(request.args(0)) 

    return dict(dot=model.diagram)

# This list must be kept in sync with the component.componenttype(s) in the database,
# Plus battery and connector
# The "edgeattrib" has to be in the edge_attribs dict
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
    , 'Battery Charger':       
        {'id': 'battchar', 'shape': 'rect', 'attribs': 'style="filled"; fillcolor="#efefef"', 'edgeattrib': '12v 12gauge'}
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

edge_attribs = {
    'default': 'color = "#efefef";',
    '5v Servo': 'color = "#a8700f";',
    '5v Signal': 'color = "#a8700f"; style = dashed;',
    '12v 12gauge': 'color = "#2430d3"; penwidth = 4;',
    '12v 20gauge': 'color = "#2430d3"; penwidth = 2;',
}

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

def creatediagramfromcomponents(model_id):
    model_components = db(db.model_component.model == model_id).select()
    model_battery = db(db.model_battery.model == model_id).select()

    id = 0
    nodes = ['"default" [label="Default"; shape="rect"];']
    edges = []
    escid = 0

    for row in sorted(model_components, key=lambda type: type.component.componenttype):
        id += 1
        comptype = row.component.componenttype
        compname = row.component.diagramname if row.component.diagramname else row.component.name
        
        match comptype:
            
            case 'ESC': 
                nodes.append(f'"{components[comptype]["id"]}{id}" [label="{compname}\n{row.purpose}"; {components[comptype]["attribs"]}; shape="{components[comptype]["shape"]}"];')
                edges.append(f'{"receiver:f" + str(row.channel) if row.channel else "default"} -- {components[comptype]["id"]}{id} [{edge_attribs[components[comptype]["edgeattrib"]]}];')
                escid = id
            case 'Motor':
                nodes.append(f'"{components[comptype]["id"]}{id}" [label="{compname}"; {components[comptype]["attribs"]}; shape="{components[comptype]["shape"]}"];')
                edges.append(f'{"esc" + str(escid) if escid != "" else "default"} -- motor{id} [{edge_attribs[components[comptype]["edgeattrib"]]}];')
            case 'Receiver':
                count = 4 
                ports = []
                if row.component.attr_channel_count:
                    count = row.component.attr_channel_count
                ports.append(f'"receiver" [label = "<f0>{compname}')
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
                nodes.append(f'"{components[comptype]["id"]}{id}" [label="{compname}\n{row.purpose if row.purpose else ""}"; {components[comptype]["attribs"]}; shape="{components[comptype]["shape"]}"];')
                edges.append(f'{"receiver:f" + str(row.channel) if row.channel else "default"} -- {components[comptype]["id"]}{id} [{edge_attribs[components[comptype]["edgeattrib"]]}];')

    for row in model_battery.render():
        id += 1
        nodes.append(f'"batt{id}" [label = "{row.battery}"; {components["Battery"]["attribs"]}];')
        if escid != 0:
            edges.append(f'esc{escid} -- batt{id} [{edge_attribs[components["Battery"]["edgeattrib"]]}];')

    ret = '\n// Nodes\n'
    ret += "\n".join(nodes)
    ret += '\n\n// Edges\n'
    ret += "\n".join(edges)
    
    return ret

def createcomponentexamples():
    comps = []
    for name, details in components.items():
        comps.append((name, f'"{details["id"]}" [label="{name}"; shape="{details["shape"]}"; {details["attribs"]}];'))

    return comps

def editmodeldiagram():
    model = db.model(request.args(0)) 

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

// Edges
receiver:f1 -- servo [{edge_attribs['5v Servo']}];

{title}
}}
    """

    model_components_dot = f"""
graph model {{
rankdir = LR;
fontsize="10"
{legend}

{creatediagramfromcomponents(model.id)}

{title}
}}
    """

    if details_form.process().accepted:
        session.flash = "Model Updated"
        redirect(URL('model', 'index', args=details_form.vars.id, extension="html"))
    elif details_form.errors:
        response.flash = "Error Adding New Model"

    return dict(dot=model.diagram, model_name=model.name, form=details_form, default_dot=default_dot, edge_attribs=edge_attribs, components=createcomponentexamples(), model_components_dot=model_components_dot)