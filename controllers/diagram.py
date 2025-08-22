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

    if details_form.process().accepted:
        session.flash = "Model Updated"
        redirect(URL('model', 'index', args=details_form.vars.id, extension="html"))
    elif details_form.errors:
        response.flash = "Error Adding New Model"

    return dict(dot=model.diagram, model_name=model.name, form=details_form)