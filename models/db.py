# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
import os
import re
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


markmin_comment = SPAN('More on Markmin ',   A('here  ', _href='http://www.web2py.com/init/static/markmin.html',
                                               _target='_blank'), 'Upload/Insert an image ', A('here', _href=URL('image', 'index'), _target='_blank'))

diagram_comment = SPAN('Editor ', A('here', _href='https://dreampuf.github.io/GraphvizOnline/', _target='_blank'))

# LEGACY MERMAID SCAFFOLDING — diagram_comment_mermaid_legacy, model.diagram_mermaid
# below, and the read-only rendered-diagram card + mermaid.min.js include in
# views/diagram/editmodeldiagram.html (see legacy_mermaid in
# controllers/diagram.py's editmodeldiagram()) all exist only so diagrams drawn
# during the Mermaid period aren't lost from view while they get re-drawn in
# Graphviz. Delete all of them together — plus static/js/mermaid.min.js and
# static/js/mermaid-helpers.js — once every model has a model.diagram again.
diagram_comment_mermaid_legacy = SPAN('Legacy Mermaid reference only — no longer editable here.')


field_method_labels = {}

###############################################
## MODEL STATE

# -------------------------
# 1 = Retired/Disposed
# 2 = Idea
# 3 = On The Board
# 4 = Ready for Maiden
# 5 = In Service
# 6 = Out of Service
# 7 = Under Repair

db.define_table('modelstate', 
                Field('name', type='string', label='State'), 
                format=lambda row: row.name
                )


##############################################
## TAG

db.define_table('tag',
                Field('name', type='string', label='Tag'),
                format='%(name)s')

###############################################
## MIGRATIONS
# Tracks which one-time migration steps have been applied.
# Check with _migration_applied(name); record with _mark_migration(name).

db.define_table('migrations',
    Field('name',       type='string',   label='Migration',  required=True),
    Field('applied_on', type='datetime', label='Applied On',
          default=lambda: datetime.datetime.now(datetime.timezone.utc)),
    format=lambda r: r.name
)

def _migration_applied(name):
    return db(db.migrations.name == name).count() > 0

def _mark_migration(name):
    if not _migration_applied(name):
        db.migrations.insert(name=name)

###############################################
## DIAGRAM EDGE

db.define_table('diagramedge',
    Field('name',         type='string',  label='Edge Type',      required=True),
    Field('stroke_color', type='string',  label='Color',          default='#000000'),
    Field('stroke_width', type='integer', label='Width (px)',     default=1),
    Field('stroke_style', type='string',  label='Style',          default='solid',
          requires=IS_IN_SET(['solid', 'dashed', 'dotted'])),
    Field('arrow_start',  type='string',  label='Start Arrowhead', default='none',
          requires=IS_IN_SET(['none', 'arrow', 'circle', 'cross'])),
    Field('arrow_end',    type='string',  label='End Arrowhead',  default='none',
          requires=IS_IN_SET(['none', 'arrow', 'circle', 'cross'])),
    Field('dot_attribs',  type='string',  label='DOT Attributes (legacy)', default='',
          readable=False, writable=False),
    Field('sort_order',   type='integer', label='Sort Order',     default=0),
    format=lambda r: r.name
)

def _parse_dot_attribs_to_style(dot_attribs):
    """Mechanically parse the small 'key="value"; key=value;' Graphviz
    attribute fragment this app actually uses (color/penwidth/style) into
    (color, width, style). Anything else in the fragment is left alone —
    the original string is preserved verbatim in the now-hidden
    dot_attribs column, so nothing is destroyed, just not reflected here."""
    color = '#000000'
    width = 1
    style = 'solid'
    m = re.search(r'color\s*=\s*"?(#[0-9a-fA-F]{3,8}|\w+)"?', dot_attribs or '')
    if m:
        color = m.group(1)
    m = re.search(r'penwidth\s*=\s*"?(\d+)"?', dot_attribs or '')
    if m:
        width = int(m.group(1))
    if re.search(r'style\s*=\s*"?dashed"?', dot_attribs or ''):
        style = 'dashed'
    elif re.search(r'style\s*=\s*"?dotted"?', dot_attribs or ''):
        style = 'dotted'
    return color, width, style

if not _migration_applied('diagramedge_structured_style_v1'):
    for _row in db(db.diagramedge.id > 0).select():
        _color, _width, _style = _parse_dot_attribs_to_style(_row.dot_attribs)
        _row.update_record(stroke_color=_color, stroke_width=_width, stroke_style=_style)
    _mark_migration('diagramedge_structured_style_v1')
    db.commit()

if not _migration_applied('diagramedge_arrow_defaults_v1'):
    # Field(default=...) only applies at insert time, not retroactively to
    # rows that existed before these columns were added — backfill them.
    db(db.diagramedge.arrow_start == None).update(arrow_start='none')
    db(db.diagramedge.arrow_end == None).update(arrow_end='none')
    _mark_migration('diagramedge_arrow_defaults_v1')
    db.commit()

# Graphviz arrowhead name for each of the four arrow_start/arrow_end values.
# Graphviz has no X-shaped arrow type, so 'cross' maps to the perpendicular
# bar ('tee'), which is the closest thing it offers.
_DOT_ARROW_TYPES = {
    'none':   'none',
    'arrow':  'normal',
    'circle': 'odot',
    'cross':  'tee',
}

def _arrow_dot_attribs(arrow_start, arrow_end):
    """Graphviz dir/arrowtail/arrowhead fragment for a wire type's two ends.

    Only meaningful on a directed graph — Graphviz silently ignores all three
    attributes inside an undirected `graph`, which is why generated diagrams
    are `digraph`s (see _style_to_dot_attribs()). Returns '' when neither end
    has an arrowhead and there is nothing to say beyond dir=none."""
    tail = _DOT_ARROW_TYPES.get(arrow_start or 'none', 'none')
    head = _DOT_ARROW_TYPES.get(arrow_end or 'none', 'none')
    if tail == 'none' and head == 'none':
        return 'dir = none'
    if tail == 'none':
        return f'dir = forward; arrowhead = {head}'
    if head == 'none':
        return f'dir = back; arrowtail = {tail}'
    return f'dir = both; arrowtail = {tail}; arrowhead = {head}'

def _style_to_dot_attribs(row):
    """Build a Graphviz edge-attribute fragment from a diagramedge row's
    structured style columns — the inverse of _parse_dot_attribs_to_style()
    above.

    The structured columns are the source of truth: they are what the admin UI
    edits, and diagram_component.dot_attribs is empty on every row, so the
    frozen dot_attribs text can't drive generation any more. It is still kept
    verbatim in its now-hidden column as the historical record.

    Round-trips exactly against the seeded values — e.g. ('#a8700f', 1,
    'dashed') renders 'color = "#a8700f"; style = dashed;', byte-for-byte the
    string diagramedge_seed_v1 originally inserted."""
    parts = [f'color = "{row.stroke_color or "#000000"}"']
    if row.stroke_width and int(row.stroke_width) != 1:
        parts.append(f'penwidth = {int(row.stroke_width)}')
    if row.stroke_style in ('dashed', 'dotted'):
        parts.append(f'style = {row.stroke_style}')
    # Always emitted, dir=none included: a digraph defaults to dir=forward with
    # a filled arrowhead, so "no arrowheads configured" has to say so out loud
    # or every wire sprouts an arrow it was never given.
    parts.append(_arrow_dot_attribs(row.arrow_start, row.arrow_end))
    return '; '.join(parts) + ';'

def _component_style_to_dot_attribs(row):
    """Build a Graphviz node-attribute fragment from a diagram_component row's
    structured style columns, for the diagram editor's custom-component
    palette. Mirrors _style_to_dot_attribs() for nodes rather than edges: the
    border style folds into Graphviz's combined `style` attribute alongside
    `filled`, rather than being its own attribute."""
    style = 'filled'
    if row.stroke_style in ('dashed', 'dotted'):
        style += ',' + row.stroke_style
    parts = [
        f'shape = "{row.shape or "box"}"',
        f'style = "{style}"',
        f'fillcolor = "{row.fillcolor or "#efefef"}"',
    ]
    if row.stroke_color:
        parts.append(f'color = "{row.stroke_color}"')
    if row.stroke_width and int(row.stroke_width) != 1:
        parts.append(f'penwidth = {int(row.stroke_width)}')
    return '; '.join(parts) + ';'

# name -> Graphviz edge attributes, generated live from the structured columns
# so an admin edit in Wire Types takes effect without re-saving any diagram.
diagram_edge_attribs = {
    r.name: _style_to_dot_attribs(r)
    for r in db(db.diagramedge.id > 0).select(
        orderby=db.diagramedge.sort_order | db.diagramedge.name)
}

# LEGACY MERMAID SCAFFOLDING — only feeds the read-only Mermaid card that
# renders already-saved model.diagram_mermaid text. Remove with the rest.
mermaid_edge_styles = {
    r.name: {'color': r.stroke_color, 'width': r.stroke_width, 'style': r.stroke_style,
             'arrowStart': r.arrow_start, 'arrowEnd': r.arrow_end}
    for r in db(db.diagramedge.id > 0).select(
        orderby=db.diagramedge.sort_order | db.diagramedge.name)
}

###############################################
## DIAGRAM CONNECTOR

db.define_table('diagram_connector',
    Field('name',        type='string',  label='Name',            required=True),
    Field('left_count',  type='integer', label='Left Terminals',  default=1),
    Field('right_count', type='integer', label='Right Terminals', default=1),
    Field('left_label',  type='string',  label='Left Label',      default=''),
    Field('right_label', type='string',  label='Right Label',     default=''),
    Field('fillcolor',   type='string',  label='Fill Color',      default='#d4c07a'),
    Field('custom_dot',  type='text',    label='Custom DOT Label', default=''),
    Field('sort_order',  type='integer', label='Sort Order',      default=0),
    format=lambda r: r.name
)

if not _migration_applied('diagram_connector_seed_v1'):
    if db(db.diagram_connector.id > 0).count() == 0:
        for _i, (_name, _lc, _rc, _ll, _rl) in enumerate([
            ('XT-60',  2, 2, '♂', '♀'),
            ('XT-30',  2, 2, '♂', '♀'),
            ('XT-90',  2, 2, '♂', '♀'),
            ('JST',    2, 2, '♂', '♀'),
            ('Deans',  2, 2, '♂', '♀'),
            ('EC3',    2, 2, '♂', '♀'),
            ('EC5',    2, 2, '♂', '♀'),
        ], 1):
            db.diagram_connector.insert(
                name=_name, left_count=_lc, right_count=_rc,
                left_label=_ll, right_label=_rl,
                fillcolor='#d4c07a', sort_order=_i
            )
    _mark_migration('diagram_connector_seed_v1')

## DIAGRAM COMPONENT

db.define_table('diagram_component',
    Field('name',         type='string',  label='Name',            required=True),
    Field('shape',        type='string',  label='Shape',           default='box'),
    Field('fillcolor',    type='string',  label='Fill Color',      default='#efefef'),
    Field('stroke_color', type='string',  label='Border Color',    default=''),
    Field('stroke_width', type='integer', label='Border Width (px)', default=1),
    Field('stroke_style', type='string',  label='Border Style',    default='solid',
          requires=IS_IN_SET(['solid', 'dashed', 'dotted'])),
    Field('dot_attribs',  type='string',  label='DOT Attribs (legacy)', default='',
          readable=False, writable=False),
    Field('sort_order',   type='integer', label='Sort Order',      default=0),
    format=lambda r: r.name
)

###############################################
## BATTERY CHEMISTRY

db.define_table('chemistry',
    Field('name',       type='string',  label='Chemistry',        required=True),
    Field('volt',       type='double',  label='Voltage per Cell', default=0.0),
    Field('sort_order', type='integer', label='Sort Order',       default=0),
    format=lambda r: r.name
)

###############################################
## COMPONENT TYPE

db.define_table('componenttype',
    Field('name',               type='string',      label='Type',          required=True),
    Field('sort_order',         type='integer',     label='Sort Order',    default=0),
    Field('is_system',          type='boolean',     label='System',        default=False),
    Field('attrs',              type='list:string', label='Attributes',    default=[]),
    Field('diagram_shape',      type='string',      label='Diagram Shape', default=''),
    Field('diagram_color',      type='string',      label='Diagram Color', default='#efefef'),
    Field('diagram_edgeattrib', type='string',      label='Diagram Edge',  default='default'),
    # Structural, not cosmetic — deliberately NOT inferred from diagram_shape
    # == 'record'. A shape is how a node is drawn; "has addressable ports" is
    # what it is. Keying off the shape string would also silently miss
    # 'Mrecord' (Graphviz's rounded record), and would force diagram_shape to
    # start overriding the hardcoded `components` dict in controllers/diagram.py
    # — a behavior change for all 18 built-in types. See component.diagram_is_record
    # for the per-component override.
    Field('diagram_is_record',  type='boolean',     label='Port Record',   default=False,
          comment='Components of this type render as a record with individually connectable ports'),
    Field('pinned_cols',        type='text',         label='Pinned Columns', default=''),
    format=lambda r: r.name
)

###############################################
## LOOKUP

db.define_table('lookup',
    Field('category',   type='string',  label='Category',   required=True),
    Field('name',       type='string',  label='Value',      required=True),
    Field('sort_order', type='integer', label='Sort Order', default=0),
    Field('is_system',  type='boolean', label='System',     default=False),
    Field('metadata',   type='text',    label='Metadata',   default='',
          comment='JSON metadata (e.g. {"hide": [...]} for modelcategory)'),
    format=lambda r: r.name
)

