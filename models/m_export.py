# -*- coding: utf-8 -*-
###############################################
## MODEL EXPORT
##
## One registry (EXPORT_SECTIONS) describes every section of the printable
## model sheet (model/export): what it shows, which fields are available, the
## default field set, and when it applies to a model. admin/export_config edits
## the per-section choices, stored in db.export_section; a section with no row
## there falls back to its registry defaults, so new sections need no seeding.

import json as _exp_json
import re as _exp_re
from gluon.storage import Storage

db.define_table('export_section',
    Field('section_key',  type='string',      label='Section', required=True, unique=True),
    Field('enabled',      type='boolean',     label='Enabled', default=True),
    Field('sort_order',   type='integer',     label='Sort Order', default=0),
    Field('shown_fields', type='list:string', label='Fields'),
    Field('section_options', type='text',     label='Options', default='',
          comment='JSON section options, e.g. {"limit": 5}'),
    format=lambda r: r.section_key
)

# Grouped model fields. Shared by the admin hide/important editors and the
# export overview, which prints one block per group.
MODEL_FIELD_GROUPS = [
    ('General', [
        'modelorigin', 'description', 'notes', 'img', 'manufacturer',
        'kitnumber', 'kitlocation', 'subjecttype', 'attr_scale',
        'haveplans', 'havekit',
    ]),
    ('Control & Radio', [
        'controltype', 'powerplant', 'transmitter', 'protocol', 'configbackup',
    ]),
    ('Physical', [
        'attr_construction', 'attr_covering', 'attr_cog',
        'attr_length', 'attr_width', 'attr_height', 'attr_weight_oz', 'attr_flight_timer',
    ]),
    ('Airplane', [
        'attr_plane_rem_wings', 'attr_plane_rem_wing_tube', 'attr_plane_rem_struts',
        'attr_plane_wingspan_mm', 'attr_plane_wingarea',
        'attr_plane_throw_aileron', 'attr_plane_throw_elevator',
        'attr_plane_throw_rudder', 'attr_plane_throw_flap',
    ]),
    ('Helicopter / Gyro', [
        'attr_copter_headtype', 'attr_copter_mainrotor_length',
        'attr_copter_tailrotor_span', 'attr_copter_tailrotor_drive',
        'attr_copter_swashplate_type', 'attr_copter_size',
        'attr_copter_blade_count', 'attr_copter_tailrotor_blade_count',
    ]),
    ('Multirotor', ['attr_multi_rotor_count']),
    ('Rocket',    ['attr_rocket_parachute', 'attr_rocket_body_tube', 'attr_rocket_motors']),
    ('Boat / Submarine', ['attr_boat_draft', 'attr_boat_rem_planes', 'attr_sub_ballast']),
    ('Car / Vehicle', [
        'attr_car_scale', 'attr_car_drive', 'attr_car_drivetrain',
        'attr_car_bodystyle', 'attr_car_wheelbase',
    ]),
    ('Hardware', ['attr_hardware_os', 'attr_hardware_os_version', 'attr_hardware_firmware_version',]),
    ('HAM Radio', [
        'attr_radio_freq_low_mhz', 'attr_radio_freq_high_mhz', 'attr_radio_power_w',
        'attr_radio_mode', 'attr_radio_bands', 'attr_radio_memory_ch',
        'attr_radio_rf_connector', 'attr_radio_aprs', 'attr_radio_dstar', 'attr_radio_dmr',
    ]),
    ('Antenna', [
        'attr_antenna_type', 'attr_antenna_gain_dbi',
        'attr_antenna_freq_low_mhz', 'attr_antenna_freq_high_mhz',
        'attr_antenna_max_power_w', 'attr_antenna_impedance_ohm',
        'attr_antenna_connector', 'attr_antenna_polarization',
        'attr_antenna_mount', 'attr_antenna_elements',
    ]),
    ('Status & Notes', [
        'selected', 'final_disposition', 'final_value', 'fieldnotes', 'diagram',
    ]),
]


###############################################
## SHARED MODEL HELPERS

def model_card_controllers(model):
    """Card controllers that apply to this model: the modeltype set (all, when
    the type configures none) intersected with the modelcategory set. Single
    definition used by the model page and the export."""
    allowed = modeltype_controller_mapping.get(model.modeltype, [])
    mt_ctrls = set(allowed) if allowed else _ALL_CONTROLLERS
    return set(modelcategory_controllers.get(model.modelcategory, [])) & mt_ctrls


