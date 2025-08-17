# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
import os
import datetime
#from plugin_thumbnails.thumbnails import thumbnails
from gluon.contrib.appconfig import AppConfig 
# from gluon.tools import Auth

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

db = DAL(configuration.get('db.uri'),
         pool_size=configuration.get('db.pool_size'),
         migrate_enabled=configuration.get('db.migrate'),
         check_reserved=['all'],
         lazy_tables=configuration.get('db.lazy_tables'))

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = []
if request.is_local and not configuration.get('app.production'):
    response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = 'bootstrap4_inline'
response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# host names must be a list of allowed host names (glob syntax allowed)
# auth = Auth(db, host_names=configuration.get('host.names'))

# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------
# auth.settings.extra_fields['auth_user'] = []
# auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
# mail = auth.settings.mailer
# mail.settings.server = 'logging' if request.is_local else configuration.get('smtp.server')
# mail.settings.sender = configuration.get('smtp.sender')
# mail.settings.login = configuration.get('smtp.login')
# mail.settings.tls = configuration.get('smtp.tls') or False
# mail.settings.ssl = configuration.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
# auth.settings.registration_requires_verification = False
# auth.settings.registration_requires_approval = False
# auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# -------------------------------------------------------------------------
response.meta.author = configuration.get('app.author')
response.meta.description = configuration.get('app.description')
response.meta.keywords = configuration.get('app.keywords')
response.meta.generator = configuration.get('app.generator')
response.show_toolbar = configuration.get('app.toolbar')

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
# if configuration.get('scheduler.enabled'):
#    from gluon.scheduler import Scheduler
#    scheduler = Scheduler(db, heartbeat=configuration.get('scheduler.heartbeat'))

# ------------------------
# http: // www.web2pyslices.com/slice/show/2000/thumbnails-plugin
# http://www.web2pyslices.com/slice/show/1387/upload-image-and-make-a-thumbnail

# -------------------------
# 1 = Retired/Disposed
# 2 = Idea
# 3 = On The Board
# 4 = Ready for Maiden
# 5 = In Service
# 6 = Out of Service
# 7 = Under Repair


def component_select_widget(field, value):
    select = SELECT(
        _id="%s_%s" % (field._tablename, field.name), _name=field.name, _value=value, _class=field.type, requires=field.requires)

    select.append(OPTION('Choose Component...', _disabled='', _value='-1'))

    components = db(db.component).iterselect(
        orderby=db.component.componenttype | db.component.name)
    for comps in components:
        if comps.id == value:
            select.append(OPTION(comps.componenttype + ': ' +
                                 comps.name, _value=comps.id, _selected=True))
        else:
            select.append(OPTION(comps.componenttype +
                                 ': ' + comps.name, _value=comps.id))

    return select


markmin_comment = SPAN('More on Markmin ',   A('here', _href='http://www.web2py.com/init/static/markmin.html',
                                               _target='_blank'), 'Upload/Insert an image ', A('here', _href=URL('image', 'index'), _target='_blank'))

db.define_table('article'
                , Field('name', type='string', label='Name', required=True, unique=True)
                #
                , Field('articletype', type='string', label='Type', comment='The type')
                #
                , Field('img', uploadseparate=True, type='upload', autodelete=True, label='Image', comment='Cover Image (1000x1000)', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img])))
                #
                , Field('summary', type='string', label='Summary', required=False, unique=False)
                #
                , Field('notes', type='text', label='Content', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes))
                #
                , Field('author', type='string', label='Author', required=False, unique=False)
                #
                , Field('articlesource', type='string', label='Source', comment='Where did it come from?')
                #
                , Field('attachment', uploadseparate=True, type='upload', autodelete=True, label='Attachment', comment='More info')
                )