class lookup_set:
    """Lazy validator backed by the lookup table.
    Values are queried at validation/options time, not at construction time,
    so the validator is correct even on the very first request to a fresh DB
    (before the seed block has populated db.lookup).
    Exposes .options() so callers can enumerate valid values (e.g. for
    building category tab lists in controllers)."""

    multiple = False  # required by SQLFORM's field.requires.multiple check

    def __init__(self, category, empty_ok=False):
        self.category  = category
        self.empty_ok  = empty_ok

    def _vals(self):
        rows = db(db.lookup.category == self.category).select(
            db.lookup.name,
            orderby=db.lookup.sort_order | db.lookup.name
        )
        return [r.name for r in rows]

    def __call__(self, value):
        if self.empty_ok and value in ('', None):
            return (value, None)
        return IS_IN_SET(self._vals(), zero=None)(value)

    def options(self):
        """Return [(value, label), ...] — matches IS_IN_SET.options() contract."""
        return [(v, v) for v in self._vals()]

    def formatter(self, value):
        return value

# Some web2py versions omit IS_EMPTY_OR.multiple; add it if absent so SQLFORM
# doesn't raise AttributeError when wrapping a validator in IS_EMPTY_OR.
if not hasattr(IS_EMPTY_OR, 'multiple'):
    IS_EMPTY_OR.multiple = False

###############################################
## ARTICLE

db.define_table('article'
                , Field('name', type='string', label='Name', required=True, unique=True)
                , Field('articletype', type='string', label='Type', comment='The type')
                , Field('img', uploadseparate=True, type='upload', autodelete=True, label='Image', comment='Cover Image (1000px max)', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img])))
                , Field('summary', type='string', label='Summary', required=False, unique=False)
                , Field('notes', type='text', label='Content', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes))
                , Field('author', type='string', label='Author', required=False, unique=False)
                , Field('articlesource', type='string', label='Source', comment='Where did it come from?')
                , Field('attachment', uploadseparate=True, type='upload', autodelete=True, label='Attachment', comment='More info')
                , Field('tags', type='list:reference tag')
                )

db.article.showAttachmentPopup = Field.Method(
    lambda row: AttachPopup(row.article.attachment)
)
db.article.showAttachmentPopup.label = 'Attachment'

db.article.articletype.requires = lookup_set('articletype')

db.article.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))

db.article.notes.format = lambda article: MARKMIN(article.notes)


###############################################
## TRANSMITTER
## PROTOCOL

db.define_table('protocol', 
                Field('name', type='string', label='Name'), 
                Field('description', type='text', label='Description'), 
                format=lambda row: row.name   
                )

## SEMVER CUSTOM TYPE

def _semver_encode(v):
    if not v: return None
    parts = str(v).strip().split('.')
    while len(parts) < 3: parts.append('0')
    try:
        return '.'.join(f'{int(p):03d}' for p in parts[:3])
    except (ValueError, TypeError):
        return None

def _semver_decode(v):
    if not v: return None
    parts = str(v).strip().split('.')
    try:
        return '.'.join(str(int(p)) for p in parts[:3])
    except (ValueError, TypeError):
        return str(v)

from gluon.dal import SQLCustomType
semver_type = SQLCustomType(type='string', native='varchar(11)',
                            encoder=_semver_encode, decoder=_semver_decode)

db.define_table('transmitter',
                Field('name', type='string', label='Name', required=True),
                Field('nickname', type='string', label='Nickname'),
                Field('serial', type='string', label='Serial Number'), 
                Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)), 
                Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the transmitter (1000px max)', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))), 
                Field('attachment', uploadseparate=True, type='upload', autodelete=True, label='Manual', comment='The manual, etc', default=''), 
                Field('manufacturer', type='string', label='Manufacturer', comment='Who made the transmitter?'),
                Field('model', type='string', label='Model', comment='The model of the transmitter'),
                Field('processor', type='string', label='Processor', comment='The processor in the transmitter'),
                Field('radio_processor', type='string', label='Radio Processor', comment='The processor in the radio module'),
                Field('radio_firmware', type='string', label='Radio Firmware', comment='The radio firmware running on the transmitter'),
                Field('os', type='string', label='Operating System', comment='The OS name (e.g. EdgeTX, OpenTX)'),
                Field('os_version', type=semver_type, label='OS Version', comment='The OS version (e.g. 2.9.3)'),
                Field('firmware_version', type=semver_type, label='Radio Firmware Version', comment='The firmware version (e.g. 1.2.3)'),
                Field('protocol', type='list:reference protocol', label='Protocols Supported', comment='The protocols supported by this transmitter',
                widget=SQLFORM.widgets.checkboxes.widget,
                represent=lambda v, r: ', '.join([p.name for p in db(db.protocol.id.belongs(v)).select()]) ),
                Field('can_export_config', type='boolean', label='Can Export Config',
                      default=False, comment='Whether this transmitter can export a configuration file'),
                format=lambda row: row.name
                )

db.transmitter.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))
db.transmitter.firmware_version.requires = IS_EMPTY_OR(
    IS_MATCH(r'^\d+(\.\d+){0,2}$', error_message='Format: major.minor.patch (e.g. 1.2.3)'))

db.transmitter.manufacturer.widget = SQLFORM.widgets.autocomplete(
    request, db.transmitter.manufacturer, limitby=(0, 10), min_length=2, distinct=True)
db.transmitter.model.widget = SQLFORM.widgets.autocomplete(
    request, db.transmitter.model, limitby=(0, 10), min_length=2, distinct=True)
db.transmitter.processor.widget = SQLFORM.widgets.autocomplete(
    request, db.transmitter.processor, limitby=(0, 10), min_length=2, distinct=True)
db.transmitter.radio_firmware.widget = SQLFORM.widgets.autocomplete(
    request, db.transmitter.radio_firmware, limitby=(0, 10), min_length=2, distinct=True)
db.transmitter.os.widget = SQLFORM.widgets.autocomplete(
    request, db.transmitter.os, limitby=(0, 10), min_length=2, distinct=True)
db.transmitter.radio_processor.widget = SQLFORM.widgets.autocomplete(
    request, db.transmitter.radio_processor, limitby=(0, 10), min_length=2, distinct=True)
db.transmitter.os_version.requires = IS_EMPTY_OR(
    IS_MATCH(r'^\d+(\.\d+){0,2}$', error_message='Format: major.minor.patch (e.g. 2.9.3)'))

# Migrate transmitter.os: the field previously held "Operating System/Version"
# as a single freeform string. The new schema splits this into os (name) and
# os_version (semver). Existing os values are left intact; os_version stays
# empty and can be filled in manually.
if not _migration_applied('transmitter_split_os_version_v1'):
    _mark_migration('transmitter_split_os_version_v1')

db.transmitter.protocol.represent = lambda ids, row: ', '.join([db.protocol(id).name for id in ids if db.protocol(id)])
def expandProtocols(list_of_ids):
    return ', '.join([db.protocol(id).name for id in list_of_ids if db.protocol(id)])
db.transmitter.get_protocollist = Field.Method(
    lambda row: expandProtocols(row.transmitter.protocol)
)

###############################################
## MODEL

