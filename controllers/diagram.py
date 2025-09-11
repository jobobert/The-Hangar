def rendermodeldiagram():
    model = db.model(request.args(0)) 

    return dict(dot=model.diagram, model_id=model.id)

def rendermodelexport():
    model = db.model(request.args(0)) 

    return dict(dot=model.diagram)


components = {
    'Servo': '"servo" [label="Servo"; shape="trapezium"];',
    'Receiver': '"receiver" [label = "<f0>Receiver | <f1>Port 1 | <f2>Port 2 | <f3>Port 3 | <f4>Port 4";shape = "record";];',
    'Connection': '"connector" [label="Connector"; shape="house";]',
    'Battery': '"batt" [label = "3s2200";];',
    'Motor': '"motor" [label="Motor"; shape="circle"];',
    'ESC': '"esc" [label="ESC"; shape="box3d"];',   
    'Switch': '"switch" [label="Switch"; shape="diamond"];',
}

attribs = {
    '5v Servo': '[color = "#a8700f";]',
    '5v Signal': '[color = "#a8700f"; style = dashed;]',
    '12v 12gauge': '[color = "#2430d3"; penwidth = 4;]',
    '12v20gauge': '[color = "#2430d3"; penwidth = 2;]',
}

def creatediagramfromcomponents(model_id):
    model_components = db(db.model_component.model == model_id).select()
    model_battery = db(db.model_battery.model == model_id).select()

    id = 0
    nodes = []
    edges = []
    escid = 0

    for row in sorted(model_components, key=lambda type: type.component.componenttype):
        id += 1
        comp = row.component
        match comp.componenttype:
            
            case 'Servo': 
                nodes.append(f'"servo{id}" [label="{row.purpose} Servo"; shape="trapezium"];')
                if row.channel:
                    edges.append(f"receiver:f{row.channel} -- servo{id} {attribs['5v Servo']};")

            case 'Switch': 
                nodes.append(f'"switch{id}" [label="{row.purpose} Switch"; shape="diamond"];')
                if row.channel:
                    edges.append(f"receiver:f{row.channel} -- switch{id} {attribs['5v Servo']};")

            case 'ESC': 
                nodes.append(f'"esc{id}" [label="{row.component.name}"; shape="box3d"];')
                if row.channel:
                    edges.append(f"receiver:f{row.channel} -- esc{id} {attribs['5v Servo']};")
                escid = id

            case 'Motor':
                nodes.append(f'"motor{id}" [label="{row.component.name}"; shape="circle"];')
                if escid != "":
                    edges.append(f"esc{escid} -- motor{id} {attribs['12v 12gauge']};")
             
            case 'Receiver':
                count = 4 
                if comp.attr_channel_count:
                    count = comp.attr_channel_count
                recvr = '"receiver" [label = "<f0>Receiver'
                for x in range(1, count + 1):
                    recvr += f'| <f{x}>Port {x} '
                recvr += '";shape = "record";];'
                nodes.append(recvr)

            case _: 
                nodes.append(f'"other{id}" [label="{row.purpose} {row.component.name}"; shape="rect"];')
                if row.channel:
                    edges.append(f"receiver:f{row.channel} -- other{id} {attribs['5v Servo']};")

    for row in model_battery.render():
        id += 1

        nodes.append(f'"batt{id}" [label = "{row.battery}";];')
        if escid != 0:
            edges.append(f"esc{escid} -- batt{id} {attribs['12v 12gauge']};")

    ret = '\n// Nodes\n'
    ret += "\n".join(nodes)
    ret += '\n\n// Edges\n'
    ret += "\n".join(edges)
    
    return ret


def editmodeldiagram():
    model = db.model(request.args(0)) 

    details_form = SQLFORM(db.model, model.id, fields=[
                           'diagram'], showid=False, formstyle='divs')
    
    legend = f"""
// Legend
subgraph cluster_legend {{
    label = "Legend";
    node [shape = plaintext;];
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
    key:i1:e -- key2:i1:w {attribs['5v Servo']};
    key:i2:e -- key2:i2:w {attribs['5v Signal']};
    key:i3:e -- key2:i3:w {attribs['12v 12gauge']};
    key:i4:e -- key2:i4:w {attribs['12v20gauge']};
}}
    """

    title = f"""
// Title
fontsize = 30;
label = "{model.name} Wiring Diagram";
labelloc = "t";
    """

    default_dot = f"""
graph model {{
rankdir = LR;
{legend}

// Nodes
{components['Receiver']}
{components['Servo']}

// Edges
receiver:f1 -- servo {attribs['5v Servo']};

{title}
}}
    """

    model_components_dot = f"""

graph model {{
rankdir = LR;
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

    return dict(dot=model.diagram, model_name=model.name, form=details_form, default_dot=default_dot, attribs=attribs, components=components, model_components_dot=model_components_dot)