db.define_table('model'
                , Field('name', type='string', label='Name', comment='The name of the model', required=True, unique=True)
                #
                , Field('modelorigin', type='string', label='Origin', comment='The origin of the model')
                #
                , Field('modelstate', type='reference modelstate', label='State', comment='The state of the model', required=True, default=2)
                #
                , Field('modeltype', type='string', label='Type', comment='The type of model')
                #
                , Field('controltype', type='string', label='Control', comment='The type of control')
                #
                , Field('powerplant', type='string', label='Power Plant', comment='What type of power?')
                #
                , Field('description', type='string', label='Description', comment='Details of the model')
                #
                , Field('notes', type='text', label='Details', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes))
                #
                , Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the model', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img])))
                #
                , Field('attr_flight_timer', type='double', label='Flight Timer', comment='The length of the flight timer', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                #
                , Field('attr_construction', type='string', label='Construction')
                #
                , Field('attr_cog', type='string', label='CoG', comment='The COG')
                #
                , Field('attr_length', type='double', label='Length (mm)', comment='The length', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                #
                , Field('attr_width', type='double', label='Width/Beam (mm)', comment='The width/beam', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                #
                , Field('attr_height', type='double', label='Height (mm)', comment='The height', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                #
                , Field('attr_weight_oz', type='double', label='Weight (oz)', comment='The weight (oz)', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))                
                # 
                , Field('attr_covering', type='string', label='Covering', comment='The covering type')
                #
                , Field('attr_plane_rem_wings', type='boolean', label='Removable Wings?', comment='Does it have removable wings?')
                #
                , Field('attr_plane_rem_wing_tube', type='boolean', label='Removable Wing Tube?', comment='Does it have a removable wing tube?')
                #
                , Field('attr_plane_rem_struts', type='boolean', label='Removable Struts?', comment='Does it have removable struts?')
                #
                , Field('attr_plane_wingspan_mm', type='double', label='Wingspan (mm)', comment='The wingspan (in mm)', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                #
                , Field('attr_plane_wingarea', type='double', label='Wingarea (sqin)', comment='The wing area (in sqin)', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                #
                , Field('attr_plane_throw_aileron', type='string', label='Aileron Throw', comment='The aileron throws')
                #
                , Field('attr_plane_throw_elevator', type='string', label='Elevator Throw', comment='The elevator throws')
                #
                , Field('attr_plane_throw_rudder', type='string', label='Rudder Throw', comment='The rudder throws')
                #
                , Field('attr_rocket_parachute', type='string', label='Parachute', comment='What is the size of the parachute?')
                #
                , Field('attr_rocket_body_tube', type='string', label='Body Tube', comment='What is the size of the body tube?')
                #
                , Field('attr_rocket_motors', type='list:string', label='Motors', comments='Motors, seperated by "|"')
                #
                , Field('attr_boat_draft', type='double', label='Draft (mm)', comment='The draft in mm', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))                
                # 
                , Field('attr_copter_headtype', type='string', label='Head Type', comment='The type of rotor head')
                #
                , Field('attr_copter_mainrotor_length', type='double', label='Main Rotor Length (mm)', comment='The length of the main rotor blades', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                #
                , Field('attr_copter_tailrotor_span', type='double', label='Tail Rotor Length (mm)', comment='The length of the tail rotor blades', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                #
                , Field('attr_copter_tailrotor_drive', type='string', label='Tail Rotor Drive', comment='What drives the tail rotor?')
                #
                , Field('attr_copter_swashplate_type', type='string', label='Swashplate Type', comment="What type of swashplate does it use?")
                #
                , Field('attr_copter_size', type='integer', label='The "Size" of the Heli', comment='What is the common size designation of the heli?', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                #
                , Field('attr_copter_blade_count', type='integer', label='Blade Count', comment='Number of blades per rotor', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                #
                , Field('attr_copter_tailrotor_blade_count', type='integer', label='Tail Blade Count', comment='Number of blades per rotor', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                #
                , Field('attr_multi_rotor_count', type='integer', label='Rotor Count', comment='The number of rotors', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                #
                , Field('attr_car_scale', type='string', label='Vehicle Scale', comment="The scale of the vehicle")
                #
                , Field('attr_car_drive', type='string', label='X Wheel Drive', comment='How many wheels are powered?')
                #
                , Field('attr_car_bodystyle', type='string', label='Body Style', comment='What is the body style?')
                #
                , Field('attr_scale', type='string', label='Model Scale', comment='What is the scale of the model?')
                #
                , Field('haveplans', type='boolean', label='Are plans in hand?')
                #
                , Field('havekit', type='boolean', label='Have kit/model?')
                #
                , Field('configbackup', uploadseparate=True, type='upload', autodelete=True, label='Radio Config', comment='The backup of the radio/receiver configuration')
                #
                , Field('transmitter', type='reference transmitter', label='Transmitter', comment='Which transmitter is this model bound to?')
                #
                , Field('selected', type='boolean', label='Mark Selected', comment='Avoid manual changes', default=False)
                #
                , Field('subjecttype', type='string', label='Model Subject', comment='Is this a scale model?')
                #
                , Field('final_disposition', type='string', label='Final Disposition', comment='How to liquidate the fleet')
                #
                , Field('final_value', type='double', label='Reasonable Value', comment='A reasonable value for the model')
                #
                , Field('attr_sub_ballast', type='string', label='Ballast Type', comment='The ballast type')
                #
                , Field('fieldnotes', type='text', label='Field Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes))
                #
                , format=lambda row: row.name)

db.define_table('modelstate', Field('name', type='string', label='State'), format=lambda row: row.name
                )

db.define_table('transmitter', Field('name', type='string', label='Name'), Field('nickname', type='string', label='Nickname'), 
                Field('serial', type='string', label='Serial Number'), 
                Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)), 
                Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the transmitter', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))), 
                Field('attachment', uploadseparate=True, type='upload', autodelete=True, label='Manual', comment='The manual, etc', default=''), 
                Field('os', type='string', label='Operating System/Version'),
                format=lambda row: row.name
                )

db.define_table('todo', Field('todo', type='string', label='To Do'), Field('model', type='reference model'), Field('critical', type='boolean', default=False), Field('notes', type='text', label='Notes',
                                                                                                                                                                     comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)), Field('complete', type='boolean', label="Complete?", default=False), format=lambda row: 'Unknown' if row is None else row.todo)

db.define_table('activity', Field('activitydate', type='date', label='Date', required=True, default=request.now), Field('model', type='reference model', label='Model'), Field('activitytype', type='string', label='Type'), Field('duration', type='double', Label='Duration (min)', comment='The duration, in minutes', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')), Field('activitylocation', type='string', label='Location'), Field('notes', type='text', label='Notes', comment='Notes about the event'), Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the activity', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img_thumbnail]))), format=lambda row: 'Unknown' if row is None else row.name
                )

db.define_table('component', Field('name', type='string', label='Name'), Field('componenttype', type='string', label='Type'), Field('componentsubtype', type='string', label='Subtype', comment='The Sub Type'), Field('ownedcount', type='integer', label='Count', comment='How many are owned?', default=0, widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))                # , args=[row.img_thumbnail])))
                , Field('significantdetail', type='string', label='Significant Detail'), Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)), Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the component', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))), Field('attachment', uploadseparate=True, type='upload', autodelete=True, label='Attachment', comment='More info'), format=lambda row: 'Unknown' if row is None else row.name)
db.component.componentsubtype.widget = SQLFORM.widgets.autocomplete(
    request, db.component.componentsubtype, limitby=(0, 10), min_length=2, distinct=True
)

db.define_table('model_component'
                , Field('model', 'reference model')
                , Field('component', 'reference component')
                , Field('purpose', type='string', label='Purpose', comment='Purpose of this component', represent=lambda v, r: '' if v is None else v), Field('channel', type='integer', label='Channel', comment='Channel Assignment', represent=lambda v, r: '' if v is None else v, widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                )
db.model_component.modelstate = Field.Virtual(
    lambda row: row.model.modelstate.id)
db.model_component.component.widget = component_select_widget

db.define_table('tool', Field('name', type='string', label='Name', required=True, unique=True), Field('tooltype', type='string', label='Type'), Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)), Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the tool', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))), Field('attachment', type='upload', autodelete=True, label='Attachment', comment='Manual'), format=lambda row: 'Unknown' if row is None else row.tooltype + ': ' + row.name
                )

db.define_table('model_tool', Field('model', 'reference model'), Field('tool', 'reference tool')
                )
db.model_tool.tool.requires = IS_IN_DB(
    db, 'tool.id', label=db.tool._format, sort=True)

db.define_table('battery', Field('cellcount', type='integer', label='Cell Count', required=True, widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')), Field('mah', type='integer', label='mAh', required=True, widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _class='generic-widget form-control')), Field('chemistry', required=True), Field('crating', type='integer', label='C Rating', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')), Field('ownedcount', type='integer', label='How many are owned?', default=1, widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')), format=lambda row: row.chemistry + ': ' + str(row.cellcount) + 's' + str(row.mah) + ' (' + str(row.crating) + ') '
                )

db.define_table('model_battery', Field('model', 'reference model'), Field('battery', 'reference battery')
                )
db.model_battery.battery.requires = IS_IN_DB(
    db, 'battery.id', label=db.battery._format, sort=True)

db.define_table('sailrig', Field('rigname', type='string', label='Designation (A, B, C)', required=True, unique=False), Field('model', 'reference model'), Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the sail rig', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))), Field('mast_length_mm', type='integer', label='Mast Length (mm)', required=False), Field('mast_material', type='string', label='Mast Material', required=False), Field('main_boom_length_mm', type='integer', label='Main Boom Length (mm)', required=False), Field('main_boom_material', type='string', label='Main Boom Material', required=False), Field('main_sail_material', type='string', label='Main Sail Material', required=False), Field('main_sail_area_dm2', type='double', label='Main Sail Area (dm2)', required=False), Field('jib_boom_length_mm', type='integer', label='Jib Boom Length (mm)', required=False), Field('jib_boom_material', type='string', label='Jib Boom Material', required=False), Field('jib_sail_material', type='string', label='Jib Sail Material', required=False), Field('jib_sail_area_dm2', type='double', label='Jib Sail Area (dm2)', required=False), Field('notes', type='string', label='Rig Notes', required=False)
                )

db.define_table('eflite_time', 
                #
                Field('model', type='reference model', required=True), 
                #
                Field('motor', type='reference component', required=True), 
                #
                Field('battery', type='reference battery', required=True), 
                #
                Field('propeller', type='string'), 
                #
                Field('amps', type='double', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'), required=True), 
                #
                Field('watts', type='double', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'), required=True)
                )

db.define_table('supportitem', Field('item', type='string', Label='Support Item'), Field('model', type='reference model'), Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)), Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the support item', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img_thumbnail]))), format=lambda row: row.item
                )
db.supportitem.item.widget = SQLFORM.widgets.autocomplete(
    request, db.supportitem.item, limitby=(0, 10), min_length=2, distinct=True)

db.define_table('propeller', Field('item', type='string', Label='Propeller', required=True), Field('model', type='reference model'), format=lambda row: row.item
                )
db.propeller.item.widget = SQLFORM.widgets.autocomplete(
    request, db.propeller.item, limitby=(0, 10), min_length=2, distinct=True)

db.model_component.purpose.widget = SQLFORM.widgets.autocomplete(
    request, db.model_component.purpose, limitby=(0, 10), min_length=1, distinct=True)
db.model.attr_covering.widget = SQLFORM.widgets.autocomplete(
    request, db.model.attr_covering, limitby=(0, 10), min_length=2, distinct=True)
db.activity.activitylocation.widget = SQLFORM.widgets.autocomplete(
    request, db.activity.activitylocation, limitby=(0, 10), min_length=2, distinct=True)


db.define_table('attachment', Field('name', type='string', label='Name'), Field('attachmenttype', type='string', label='Type'), Field('model', 'reference model'), Field('attachment', uploadseparate=True, type='upload', autodelete=True, label='Attachment', comment='The attachment')
                )

db.define_table('packingitems', Field('name', type='string', label='Name'), Field('itemtype', type='string', label='Type')
                )

db.define_table('images', Field('img', type='upload', autodelete=True, uploadseparate=True, required=True, label='Image', comment='The image'), Field('tags', type='list:string', label='Tags', comment='A list of tags')
                )

db.define_table('model_wtc', Field('model', 'reference model'), Field('wtc', 'reference tool')
                )

db.define_table('switch'
                , Field('switch', type='string', label='Switch')
                , Field('model', type='reference model', label='Model')
                , Field('switchtype', type='string', label='Type')
                , Field('purpose',type='string', label='Purpose')
                , format=lambda row: row.model.name + " : " + row.purpose)

db.define_table('switch_position'
                , Field('switch', type='reference switch', label='Switch')
                , Field('pos', type='string', label='Position')
                , Field('func', type='string', label='Function')
                )

db.model.attr_length.extra = {'measurement': 'mm'}
db.model.attr_width.extra = {'measurement': 'mm'}
db.model.attr_height.extra = {'measurement': 'mm'}
db.model.attr_weight_oz.extra = {'measurement': 'oz'}
db.model.attr_plane_wingspan_mm.extra = {'measurement': 'mm'}
db.model.attr_plane_wingarea.extra = {'measurement': 'sqin'}
db.model.attr_boat_draft.extra = {'measurement': 'mm'}
db.model.attr_copter_mainrotor_length.extra = {'measurement': 'mm'}
db.model.attr_copter_tailrotor_span.extra = {'measurement': 'mm'}

db.sailrig.mast_length_mm.extra = {'measurement': 'mm'}
db.sailrig.main_boom_length_mm.extra = {'measurement': 'mm'}
db.sailrig.jib_boom_length_mm.extra = {'measurement': 'mm'}
db.sailrig.main_sail_area_dm2.extra = {'measurement': 'dm2'}
db.sailrig.jib_sail_area_dm2.extra = {'measurement': 'dm2'}


def Model_ConvertMeasurementField(model, FieldName):
    if not hasattr(db.model[FieldName], "extra"):
        return ""

    match getattr(db.model, FieldName).extra['measurement']:
        case 'mm':
            return str(TwoDecimal((model[FieldName] or 0) / 25.4)) + " in"
        case 'oz':
            return str(TwoDecimal((model[FieldName] or 0) / 16)) + " lbs"
        case 'dm2':
            return str(TwoDecimal((model[FieldName] or 0) / 9.29)) + " sqin"
        case 'sqin':
            return str(TwoDecimal((model[FieldName] or 0) * 9.29)) + "dm2"
        case _:
            return ""


def Sailrig_ConvertMeasurementField(sailrig, FieldName):
    if not hasattr(db.sailrig[FieldName], "extra"):
        return ""

    match getattr(db.sailrig, FieldName).extra['measurement']:
        case 'mm':
            return str(TwoDecimal((sailrig[FieldName] or 0) / 25.4)) + " in"
        case 'oz':
            return str(TwoDecimal((sailrig[FieldName] or 0) / 16)) + " lbs"
        case 'dm2':
            return str(TwoDecimal((sailrig[FieldName] or 0) / 9.29)) + " sqin"
        case _:
            return ""


def TwoDecimal(number):
    return "{:.2f}".format(number)


def ZeroDecimal(number):
    return "{:.0f}".format(number)


db.model.search = Field.Method(
    lambda row: row.name
)
db.model.open_todos_count = Field.Method(
    lambda row: db((db.todo.model == row.model.id) &
                   (db.todo.complete == False)).count()
)
db.model.activity_count = Field.Method(
    lambda row: db(db.activity.model == row.model.id).count()
)
db.model.activity_flightcount = Field.Method(
    lambda row: db(
        (db.activity.model == row.model.id) &
        (db.activity.activitytype == 'Flight')
    ).count()
)
db.model.get_wingspan = Field.Method(
    lambda row: TwoDecimal(row.model.attr_plane_wingspan_in)
)
db.model.get_wingspan0 = Field.Method(
    lambda row: ZeroDecimal(row.model.attr_plane_wingspan_mm)
)
db.model.get_length = Field.Method(
    lambda row: ZeroDecimal(row.model.attr_length)
)


def AttachPopup(attachment):
    if isimage(attachment):
        attributes = {
            '_data-toggle': 'modal',
            '_data-target': '#mainModal',
            '_data-whatever': '<img class="card-img-top" src=' + URL("default", "download", args=attachment) + '>'
        }
        return A(show_icon("OpenTab.png", 16), **attributes)
    else:
        return ""


db.component.showAttachmentPopup = Field.Method(
    lambda row: AttachPopup(row.component.attachment)  # AttachPopup(row.name)
)
db.article.showAttachmentPopup = Field.Method(
    lambda row: AttachPopup(row.article.attachment)  # AttachPopup(row.name)
)


def get_motor_component(model_id):
    components = models_and_components(db.model.id == model_id)  # .select()
    # return components
    ret = None
    for c in components.select():
        if c.component.componenttype == 'Motor':
            ret = c.model_component.component

    return ret


db.model.get_motor = Field.Method(
    lambda row: get_motor_component(row.model.id)
)


def get_receiver_component(model_id):
    components = models_and_components(db.model.id == model_id)  # .select()
    # return components
    for c in components.select():
        if c.component.componenttype == 'Receiver':
            return c.model_component.component


db.model.get_receiver = Field.Method(
    lambda row: get_receiver_component(row.model.id)
)


def has_radio_backup(model_id):
    model = db(db.model.id == model_id).select().first()

    # if model.get_receiver() != None:
    if model.transmitter != None:
        if model.configbackup != None:
            if len(model.configbackup) > 0:
                return 'Yes'
            else:
                return 'No'
        else:
            return 'No'
    else:
        return 'NA'


db.model.radio_config_backedup = Field.Method(
    lambda row: has_radio_backup(row.model.id)
)


def model_battery_count(model_id):
    batteries = models_and_batteries(db.model.id == model_id).select()
    count = 0
    for m_b in batteries:
        count = count + m_b.battery.ownedcount
    return count


def model_battery_list(model_id):
    batts = []
    batteries = models_and_batteries(db.model.id == model_id).select()
    for b in batteries:
        name = str(b.battery.cellcount) + "s" + \
            str(b.battery.mah) + " " + str(b.battery.chemistry)
        if name not in batts:
            batts.append(name)
    return batts


db.model.get_batterycount = Field.Method(
    lambda row: model_battery_count(row.model.id)
)

db.model.get_battery_list = Field.Method(
    lambda row: model_battery_list(row.model.id)
)


# def model_state_id(model_id):
#    return db(db.model == model_id).select().modelstate.id
# db.model.get_state_id = Field.Method(
#    lambda row: model_state_id(row.model.id)
# )


def model_sailrig_count(model_id):
    return db(db.sailrig.model == model_id).count()


def model_sailrig_list(model_id):
    rigs = []
    m_r = db(db.sailrig.model == model_id).select()

    for r in m_r:
        rigs.append(r.rigname)
    return rigs


db.model.get_sailrigcount = Field.Method(
    lambda row: model_sailrig_count(row.model.id)
)

db.model.get_sailrig_list = Field.Method(
    lambda row: model_sailrig_list(row.model.id)
)


def model_component_count(model_id):
    return models_and_components(db.model.id == model_id).count()


db.model.componentcount = Field.Method(
    lambda row: model_component_count(row.model.id)
)


def model_attachment_count(model_id):
    return db(db.attachment.model == model_id).count()


db.model.get_attachmentcount = Field.Method(
    lambda row: model_attachment_count(row.model.id)
)

db.battery.get_name = Field.Method(
    lambda row: str(row.battery.cellcount) + 's' + str(row.battery.mah) +
    ' (' + str(row.battery.crating) + ') ' + row.battery.chemistry
)
db.battery.get_maxamps = Field.Method(
    lambda row: (row.battery.crating * row.battery.mah) / 1000
)


def component_used_count(comp_id):
    count = 0
    m_c = db(db.model_component.component == comp_id).select()
    for c in m_c:
        if c.model.modelstate > 1:
            count = count + 1
    return count


db.component.get_usedcount = Field.Method(
    lambda row: component_used_count(row.component.id)
)
db.component.get_remainingcount = Field.Method(
    lambda row: row.component.ownedcount - row.component.get_usedcount()
)


def get_min(mah, amps):
    return ((mah * .8) / (amps * 1000)) * 60


db.eflite_time.get_minutes = Field.Method(
    lambda row: TwoDecimal(
        get_min(row.eflite_time.battery.mah, row.eflite_time.amps))
)


def g_wpp(row):
    if (not row.eflite_time.model.attr_weight_lbs):
        return "No Weight Set"
    return TwoDecimal(row.eflite_time.watts / row.eflite_time.model.attr_weight_lbs)


db.eflite_time.get_wattsperpound = Field.Method(
    lambda row: g_wpp(
        row)
)

db.eflite_time.is_overrating = Field.Method(
    lambda row: (row.eflite_time.amps > row.eflite_time.battery.get_maxamps())
)

# This dict must contain the same keys as the IS_IN_SET of the chemistry .requires
chem_volt = {'LiPo': 3.7, 'LiFE': 3.3, 'NiMH': 1.2, 'NiCad': 1.2}
db.battery.voltage = Field.Virtual(
    lambda row: row.battery.cellcount*chem_volt[row.battery.chemistry])
db.battery.voltage.label = 'Voltage'

db.battery.name = Field.Virtual(
    lambda row: str(row.battery.cellcount) + 's' + str(row.battery.mah) + ' (' + str(row.battery.crating) + ') ' + row.battery.chemistry)
db.battery.name.label = 'Name'

db.article.articletype.requires = IS_IN_SET(
    ('Article', 'Book', 'Idea'), sort=True)
db.article.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))
db.activity.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1500, 1500)))
db.images.img.requires = IS_EMPTY_OR(IS_IMAGE())

