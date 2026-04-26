

def index():
    response.title = 'Hardware'

    hardware_id = VerifyTableID('hardware', request.args(0)) or redirect(URL('hardware', 'listview'))

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    item = db.hardware(hardware_id)
    model = db.model(item.model) if item else None

    return dict(item=item, model=model)


def listview():

    session.ReturnHere = URL(
        args=request.args, vars=request.get_vars, host=True)

    hardware = db(db.hardware).select(
        orderby=db.hardware.hardwaretype | db.hardware.diameter | db.hardware.length_mm)
    return dict(hardware=hardware)


def update():

    response.title = 'Add/Update Hardware'

    hardware_id = VerifyTableID('hardware', request.args(0)) if request.args(0) else None

    form = SQLFORM(db.hardware, hardware_id, upload=URL(
        'default', 'download'), deletable=bool(hardware_id), showid=False,
        fields=['model', 'hardwaretype', 'diameter', 'length_mm', 'purpose', 'quantity']
    ).process(message_onsuccess='Hardware %s' % ('updated' if request.args(0) else 'added'))

    if form.accepted:
        redirect(URL('hardware', 'index', args=form.vars.id, extension='html')
                 or session.ReturnHere)

    disable_autocomplete(form)

    return dict(form=form)


def rendercard():

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'hardware', 'Hardware')

    fields = ['hardwaretype', 'diameter', 'length_mm', 'purpose', 'quantity']
    addform = SQLFORM(db.hardware, fields=fields, formstyle='bootstrap4_inline', submit_button='Submit')
    disable_autocomplete(addform)
    addform.vars.model = model_id
    if addform.process(session=None, formname='hwform').accepted:
        response.flash = "New Hardware Added"
    elif addform.errors:
        response.flash = "Error Adding New Hardware"

    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='hwdeleteform').accepted:
        for y, z in request.vars.items():
            if z == "Remove":
                db(db.hardware.id == y).delete()
                response.flash = "Removal Success"
    elif deleteform.errors:
        response.flash = "Removal Failure"

    hardware = db(db.hardware.model == model_id).select()

    return dict(hardware=hardware, model_id=model_id, addform=addform, deleteform=deleteform)


def renderexport():
    session.forget(response)

    model_id = VerifyTableID('model', request.args(0)) or None

    hardware = db(db.hardware.model == model_id).select() or None

    torender = {
        'title': 'Hardware',
        'items': None,
        'emptymsg': 'No hardware is associated with this model',
        'controller': None,
        'header': None,
    }

    if hardware:
        table = TABLE(_class="table export-table")
        header = [
            TH(db.hardware.hardwaretype.label, _class="col export-field_name"),
            TH(db.hardware.diameter.label, _class="col export-field_name"),
            TH(db.hardware.length_mm.label, _class="col export-field_name"),
            TH(db.hardware.purpose.label, _class="col export-field_name"),
            TH(db.hardware.quantity.label, _class="col export-field_name"),
        ]
        table.append(TR(*header, _class="row export-row"))
        for h in hardware:
            row = [
                TD(h.hardwaretype, _class="col export-field_value"),
                TD(h.diameter, _class="col export-field_value"),
                TD(h.length_mm, _class="col export-field_value"),
                TD(h.purpose, _class="col export-field_value"),
                TD(h.quantity, _class="col export-field_value"),
            ]
            table.append(TR(*row, _class="row export-row"))

        torender['items'] = table

    response.view = 'renderexport.load'
    return dict(content=torender)


def delete():
    hardware_id = VerifyTableID('hardware', request.args(0)) or redirect(URL('hardware', 'listview'))

    db(db.hardware.id == hardware_id).delete()
    session.flash = "Deleted"
    redirect(session.ReturnHere or URL('hardware', 'listview'))