def model_hidden_fields(model):
    """Model fields hidden for this model's type or category."""
    return (set(modeltype_hide_attribs.get(model.modeltype, [])) |
            set(modelcategory_hide_attribs.get(model.modelcategory, [])))


def model_switch_list(model_id):
    """A model's switches as dicts (switch, type, purpose, positions {pos: func}).
    Reads the new model_switch system, falling back to legacy db.switch rows for
    models that have not been migrated."""
    out = []
    new_switches = db(db.model_switch.model == model_id).select(orderby=db.model_switch.id)
    if new_switches:
        pos_map = {}
        for p in db(db.model_switch_position.model_switch.belongs(
                [s.id for s in new_switches])).select(orderby=db.model_switch_position.id):
            pos_map.setdefault(p.model_switch, {})[p.pos] = p.func
        for s in new_switches:
            ts = db.transmitter_switch[s.transmitter_switch] if s.transmitter_switch else None
            out.append({
                'id':        s.id,
                'mid':       s.model,
                'switch':    ts.name if ts else (s.name or ''),
                'type':      ts.switchtype if ts else (s.switchtype or ''),
                'purpose':   s.purpose or '',
                'positions': pos_map.get(s.id, {}),
            })
    else:
        for s in db(db.switch.model == model_id).select():
            out.append({
                'id':        s.id,
                'mid':       s.model.id,
                'switch':    s.switch,
                'type':      s.switchtype,
                'purpose':   s.purpose,
                'positions': {p.pos: p.func for p in
                              db(db.switch_position.switch == s.id).select()},
            })
    return out


###############################################
## VALUE FORMATTING

def _exp_num(v):
    """Compact number: 1200.0 -> '1200', 3.250 -> '3.25'."""
    if v is None:
        return ''
    return ('%.2f' % float(v)).rstrip('0').rstrip('.')


def _exp_ref(tablename, rec_id):
    rec = db[tablename](rec_id) if rec_id else None
    if not rec:
        return None
    fmt = db[tablename]._format
    if callable(fmt):
        return fmt(rec)
    return (fmt % rec.as_dict()) if fmt else str(rec_id)


def _exp_value(table, row, fname):
    """Display value of one field, or None when it should be left off the sheet.
    Empty values, zero numeric attributes and False attr_* flags are dropped:
    on a printout they are noise, not information."""
    field = table[fname]
    v = row[fname]
    if v is None or v == '' or v == []:
        return None
    ftype = field.type if isinstance(field.type, str) else 'string'
    if ftype == 'boolean':
        if not v and fname.startswith('attr_'):
            return None
        return 'Yes' if v else 'No'
    if ftype in ('double', 'integer'):
        if not v and fname.startswith('attr_'):
            return None
        if ftype == 'integer':
            return str(v)
        unit = (getattr(field, 'extra', None) or {}).get('measurement', '')
        return _exp_num(v) + (' ' + unit if unit else '') + \
            ConvertMeasurementField(table, row, fname, separator=' / ')
    if ftype.startswith('list:'):
        return ', '.join(str(x) for x in v) or None
    if ftype.startswith('reference '):
        return _exp_ref(ftype[len('reference '):], v)
    return str(v)


def _exp_plain(text, limit):
    """MARKMIN source flattened to one plain line, truncated."""
    s = _exp_re.sub(r'[*`\'~#\[\]]+', '', text or '')
    s = ' '.join(s.split())
    return s if len(s) <= limit else s[:limit - 1].rstrip() + '…'


###############################################
## SECTION BUILDERS
## Each returns a dict {'kind': ..., ...} or None when there is nothing to show.

_OVERVIEW_EXCLUDE = frozenset([
    'description', 'notes', 'img', 'fieldnotes', 'diagram', 'selected',
    'transmitter', 'protocol', 'configbackup',
])


def _overview_available():
    return [(f, db.model[f].label)
            for _grp, fields in MODEL_FIELD_GROUPS for f in fields
            if f in db.model.fields and f not in _OVERVIEW_EXCLUDE]