db.model.modeltype.requires = IS_IN_SET(
    ('Airplane', 'Rocket', 'Boat', 'Helicopter', 'Multirotor', 'Robot', 'Experimental', 'Car', 'Autogyro', 'Submarine'), sort=True)
db.model.modelorigin.requires = IS_EMPTY_OR(IS_IN_SET(
    ('Plan', 'Kit', 'ARF', 'RTF', 'Unknown'), sort=True))
db.model.controltype.requires = IS_EMPTY_OR(IS_IN_SET(
    ('Radio Control', 'Free Flight', 'Control Line', 'Other'), sort=True))
db.model.powerplant.requires = IS_EMPTY_OR(IS_IN_SET(
    ('Electric', 'Internal Combustion', 'Rocket', 'Rubber', 'Sail', 'None'), sort=True))
db.model.attr_construction.requires = IS_EMPTY_OR(IS_IN_SET(
    ('Balsa', 'Foam', 'Plastic', 'Composite', 'Other'), sort=True))
db.model.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))
db.model.attr_copter_headtype.requires = IS_EMPTY_OR(IS_IN_SET(
    ('Collective Pitch', 'Collective Pitch - Flybar', 'Fixed Pitch'), sort=True))
db.model.attr_copter_tailrotor_drive.requires = IS_EMPTY_OR(IS_IN_SET(
    ('Direct', 'Belt', 'Shaft'), sort=True))