db.define_table('model'
                , Field('name', type='string', label='Name', comment='The name of the model', required=True, unique=True)
                , Field('modelorigin', type='string', label='Origin', comment='The origin of the model')
                , Field('modelstate', type='reference modelstate', label='State', comment='The state of the model', required=True, default=2)
                , Field('modeltype', type='string', label='Type', comment='The genere of the model')
                , Field('controltype', type='string', label='Control', comment='The type of control')
                , Field('powerplant', type='string', label='Power Plant', comment='What type of power?')
                , Field('description', type='string', label='Description', comment='Details of the model')
                , Field('notes', type='text', label='Details', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes))
                , Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the model (1000px max)', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img])))
                , Field('manufacturer', type='string', label='Manufacturer', comment='Who made the model?')
                , Field('kitnumber', type='string', label='Kit Number', comment="Manufacturer's kit number")
                , Field('kitlocation', type='string', label='Kit/Plan Location', comment='Where the kit/plan is stored')
                , Field('modelcategory', type='string', label='Category', comment='Model category', required=True, default='Non-Model')
                #
                , Field('attr_flight_timer', type='double', label='Flight Timer', comment='The length of the flight timer', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_construction', type='string', label='Construction', comment='What the model is, mainly, made of')
                , Field('attr_cog', type='string', label='CoG', comment='The Center Of Gravity')
                , Field('attr_length', type='double', label='Length', comment='The length', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_width', type='double', label='Width/Beam', comment='The width/beam', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_height', type='double', label='Height', comment='The height', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_weight_oz', type='double', label='Weight', comment='The weight', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))                
                , Field('attr_covering', type='string', label='Covering', comment='The covering type')
                #
                , Field('attr_plane_rem_wings', type='boolean', notnull=True, label='Removable Wings?', comment='Does it have removable wings?')
                , Field('attr_plane_rem_wing_tube', type='boolean', notnull=True, label='Removable Wing Tube?', comment='Does it have a removable wing tube?')
                , Field('attr_plane_rem_struts', type='boolean', notnull=True, label='Removable Struts?', comment='Does it have removable struts?')
                , Field('attr_plane_wingspan_mm', type='double', label='Wingspan', comment='The wingspan (in mm)', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_plane_wingarea', type='double', label='Wingarea', comment='The wing area (in sqin)', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_plane_throw_aileron', type='string', label='Aileron Throw', comment='The aileron throws')
                , Field('attr_plane_throw_elevator', type='string', label='Elevator Throw', comment='The elevator throws')
                , Field('attr_plane_throw_rudder', type='string', label='Rudder Throw', comment='The rudder throws')
                , Field('attr_plane_throw_flap', type='string', label='Flap Throw', comment='The flap throw')
                #
                , Field('attr_rocket_parachute', type='string', label='Parachute', comment='What is the size of the parachute?')
                , Field('attr_rocket_body_tube', type='string', label='Body Tube', comment='What is the size of the body tube?')
                , Field('attr_rocket_motors', type='list:string', label='Motors', comments='Motors, seperated by "|"')
                #
                , Field('attr_boat_draft', type='double', label='Draft', comment='The draft in mm', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))                
                # 
                , Field('attr_sub_ballast', type='string', label='Ballast Type', comment='The ballast type')
                #
                , Field('attr_copter_headtype', type='string', label='Head Type', comment='The type of rotor head')
                , Field('attr_copter_mainrotor_length', type='double', label='Main Rotor Length', comment='The length of the main rotor blades', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_copter_tailrotor_span', type='double', label='Tail Rotor Length', comment='The length of the tail rotor blades', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_copter_tailrotor_drive', type='string', label='Tail Rotor Drive', comment='What drives the tail rotor?')
                , Field('attr_copter_swashplate_type', type='string', label='Swashplate Type', comment="What type of swashplate does it use?")
                , Field('attr_copter_size', type='integer', label='The "Size" of the Heli', comment='What is the common size designation of the heli?', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                , Field('attr_copter_blade_count', type='integer', label='Blade Count', comment='Number of blades per rotor', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                , Field('attr_copter_tailrotor_blade_count', type='integer', label='Tail Blade Count', comment='Number of blades per rotor', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                #
                , Field('attr_multi_rotor_count', type='integer', label='Rotor Count', comment='The number of rotors', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                #
                , Field('attr_car_scale', type='string', label='Vehicle Scale', comment="The scale of the vehicle")
                , Field('attr_car_drive', type='string', label='X Wheel Drive', comment='How many wheels are powered?')
                , Field('attr_car_drivetrain', type='string', label='Drivetrain', comment='What type of drivetrain?')
                , Field('attr_car_bodystyle', type='string', label='Body Style', comment='What is the body style?')
                , Field('attr_car_wheelbase', type='double', label='Wheelbase', comment='The wheelbase', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                #
                , Field('attr_scale', type='string', label='Model Scale', comment='Model scale (1:x)?')
                #
                , Field('haveplans', type='boolean', notnull=True, label='Are plans in hand?')
                , Field('havekit', type='boolean', notnull=True,label='Have kit/model?')
                , Field('configbackup', uploadseparate=True, type='upload', autodelete=True, label='Radio Config', comment='The backup of the radio/receiver configuration')
                , Field('transmitter', type='reference transmitter', label='Transmitter', comment='Which transmitter is this model bound to?')
                , Field('selected', type='boolean', notnull=True, label='Mark Selected', comment='Avoid manual changes', default=False)
                , Field('subjecttype', type='string', label='Model Subject', comment='Is this a scale model?')
                , Field('final_disposition', type='string', label='Final Disposition', comment='How to liquidate the fleet')
                , Field('final_value', type='double', label='Reasonable Value', comment='A reasonable value for the model')
                , Field('fieldnotes', type='text', label='Field Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes))
                , Field('diagram', type='text', label='Diagram Code (.dot)', comment=diagram_comment, represent=lambda id, row: XML(row.diagram))
                # LEGACY MERMAID SCAFFOLDING — see the note near diagram_comment_mermaid_legacy above.
                , Field('diagram_mermaid', type='text', label='Diagram Code (Mermaid) — Legacy', comment=diagram_comment_mermaid_legacy, represent=lambda id, row: XML(row.diagram_mermaid))
                , Field('protocol', type='reference protocol', label='Protocol', comment='The radio protocol used by this model')
                #
                , Field('attr_hardware_os', type='string', label='Operating System', comment='The OS name (e.g. EdgeTX, Windows)')
                , Field('attr_hardware_os_version', type=semver_type, label='OS Version', comment='The OS version (e.g. 2.9.3)')
                , Field('attr_hardware_firmware_version', type=semver_type, label='Radio Firmware Version', comment='The firmware version (e.g. 1.2.3)')
                #
                # HAM Radio
                , Field('attr_radio_freq_low_mhz', type='double', label='Freq Low (MHz)', comment='Lowest transmit/receive frequency in MHz', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_radio_freq_high_mhz', type='double', label='Freq High (MHz)', comment='Highest transmit/receive frequency in MHz', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_radio_power_w', type='double', label='Max Power (W)', comment='Maximum transmit power in watts', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_radio_mode', type='string', label='Modes', comment='Supported operating modes (e.g. FM, SSB, AM, CW, Digital)')
                , Field('attr_radio_bands', type='string', label='Bands', comment='Supported bands (e.g. 2m/70cm, HF/VHF/UHF)')
                , Field('attr_radio_memory_ch', type='integer', label='Memory Channels', comment='Number of programmable memory channels', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                , Field('attr_radio_rf_connector', type='string', label='RF Connector', comment='RF output connector type (e.g. SO-239, BNC, SMA)')
                , Field('attr_radio_aprs', type='boolean', notnull=True, default=False, label='APRS Capable?', comment='Does this radio support APRS position reporting?')
                , Field('attr_radio_dstar', type='boolean', notnull=True, default=False, label='D-STAR Capable?', comment='Does this radio support D-STAR digital voice mode?')
                , Field('attr_radio_dmr', type='boolean', notnull=True, default=False, label='DMR Capable?', comment='Does this radio support DMR digital mode?')
                #
                # Antenna
                , Field('attr_antenna_type', type='string', label='Antenna Type', comment='Antenna design (e.g. Yagi, Vertical, Dipole, Beam)')
                , Field('attr_antenna_gain_dbi', type='double', label='Gain (dBi)', comment='Antenna gain referenced to isotropic, in dBi', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_antenna_freq_low_mhz', type='double', label='Freq Low (MHz)', comment='Lowest operational frequency in MHz', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_antenna_freq_high_mhz', type='double', label='Freq High (MHz)', comment='Highest operational frequency in MHz', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_antenna_max_power_w', type='double', label='Max Power (W)', comment='Maximum continuous power handling in watts', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'))
                , Field('attr_antenna_impedance_ohm', type='integer', label='Impedance (Ohm)', comment='Feed impedance in ohms - typically 50 or 75', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                , Field('attr_antenna_connector', type='string', label='Connector', comment='RF connector on the antenna feed point')
                , Field('attr_antenna_polarization', type='string', label='Polarization', comment='Antenna polarization (Vertical, Horizontal, Circular)')
                , Field('attr_antenna_mount', type='string', label='Mount Type', comment='How/where the antenna is mounted (Mobile, Base, Portable, Tower, etc.)')
                , Field('attr_antenna_elements', type='integer', label='Element Count', comment='Number of elements - relevant for Yagi and beam antennas', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))

                , format=lambda row: row.name
                )


db.model.get_wingspan = Field.Method(
    lambda row: ZeroDecimal(row.model.attr_plane_wingspan_mm)
)
db.model.get_wingspan.label = 'Wingspan (mm)'

db.model.get_length = Field.Method(
    lambda row: ZeroDecimal(row.model.attr_length)
)
db.model.get_length.label = 'Length'

def get_greatest_length(model):
    return max(model.attr_length or 0, model.attr_width or 0, model.attr_height or 0)
def get_major_dimension(model_id):
    model = db(db.model.id == model_id).select().first()

    if model.attr_scale:
        return 'scale ' + str(model.attr_scale)
    
    if model.modeltype == 'Helicopter' and model.attr_copter_size:
        return str(model.attr_copter_size) + " size"

    dim = 0
    match model.modeltype:
        case 'Airplane': dim = TwoDecimal(model.attr_plane_wingspan_mm) or '---'
        case 'Rocket': dim = TwoDecimal(model.attr_length) or '---'
        case 'Boat': dim = TwoDecimal(model.attr_length) or '---'
        case 'Helicopter' | 'Multirotor': 
            if model.attr_copter_size:
                dim = TwoDecimal(model.attr_copter_size)
            elif model.attr_copter_mainrotor_length:
                dim = TwoDecimal(model.attr_copter_mainrotor_length)
            else:
                dim = '---'
        case 'Car': dim = TwoDecimal(model.attr_length) or '---'
        case 'Autogyro': dim = TwoDecimal(model.attr_copter_mainrotor_length) or '---'
        case 'Submarine': dim = TwoDecimal(model.attr_length) or '---'
        case 'Train': dim = TwoDecimal(model.attr_length) or '---'
        case _: dim = get_greatest_length(model) or '---'

    if dim != '---':
        return str(dim) + 'mm'
    
    return dim
db.model.get_major_dimension = Field.Method( lambda row: get_major_dimension(row.model.id) )
db.model.get_major_dimension.label = 'Major Dimension'

db.model.search = Field.Method(lambda row: row.name)
db.model.search.label = 'Search'

def get_motor_component(model_id):
    components = models_and_components(db.model.id == model_id) 
    
    ret = None
    for c in components.select():
        if c.component.componenttype == 'Motor':
            ret = c.model_component.component

    return ret
db.model.get_motor = Field.Method(lambda row: get_motor_component(row.model.id) )
db.model.get_motor.label = 'Motor'

def get_receiver_component(model_id):
    components = models_and_components(db.model.id == model_id)

    for c in components.select():
        if c.component.componenttype == 'Receiver':
            return c.model_component.component
db.model.get_receiver = Field.Method(lambda row: get_receiver_component(row.model.id) )
db.model.get_receiver.label = 'Receiver'

def has_radio_backup(model_id):
    model = db(db.model.id == model_id).select().first()
    if model.transmitter is None:
        return 'NA'
    tx = db.transmitter(model.transmitter)
    if not tx or not tx.can_export_config:
        return 'NA'
    if model.configbackup and len(model.configbackup) > 0:
        return 'Yes'
    return 'No'
db.model.get_radio_config_backedup = Field.Method( lambda row: has_radio_backup(row.model.id) )
db.model.get_radio_config_backedup.label = 'Config Backed Up'

def _model_has_integrity_issues(model_id):
    import json as _json
    def _safe_parse(s):
        try:
            return _json.loads(s or '{}')
        except (ValueError, TypeError):
            return {}
    model = db.model(model_id)
    if not model or model.modelstate <= 3:
        return False
    mt_row = db((db.lookup.category == 'modeltype') & (db.lookup.name == model.modeltype)).select().first()
    cat_row = db((db.lookup.category == 'modelcategory') & (db.lookup.name == model.modelcategory)).select().first()
    if mt_row and cat_row:
        mt_imp = set(_safe_parse(mt_row.metadata).get('important', []))
        cat_imp = set(_safe_parse(cat_row.metadata).get('important', []))
        for f in (mt_imp & cat_imp):
            if f != 'configbackup' and not model[f]:
                return True
    if model.transmitter:
        tx = db.transmitter(model.transmitter)
        if tx and tx.can_export_config and not model.configbackup:
            return True
    return False
db.model.has_integrity_issues = Field.Method(lambda row: _model_has_integrity_issues(row.model.id))

def model_battery_count(model_id):
    batteries = models_and_batteries(db.model.id == model_id).select()
    count = 0
    for m_b in batteries:
        count = count + m_b.battery.ownedcount
    return count
db.model.get_batterycount = Field.Method( lambda row: model_battery_count(row.model.id) )
db.model.get_batterycount.label = 'Battery Count'

def model_battery_list(model_id):
    batts = []
    batteries = models_and_batteries(db.model.id == model_id).select()
    for b in batteries:
        name = str(b.battery.cellcount) + "s" + \
            str(b.battery.mah) + " " + str(b.battery.chemistry)
        if name not in batts:
            batts.append(name)
    return batts
db.model.get_batterylist = Field.Method( lambda row: model_battery_list(row.model.id) )
db.model.get_batterylist.label = 'Battery List'

def model_sailrig_count(model_id):
    return db(db.sailrig.model == model_id).count()
db.model.get_sailrigcount = Field.Method( lambda row: model_sailrig_count(row.model.id) )
db.model.get_sailrigcount.label = 'Sailrig Count'

def model_sailrig_list(model_id):
    rigs = []
    m_r = db(db.sailrig.model == model_id).select()

    for r in m_r:
        rigs.append(r.rigname)
    return rigs
db.model.get_sailrig_list = Field.Method( lambda row: model_sailrig_list(row.model.id) )
db.model.get_sailrig_list.label = 'Sailrig List'

def model_component_count(model_id):
    return models_and_components(db.model.id == model_id).count()
db.model.get_componentcount = Field.Method( lambda row: model_component_count(row.model.id) )
db.model.get_componentcount.label = 'Component Count'

def model_tool_count(model_id):
    return models_and_tools(db.model.id == model_id).count()
db.model.get_toolcount = Field.Method( lambda row: model_tool_count(row.model.id) )
db.model.get_toolcount.label = 'Tool Count'

def model_switch_count(model_id):
    return db(db.switch.model == model_id).count()
db.model.get_switchcount = Field.Method( lambda row: model_switch_count(row.model.id) )
db.model.get_switchcount.label = 'Switch Count'

def model_note_count(model_id):
    return db((db.activity.model == model_id) & (db.activity.activitytype == 'Note')).count()
db.model.get_notecount = Field.Method( lambda row: model_note_count(row.model.id) )
db.model.get_notecount.label = 'Note Count'

def model_attachment_count(model_id):
    return db(db.attachment.model == model_id).count()
db.model.get_attachmentcount = Field.Method( lambda row: model_attachment_count(row.model.id) )
db.model.get_attachmentcount.label = 'Attachment Count'

db.model.get_opentodocount = Field.Method(
    lambda row: db((db.todo.model == row.model.id) &
                   (db.todo.complete == False)).count()
)
db.model.get_opentodocount.label = 'Open Todo Count'

db.model.get_activitycount = Field.Method( lambda row: db(db.activity.model == row.model.id).count() )
db.model.get_activitycount.label = 'Activity Count'

db.model.get_flightcount = Field.Method(
    lambda row: db(
        (db.activity.model == row.model.id) &
        (db.activity.activitytype == 'Flight')
    ).count()
)
db.model.get_flightcount.label = 'Flight Count'

db.model.attr_length.extra = {'measurement': 'mm'}
db.model.attr_width.extra = {'measurement': 'mm'}
db.model.attr_height.extra = {'measurement': 'mm'}
db.model.attr_weight_oz.extra = {'measurement': 'oz'}
db.model.attr_plane_wingspan_mm.extra = {'measurement': 'mm'}
db.model.attr_plane_wingarea.extra = {'measurement': 'sqin'}
db.model.attr_boat_draft.extra = {'measurement': 'mm'}
db.model.attr_copter_mainrotor_length.extra = {'measurement': 'mm'}
db.model.attr_copter_tailrotor_span.extra = {'measurement': 'mm'}
db.model.attr_car_wheelbase.extra = {'measurement': 'mm'}

db.model.modelcategory.requires = lookup_set('modelcategory')
db.model.modeltype.requires = lookup_set('modeltype')
db.model.modelorigin.requires = lookup_set('modelorigin', empty_ok=True)
db.model.controltype.requires = lookup_set('controltype', empty_ok=True)
db.model.powerplant.requires = lookup_set('powerplant', empty_ok=True)
db.model.attr_construction.requires = lookup_set('attr_construction', empty_ok=True)
db.model.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))
db.model.attr_copter_headtype.requires = lookup_set('attr_copter_headtype', empty_ok=True)
db.model.attr_copter_tailrotor_drive.requires = lookup_set('attr_copter_tailrotor_drive', empty_ok=True)
db.model.subjecttype.requires = lookup_set('subjecttype', empty_ok=True)
db.model.attr_car_bodystyle.requires = lookup_set('attr_car_bodystyle', empty_ok=True)
db.model.attr_car_drive.requires = lookup_set('attr_car_drive', empty_ok=True)
db.model.attr_car_drivetrain.requires = lookup_set('attr_car_drivetrain', empty_ok=True)
db.model.attr_sub_ballast.requires = lookup_set('attr_sub_ballast', empty_ok=True)

db.model.attr_radio_mode.requires           = lookup_set('attr_radio_mode', empty_ok=True)
db.model.attr_radio_rf_connector.requires   = lookup_set('attr_rf_connector', empty_ok=True)
db.model.attr_antenna_type.requires         = lookup_set('attr_antenna_type', empty_ok=True)
db.model.attr_antenna_connector.requires    = lookup_set('attr_rf_connector', empty_ok=True)
db.model.attr_antenna_polarization.requires = lookup_set('attr_antenna_polarization', empty_ok=True)
db.model.attr_antenna_mount.requires        = lookup_set('attr_antenna_mount', empty_ok=True)

db.model.notes.format = lambda model: MARKMIN(model.notes)

# NB: img.default deliberately stays '' (set on the Field itself). Do NOT point
# it at static/images/defaultUpload.png. Field(default='path/to/file') is a real
# web2py feature, but the path it stores is not servable here: everything renders
# through default/download, which only accepts table.field.uuid.name.ext, so the
# path 404s. Worse, every upload field here is uploadseparate+autodelete, and
# pydal's delete_uploaded_files splits the old value on '.' and reads items[2] —
# a path has too few parts, so the first update that added a real image crashed
# with IndexError. The fallback lives in default/download() instead.

db.model.attr_covering.widget = SQLFORM.widgets.autocomplete(
    request, db.model.attr_covering, limitby=(0, 10), min_length=2, distinct=True)

db.model.manufacturer.widget = SQLFORM.widgets.autocomplete(
    request, db.model.manufacturer, limitby=(0, 10), min_length=2, distinct=True)

# Full set of card controllers. Used as the pass-through default when a
# modeltype has no controllers configured (empty list = no type-level restriction).
_ALL_CONTROLLERS = frozenset([
    'attachment', 'battery', 'component', 'diagram', 'model_model', 'paint',
    'propeller', 'radio_channel', 'rotor', 'sailrig', 'supportitem', 'switch', 'tool', 'wtc',
])

# Which nav-tab controllers are shown for each model type.
# Seeds new modeltype DB entries only — the admin UI is the source of truth for existing rows.
modeltype_controller_mapping = {
    'Airplane'    : ['attachment', 'battery', 'component', 'diagram', 'paint', 'propeller', 'supportitem', 'switch', 'tool'],
    'Rocket'      : ['attachment', 'component', 'diagram', 'paint', 'supportitem', 'tool'],
    'Boat'        : ['attachment', 'battery', 'component', 'diagram', 'paint', 'propeller', 'sailrig', 'supportitem', 'switch', 'tool'],
    'Helicopter'  : ['attachment', 'battery', 'component', 'diagram', 'paint', 'rotor', 'supportitem', 'switch', 'tool'],
    'Multirotor'  : ['attachment', 'battery', 'component', 'diagram', 'paint', 'rotor', 'supportitem', 'switch', 'tool'],
    'Robot'       : ['attachment', 'battery', 'component', 'diagram', 'paint', 'supportitem', 'switch', 'tool'],
    'Experimental': ['attachment', 'battery', 'component', 'diagram', 'paint', 'propeller', 'rotor', 'sailrig', 'supportitem', 'switch', 'tool', 'wtc'],
    'Car'         : ['attachment', 'battery', 'component', 'diagram', 'paint', 'supportitem', 'switch', 'tool'],
    'Autogyro'    : ['attachment', 'battery', 'component', 'diagram', 'paint', 'propeller', 'rotor', 'supportitem', 'switch', 'tool'],
    'Submarine'   : ['attachment', 'battery', 'component', 'diagram', 'paint', 'propeller', 'supportitem', 'switch', 'tool', 'wtc'],
    'Non-Model'   : ['attachment', 'component', 'supportitem', 'tool'],
    'Miniature'   : ['attachment', 'battery', 'component', 'paint', 'supportitem', 'tool'],
    'Train'       : ['attachment', 'battery', 'component', 'diagram', 'paint', 'supportitem', 'switch', 'tool'],
    'Other'       : ['attachment', 'battery', 'component', 'diagram', 'paint', 'supportitem', 'switch', 'tool'],
    'HAM Radio'   : ['attachment', 'battery', 'component', 'model_model', 'radio_channel', 'supportitem', 'tool'],
    'Antenna'     : ['attachment', 'component', 'model_model', 'supportitem', 'tool'],
}

# Fields that are not editable when a modeltype is selected
# This list seeds new modeltype DB entries only — the admin is the source of truth.
modeltype_hide_attribs = {
    'Airplane'    : [],
    'Rocket'      : ['controltype', 'attr_covering'],
    'Boat'        : ['attr_covering'],
    'Helicopter'  : ['attr_covering'],
    'Multirotor'  : ['attr_covering'],
    'Robot'       : ['attr_covering'],
    'Experimental': [],
    'Car'         : ['attr_cog', 'attr_covering'],
    'Autogyro'    : [],
    'Submarine'   : ['attr_covering'],
    'Non-Model'   : ['controltype', 'powerplant', 'attr_flight_timer', 'attr_cog',
                     'attr_covering', 'configbackup', 'transmitter', 'protocol'],
    'Miniature'   : ['controltype', 'powerplant', 'attr_flight_timer', 'attr_cog',
                     'attr_covering', 'configbackup', 'transmitter', 'protocol'],
    'Train'       : ['attr_cog', 'attr_covering', 'configbackup'],
    'Other'       : [],
    'HAM Radio'   : ['controltype', 'powerplant', 'attr_flight_timer', 'attr_cog', 'attr_covering',
                     'configbackup', 'transmitter', 'protocol',
                     'attr_antenna_type', 'attr_antenna_gain_dbi', 'attr_antenna_freq_low_mhz',
                     'attr_antenna_freq_high_mhz', 'attr_antenna_max_power_w',
                     'attr_antenna_impedance_ohm', 'attr_antenna_connector',
                     'attr_antenna_polarization', 'attr_antenna_mount', 'attr_antenna_elements'],
    'Antenna'     : ['controltype', 'powerplant', 'attr_flight_timer', 'attr_cog', 'attr_covering',
                     'configbackup', 'transmitter', 'protocol',
                     'attr_hardware_os', 'attr_hardware_os_version', 'attr_hardware_firmware_version',
                     'attr_radio_freq_low_mhz', 'attr_radio_freq_high_mhz', 'attr_radio_power_w',
                     'attr_radio_mode', 'attr_radio_bands', 'attr_radio_memory_ch',
                     'attr_radio_rf_connector', 'attr_radio_aprs', 'attr_radio_dstar', 'attr_radio_dmr'],
}

# Fields that are not editable when a modelcategory is selected
# This list must be updated if a new modelcategory is added
modelcategory_hide_attribs = {
    'Remote Control' : [], 
    'Dynamic' : [],
    'Static' : [
        'controltype', 
        'powerplant', 
        'attr_flight_timer', 
        'attr_cog',
        'attr_boat_draft',
        'attr_sub_ballast',
        'attr_copter_swashplate_type',
        'configbackup',
        'transmitter',
        'protocol'
        ], 
    'Non-Model' : [
        'controltype', 
        'powerplant', 
        'attr_cog', 
        'attr_plane_rem_wings', 
        'attr_plane_rem_wing_tube',
        'attr_plane_rem_struts',
        'attr_boat_draft',
        'attr_sub_ballast',
        'attr_copter_swashplate_type',
        'configbackup',
        'transmitter',
        'protocol'
        ]
}



###############################################
## RADIO CHANNEL

db.define_table('radio_channel',
                Field('model',         type='reference model', label='Model', required=True),
                Field('channel_num',   type='integer', label='Channel #', comment='Memory slot number (0-based, as exported by CHIRP)', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')),
                Field('name',          type='string', label='Name', comment='Channel name (up to 8 characters)'),
                Field('frequency_mhz', type='double', label='Frequency (MHz)', comment='Receive frequency in MHz', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('duplex',        type='string', label='Duplex', comment='Duplex shift: blank=simplex, +=plus offset, -=minus offset, split=split'),
                Field('offset_mhz',    type='double', label='Offset (MHz)', comment='Transmit offset in MHz (for repeaters)', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('tone_mode',     type='string', label='Tone Mode', comment='CTCSS/DCS tone mode (Tone, TSQL, DTCS, Cross, or blank)'),
                Field('ctcss_freq',    type='double', label='CTCSS Tone (Hz)', comment='CTCSS tone frequency in Hz (e.g. 88.5, 100.0, 127.3)', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('dtcs_code',     type='string', label='DCS Code', comment='DCS/DTCS code (e.g. 023, 025, 432)'),
                Field('channel_mode',   type='string', label='Mode', comment='Operating mode (FM, NFM, AM, WFM, DV)'),
                Field('skip',          type='boolean', notnull=True, default=False, label='Skip?', comment='Skip this channel during scanning'),
                Field('channel_comment', type='string', label='Comment', comment='Free-text channel comment'),
                format=lambda row: f'Ch{row.channel_num}: {row.name or ""} ({row.frequency_mhz} MHz)'
                )

db.radio_channel.duplex.requires    = IS_EMPTY_OR(IS_IN_SET(['', '+', '-', 'split', 'off']))
db.radio_channel.tone_mode.requires = IS_EMPTY_OR(IS_IN_SET(['', 'Tone', 'TSQL', 'DTCS', 'Cross', 'DTCS-R', 'Tone->DTCS']))
db.radio_channel.channel_mode.requires = IS_EMPTY_OR(IS_IN_SET(['FM', 'NFM', 'AM', 'WFM', 'DV']))


###############################################
## MODEL ↔ MODEL (related models, undirected many-to-many)

db.define_table('model_model',
                Field('model_a', type='reference model', label='Model', required=True),
                Field('model_b', type='reference model', label='Related Model', required=True),
                Field('notes',   type='string', label='Notes'),
                format=lambda row: f'{row.model_a} ↔ {row.model_b}'
                )

db.model_model.model_b.requires = IS_IN_DB(
    db, 'model.id',
    lambda r: f'{r.name} ({r.modeltype})',
    zero='-- select model --'
)


###############################################
## TODO

db.define_table('todo',
                Field('todo', type='string', label='To Do', required=True), 
                Field('model', type='reference model'), 
                Field('critical', type='boolean', default=False, comment='Does this prevent the model from operating?'), 
                Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)), 
                Field('complete', type='boolean', label="Complete?", default=False), 
                format=lambda row: 'Unknown' if row is None else row.todo)

db.todo.notes.format = lambda tool: MARKMIN(tool.notes)


###############################################
## ACTIVITY

db.define_table('activity', 
                Field('activitydate', type='date', label='Date', required=True, default=request.now), 
                Field('model', type='reference model', label='Model'), 
                Field('activitytype', type='string', label='Type'), 
                Field('duration', type='double', label='Duration (min)', comment='The duration, in minutes', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')), 
                Field('activitylocation', type='string', label='Location'), 
                Field('notes', type='text', label='Notes', comment='Notes about the event'), 
                Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the activity (1500px max)', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))),
                format=lambda row: 'Unknown' if row is None else f'{row.activitydate}: {row.activitytype or "Activity"}'
                )

db.activity.activitytype.requires = lookup_set('activitytype')
db.activity.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1500, 1500)))

db.activity.activitylocation.widget = SQLFORM.widgets.autocomplete(
    request, db.activity.activitylocation, limitby=(0, 10), min_length=2, distinct=True)

db.activity.notes.format = lambda model: MARKMIN(model.notes)


###############################################
## COMPONENT

db.define_table('component', 
                Field('name', type='string', label='Name', required=True, unique=True), 
                Field('serial', type='string', label='Serial Number'), 
                Field('diagramname', type='string', label='Diagram Name', comment='The name used in the diagram', required=False, unique=False),
                Field('customdot', type='string', label='Custom .dot Code', comment='Custom .dot code for diagrams', required=False, unique=False),
                # Tri-state rather than boolean: '' means "inherit from the
                # componenttype", which is what makes this a hierarchy instead of
                # two independent switches. A boolean could not distinguish
                # "not specified" from "explicitly no".
                Field('diagram_is_record', type='string', label='Port Record', default='',
                      requires=IS_IN_SET([('', 'Inherit from type'), ('yes', 'Yes'), ('no', 'No')], zero=None),
                      comment='Render as a record with individually connectable ports'),
                Field('componenttype', type='string', label='Type', comment='The type of component', required=True), 
                Field('componentsubtype', type='string', label='Subtype', comment='The Sub Type'), 
                Field('ownedcount', type='integer', label='Count', comment='How many are owned?', default=0, widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')), 
                Field('significantdetail', type='string', label='Significant Detail', comment='A significant detail of this component'), 
                Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)), 
                Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the component (1000px max)', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))), 
                Field('attachment', uploadseparate=True, type='upload', autodelete=True, label='Attachment', comment='More info'), 
                Field('storedat', type='string', label='Location', comment='Where is this component stored?'),
                Field('attr_length', type='double', label='Length', comment='The length', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('attr_width', type='double', label='Width/Beam', comment='The width/beam', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('attr_height', type='double', label='Height', comment='The height', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('attr_weight_oz', type='double', label='Weight', comment='The weight', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),               
                #
                Field('attr_channel_count', type='integer', label='Channel Count', comment='Number of channels', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')),
                Field('attr_telemetry_port', type='boolean', notnull=True, label='Telemetry Port', comment='This component has a telemetry port'),
                Field('attr_sbus_port', type='boolean', notnull=True, label='SBUS Port', comment='This component has an SBUS port'),
                Field('attr_pwr_port', type='boolean', notnull=True, label='Power Port', comment='This component has an power port'),
                Field('attr_protocol', type='reference protocol', label='Protocol', comment='The radio protocol used by this model'),
                Field('attr_gear_type', type='string', label='Gear Type', comment='The material the gears are made of'),
                Field('attr_amps_in', type='double', label='Rated Amps In', comment='The rated input amps'),
                Field('attr_amps_out', type='double', label='Rated Amps Out', comment='The rated output amps'),
                Field('attr_torque', type='string', label="Rated Torque", comment='The rated torque'),
                Field('attr_switch_type', type='string', label='Switch Type', comment='The type of switch'),
                Field('attr_displacement_cc', type='double', label='Displacement (cc)', comment='The engine displacement', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('attr_motor_kv', type='integer', label='Motor KV', comment='The motor KV rating'),              
                Field('attr_voltage_in', type='double', label='Max Voltage In', comment='The maximum voltage in'),
                Field('attr_voltage_out', type='double', label='Max Voltage Out', comment='The maximum voltage out'),
                Field('attr_num_turns', type='integer', label='Number of Turns', comment='The number of rotations'),
                Field('attr_watts_in', type='double', label='Max Watts In', comment='The maximum watts in'),
                Field('attr_watts_out', type='double', label='Max Watts Out', comment='The maximum watts out'),
                Field('attr_pump_type', type='string', label='Pump Type', comment='The type of pump'),
                Field('attr_travel', type='double', label='Travel', comment='The travel distance', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('attr_model_scale', type='string', label='Model Scale', comment='The model scale the component is for (1:x)?'),
                Field('attr_firmware_version', type=semver_type, label='Firmware Version', comment='The firmware version of the component (e.g. 1.2.3)'),
                #
                # RF / Radio
                Field('attr_freq_low_mhz', type='double', label='Freq Low (MHz)', comment='Minimum operational frequency in MHz', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('attr_freq_high_mhz', type='double', label='Freq High (MHz)', comment='Maximum operational frequency in MHz', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('attr_max_power_w', type='double', label='Max Power (W)', comment='Maximum RF power handling in watts', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('attr_rf_connector', type='string', label='RF Connector', comment='RF connector type (e.g. SO-239, BNC, SMA, N-Type)'),
                #
                Field('manufacturer', type='string', label='Manufacturer', comment='Who made the component?'),
                Field('model', type='string', label='Model', comment='The model of the component'),
                #
                format=lambda row: 'Unknown' if row is None else row.name
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
db.component.get_usedcount.label = 'Used Count'

db.component.get_remainingcount = Field.Method(
    lambda row: row.component.ownedcount - row.component.get_usedcount()
)
db.component.get_remainingcount.label = 'Remaining Count'

db.component.showAttachmentPopup = Field.Method(
    lambda row: AttachPopup(row.component.attachment)
)
db.component.showAttachmentPopup.label = 'Attachment'

db.component.attr_length.extra = {'measurement': 'mm'}
db.component.attr_width.extra = {'measurement': 'mm'}
db.component.attr_height.extra = {'measurement': 'mm'}
db.component.attr_weight_oz.extra = {'measurement': 'oz'}
db.component.attr_displacement_cc.extra = {'measurement': 'cc'}
db.component.attr_travel.extra = {'measurement': 'mm'}

# See the note on db.model.img above: no path default here either.

db.component.attr_pump_type.requires    = lookup_set('attr_pump_type', empty_ok=True)
db.component.attr_rf_connector.requires = lookup_set('attr_rf_connector', empty_ok=True)

db.component.componenttype.requires = IS_IN_SET(
    [r.name for r in db(db.componenttype.id > 0).select(
        db.componenttype.name, orderby=db.componenttype.sort_order | db.componenttype.name)],
    zero=None)

component_attribs = {
    'Engine': ['attr_displacement_cc'], 
    'Servo': ['attr_voltage_in','attr_gear_type', 'attr_torque'], 
    'Receiver': ['attr_voltage_in','attr_channel_count', 'attr_telemetry_port', 'attr_sbus_port', 'attr_pwr_port', 'attr_protocol','attr_firmware_version'], 
    'Motor': ['attr_motor_kv', 'attr_amps_in', 'attr_amps_out', 'attr_voltage_in','attr_voltage_out', 'attr_watts_in', 'attr_watts_out'], 
    'ESC': ['attr_amps_in', 'attr_amps_out', 'attr_voltage_in','attr_voltage_out', 'attr_watts_in', 'attr_watts_out','attr_firmware_version'], 
    'BEC': ['attr_amps_in', 'attr_amps_out', 'attr_voltage_in','attr_voltage_out', 'attr_watts_in', 'attr_watts_out'], 
    'Regulator': ['attr_amps_in', 'attr_amps_out', 'attr_voltage_in','attr_voltage_out', 'attr_watts_in', 'attr_watts_out'], 
    'Flight Controller': ['attr_amps_in', 'attr_voltage_in','attr_channel_count', 'attr_telemetry_port', 'attr_sbus_port', 'attr_pwr_port', 'attr_protocol','attr_firmware_version'], 
    'Gyro': ['attr_voltage_in'], 
    'Battery Charger': ['attr_channel_count','attr_amps_in','attr_voltage_in', 'attr_watts_in','attr_amps_out','attr_voltage_out', 'attr_watts_out','attr_firmware_version'], 
    'Flybarless Controller': ['attr_voltage_in','attr_channel_count', 'attr_telemetry_port', 'attr_sbus_port', 'attr_pwr_port', 'attr_protocol','attr_firmware_version' ], 
    'Electrical': ['attr_amps_in','attr_voltage_in','attr_amps_out','attr_voltage_out'], 
    'Switch': ['attr_switch_type','attr_voltage_in'], 
    'Winch': ['attr_voltage_in', 'attr_num_turns'], 
    'Other': ['attr_amps_in', 'attr_amps_out', 'attr_voltage_in','attr_voltage_out', 'attr_watts_in', 'attr_watts_out','attr_firmware_version'],
    'Retracts': ['attr_voltage_in'],
    'Pump': ['attr_voltage_in','attr_amps_in','attr_amps_out', 'attr_pump_type'],
    'Sensor': ['attr_voltage_in','attr_amps_in','attr_firmware_version'],
    'Tire': ['attr_model_scale'],
    'Shock': ['attr_travel'],
    'SWR/Power Meter' : ['attr_freq_low_mhz', 'attr_freq_high_mhz', 'attr_max_power_w', 'attr_rf_connector'],
    'Antenna Tuner'   : ['attr_freq_low_mhz', 'attr_freq_high_mhz', 'attr_max_power_w', 'attr_voltage_in', 'attr_rf_connector', 'attr_firmware_version'],
    'Coaxial Cable'   : ['attr_freq_high_mhz', 'attr_rf_connector', 'attr_length'],
    'TNC'             : ['attr_voltage_in', 'attr_firmware_version'],
    'Rotator'         : ['attr_voltage_in', 'attr_watts_in'],
}

db.component.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))
db.component.attr_firmware_version.requires = IS_EMPTY_OR(
    IS_MATCH(r'^\d+(\.\d+){0,2}$', error_message='Format: major.minor.patch (e.g. 1.2.3)'))

if not _migration_applied('semver_encode_component_version_v1'):
    for _row in db((db.component.attr_firmware_version != None) &
                   (db.component.attr_firmware_version != '')).select(
                       db.component.id, db.component.attr_firmware_version):
        _enc = _semver_encode(_row.attr_firmware_version)
        if _enc and _enc != _row.attr_firmware_version:
            db(db.component.id == _row.id).update(attr_firmware_version=_enc)
    _mark_migration('semver_encode_component_version_v1')

db.component.componentsubtype.widget = SQLFORM.widgets.autocomplete(
    request, db.component.componentsubtype, limitby=(0, 10), min_length=2, distinct=True)
db.component.storedat.widget = SQLFORM.widgets.autocomplete(
    request, db.component.storedat, limitby=(0, 10), min_length=2, distinct=True)
db.component.attr_gear_type.widget = SQLFORM.widgets.autocomplete(
    request, db.component.attr_gear_type, limitby=(0, 10), min_length=2, distinct=True)
db.component.attr_switch_type.widget = SQLFORM.widgets.autocomplete(
    request, db.component.attr_switch_type, limitby=(0, 10), min_length=2, distinct=True)
db.component.manufacturer.widget = SQLFORM.widgets.autocomplete(
    request, db.component.manufacturer, limitby=(0, 10), min_length=1, distinct=True)

db.component.notes.format = lambda component: MARKMIN(component.notes)


###############################################
## MODEL COMPONENT

db.define_table('model_component'
                , Field('model', type='reference model', label='Model')
                , Field('component', type='reference component', label='Component')
                , Field('purpose', type='string', label='Purpose', comment='Purpose of this component', represent=lambda v, r: '' if v is None else v)
                , Field('channel', type='integer', label='Channel', comment='Channel Assignment', represent=lambda v, r: '' if v is None else v, widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control'))
                , Field('note', type='string', label='Comment', comment='Optional note shown on the wiring diagram', represent=lambda v, r: '' if v is None else v)
                )

db.model_component.modelstate = Field.Virtual(
    lambda row: row.model.modelstate.id)

db.model_component.component.widget = component_select_widget

db.model_component.purpose.widget = SQLFORM.widgets.autocomplete(
    request, db.model_component.purpose, limitby=(0, 10), min_length=1, distinct=True)

models_and_components = db(
    (db.model.id == db.model_component.model)
    &
    (db.component.id == db.model_component.component)
)

###############################################
## TOOL

db.define_table('tool', 
                Field('name', type='string', label='Name', required=True, unique=True), 
                Field('tooltype', type='string', label='Type'), 
                Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)), 
                Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the tool (1000px max)', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))), 
                Field('attachment', uploadseparate=True, type='upload', autodelete=True, label='Attachment', comment='Manual'), format=lambda row: 'Unknown' if row is None else row.tooltype + ': ' + row.name
                )

db.tool.tooltype.requires = lookup_set('tooltype')
db.tool.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))

db.tool.notes.format = lambda tool: MARKMIN(tool.notes)


###############################################
## MODEL TOOL

db.define_table('model_tool', 
                Field('model', type='reference model', label='Model'), 
                Field('tool', type='reference tool', label='Tool'),
                Field('purpose', type='string', label='Purpose')
                )

db.model_tool.tool.requires = IS_IN_DB(
    db, 'tool.id', label=db.tool._format, sort=True)

models_and_tools = db(
    (db.model.id == db.model_tool.model)
    &
    (db.tool.id == db.model_tool.tool)
)

###############################################
## BATTERY

db.define_table('battery', 
                Field('cellcount', type='integer', label='Cell Count', comment="Number of cells in the pack", required=True, widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')), 
                Field('mah', type='integer', label='mAh', required=True, widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _class='generic-widget form-control')), 
                Field('chemistry', required=True), 
                Field('crating', type='integer', label='C Rating', required=True, widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')), 
                Field('ownedcount', type='integer', label='Number Owned', comment='How many are owned?', required=True, default=1, widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')), 
                format=lambda row: row.chemistry + ': ' + str(row.cellcount) + 's' + str(row.mah) + ' (' + str(row.crating) + ') '
                )

######################
# Can you add a lable to this? If so, use it in the listview
######################
db.battery.get_name = Field.Method(
    lambda row: str(row.battery.cellcount) + 's' + str(row.battery.mah) +
    ' (' + str(row.battery.crating) + ') ' + row.battery.chemistry
)
db.battery.get_name.label = 'Battery Size'

db.battery.get_maxamps = Field.Method(
    lambda row: (row.battery.crating * row.battery.mah) / 1000
)
db.battery.get_maxamps.label = 'Max Amps'

# Initial fallback — overridden at end of db.py after db.chemistry is populated.
db.battery.chemistry.requires = IS_IN_SET(
    ('LiPo', 'LiFE', 'NiMH', 'NiCad', 'Li-Ion', 'Alkaline', 'SLA'), sort=True)

# Initial fallback — overridden at end of db.py after db.chemistry is populated.
chem_volt = {'LiPo': 3.7, 'LiFE': 3.3, 'NiMH': 1.2, 'NiCad': 1.2, 'Li-Ion': 3.7, 'Alkaline': 1.5, 'SLA': 2.0}
db.battery.voltage = Field.Virtual(
    lambda row: row.battery.cellcount * chem_volt.get(row.battery.chemistry, 0))
db.battery.voltage.label = 'Voltage'

db.battery.name = Field.Virtual(
    lambda row: str(row.battery.cellcount) + 's' + str(row.battery.mah) + ' (' + str(row.battery.crating) + ') ' + row.battery.chemistry)
db.battery.name.label = 'Name'

###############################################
## MODEL BATTERY

db.define_table('model_battery', 
                Field('model', type='reference model', label='Model'), 
                Field('battery', type='reference battery', label='Battery'),
                Field('quantity', type='integer', label='Num required', default=1)
                )
db.model_battery.battery.requires = IS_IN_DB(
    db, 'battery.id', label=db.battery._format, sort=True)

models_and_batteries = db(
    (db.model.id == db.model_battery.model)
    &
    (db.battery.id == db.model_battery.battery)
)

###############################################
## SAIL RIG

db.define_table('sailrig', 
                Field('rigname', type='string', label='Name', comment='e.g. A, B, or C', required=True, unique=False), 
                Field('model', type='reference model', label='Model'), 
                Field('img', type='upload', uploadseparate=True, autodelete=True, label='Picture', comment='The picture of the sail rig', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))), 
                Field('mast_length_mm', type='integer', label='Mast Length', required=False), 
                Field('mast_material', type='string', label='Mast Material', required=False), 
                Field('main_boom_length_mm', type='integer', label='Main Boom Length', required=False), 
                Field('main_boom_material', type='string', label='Main Boom Material', required=False), 
                Field('main_sail_material', type='string', label='Main Sail Material', required=False), 
                Field('main_sail_area_dm2', type='double', label='Main Sail Area', required=False), 
                Field('jib_boom_length_mm', type='integer', label='Jib Boom Length', required=False), 
                Field('jib_boom_material', type='string', label='Jib Boom Material', required=False), 
                Field('jib_sail_material', type='string', label='Jib Sail Material', required=False), 
                Field('jib_sail_area_dm2', type='double', label='Jib Sail Area', required=False), 
                Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)), 
                format=lambda row: 'Unknown' if row is None else row.rigname
                )

db.sailrig.mast_length_mm.extra = {'measurement': 'mm'}
db.sailrig.main_boom_length_mm.extra = {'measurement': 'mm'}
db.sailrig.jib_boom_length_mm.extra = {'measurement': 'mm'}
db.sailrig.main_sail_area_dm2.extra = {'measurement': 'dm2'}
db.sailrig.jib_sail_area_dm2.extra = {'measurement': 'dm2'}


###############################################
## EFLIGHT TIME

db.define_table('eflite_time', 
                Field('model', type='reference model', label='Model', required=True), 
                Field('motor', type='reference component', label='Motor', required=True), 
                Field('battery', type='reference battery', label='Battery', required=True), 
                Field('propeller', type='string', label='Propeller'), 
                Field('amps', type='double', label='Amps Drawn', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'), required=True), 
                Field('watts', type='double', label='Watts Drawn', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control'), required=True)
                )

db.eflite_time.amps.requires = IS_NOT_EMPTY()
db.eflite_time.watts.requires = IS_NOT_EMPTY()

def get_min(mah, amps):
    return ((mah * .8) / (amps * 1000)) * 60
db.eflite_time.get_minutes = Field.Method(
    lambda row: TwoDecimal(
        get_min(row.eflite_time.battery.mah, row.eflite_time.amps))
)
db.eflite_time.get_minutes.label = 'Flight Minutes'

def get_watts_per_pound(row):
    if (not row.eflite_time.model.attr_weight_oz):
        return "No Weight Set"
    return TwoDecimal(row.eflite_time.watts / (row.eflite_time.model.attr_weight_oz * 16))
db.eflite_time.get_wattsperpound = Field.Method(
    lambda row: get_watts_per_pound(
        row)
)
db.eflite_time.get_wattsperpound.label = 'Watts/Pound'

db.eflite_time.is_overrating = Field.Method(
    lambda row: (row.eflite_time.amps > row.eflite_time.battery.get_maxamps())
)
db.eflite_time.is_overrating.label = 'Is Overrating'

###############################################
## SUPPORT ITEM

db.define_table('supportitem', 
                Field('item', type='string', label='Support Item'), 
                Field('model', type='reference model', label='Model'), 
                Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)), 
                Field('img', uploadseparate=True, type='upload', autodelete=True, label='Picture', comment='The picture of the support item (1000px max)', default='', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))), 
                format=lambda row: row.item
                )
db.supportitem.item.widget = SQLFORM.widgets.autocomplete(
    request, db.supportitem.item, limitby=(0, 10), min_length=2, distinct=True)

db.supportitem.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))

###############################################
## PROPELLER

db.define_table('propeller', 
                Field('item', type='string', label='Propeller', required=True), 
                Field('model', type='reference model'), format=lambda row: row.item
                )
db.propeller.item.widget = SQLFORM.widgets.autocomplete(
    request, db.propeller.item, limitby=(0, 10), min_length=2, distinct=True)


###############################################
## ATTACHMENT

db.define_table('attachment', 
                Field('name', type='string', label='Name'), 
                Field('attachmenttype', type='string', label='Type'), 
                Field('model', type='reference model', label='Model'), 
                Field('attachment', uploadseparate=True, type='upload', autodelete=True, label='Attachment', comment='The attachment')
                )

db.attachment.attachmenttype.requires = lookup_set('attachmenttype')



###############################################
## PACKING ITEMS

db.define_table('packingitems', 
                Field('name', type='string', label='Name', required=True), 
                Field('itemtype', type='string', label='Type', required=True)
                )

db.packingitems.itemtype.requires = lookup_set('itemtype')


###############################################
## IMAGES

db.define_table('images', 
                Field('img', type='upload', autodelete=True, uploadseparate=True, required=True, label='Image', comment='The image'), 
                Field('tags', type='list:string', label='Tags', comment='A list of tags')
                )

db.images.img.requires = IS_EMPTY_OR(IS_IMAGE())

###############################################
## WTC

db.define_table('wtc',
                Field('name', type='string', label='Name', required=True, unique=True),
                Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)),
                Field('img', type='upload', uploadseparate=True, autodelete=True, label='Picture', comment='The picture of the WTC (1000px max)', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))),
                Field('make', type='string', label='Make'),
                Field('model', type='string', label='Model'),
                Field('attr_length_mm', type='double', label='Length', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')),
                Field('attr_outer_diameter_mm', type='double', label='Outer Diameter', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')),
                Field('attr_width_mm', type='double', label='Width/Beam', comment='The width/beam', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('attr_height_mm', type='double', label='Height', comment='The height', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('attr_weight_oz', type='double', label='Weight', comment='The weight', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                Field('attr_ballast_capacity', type='double', label='Ballast Capacity', comment='The ballast capacity', widget=lambda field, value: SQLFORM.widgets.double.widget(field, value, _type='number', _step='any', _class='generic-widget form-control')),
                #
                format=lambda row: 'Unknown' if row is None else row.name
                )

db.wtc.attr_length_mm.extra = {'measurement': 'mm'}
db.wtc.attr_outer_diameter_mm.extra = {'measurement': 'mm'}
db.wtc.attr_width_mm.extra = {'measurement': 'mm'}
db.wtc.attr_height_mm.extra = {'measurement': 'mm'}
db.wtc.attr_weight_oz.extra = {'measurement': 'oz'}
db.wtc.attr_ballast_capacity.extra = {'measurement': 'oz'}

db.wtc.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(1000, 1000)))

###############################################
## MODEL WTC

db.define_table('model_wtc', 
                Field('model', type='reference model', label='Model'), 
                Field('wtc',   type='reference wtc', label="Water Tight Cylinder"),
                Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)),
                format=lambda row: 'Unknown' if row is None else row.model.name + " : " + row.wtc.name
                )