def _build_overview(model, fields, opts):
    wanted = set(fields) - model_hidden_fields(model)
    groups = []
    for grp, gfields in MODEL_FIELD_GROUPS:
        pairs = []
        for f in gfields:
            if f in wanted and f in db.model.fields:
                val = _exp_value(db.model, model, f)
                if val is not None:
                    pairs.append((db.model[f].label, val))
        if pairs:
            groups.append((grp, pairs))
    return {'kind': 'groups', 'groups': groups} if groups else None


def _build_text(model, fields, opts):
    parts = []
    if 'description' in fields and model.description:
        parts.append(P(model.description, _class='exp-lead'))
    for f in ('notes', 'fieldnotes'):
        if f in fields and model[f]:
            parts.append(DIV(MARKMIN(model[f]), _class='exp-markmin'))
    return {'kind': 'text', 'body': CAT(*parts)} if parts else None


def _transmitter_columns():
    tx = db.transmitter
    return [
        ('name',             tx.name.label,             lambda t, m: t.name + (' (%s)' % t.nickname if t.nickname else '')),
        ('manufacturer',     tx.manufacturer.label,     lambda t, m: t.manufacturer),
        ('model',            tx.model.label,            lambda t, m: t.model),
        ('serial',           tx.serial.label,           lambda t, m: t.serial),
        ('protocol',         db.model.protocol.label,   lambda t, m: _exp_ref('protocol', m.protocol)),
        ('os',               tx.os.label,               lambda t, m: ' '.join(x for x in (t.os, t.os_version) if x)),
        ('firmware_version', tx.firmware_version.label, lambda t, m: ' '.join(x for x in (t.radio_firmware, t.firmware_version) if x)),
        ('processor',        tx.processor.label,        lambda t, m: t.processor),
        ('radio_processor',  tx.radio_processor.label,  lambda t, m: t.radio_processor),
        ('configbackup',     'Config Backup',           lambda t, m: {'Yes': 'Backed up', 'No': 'NOT backed up'}.get(m.get_radio_config_backedup())),
    ]


def _build_transmitter(model, fields, opts):
    t = db.transmitter(model.transmitter) if model.transmitter else None
    if not t:
        return None
    pairs = []
    for key, label, getter in _transmitter_columns():
        if key in fields:
            val = getter(t, model)
            if val:
                pairs.append((label, val))
    if not pairs:
        return None
    return {'kind': 'kv', 'pairs': pairs, 'thumb': t.img if opts.get('thumbs') else None}


def _build_table(spec, model, fields, opts):
    """Generic builder for sections declared with 'rows' + 'columns'."""
    rows = spec['rows'](model)
    if not rows:
        return None
    cols = [(k, label, getter) for k, label, getter in spec['columns'] if k in fields]
    if not cols:
        return None
    thumb_fn = spec.get('thumb') if opts.get('thumbs') else None
    body = []
    for r in rows:
        cells = []
        for _k, _label, getter in cols:
            val = getter(r)
            cells.append('' if val is None else val)
        body.append({'thumb': thumb_fn(r) if thumb_fn else None, 'cells': cells})
    # A column of nothing but placeholders is just noise.
    thumbs = any(b['thumb'] for b in body)
    labels = [label for _k, label, _g in cols]
    if _exp_redundant_label(labels[0], spec.get('title', '')):
        labels[0] = ''
    return {'kind': 'table', 'cols': labels, 'rows': body, 'thumbs': thumbs,
            'show_head': any(labels)}


def _exp_singular(word):
    if word.endswith('ies'):
        return word[:-3] + 'y'
    if word.endswith(('ches', 'shes', 'sses', 'xes')):
        return word[:-2]
    if word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word


def _exp_redundant_label(label, title):
    """True when a table's first column header only repeats the section heading:
    the same words (singular or plural, e.g. 'Propeller' under 'Propellers',
    'To Do' under 'Open Todos'), or a bare 'Name' column."""
    norm = lambda s: ''.join(_exp_singular(w) for w in
                             _exp_re.findall(r'[a-z0-9]+', str(s or '').lower()))
    lbl, ttl = norm(label), norm(title)
    return bool(lbl) and (lbl == 'name' or lbl in ttl)


def _activity_columns():
    a = db.activity
    return [
        ('activitydate',     a.activitydate.label,     lambda r: r.activitydate),
        ('activitytype',     a.activitytype.label,     lambda r: activity_label(r)),
        ('duration',         a.duration.label,         lambda r: _exp_num(r.duration) if r.duration else ''),
        ('activitylocation', a.activitylocation.label, lambda r: r.activitylocation),
        ('notes',            a.notes.label,            lambda r: _exp_plain(r.notes, 140)),
    ]