db.model.subjecttype.requires = IS_EMPTY_OR(IS_IN_SET(
    ('Scale', 'Semi-Scale', 'Fantasy', 'Sport'), sort=True))
db.model.attr_car_bodystyle.requires = IS_EMPTY_OR(IS_IN_SET(
    ('Truggy', 'Car', 'Truck', 'Other'), sort=True))
db.model.attr_car_drive.requires = IS_EMPTY_OR(IS_IN_SET(
    ('2 Wheel', '4 Wheel', 'All Wheel', 'Other'), sort=True))
db.model.attr_sub_ballast.requires = IS_EMPTY_OR(IS_IN_SET(
    ('Piston Tank','SAS - Semi-Aspirated','RCABS - Recirculating Compressed Air Ballast', 'Vented Low-Pressure', 'Compressed Gas', 'Pressure Pump', 'Dynamic'), sort=True
))

db.transmitter.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))
db.attachment.attachmenttype.requires = IS_IN_SET(
    ('Image', 'Manual', 'Diagram', 'Plan', 'Article', 'Configuration', 'Checklist', 'Transmitter Image'), sort=True)
db.component.componenttype.requires = IS_IN_SET((
    'Engine', 'Servo', 'Receiver', 'Motor', 'ESC', 'BEC', 'Regulator', 'Flight Controller', 'Gyro', 'Battery Charger', 'Flybarless Controller', 'Electrical', 'Switch', 'Winch', 'Other'), sort=True)