models_and_wtcs = db(
    (db.model.id == db.model_wtc.model)
    &
    (db.wtc.id == db.model_wtc.wtc)
)

###############################################
## HARDWARE

db.define_table('hardware',
                Field('model', type='reference model', label='Model', required=True),
                Field('hardwaretype', type='string', label='Type', required=True),
                Field('diameter', type='string', label='Size/Dimensions'),
                Field('length_mm', type='double', label='Length', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')),
                Field('purpose', type='string', label='Purpose'),
                Field('quantity', type='integer', label='Quantity', widget=lambda field, value: SQLFORM.widgets.integer.widget(field, value, _type='number', _class='generic-widget form-control')),
                format=lambda row: row.hardwaretype + " : " + row.diameter + (" x " + str(row.length_mm) if row.length_mm is not None else "")
                )
db.hardware.length_mm.extra = {'measurement': 'mm'}

db.hardware.hardwaretype.requires = lookup_set('hardwaretype')
db.hardware.diameter.widget = SQLFORM.widgets.autocomplete(
    request, db.hardware.diameter, limitby=(0, 10), min_length=1, distinct=True)
db.hardware.purpose.widget = SQLFORM.widgets.autocomplete(
    request, db.hardware.purpose, limitby=(0, 10), min_length=1, distinct=True)

###############################################
## PAINT

db.define_table('paint',
                Field('manufacturer', type='string', label='Manufacturer', required=True),
                Field('brand', type='string', label='Brand'),
                Field('color', type='string', label='Color', required=True),
                Field('colorid', type='string', label='Color ID'),
                Field('notes', type='text', label='Notes', comment=markmin_comment, represent=lambda id, row: MARKMIN(row.notes)),
                Field('colorhex', type='string', label='The HTML/hex code that matches the color'),
                Field('img', type='upload', uploadseparate=True, autodelete=True, label='Image', comment='The image of the paint color (500px max)', represent=lambda id, row: IMG(_src=URL('default', 'download', args=[row.img]))),
                format=lambda row: f"{row.manufacturer} {row.brand or ''} {row.color}" 
                )

db.paint.get_name = Field.Method(
    lambda row: f"{row.paint.manufacturer or 'Unspecified manufacturer'} {row.paint.brand or ''} {row.paint.color or 'Unspecified color'}" 
)
db.paint.get_name.label = 'Name'

db.paint.img.requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(500, 500)))