def _build_activity(model, fields, opts):
    q = db(db.activity.model == model.id)
    total = q.count()
    if not total:
        return None
    count = db.activity.id.count()
    dur = db.activity.duration.sum()
    stats = q.select(db.activity.activitytype, count, dur,
                     groupby=db.activity.activitytype, orderby=~count)
    summary = []
    for s in stats:
        part = '%s ×%d' % (activity_type_label(s.activity.activitytype, model.modeltype), s[count])
        if s[dur]:
            part += ' (%s min)' % _exp_num(s[dur])
        summary.append(part)
    first = q.select(db.activity.activitydate.min()).first()[db.activity.activitydate.min()]
    last = q.select(db.activity.activitydate.max()).first()[db.activity.activitydate.max()]
    if first and last:
        summary.append('%s – %s' % (first, last))

    out = {'kind': 'activity', 'summary': ' · '.join(summary), 'table': None}
    limit = int(opts.get('limit') or 0)
    if limit > 0:
        spec = {
            'rows': lambda m: db(db.activity.model == m.id).select(
                orderby=~db.activity.activitydate | ~db.activity.id, limitby=(0, limit)),
            'columns': _activity_columns(),
        }
        out['table'] = _build_table(spec, model, fields, {})
        if total > limit:
            out['more'] = 'Showing the latest %d of %d.' % (limit, total)
    return out


def _build_diagram(model, fields, opts):
    return {'kind': 'diagram', 'dot': model.diagram} if model.diagram else None


###############################################
## ROW SOURCES for table sections

def _related_models(model):
    out = []
    for r in db((db.model_model.model_a == model.id) |
                (db.model_model.model_b == model.id)).select():
        other = db.model(r.model_b if r.model_a == model.id else r.model_a)
        if other and other.modelstate != 1:   # 1 = retired/disposed
            out.append(Storage(name=other.name, modeltype=other.modeltype,
                               state=other.modelstate.name, notes=r.notes))
    return out


def _component_function(r):
    mc = r.model_component
    func = mc.purpose or 'General Purpose'
    if mc.channel:
        func += ' (ch %s)' % mc.channel
    return func


def _switch_positions(s):
    return '; '.join('%s: %s' % (p, f) for p, f in s['positions'].items() if f)


def _is_dynamic(m):
    return m.modelcategory == 'Dynamic'


###############################################
## REGISTRY
## width: 'full' sections span the sheet; 'half' sections pack two per row.
## Order here is the default print order.