db.component.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))
db.activity.activitytype.requires = IS_IN_SET(
    ('Flight', 'Crash', 'Repair', 'Purchase', 'Retirement', 'Note', 'StateChange', 'Other'), sort=True)
db.tool.tooltype.requires = IS_IN_SET(
    ('Hand Tool', 'Fuel Tool', 'Power Tool', 'Electric Tool', 'Radio'), sort=True)
db.tool.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))
db.battery.chemistry.requires = IS_IN_SET(
    ('LiPo', 'LiFE', 'NiMH', 'NiCad'), sort=True)
db.battery.crating.requires = IS_NOT_EMPTY()
db.supportitem.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))
db.packingitems.itemtype.requires = IS_IN_SET(
    ('Standard', 'Overnight', 'Event', 'Plane Event', 'Boat Event', 'Sub Event', 'Night Event', 'Heli Event'))

db.switch.switchtype.requires = IS_EMPTY_OR(IS_IN_SET(
    ('3-Position', '2-Position', '6-Position', 'Momentary', 'Rotary', 'Slider', 'Gimbal-Left-Horizontal','Gimbal-Left-Vertical','Gimbal-Right-Horizontal','Gimbal-Right-Vertical','Trim_Horizontal','Trim-Vertical'), sort=True
))
db.switch_position.pos.requires = IS_EMPTY_OR(IS_IN_SET(
    ('Back', 'Middle', 'Forward', 'Up', 'Down', 'Left', 'Right'), sort=True
))