db.paint.manufacturer.widget = SQLFORM.widgets.autocomplete(
    request, db.paint.manufacturer, limitby=(0, 10), min_length=1, distinct=True)
db.paint.brand.widget = SQLFORM.widgets.autocomplete(
    request, db.paint.brand, limitby=(0, 10), min_length=1, distinct=True)

db.paint.colorhex.extra = {'input': 'color'}

###############################################
## MODEL PAINT

db.define_table('model_paint', 
                Field('model', type='reference model', label='Model', required=True), 
                Field('paint', type='reference paint', label='Paint', required=True),
                Field('purpose', type='string', label='On what part was the paint used?', required=True)
                )
db.model_paint.paint.requires = IS_IN_DB(
    db, 'paint.id', label=db.paint._format, sort=True)

models_and_paints = db(
    (db.model.id == db.model_paint.model)
    &
    (db.paint.id == db.model_paint.paint)
)

###############################################
## URL
db.define_table('url'
            , Field('url', type='string', label='URL', required=True)
            , Field('model', type='reference model', label='Model', required=True)
            , Field('notes', type='string', label='Notes')
            )
db.url.url.requires = IS_URL()
db.url.notes.widget = SQLFORM.widgets.autocomplete(
    request, db.url.notes, limitby=(0, 10), min_length=1, distinct=True)

