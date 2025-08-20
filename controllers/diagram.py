def rendermodeldiagram():
    model = db.model(request.args(0)) 

    return dict(dot=model.diagram)

def rendermodelexport():
    model = db.model(request.args(0)) 

    return dict(dot=model.diagram)