#db.eflite_time.model.requires = IS_NOT_EMPTY()
#db.eflite_time.motor.requires = IS_NOT_EMPTY()
#db.eflite_time.battery.requires = IS_NOT_EMPTY()
db.eflite_time.amps.requires = IS_NOT_EMPTY()
db.eflite_time.watts.requires = IS_NOT_EMPTY()

models_and_components = db(
    (db.model.id == db.model_component.model)
    &
    (db.component.id == db.model_component.component)
)
models_and_tools = db(
    (db.model.id == db.model_tool.model)
    &
    (db.tool.id == db.model_tool.tool)
)
models_and_batteries = db(
    (db.model.id == db.model_battery.model)
    &
    (db.battery.id == db.model_battery.battery)
)
switches_and_positions = db(
    (db.switch.id == db.switch_position.switch)
)

db.model.notes.format = lambda model: MARKMIN(model.notes)
db.component.notes.format = lambda component: MARKMIN(component.notes)
db.tool.notes.format = lambda tool: MARMIN(tool.notes)
db.todo.notes.format = lambda tool: MARMIN(tool.notes)
db.activity.notes.format = lambda model: MARKMIN(model.notes)
db.article.notes.format = lambda article: MARKMIN(article.notes)


db.model.img.default = os.path.join(
    request.folder, 'static', 'images', 'defaultUpload.png')


if db(db.modelstate.id > 0).count() == 0:
    db.modelstate.insert('Retired/Disposed')  # 1
    db.modelstate.insert('Idea')  # 2
    db.modelstate.insert('On The Board')  # 3
    db.modelstate.insert('Ready for Maiden')  # 4
    db.modelstate.insert('In Service')  # 5
    db.modelstate.insert('Out of Service')  # 6
    db.modelstate.insert('Under Repair')  # 7
# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