###############################################
## SWITCH

db.define_table('switch'
                , Field('switch', type='string', label='Switch')
                , Field('model', type='reference model', label='Model')
                , Field('switchtype', type='string', label='Type')
                , Field('purpose',type='string', label='Purpose')
                , format=lambda row: row.model.name + " : " + row.purpose)

db.switch.switchtype.requires = lookup_set('switchtype', empty_ok=True)

db.define_table('switch_position'
                , Field('switch', type='reference switch', label='Switch')
                , Field('pos', type='string', label='Position')
                , Field('func', type='string', label='Function')
                )

db.switch_position.pos.requires = lookup_set('pos', empty_ok=True)

switches_and_positions = db(
    (db.switch.id == db.switch_position.switch)
)

###############################################
## TRANSMITTER SWITCH (v2 switch system)

db.define_table('transmitter_switch',
    Field('transmitter', 'reference transmitter', label='Transmitter', required=True),
    Field('name',        'string',  label='Name',       comment='e.g. SA, SB, T1, T2'),
    Field('switchtype',  'string',  label='Type'),
    Field('x',           'double',  label='X (%)',      default=50.0,
          comment='Horizontal position on layout canvas (0-100)'),
    Field('y',           'double',  label='Y (%)',      default=50.0,
          comment='Vertical position on layout canvas (0-100)'),
    Field('sort_order',  'integer', label='Sort Order', default=0),
    format=lambda r: r.name
)
db.transmitter_switch.switchtype.requires = lookup_set('switchtype', empty_ok=True)

db.define_table('model_switch',
    Field('model',              'reference model',              required=True),
    Field('transmitter_switch', 'reference transmitter_switch'),
    Field('name',               'string', label='Switch Name',
          comment='Required when not linked to a transmitter switch'),
    Field('switchtype',         'string', label='Type',
          comment='Required when not linked to a transmitter switch'),
    Field('purpose',            'string', label='Purpose'),
    Field('notes',              'text',   label='Notes'),
    format=lambda r: (r.transmitter_switch.name
                      if r.transmitter_switch else r.name) if r else '?'
)
db.model_switch.switchtype.requires = IS_EMPTY_OR(lookup_set('switchtype', empty_ok=True))

db.define_table('model_switch_position',
    Field('model_switch', 'reference model_switch', required=True),
    Field('pos',          'string', label='Position'),
    Field('func',         'string', label='Function'),
)
db.model_switch_position.pos.requires = lookup_set('pos', empty_ok=True)

if not _migration_applied('model_switch_v2_available'):
    _mark_migration('model_switch_v2_available')

###############################################
## WISH LIST

db.define_table('wishlist'
                , Field('item', type='string', label='Item', required=True, unique=True)
                , Field('notes', type='string', label='Notes')
                , Field('modeltype', type='string', label=db.model.modeltype.label)
                , Field('modelcategory', type='string', label=db.model.modelcategory.label)
                )
db.wishlist.modeltype.requires = db.model.modeltype.requires
db.wishlist.modelcategory.requires = db.model.modelcategory.requires

###############################################
## INITIAL DATABASE SETUP

if db(db.modelstate.id > 0).count() == 0:
    db.modelstate.insert(name='Retired/Disposed')  # 1
    db.modelstate.insert(name='Idea')  # 2
    db.modelstate.insert(name='On The Board')  # 3
    db.modelstate.insert(name='Ready for Maiden')  # 4
    db.modelstate.insert(name='In Service')  # 5
    db.modelstate.insert(name='Out of Service')  # 6
    db.modelstate.insert(name='Under Repair')  # 7

if db(db.tag.id > 0).count() == 0:
    db.tag.insert(name='Modeling')
    db.tag.insert(name='Electronics')
    db.tag.insert(name='Scale')