EXPORT_SECTIONS = [
    dict(key='overview', title='Specifications', icon='model', width='full',
         applies=lambda m, c: True,
         available=_overview_available,
         default=[f for f, _l in _overview_available()
                  if f not in ('kitlocation', 'final_disposition', 'final_value')],
         build=_build_overview),

    dict(key='description', title='Description', icon='model', width='full',
         applies=lambda m, c: True,
         available=lambda: [('description', db.model.description.label),
                            ('notes', db.model.notes.label)],
         default=['description', 'notes'],
         build=_build_text),

    dict(key='fieldnotes', title='Field Notes', icon='model', width='full',
         applies=lambda m, c: True,
         available=lambda: [('fieldnotes', db.model.fieldnotes.label)],
         default=['fieldnotes'],
         build=_build_text),

    dict(key='transmitter', title='Radio', icon='transmitter', width='half',
         applies=lambda m, c: _is_dynamic(m) and bool(m.transmitter),
         available=lambda: [(k, l) for k, l, _g in _transmitter_columns()],
         default=['name', 'protocol', 'os', 'configbackup'],
         options={'thumbs': False},
         build=_build_transmitter),

    dict(key='switch', title='Switches', icon='switch', width='half',
         applies=lambda m, c: _is_dynamic(m) and 'switch' in c,
         rows=lambda m: model_switch_list(m.id),
         columns=[('switch',    'Switch',    lambda s: s['switch']),
                  ('type',      'Type',      lambda s: s['type']),
                  ('purpose',   'Purpose',   lambda s: s['purpose']),
                  ('positions', 'Positions', _switch_positions)],
         default=['switch', 'purpose', 'positions']),

    dict(key='battery', title='Batteries', icon='battery', width='half',
         applies=lambda m, c: _is_dynamic(m) and 'battery' in c,
         rows=lambda m: models_and_batteries(db.model.id == m.id).select(),
         columns=[('name',     'Battery',                         lambda r: r.battery.name),
                  ('quantity', db.model_battery.quantity.label,   lambda r: r.model_battery.quantity),
                  ('voltage',  'Voltage',                         lambda r: _exp_num(r.battery.voltage) + ' V'),
                  ('maxamps',  'Max Amps',                        lambda r: _exp_num(r.battery.get_maxamps())),
                  ('owned',    db.battery.ownedcount.label,       lambda r: r.battery.ownedcount)],
         default=['name', 'quantity', 'voltage']),

    dict(key='propeller', title='Propellers', icon='propeller', width='half',
         applies=lambda m, c: _is_dynamic(m) and 'propeller' in c,
         rows=lambda m: db(db.propeller.model == m.id).select(),
         columns=[('item', db.propeller.item.label, lambda r: r.item)],
         default=['item']),

    dict(key='flighttimes', title='Flight Times', icon='battery', width='half',
         applies=lambda m, c: _is_dynamic(m),
         rows=lambda m: db(db.eflite_time.model == m.id).select(),
         columns=[('motor',     db.eflite_time.motor.label,     lambda r: r.motor.name if r.motor else ''),
                  ('battery',   db.eflite_time.battery.label,   lambda r: r.battery.name if r.battery else ''),
                  ('propeller', db.eflite_time.propeller.label, lambda r: r.propeller),
                  ('amps',      'Amps',                         lambda r: _exp_num(r.amps)),
                  ('watts',     'Watts',                        lambda r: _exp_num(r.watts)),
                  ('minutes',   'Minutes',                      lambda r: r.get_minutes()),
                  ('wpp',       'W/lb',                         lambda r: r.get_wattsperpound()),
                  ('over',      'Over Rating?',                 lambda r: 'YES' if r.is_overrating() else '')],
         default=['battery', 'propeller', 'amps', 'minutes', 'wpp', 'over']),

    dict(key='component', title='Components', icon='component', width='full',
         applies=lambda m, c: 'component' in c,
         rows=lambda m: models_and_components(db.model.id == m.id).select(
             orderby=db.component.componenttype | db.component.name),
         columns=[('name',              db.component.name.label,              lambda r: r.component.name),
                  ('componenttype',     db.component.componenttype.label,     lambda r: ' / '.join(x for x in (r.component.componenttype, r.component.componentsubtype) if x)),
                  ('function',          'Function',                           _component_function),
                  ('note',              db.model_component.note.label,        lambda r: r.model_component.note),
                  ('manufacturer',      db.component.manufacturer.label,      lambda r: r.component.manufacturer),
                  ('significantdetail', db.component.significantdetail.label, lambda r: r.component.significantdetail),
                  ('serial',            db.component.serial.label,            lambda r: r.component.serial),
                  ('storedat',          db.component.storedat.label,          lambda r: r.component.storedat)],
         default=['name', 'componenttype', 'function', 'serial'],
         options={'thumbs': True},
         thumb=lambda r: r.component.img),

    dict(key='radio_channel', title='Radio Channels', icon='transmitter', width='full',
         applies=lambda m, c: 'radio_channel' in c,
         rows=lambda m: db(db.radio_channel.model == m.id).select(orderby=db.radio_channel.channel_num),
         columns=[(f, db.radio_channel[f].label,
                   (lambda f: lambda r: _exp_value(db.radio_channel, r, f) or '')(f))
                  for f in ('channel_num', 'name', 'frequency_mhz', 'duplex', 'offset_mhz',
                            'tone_mode', 'ctcss_freq', 'dtcs_code', 'channel_mode', 'skip',
                            'channel_comment')],
         default=['channel_num', 'name', 'frequency_mhz', 'duplex', 'offset_mhz',
                  'tone_mode', 'ctcss_freq', 'channel_mode']),

    dict(key='hardware', title='Hardware', icon='hardware', width='half',
         applies=lambda m, c: m.modelcategory in ('Dynamic', 'Non-Model'),
         rows=lambda m: db(db.hardware.model == m.id).select(
             orderby=db.hardware.hardwaretype | db.hardware.diameter),
         columns=[('hardwaretype', db.hardware.hardwaretype.label, lambda r: r.hardwaretype),
                  ('diameter',     db.hardware.diameter.label,     lambda r: r.diameter),
                  ('length_mm',    db.hardware.length_mm.label,    lambda r: _exp_num(r.length_mm) + ' mm' if r.length_mm else ''),
                  ('purpose',      db.hardware.purpose.label,      lambda r: r.purpose),
                  ('quantity',     'Qty',                          lambda r: r.quantity)],
         default=['hardwaretype', 'diameter', 'length_mm', 'purpose', 'quantity']),

    dict(key='tool', title='Tools', icon='tool', width='half',
         applies=lambda m, c: 'tool' in c,
         rows=lambda m: models_and_tools(db.model.id == m.id).select(orderby=db.tool.tooltype | db.tool.name),
         columns=[('name',     db.tool.name.label,          lambda r: r.tool.name),
                  ('tooltype', db.tool.tooltype.label,      lambda r: r.tool.tooltype),
                  ('purpose',  db.model_tool.purpose.label, lambda r: r.model_tool.purpose)],
         default=['name', 'purpose']),

    dict(key='supportitem', title='Support Items', icon='supportitem', width='half',
         applies=lambda m, c: 'supportitem' in c,
         rows=lambda m: db(db.supportitem.model == m.id).select(orderby=db.supportitem.item),
         columns=[('item',  db.supportitem.item.label,  lambda r: r.item),
                  ('notes', db.supportitem.notes.label, lambda r: _exp_plain(r.notes, 100))],
         default=['item', 'notes']),

    dict(key='wtc', title='Water Tight Cylinders', icon='wtc', width='half',
         applies=lambda m, c: _is_dynamic(m) and 'wtc' in c,
         rows=lambda m: models_and_wtcs(db.model.id == m.id).select(),
         columns=[('name',    db.wtc.name.label,                  lambda r: r.wtc.name),
                  ('make',    'Make / Model',                     lambda r: ' '.join(x for x in (r.wtc.make, r.wtc.model) if x)),
                  ('ballast', db.wtc.attr_ballast_capacity.label, lambda r: _exp_num(r.wtc.attr_ballast_capacity) if r.wtc.attr_ballast_capacity else ''),
                  ('notes',   db.model_wtc.notes.label,           lambda r: _exp_plain(r.model_wtc.notes, 100))],
         default=['name', 'make', 'ballast']),

    dict(key='sailrig', title='Sail Rigs', icon='sailrig', width='half',
         applies=lambda m, c: _is_dynamic(m) and 'sailrig' in c,
         rows=lambda m: db(db.sailrig.model == m.id).select(orderby=db.sailrig.rigname),
         columns=[(f, db.sailrig[f].label,
                   (lambda f: lambda r: _exp_value(db.sailrig, r, f) or '')(f))
                  for f in ('rigname', 'mast_length_mm', 'mast_material', 'main_boom_length_mm',
                            'main_sail_material', 'main_sail_area_dm2', 'jib_boom_length_mm',
                            'jib_sail_material', 'jib_sail_area_dm2')]
                 + [('notes', db.sailrig.notes.label, lambda r: _exp_plain(r.notes, 100))],
         default=['rigname', 'mast_length_mm', 'main_sail_area_dm2', 'jib_sail_area_dm2']),

    dict(key='paint', title='Paint', icon='paint', width='half',
         applies=lambda m, c: 'paint' in c,
         rows=lambda m: models_and_paints(db.model.id == m.id).select(),
         columns=[('swatch',       '',                               lambda r: SPAN(_class='exp-swatch', _style='background:%s' % r.paint.colorhex) if r.paint.colorhex else ''),
                  ('color',        db.paint.color.label,             lambda r: r.paint.color),
                  ('manufacturer', db.paint.manufacturer.label,      lambda r: ' '.join(x for x in (r.paint.manufacturer, r.paint.brand) if x)),
                  ('colorid',      db.paint.colorid.label,           lambda r: r.paint.colorid),
                  ('purpose',      'Used On',                        lambda r: r.model_paint.purpose)],
         default=['swatch', 'color', 'manufacturer', 'colorid', 'purpose']),

    dict(key='todo', title='Open Todos', icon='todo', width='half',
         applies=lambda m, c: True,
         rows=lambda m: db((db.todo.model == m.id) & (db.todo.complete == False)).select(
             orderby=~db.todo.critical | db.todo.todo),
         columns=[('todo',  db.todo.todo.label,  lambda r: CAT(B('! ') if r.critical else '', r.todo)),
                  ('notes', db.todo.notes.label, lambda r: _exp_plain(r.notes, 100))],
         default=['todo']),

    dict(key='model_model', title='Related Models', icon='model', width='half',
         applies=lambda m, c: 'model_model' in c,
         rows=_related_models,
         columns=[('name',      'Model',                     lambda r: r.name),
                  ('modeltype', db.model.modeltype.label,    lambda r: r.modeltype),
                  ('state',     db.model.modelstate.label,   lambda r: r.state),
                  ('notes',     db.model_model.notes.label,  lambda r: r.notes)],
         default=['name', 'notes']),

    dict(key='url', title='Links', icon='attachment', width='half',
         applies=lambda m, c: True,
         rows=lambda m: db(db.url.model == m.id).select(),
         columns=[('url',   db.url.url.label,   lambda r: r.url),
                  ('notes', db.url.notes.label, lambda r: r.notes)],
         default=['url', 'notes']),

    dict(key='attachment', title='Attachments', icon='attachment', width='half',
         applies=lambda m, c: 'attachment' in c,
         rows=lambda m: db(db.attachment.model == m.id).select(orderby=db.attachment.name),
         columns=[('name',           db.attachment.name.label,           lambda r: r.name),
                  ('attachmenttype', db.attachment.attachmenttype.label, lambda r: r.attachmenttype)],
         default=['name', 'attachmenttype']),

    dict(key='activity', title='History', icon='activity', width='full',
         applies=lambda m, c: True,
         available=lambda: [(k, l) for k, l, _g in _activity_columns()],
         default=['activitydate', 'activitytype', 'duration', 'activitylocation', 'notes'],
         options={'limit': 5},
         build=_build_activity),

    dict(key='diagram', title='Wiring Diagram', icon='diagram', width='full',
         applies=lambda m, c: 'diagram' in c,
         available=lambda: [],
         default=[],
         build=_build_diagram),
]

