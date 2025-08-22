def rendermodeldiagram():
    model = db.model(request.args(0)) 

    return dict(dot=model.diagram, model_id=model.id)

def rendermodelexport():
    model = db.model(request.args(0)) 

    return dict(dot=model.diagram)

def editmodeldiagram():
    model = db.model(request.args(0)) 

    details_form = SQLFORM(db.model, model.id, fields=[
                           'diagram'], showid=False, formstyle='divs')
    
    default_dot = """
    graph model {
    rankdir = LR;
    
    // Legend
    subgraph cluster_legend {
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
        key:i1:e -- key2:i1:w [color = "#a8700f";];
        key:i2:e -- key2:i2:w [color = "#a8700f"; style = dashed;];
        key:i3:e -- key2:i3:w [color = "#2430d3"; penwidth = 4;];
        key:i4:e -- key2:i4:w [color = "#2430d3"; pendwidth = 2;];
    }

    // Nodes
    "receiver" [label = "<f0>Receiver | <f1>Port 1 | <f2>Port 2 | <f3>Port 3 | <f4>Port 4 | <f5>Port 5 | <f6>Port 6";shape = "record";];
    "servo" [label="Servo"; shape="box"];
    
    // Edges
    receiver:f1 -- servo [color = "#a8700f";];

    // Title
    fontsize = 30;
    label = "<Model Name> Wiring Diagram";
    labelloc = "t";
    }
    }"""

    if details_form.process().accepted:
        session.flash = "Model Updated"
        redirect(URL('model', 'index', args=details_form.vars.id, extension="html"))
    elif details_form.errors:
        response.flash = "Error Adding New Model"

    return dict(dot=model.diagram, model_name=model.name, form=details_form, default_dot=default_dot)