if db(db.lookup.id > 0).count() == 0:
    _seed = [
        ('articletype',                 ['Article', 'Book', 'Idea']),
        ('modelcategory',               ['Static', 'Non-Model', 'Dynamic']),
        ('modeltype',                   ['Airplane', 'Rocket', 'Boat', 'Helicopter', 'Multirotor',
                                         'Robot', 'Experimental', 'Car', 'Autogyro', 'Submarine',
                                         'Non-Model', 'Miniature', 'Other', 'Train']),
        ('modelorigin',                 ['Plan', 'Kit', 'ARF', 'RTF', 'Unknown']),
        ('controltype',                 ['Radio Control', 'Free Flight', 'Control Line', 'Other']),
        ('powerplant',                  ['Electric', 'Internal Combustion', 'Rocket', 'Rubber', 'Sail', 'None']),
        ('attr_construction',           ['Balsa', 'Foam', 'Plastic', 'Composite', 'Other', 'Resin', 'Wood', 'Carbon Fiber']),
        ('attr_copter_headtype',        ['Collective Pitch', 'Collective Pitch - Flybar', 'Fixed Pitch']),
        ('attr_copter_tailrotor_drive', ['Direct', 'Belt', 'Shaft']),
        ('subjecttype',                 ['Scale', 'Semi-Scale', 'Fantasy', 'Sport']),
        ('attr_car_bodystyle',          ['Truggy', 'Car', 'Truck', 'Buggy', 'Other']),
        ('attr_car_drive',              ['2 Wheel', '4 Wheel', 'All Wheel', 'Other']),
        ('attr_car_drivetrain',         ['Shaft Drive', 'Belt Drive', 'Gear-Reduction', 'Direct Drive']),
        ('attr_sub_ballast',            ['Piston Tank', 'SAS - Semi-Aspirated',
                                         'RCABS - Recirculating Compressed Air Ballast',
                                         'Vented Low-Pressure', 'Compressed Gas', 'Pressure Pump', 'Dynamic']),
        ('activitytype',                ['Flight', 'Crash', 'Repair', 'Purchase', 'Retirement',
                                         'Note', 'StateChange', 'Other', 'Reconfiguration']),
        ('attr_pump_type',              ['Diaphragm', 'Centrifugal', 'Peristaltic', 'Gear', 'Piston', 'Other']),
        ('tooltype',                    ['Hand Tool', 'Fuel Tool', 'Power Tool', 'Electric Tool', 'Other']),
        ('chemistry',                   ['LiPo', 'LiFE', 'NiMH', 'NiCad', 'Li-Ion', 'Alkaline', 'SLA']),
        ('attachmenttype',              ['Image', 'Manual', 'Diagram', 'Plan', 'Article',
                                         'Configuration', 'Checklist', 'Transmitter Image']),
        ('itemtype',                    ['Standard', 'Overnight', 'Event', 'Plane Event', 'Boat Event',
                                         'Sub Event', 'Night Event', 'Heli Event']),
        ('hardwaretype',                ['Wood Screw, Pan Head', 'Wood Screw, Flat Head', 'Bolt, Socket Head',
                                         'Servo Screw', 'Grub Screw', 'Nylon Bolt']),
        ('switchtype',                  ['3-Position', '2-Position', '6-Position', 'Momentary', 'Rotary',
                                         'Slider', 'Gimbal-Left-Horizontal', 'Gimbal-Left-Vertical',
                                         'Gimbal-Right-Horizontal', 'Gimbal-Right-Vertical',
                                         'Trim_Horizontal', 'Trim-Vertical', 'Latching']),
        ('pos',                         ['Back', 'Middle', 'Forward', 'Up', 'Down', 'Left', 'Right',
                                         'Position 1', 'Position 2']),
        ('attr_radio_mode',             ['FM', 'AM', 'SSB', 'CW', 'FT8', 'FT4', 'RTTY',
                                         'Packet', 'APRS', 'D-STAR', 'DMR', 'C4FM', 'Digital']),
        ('attr_rf_connector',           ['SO-239 (UHF-F)', 'PL-259 (UHF-M)', 'BNC', 'N-Type',
                                         'SMA-Female', 'SMA-Male', 'RP-SMA', 'Other']),
        ('attr_antenna_type',           ['Vertical', 'Yagi', 'Dipole', 'Beam', 'Magnetic Loop',
                                         'End-Fed Half Wave', 'Quad', 'Wire', 'Discone',
                                         'J-Pole', 'Slim Jim', 'Collinear', 'Moxon',
                                         'Inverted-V', 'Other']),
        ('attr_antenna_polarization',   ['Vertical', 'Horizontal', 'Circular RHCP', 'Circular LHCP']),
        ('attr_antenna_mount',          ['Mobile', 'Base Station', 'Portable', 'Tower',
                                         'Roof', 'Attic', 'Vehicle Roof', 'Tripod', 'Other']),
    ]
    for category, values in _seed:
        for i, v in enumerate(values, 1):
            db.lookup.insert(category=category, name=v, sort_order=i, is_system=False)

##############################################
## Migration Steps

# Populate lookup.metadata for modeltype and modelcategory rows from hardcoded dicts.
# Runs once per row — skips any row that already has metadata set.
import json as _json

# One-time seed of 'hide' and 'controllers' metadata for modeltype rows.
# Admin edits after this migration runs are never overwritten.
if not _migration_applied('modeltype_metadata_v1'):
    for _row in db(db.lookup.category == 'modeltype').select():
        try:
            _meta = _json.loads(_row.metadata or '{}')
        except (ValueError, TypeError):
            _meta = {}
        _changed = False
        if 'hide' not in _meta:
            _meta['hide'] = modeltype_hide_attribs.get(_row.name, [])
            _changed = True
        if 'controllers' not in _meta:
            _meta['controllers'] = modeltype_controller_mapping.get(_row.name, [])
            _changed = True
        if _changed:
            _row.update_record(metadata=_json.dumps(_meta))
    _mark_migration('modeltype_metadata_v1')
    db.commit()

_MODELCATEGORY_CONTROLLERS = {
    'Dynamic':   ['attachment', 'battery', 'component', 'diagram', 'paint',
                  'propeller', 'rotor', 'sailrig', 'supportitem', 'switch', 'tool', 'wtc'],
    'Static':    ['attachment', 'component', 'paint'],
    'Non-Model': ['attachment', 'component', 'supportitem', 'tool'],
}
# One-time seed of 'hide', 'controllers', and is_system for modelcategory rows.
if not _migration_applied('modelcategory_metadata_v1'):
    for _row in db(db.lookup.category == 'modelcategory').select():
        try:
            _meta = _json.loads(_row.metadata or '{}')
        except (ValueError, TypeError):
            _meta = {}
        _updates = {}
        if 'hide' not in _meta:
            _hide = modelcategory_hide_attribs.get(_row.name) \
                    or modelcategory_hide_attribs.get('Dynamic', [])
            _meta['hide'] = _hide
            _updates['metadata'] = _json.dumps(_meta)
        if 'controllers' not in _meta:
            _meta['controllers'] = _MODELCATEGORY_CONTROLLERS.get(_row.name, [])
            _updates['metadata'] = _json.dumps(_meta)
        if not _row.is_system:
            _updates['is_system'] = True
        if _updates:
            _row.update_record(**_updates)
    _mark_migration('modelcategory_metadata_v1')
    db.commit()

# One-time forced reseed of modelcategory controllers metadata.
# Needed because the admin UI was exercised before defaults were finalized,
# leaving controllers: [] in some rows. Runs exactly once per DB.
if not _migration_applied('modelcategory_controllers_v1'):
    _MC_CTRL_DEFAULTS = {
        'Dynamic':   sorted(_ALL_CONTROLLERS),
        'Static':    ['attachment', 'component', 'paint'],
        'Non-Model': ['attachment', 'component', 'supportitem', 'tool'],
    }
    for _row in db(db.lookup.category == 'modelcategory').select():
        try:
            _meta = _json.loads(_row.metadata or '{}')
        except (ValueError, TypeError):
            _meta = {}
        _meta['controllers'] = _MC_CTRL_DEFAULTS.get(_row.name, sorted(_ALL_CONTROLLERS))
        _row.update_record(metadata=_json.dumps(_meta))
    _mark_migration('modelcategory_controllers_v1')

# Activitytype: mark system values is_system=True and seed color metadata from CSS values.
_ACTIVITY_COLORS = {
    'Flight':          '#24a718',
    'Crash':           '#e4274a',
    'Repair':          '#2435d1',
    'Purchase':        '#830c83',
    'Reconfiguration': '#379aa5',
    'Retirement':      '#4c4d49',
    'Note':            '#108aa0',
    'StateChange':     '#f52397',
    'Other':           '#bff52b',
}
_ACTIVITY_SYSTEM = frozenset(['Flight', 'Crash', 'Note', 'StateChange', 'Reconfiguration'])
# One-time seed of is_system and color metadata for activitytype rows.
if not _migration_applied('activitytype_metadata_v1'):
    for _row in db(db.lookup.category == 'activitytype').select():
        _updates = {}
        if _row.name in _ACTIVITY_SYSTEM and not _row.is_system:
            _updates['is_system'] = True
        try:
            _m = _json.loads(_row.metadata or '{}')
        except (ValueError, TypeError):
            _m = {}
        if not _m.get('color') and _row.name in _ACTIVITY_COLORS:
            _m['color'] = _ACTIVITY_COLORS[_row.name]
            _updates['metadata'] = _json.dumps(_m)
        if _updates:
            _row.update_record(**_updates)
    _mark_migration('activitytype_metadata_v1')
    db.commit()

if not _migration_applied('diagramedge_seed_v1'):
    if db(db.diagramedge.id > 0).count() == 0:
        # Seeds the structured columns directly. This block runs far below
        # diagramedge_structured_style_v1, which would already have been marked
        # applied against an empty table, so seeding dot_attribs alone would
        # leave every wire type at the Field defaults (black/1px/solid) on a
        # fresh database. dot_attribs is still filled in to match what the
        # original seed wrote, as the historical record.
        for _i, (_name, _color, _width, _style, _attribs) in enumerate([
            ('default',     '#efefef', 1, 'solid',  'color = "#efefef";'),
            ('5v Servo',    '#a8700f', 1, 'solid',  'color = "#a8700f";'),
            ('5v Signal',   '#a8700f', 1, 'dashed', 'color = "#a8700f"; style = dashed;'),
            ('12v 12gauge', '#2430d3', 4, 'solid',  'color = "#2430d3"; penwidth = 4;'),
            ('12v 20gauge', '#2430d3', 2, 'solid',  'color = "#2430d3"; penwidth = 2;'),
        ], 1):
            db.diagramedge.insert(name=_name, stroke_color=_color, stroke_width=_width,
                                  stroke_style=_style, arrow_start='none', arrow_end='none',
                                  dot_attribs=_attribs, sort_order=_i)
        diagram_edge_attribs = {
            r.name: _style_to_dot_attribs(r)
            for r in db(db.diagramedge.id > 0).select(
                orderby=db.diagramedge.sort_order | db.diagramedge.name)
        }
    _mark_migration('diagramedge_seed_v1')

_BUILTIN_CT = {
    'Engine', 'Servo', 'Receiver', 'Motor', 'ESC', 'BEC', 'Regulator',
    'Flight Controller', 'Gyro', 'Battery Charger', 'Flybarless Controller',
    'Electrical', 'Switch', 'Winch', 'Other', 'Retracts', 'Pump',
    'Sensor', 'Tire', 'Shock',
}

if not _migration_applied('componenttype_seed_v1'):
    _COMPONENTTYPE_DIAGRAM = {
        'Engine':                {'shape': 'invhouse',      'color': '#efefef', 'edge': '5v Servo'},
        'Servo':                 {'shape': 'trapezium',     'color': '#efefef', 'edge': '5v Servo'},
        'Receiver':              {'shape': 'record',        'color': '#ffffff', 'edge': '5v Servo'},
        'Motor':                 {'shape': 'cylinder',      'color': '#cc33ff', 'edge': '12v 12gauge'},
        'ESC':                   {'shape': 'polygon',       'color': '#336600', 'edge': '5v Servo'},
        'BEC':                   {'shape': 'box3d',         'color': '#668cff', 'edge': '5v Servo'},
        'Regulator':             {'shape': 'box3d',         'color': '#efefef', 'edge': '5v Servo'},
        'Flight Controller':     {'shape': 'Msquare',       'color': '#df80ff', 'edge': '5v Servo'},
        'Gyro':                  {'shape': 'Mcircle',       'color': '#ff0066', 'edge': '5v Servo'},
        'Battery Charger':       {'shape': 'rect',          'color': '#efefef', 'edge': '12v 12gauge'},
        'Flybarless Controller': {'shape': 'tripleoctagon', 'color': '#9900cc', 'edge': '5v Servo'},
        'Electrical':            {'shape': 'cds',           'color': '#efefef', 'edge': 'default'},
        'Switch':                {'shape': 'septagon',      'color': '#efefef', 'edge': '5v Servo'},
        'Winch':                 {'shape': 'component',     'color': '#efefef', 'edge': '5v Servo'},
        'Other':                 {'shape': 'component',     'color': '#efefef', 'edge': 'default'},
        'Retracts':              {'shape': 'parallelogram', 'color': '#666699', 'edge': '5v Servo'},
        'Pump':                  {'shape': 'hexagon',       'color': '#efefef', 'edge': '12v 12gauge'},
        'Sensor':                {'shape': 'cds',           'color': '#797979', 'edge': '5v Servo'},
    }
    if db(db.componenttype.id > 0).count() == 0:
        _lookup_ct = {}
        for _r in db(db.lookup.category == 'componenttype').select():
            try: _lm = _json.loads(_r.metadata or '{}')
            except (ValueError, TypeError): _lm = {}
            _lookup_ct[_r.name] = (_r.sort_order, _lm)
        _ct_names = list(_lookup_ct.keys()) if _lookup_ct else [
            'Engine', 'Servo', 'Receiver', 'Motor', 'ESC', 'BEC', 'Regulator',
            'Flight Controller', 'Gyro', 'Battery Charger', 'Flybarless Controller',
            'Electrical', 'Switch', 'Winch', 'Other', 'Retracts', 'Pump',
            'Sensor', 'Tire', 'Shock',
        ]
        for _i, _name in enumerate(_ct_names, 1):
            _sort, _lm = _lookup_ct.get(_name, (_i, {}))
            _diag = _COMPONENTTYPE_DIAGRAM.get(_name, {})
            db.componenttype.insert(
                name               = _name,
                sort_order         = _sort or _i,
                is_system          = _name in _BUILTIN_CT,
                attrs              = _lm.get('attrs') or component_attribs.get(_name, []),
                diagram_shape      = _lm.get('diagram_shape') or _diag.get('shape', ''),
                diagram_color      = _diag.get('color', '#efefef'),
                diagram_edgeattrib = _diag.get('edge', 'default'),
                diagram_is_record  = (_lm.get('diagram_shape') or _diag.get('shape', '')) in ('record', 'Mrecord'),
            )
    # Remove lookup componenttype rows now that db.componenttype is the authority.
    db(db.lookup.category == 'componenttype').delete()
    _mark_migration('componenttype_seed_v1')