EXPORT_SECTION_MAP = {s['key']: s for s in EXPORT_SECTIONS}


def export_available_fields(spec):
    """[(fieldkey, label)] the admin can pick from for a section."""
    if 'columns' in spec:
        return [(k, label or k.title()) for k, label, _g in spec['columns']]
    return spec['available']()


def export_section_config():
    """Every registry section merged with its saved settings, in print order.
    Returns Storage(spec, key, enabled, order, fields, options) per section."""
    saved = {r.section_key: r for r in db(db.export_section.id > 0).select()}
    out = []
    for i, spec in enumerate(EXPORT_SECTIONS):
        avail = [k for k, _l in export_available_fields(spec)]
        opts = dict(spec.get('options') or {})
        row = saved.get(spec['key'])
        if row:
            chosen = set(row.shown_fields or [])
            fields = [k for k in avail if k in chosen]
            try:
                opts.update(_exp_json.loads(row.section_options or '{}'))
            except (ValueError, TypeError):
                pass
            enabled, order = bool(row.enabled), row.sort_order or 0
        else:
            fields, enabled, order = list(spec['default']), True, (i + 1) * 10
        out.append(Storage(spec=spec, key=spec['key'], enabled=enabled,
                           order=order, fields=fields, options=opts))
    out.sort(key=lambda c: c.order)
    return out


def build_model_export(model):
    """The export sheet for one model as layout blocks:
    [('full', section)] or [('grid', [section, ...])], sections being
    Storage(key, title, icon, data). Sections that do not apply to the model,
    are disabled, or have nothing to show are left out entirely."""
    ctrls = model_card_controllers(model)
    blocks = []
    for cfg in export_section_config():
        spec = cfg.spec
        if not cfg.enabled or not spec['applies'](model, ctrls):
            continue
        if 'build' in spec:
            data = spec['build'](model, cfg.fields, cfg.options)
        else:
            data = _build_table(spec, model, cfg.fields, cfg.options)
        if not data:
            continue
        sec = Storage(key=cfg.key, title=spec['title'], icon=spec['icon'], data=data)
        if spec['width'] == 'half':
            if blocks and blocks[-1][0] == 'grid':
                blocks[-1][1].append(sec)
            else:
                blocks.append(('grid', [sec]))
        else:
            blocks.append(('full', sec))
    return blocks