# Backfill the record flag for types already configured with a record shape —
# today that is exactly Receiver, so existing diagrams keep their ports without
# anyone having to tick a box. Field(default=...) only applies at insert time,
# not to rows that predate the column.
if not _migration_applied('componenttype_is_record_v1'):
    db(db.componenttype.diagram_shape.belongs(('record', 'Mrecord'))).update(diagram_is_record=True)
    db(db.componenttype.diagram_is_record == None).update(diagram_is_record=False)
    _mark_migration('componenttype_is_record_v1')
    db.commit()

# Built-in component types are system-locked to prevent deletion/renaming of core types.
# This corrects an earlier seed that left all types with is_system=False.
if not _migration_applied('componenttype_system_v1'):
    for _row in db(db.componenttype.id > 0).select():
        _want = _row.name in _BUILTIN_CT
        if _row.is_system != _want:
            _row.update_record(is_system=_want)
    _mark_migration('componenttype_system_v1')

# One-time seed: Standard is the only system itemtype.
if not _migration_applied('itemtype_system_v1'):
    for _row in db(db.lookup.category == 'itemtype').select():
        _want_system = (_row.name == 'Standard')
        if _row.is_system != _want_system:
            _row.update_record(is_system=_want_system)
    _mark_migration('itemtype_system_v1')
    db.commit()

# chemistry: one-time seed of db.chemistry from lookup rows; delete lookup rows after.
if not _migration_applied('chemistry_seed_v1'):
    _CHEM_VOLT_SEED = {'LiPo': 3.7, 'LiFE': 3.3, 'NiMH': 1.2, 'NiCad': 1.2,
                       'Li-Ion': 3.7, 'Alkaline': 1.5, 'SLA': 2.0}
    if db(db.chemistry.id > 0).count() == 0:
        _lookup_chem = {r.name: (r.sort_order, r.metadata) for r in db(db.lookup.category == 'chemistry').select()}
        _chem_names = list(_lookup_chem.keys()) if _lookup_chem else list(_CHEM_VOLT_SEED.keys())
        for _i, _name in enumerate(_chem_names, 1):
            _sort, _lmeta = _lookup_chem.get(_name, (_i, None))
            try: _lm = _json.loads(_lmeta or '{}')
            except (ValueError, TypeError): _lm = {}
            db.chemistry.insert(
                name       = _name,
                volt       = _lm.get('volt') or _CHEM_VOLT_SEED.get(_name, 0.0),
                sort_order = _sort or _i,
            )
    # Remove lookup chemistry rows now that db.chemistry is the authority.
    db(db.lookup.category == 'chemistry').delete()
    _mark_migration('chemistry_seed_v1')

# Add HAM Radio / Antenna model types, new lookup categories, and HAM component types.
if not _migration_applied('hamradio_types_v1'):
    _rf_lookup_seeds = [
        ('attr_radio_mode',          ['FM', 'AM', 'SSB', 'CW', 'FT8', 'FT4', 'RTTY',
                                      'Packet', 'APRS', 'D-STAR', 'DMR', 'C4FM', 'Digital']),
        ('attr_rf_connector',        ['SO-239 (UHF-F)', 'PL-259 (UHF-M)', 'BNC', 'N-Type',
                                      'SMA-Female', 'SMA-Male', 'RP-SMA', 'Other']),
        ('attr_antenna_type',        ['Vertical', 'Yagi', 'Dipole', 'Beam', 'Magnetic Loop',
                                      'End-Fed Half Wave', 'Quad', 'Wire', 'Discone',
                                      'J-Pole', 'Slim Jim', 'Collinear', 'Moxon',
                                      'Inverted-V', 'Other']),
        ('attr_antenna_polarization', ['Vertical', 'Horizontal', 'Circular RHCP', 'Circular LHCP']),
        ('attr_antenna_mount',        ['Mobile', 'Base Station', 'Portable', 'Tower',
                                       'Roof', 'Attic', 'Vehicle Roof', 'Tripod', 'Other']),
    ]
    for _cat, _vals in _rf_lookup_seeds:
        if not db(db.lookup.category == _cat).count():
            for _i, _v in enumerate(_vals, 1):
                db.lookup.insert(category=_cat, name=_v, sort_order=_i, is_system=False)

    for _name, _sort in [('HAM Radio', 15), ('Antenna', 16)]:
        if not db((db.lookup.category == 'modeltype') & (db.lookup.name == _name)).count():
            _meta = _json.dumps({
                'hide'       : modeltype_hide_attribs.get(_name, []),
                'controllers': modeltype_controller_mapping.get(_name, []),
            })
            db.lookup.insert(category='modeltype', name=_name,
                             sort_order=_sort, is_system=False, metadata=_meta)

    _max_sort_row = db(db.componenttype.id > 0).select(db.componenttype.sort_order.max()).first()
    _max_sort = (_max_sort_row[db.componenttype.sort_order.max()] or 0) if _max_sort_row else 0
    _new_comp_types = [
        ('SWR/Power Meter', ['attr_freq_low_mhz', 'attr_freq_high_mhz', 'attr_max_power_w', 'attr_rf_connector']),
        ('Antenna Tuner',   ['attr_freq_low_mhz', 'attr_freq_high_mhz', 'attr_max_power_w',
                             'attr_voltage_in', 'attr_rf_connector', 'attr_firmware_version']),
        ('Coaxial Cable',   ['attr_freq_high_mhz', 'attr_rf_connector', 'attr_length']),
        ('TNC',             ['attr_voltage_in', 'attr_firmware_version']),
        ('Rotator',         ['attr_voltage_in', 'attr_watts_in']),
    ]
    for _i, (_cname, _attrs) in enumerate(_new_comp_types, 1):
        if not db(db.componenttype.name == _cname).count():
            db.componenttype.insert(name=_cname, sort_order=_max_sort + _i, attrs=_attrs)

    _mark_migration('hamradio_types_v1')
    db.commit()

# Add model_model to HAM Radio and Antenna controller lists in existing DBs.
if not _migration_applied('model_model_v1'):
    for _mtype in ['HAM Radio', 'Antenna']:
        _mm_row = db((db.lookup.category == 'modeltype') &
                     (db.lookup.name == _mtype)).select().first()
        if _mm_row and _mm_row.metadata:
            _mm_meta = _json.loads(_mm_row.metadata)
            if 'model_model' not in _mm_meta.get('controllers', []):
                _mm_meta['controllers'].append('model_model')
                _mm_row.update_record(metadata=_json.dumps(_mm_meta))
    _mark_migration('model_model_v1')
    db.commit()

# Add radio_channel and model_model to every modelcategory controllers list.
# modelcategory_controllers_v1 ran before these controllers existed, so existing
# DBs have stale lists. The view intersection logic requires both the modeltype
# AND modelcategory lists to contain a controller name for the card to appear.
if not _migration_applied('modelcategory_new_controllers_v1'):
    for _row in db(db.lookup.category == 'modelcategory').select():
        try:
            _meta = _json.loads(_row.metadata or '{}')
        except (ValueError, TypeError):
            _meta = {}
        _ctrl = _meta.get('controllers', [])
        _changed = False
        for _cname in ('radio_channel', 'model_model'):
            if _cname not in _ctrl:
                _ctrl.append(_cname)
                _changed = True
        if _changed:
            _meta['controllers'] = _ctrl
            _row.update_record(metadata=_json.dumps(_meta))
    _mark_migration('modelcategory_new_controllers_v1')
    db.commit()

###############################################
## UPLOAD FIELD SAFETY

from pydal.helpers.regex import REGEX_UPLOAD_PATTERN


def _safe_upload_delete(field):
    """Build a custom_delete for one upload field.

    pydal's own delete_uploaded_files (pydal/helpers/methods.py) assumes every
    stored value is a web2py upload name — table.field.uuidkey.b16name.ext — and
    does `oldname.split('.')` then reads items[2] to find the uploadseparate
    subfolder. Any value with fewer than three dot-separated parts raises
    IndexError, and because that runs from _before_update/_before_delete it takes
    the whole save down with it. That is what a path-style Field default did to
    db.model.img and db.component.img.

    Setting field.custom_delete makes pydal call this instead and skip its own
    parsing entirely, so a malformed value can no longer break a write: there is
    nothing on disk under such a name, so there is nothing to delete.
    """
    def _delete(name):
        if not name or not re.match(REGEX_UPLOAD_PATTERN, name):
            return
        items = name.split('.')
        folder = field.uploadfolder or os.path.join(request.folder, 'uploads')
        if field.uploadseparate:
            folder = os.path.join(folder, '%s.%s' % (items[0], items[1]), items[2][:2])
        path = os.path.join(folder, name)
        if os.path.exists(path):
            os.unlink(path)
    return _delete


# Install on every autodelete upload field. Covers deletes as well as updates —
# delete_uploaded_files backs both _before_update and _before_delete.
for _tname in db.tables:
    for _field in db[_tname]:
        if _field.type == 'upload' and _field.autodelete:
            _field.custom_delete = _safe_upload_delete(_field)

# Clear upload values that are not web2py upload names. db.model.img and
# db.component.img used to default to a filesystem path
# (applications/init/static/images/defaultUpload.png), which web2py stored
# verbatim on every record saved without a picture. Those values never served —
# default/download and Field.retrieve both require a table.field.uuid.name.ext
# name and 404 on anything else — and they crashed the first update that added a
# real image. Clearing rather than rewriting: there is no upload behind them, so
# NULL is the honest value, and default/download() now supplies the placeholder.
# Table-driven so a restored older snapshot gets repaired too.
# Depends on the custom_delete guard above being installed first, since the
# UPDATEs below fire _before_update on the very rows holding bad values.
if not _migration_applied('clear_invalid_upload_values_v1'):
    for _tname in db.tables:
        for _field in db[_tname]:
            if _field.type != 'upload':
                continue
            _rows = db((_field != None) & (_field != '')).select(db[_tname].id, _field)
            for _r in _rows:
                if not re.match(REGEX_UPLOAD_PATTERN, _r[_field.name] or ''):
                    db(db[_tname].id == _r.id).update(**{_field.name: None})
    _mark_migration('clear_invalid_upload_values_v1')
    db.commit()

# Load runtime dicts from lookup metadata (overrides the hardcoded dicts above).
# These run after all migration/sync steps so they reflect current DB state.
modeltype_controller_mapping = {}
modeltype_hide_attribs = {}
for _row in db(db.lookup.category == 'modeltype').select():
    try:
        _m = _json.loads(_row.metadata or '{}')
    except (ValueError, TypeError):
        _m = {}
    modeltype_controller_mapping[_row.name] = _m.get('controllers', [])
    modeltype_hide_attribs[_row.name] = _m.get('hide', [])

modelcategory_hide_attribs = {}
modelcategory_controllers = {}
for _row in db(db.lookup.category == 'modelcategory').select():
    try:
        _m = _json.loads(_row.metadata or '{}')
    except (ValueError, TypeError):
        _m = {}
    modelcategory_hide_attribs[_row.name] = _m.get('hide', [])
    modelcategory_controllers[_row.name] = _m.get('controllers', [])

# Override the hardcoded component_attribs with the live DB values so admin edits take effect.
component_attribs = {_row.name: (_row.attrs or []) for _row in db(db.componenttype.id > 0).select()}

activitytype_colors = {}
for _row in db(db.lookup.category == 'activitytype').select():
    try:
        _m = _json.loads(_row.metadata or '{}')
    except (ValueError, TypeError):
        _m = {}
    activitytype_colors[_row.name] = _m.get('color', '')

chem_volt = {r.name: (r.volt or 0) for r in db(db.chemistry.id > 0).select()}
db.battery.chemistry.requires = IS_IN_SET(
    [r.name for r in db(db.chemistry.id > 0).select(orderby=db.chemistry.sort_order | db.chemistry.name)],
    sort=False)

_PHYSICAL_ATTR_NAMES = [
    'attr_length', 'attr_width', 'attr_height', 'attr_weight_oz',
    'attr_travel', 'attr_model_scale',
]

component_attribs = {}
componenttype_diagram = {}
# Kept separate from componenttype_diagram, which is only populated for types
# that have a diagram_shape: the record flag is meaningful even for a type with
# no shape set (the flag implies shape="record"), so it needs its own map over
# every type.
componenttype_is_record = {}
for _row in db(db.componenttype.id > 0).select():
    _type_attrs = list(_row.attrs or [])
    for _pa in _PHYSICAL_ATTR_NAMES:
        if _pa not in _type_attrs:
            _type_attrs.append(_pa)
    component_attribs[_row.name] = _type_attrs
    componenttype_is_record[_row.name] = bool(_row.diagram_is_record)
    if _row.diagram_shape:
        componenttype_diagram[_row.name] = {
            'shape': _row.diagram_shape,
            'color': _row.diagram_color or '#efefef',
            'edge':  _row.diagram_edgeattrib or 'default',
            'is_record': bool(_row.diagram_is_record),
        }

# set all modelcategory from 'Remote Control' to 'Dynamic'
#db(db.model.modelcategory == 'Remote Control').update(modelcategory='Dynamic')
#db(db.model.havekit == None).update(havekit=False)
#db(db.model.haveplans == None).update(haveplans=False)

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
