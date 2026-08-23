# -*- coding: utf-8 -*-
"""Seed test data across every table in The Hangar.

Run from the web2py root:

    python web2py.py -S init -M -R applications/init/scripts/seed_testdata.py

Idempotent by table: each block is skipped when its table already has rows, so
re-running only fills in what is missing and never duplicates. Reference tables
that db.py bootstraps itself (modelstate, lookup, componenttype, chemistry,
diagramedge, diagram_connector, migrations) are left alone.

String values are taken from db.lookup wherever a field is validated by
lookup_set(), so the seeded rows are selectable in the real edit forms rather
than showing as off-list values.
"""

import io
import struct
import zlib

added = {}
skipped = []


def _lookup(category, index=0, fallback=None):
    """A real value from db.lookup for a lookup_set-backed field."""
    rows = db(db.lookup.category == category).select(orderby=db.lookup.sort_order)
    if not rows:
        return fallback
    return rows[index % len(rows)].name


def _png(w, h, rgb):
    """A real PNG so seeded image fields render instead of erroring."""
    raw = b''.join(b'\x00' + bytes(bytearray(rgb)) * w for _ in range(h))

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw))
            + chunk(b'IEND', b''))


def _upload(table, field, slug, rgb=(120, 150, 190), ext='png'):
    """Store a placeholder image through pydal and return its stored name.

    Field.store() is what generates the name and decides where the bytes land —
    this schema uses uploadseparate, so files live in
    uploads/<table>.<field>/<xx>/ rather than flat in uploads/. Writing them by
    hand puts them where default/download will not find them.
    """
    return db[table][field].store(io.BytesIO(_png(48, 48, rgb)),
                                  'seed_%s.%s' % (slug, ext))


def seed(table, rows):
    """Insert rows only when the table is empty. Returns the new ids."""
    if db(db[table]).count():
        skipped.append(table)
        return []
    ids = [db[table].insert(**r) for r in rows]
    added[table] = len(ids)
    return ids


def pick(modeltype=None, name=None):
    """An existing model, by name or type, else the first one."""
    if name:
        row = db(db.model.name == name).select().first()
        if row:
            return row
    if modeltype:
        row = db(db.model.modeltype == modeltype).select().first()
        if row:
            return row
    return db(db.model).select(orderby=db.model.id).first()


# --------------------------------------------------------------- diagram styles
seed('diagram_component', [
    dict(name='Custom Battery Pack', shape='box3d', fillcolor='#c8e6c9',
         stroke_color='#2e7d32', stroke_width=2, sort_order=1),
    dict(name='Custom BEC', shape='component', fillcolor='#fff9c4',
         stroke_color='#f9a825', sort_order=2),
    dict(name='Custom Antenna', shape='house', fillcolor='#e1bee7',
         stroke_color='#6a1b9a', stroke_style='dashed', sort_order=3),
    dict(name='Custom Sensor', shape='ellipse', fillcolor='#b3e5fc',
         stroke_color='#0277bd', sort_order=4),
])

# -------------------------------------------------------------------- protocols
protocol_ids = seed('protocol', [
    dict(name='FrSky ACCST D16', description='FrSky 2.4GHz, 16 channel'),
    dict(name='FrSky ACCESS', description='Newer FrSky protocol with OTA updates'),
    dict(name='Spektrum DSMX', description='Spektrum 2.4GHz frequency agile'),
    dict(name='FlySky AFHDS 2A', description='FlySky automatic hopping'),
    dict(name='Crossfire', description='TBS Crossfire 900MHz long range'),
])
if not protocol_ids:
    protocol_ids = [r.id for r in db(db.protocol).select()]

# ----------------------------------------------------------------- transmitters
transmitter_ids = seed('transmitter', [
    dict(name='Taranis X9D Plus', nickname='Big Radio', serial='TX-X9D-0001',
         manufacturer='FrSky', model='X9D Plus', os='OpenTX', os_version='2.3.15',
         radio_firmware='ACCST 2.1.0', firmware_version='2.3.15',
         processor='STM32F429', can_export_config=True,
         protocol=protocol_ids[:2],
         notes='Primary radio. SD card holds all model configs.',
         img=_upload('transmitter', 'img', 'tx1', (90, 110, 140))),
    dict(name='Spektrum DX8e', nickname='Backup', serial='TX-DX8E-0002',
         manufacturer='Spektrum', model='DX8e', os='Spektrum AirWare',
         os_version='1.02', firmware_version='1.02', can_export_config=False,
         protocol=protocol_ids[2:3],
         notes='Loaner radio for guests.',
         img=_upload('transmitter', 'img', 'tx2', (140, 110, 90))),
    dict(name='RadioMaster TX16S', nickname='EdgeTX', serial='TX-TX16S-0003',
         manufacturer='RadioMaster', model='TX16S MkII', os='EdgeTX',
         os_version='2.9.3', firmware_version='2.9.3', processor='STM32F407',
         can_export_config=True,
         protocol=[protocol_ids[0], protocol_ids[4]] if len(protocol_ids) > 4 else protocol_ids[:1],
         notes='Multi-protocol module installed.'),
])
if not transmitter_ids:
    transmitter_ids = [r.id for r in db(db.transmitter).select()]

# ------------------------------------------------------- transmitter switches
sw_types = [_lookup('switchtype', i, '3-Position') for i in range(4)]
seed('transmitter_switch', [
    dict(transmitter=transmitter_ids[0], name='SA', switchtype=sw_types[0],
         x=12.0, y=22.0, sort_order=1),
    dict(transmitter=transmitter_ids[0], name='SB', switchtype=sw_types[0],
         x=30.0, y=18.0, sort_order=2),
    dict(transmitter=transmitter_ids[0], name='SD', switchtype=sw_types[1],
         x=70.0, y=18.0, sort_order=3),
    dict(transmitter=transmitter_ids[0], name='SF', switchtype=sw_types[3],
         x=88.0, y=22.0, sort_order=4),
    dict(transmitter=transmitter_ids[1], name='Gear', switchtype=sw_types[1],
         x=20.0, y=30.0, sort_order=1),
    dict(transmitter=transmitter_ids[1], name='Flap', switchtype=sw_types[0],
         x=80.0, y=30.0, sort_order=2),
])

# ------------------------------------------- two more models for wider coverage
extra_models = {}

# db.model has a handful of notnull booleans with no default, so every insert
# has to name them explicitly or SQLite rejects the row.
model_notnull = {f: False for f in db.model.fields
                 if getattr(db.model[f], 'notnull', False)
                 and db.model[f].default is None}

for mname, fields in [
    ('HAM Base Station', dict(
        modeltype=_lookup('modeltype', 6, 'Experimental'),
        modelcategory='Non-Model',
        modelstate=5, modelorigin=_lookup('modelorigin', 4, 'Unknown'),
        controltype=_lookup('controltype', 3, 'Other'),
        powerplant=_lookup('powerplant', 5, 'None'),
        description='2m/70cm base station with rooftop vertical',
        notes='Seeded test data. Covers the HAM radio attribute set.',
        attr_radio_mode=_lookup('attr_radio_mode', 0, 'FM'),
        attr_antenna_type=_lookup('attr_antenna_type', 0, 'Vertical'),
        attr_antenna_mount=_lookup('attr_antenna_mount', 1, 'Base Station'),
        attr_rf_connector=_lookup('attr_rf_connector', 0, 'SO-239 (UHF-F)'),
        haveplans=False, havekit=True, selected=False)),
    ('Dirt Basher', dict(
        modeltype='Car', modelcategory='Dynamic', modelstate=5,
        modelorigin=_lookup('modelorigin', 3, 'RTF'),
        controltype=_lookup('controltype', 0, 'Radio Control'),
        powerplant=_lookup('powerplant', 0, 'Electric'),
        subjecttype=_lookup('subjecttype', 3, 'Sport'),
        description='1/10 electric short course truck',
        notes='Seeded test data. Covers the car attribute set.',
        attr_car_bodystyle=_lookup('attr_car_bodystyle', 2, 'Truck'),
        attr_car_drive=_lookup('attr_car_drive', 1, '4 Wheel'),
        attr_car_drivetrain=_lookup('attr_car_drivetrain', 0, 'Shaft Drive'),
        attr_construction=_lookup('attr_construction', 2, 'Plastic'),
        haveplans=False, havekit=True, selected=False)),
]:
    row = db(db.model.name == mname).select().first()
    if row:
        extra_models[mname] = row.id
    else:
        values = dict(model_notnull)
        values.update(fields)
        extra_models[mname] = db.model.insert(name=mname, **values)
        added['model'] = added.get('model', 0) + 1

ham = extra_models['HAM Base Station']
car = extra_models['Dirt Basher']

# ------------------------------------ point some models at a transmitter/protocol
linked = 0
for i, m in enumerate(db(db.model.modelcategory == 'Dynamic').select(limitby=(0, 4))):
    if m.transmitter is None and m.protocol is None:
        m.update_record(transmitter=transmitter_ids[i % len(transmitter_ids)],
                        protocol=protocol_ids[i % len(protocol_ids)])
        linked += 1
if linked:
    added['model.transmitter/protocol'] = linked

# ------------------------------------------------------------- radio channels
seed('radio_channel', [
    dict(model=ham, channel_num=1, name='NOAA WX', frequency_mhz=162.550,
         duplex='off', tone_mode='', channel_mode='FM', skip=False,
         channel_comment='Weather radio'),
    dict(model=ham, channel_num=2, name='2m Call', frequency_mhz=146.520,
         duplex='simplex', tone_mode='', channel_mode='FM', skip=False,
         channel_comment='National 2m calling frequency'),
    dict(model=ham, channel_num=3, name='Local Rpt', frequency_mhz=146.940,
         duplex='-', offset_mhz=0.600, tone_mode='Tone', ctcss_freq=100.0,
         channel_mode='FM', skip=False, channel_comment='Club repeater'),
    dict(model=ham, channel_num=4, name='70cm Call', frequency_mhz=446.000,
         duplex='simplex', channel_mode='FM', skip=False),
    dict(model=ham, channel_num=5, name='APRS', frequency_mhz=144.390,
         duplex='simplex', channel_mode='FM', skip=True,
         channel_comment='APRS digipeater frequency'),
    dict(model=ham, channel_num=6, name='DTCS Test', frequency_mhz=147.180,
         duplex='+', offset_mhz=0.600, tone_mode='DTCS', dtcs_code='023',
         channel_mode='FM', skip=False),
])

# ------------------------------------------------------------ model relations
plane = pick('Airplane')
heli = pick('Helicopter')
boat = pick('Boat')
quad = pick('Multirotor')
seed('model_model', [
    dict(model_a=plane.id, model_b=quad.id, notes='Share the same transmitter'),
    dict(model_a=heli.id, model_b=quad.id, notes='Share 3S packs'),
    dict(model_a=boat.id, model_b=plane.id, notes='Both use the same paint set'),
])

# --------------------------------------------------------------------- todos
seed('todo', [
    dict(todo='Replace worn aileron servo', model=plane.id, critical=True,
         complete=False, notes='Servo 2 is jittering at centre'),
    dict(todo='Balance new propeller', model=plane.id, critical=False, complete=False),
    dict(todo='Re-glue canopy latch', model=plane.id, critical=False, complete=True),
    dict(todo='Check tail rotor linkage', model=heli.id, critical=True, complete=False,
         notes='Play detected during last hover'),
    dict(todo='Order spare main blades', model=heli.id, critical=False, complete=False),
    dict(todo='Reflash flight controller', model=quad.id, critical=False, complete=False,
         notes='Betaflight 4.5'),
    dict(todo='Seal hull seam', model=boat.id, critical=True, complete=False),
    dict(todo='Log antenna SWR readings', model=ham, critical=False, complete=False),
])

# ------------------------------------------------------------------- sail rigs
seed('sailrig', [
    dict(rigname='A Rig (light air)', model=boat.id, mast_length_mm=1400,
         mast_material='Carbon Fiber', main_boom_length_mm=560,
         main_boom_material='Aluminium', main_sail_material='Mylar',
         main_sail_area_dm2=42.5, jib_boom_length_mm=340,
         jib_boom_material='Carbon Fiber', jib_sail_material='Mylar',
         jib_sail_area_dm2=18.0, notes='Full size rig for under 8 knots',
         img=_upload('sailrig', 'img', 'rig1', (110, 160, 200))),
    dict(rigname='C Rig (heavy air)', model=boat.id, mast_length_mm=1050,
         mast_material='Carbon Fiber', main_boom_length_mm=430,
         main_boom_material='Aluminium', main_sail_material='Dacron',
         main_sail_area_dm2=26.0, jib_sail_area_dm2=11.0,
         notes='Reefed rig for 15 knots plus'),
])

# ------------------------------------------------------- flight time records
motors = db(db.component.componenttype == 'Motor').select()
packs = db(db.battery).select()
if motors and packs:
    seed('eflite_time', [
        dict(model=quad.id, motor=motors[0].id, battery=packs[0].id,
             propeller='5x4.5', amps=28.4, watts=315.0),
        dict(model=quad.id, motor=motors[0].id, battery=packs[1].id,
             propeller='5x4.5', amps=33.1, watts=367.0),
        dict(model=plane.id, motor=motors[min(1, len(motors) - 1)].id,
             battery=packs[min(1, len(packs) - 1)].id,
             propeller='10x5', amps=41.8, watts=464.0),
        dict(model=heli.id, motor=motors[min(2, len(motors) - 1)].id,
             battery=packs[min(2, len(packs) - 1)].id,
             propeller='325mm blades', amps=52.0, watts=770.0),
    ])

# ---------------------------------------------------------------- support items
seed('supportitem', [
    dict(item='Wing bag (60in)', model=plane.id, notes='Padded, holds both panels',
         img=_upload('supportitem', 'img', 'sup1', (170, 150, 120))),
    dict(item='Blade holder', model=heli.id, notes='Foam blade caddy'),
    dict(item='Boat stand', model=boat.id, notes='Carpeted cradle'),
])

# ------------------------------------------------------------------ propellers
seed('propeller', [
    dict(item='10x5 APC Electric', model=plane.id),
    dict(item='11x5.5 APC Electric', model=plane.id),
    dict(item='5x4.5 tri-blade', model=quad.id),
    dict(item='5x4.3 bi-blade', model=quad.id),
    dict(item='45mm 3-blade scale', model=boat.id),
])

# ----------------------------------------------------------------- attachments
att_types = [_lookup('attachmenttype', i, 'Manual') for i in range(4)]
seed('attachment', [
    dict(name='Assembly manual', attachmenttype=att_types[1], model=plane.id,
         attachment=_upload('attachment', 'attachment', 'att1', (200, 200, 200))),
    dict(name='Full size plan', attachmenttype=att_types[3], model=plane.id,
         attachment=_upload('attachment', 'attachment', 'att2', (220, 210, 180))),
    dict(name='Setup checklist', attachmenttype=att_types[0], model=heli.id,
         attachment=_upload('attachment', 'attachment', 'att3', (180, 200, 180))),
])

# --------------------------------------------------------------- packing items
item_types = [_lookup('itemtype', i, 'Standard') for i in range(8)]
seed('packingitems', [
    dict(name='Transmitter', itemtype=item_types[0]),
    dict(name='LiPo charger + PSU', itemtype=item_types[0]),
    dict(name='Field toolbox', itemtype=item_types[0]),
    dict(name='Folding table', itemtype=item_types[1]),
    dict(name='Canopy / shade', itemtype=item_types[2]),
    dict(name='Wing bags', itemtype=item_types[3]),
    dict(name='Boat stand + towel', itemtype=item_types[4]),
    dict(name='Head torch', itemtype=item_types[6]),
])

# ---------------------------------------------------------------- image library
seed('images', [
    dict(img=_upload('images', 'img', 'img1', (200, 120, 120)), tags=['plane', 'build']),
    dict(img=_upload('images', 'img', 'img2', (120, 200, 140)), tags=['heli']),
    dict(img=_upload('images', 'img', 'img3', (120, 140, 210)), tags=['boat', 'scale']),
    dict(img=_upload('images', 'img', 'img4', (210, 190, 110)), tags=['field']),
])

# ------------------------------------------------------- water tight cylinders
wtc_ids = seed('wtc', [
    dict(name='WTC 60mm x 300mm', make='SubTech', model='ST-60',
         attr_length_mm=300.0, attr_outer_diameter_mm=60.0, attr_weight_oz=11.5,
         attr_ballast_capacity=180.0, notes='Piston tank, single motor pass-through',
         img=_upload('wtc', 'img', 'wtc1', (150, 150, 160))),
    dict(name='WTC 90mm x 420mm', make='DeepDive', model='DD-90',
         attr_length_mm=420.0, attr_outer_diameter_mm=90.0, attr_weight_oz=26.0,
         attr_ballast_capacity=420.0, notes='RCABS system'),
])
if wtc_ids:
    seed('model_wtc', [
        dict(model=boat.id, wtc=wtc_ids[0], notes='Fitted for the 2026 season'),
        dict(model=boat.id, wtc=wtc_ids[1], notes='Spare, needs new O-rings'),
    ])

# -------------------------------------------------------------------- hardware
hw_types = [_lookup('hardwaretype', i, 'Servo Screw') for i in range(6)]
seed('hardware', [
    dict(model=plane.id, hardwaretype=hw_types[3], diameter='M2', length_mm=8.0,
         purpose='Servo mounting', quantity=8),
    dict(model=plane.id, hardwaretype=hw_types[2], diameter='M3', length_mm=25.0,
         purpose='Wing bolts', quantity=4),
    dict(model=plane.id, hardwaretype=hw_types[5], diameter='M4', length_mm=30.0,
         purpose='Wing hold-down (shear bolt)', quantity=2),
    dict(model=heli.id, hardwaretype=hw_types[2], diameter='M2.5', length_mm=12.0,
         purpose='Main frame', quantity=12),
    dict(model=heli.id, hardwaretype=hw_types[4], diameter='M3', length_mm=4.0,
         purpose='Motor pinion', quantity=2),
    dict(model=quad.id, hardwaretype=hw_types[2], diameter='M3', length_mm=6.0,
         purpose='Arm mounting', quantity=8),
    dict(model=boat.id, hardwaretype=hw_types[0], diameter='#4', length_mm=12.0,
         purpose='Deck fittings', quantity=16),
    dict(model=car, hardwaretype=hw_types[2], diameter='M3', length_mm=10.0,
         purpose='Shock towers', quantity=6),
])

# ----------------------------------------------------------------------- paint
paint_ids = seed('paint', [
    dict(manufacturer='Tamiya', brand='TS', color='Racing White', colorid='TS-7',
         colorhex='#F2F2EF', notes='Lacquer spray',
         img=_upload('paint', 'img', 'p1', (242, 242, 239))),
    dict(manufacturer='Tamiya', brand='TS', color='Bright Red', colorid='TS-49',
         colorhex='#C8102E'),
    dict(manufacturer='Tamiya', brand='XF', color='Flat Black', colorid='XF-1',
         colorhex='#1A1A1A'),
    dict(manufacturer='Vallejo', brand='Model Air', color='Sky Blue', colorid='71.008',
         colorhex='#7FB2D9'),
    dict(manufacturer='Rust-Oleum', brand='Painters Touch', color='Gloss Sunburst Yellow',
         colorid='7747', colorhex='#F5C518'),
    dict(manufacturer='Krylon', brand='Fusion', color='Satin Hunter Green',
         colorid='2436', colorhex='#2E5B3A'),
])
if paint_ids:
    seed('model_paint', [
        dict(model=plane.id, paint=paint_ids[0], purpose='Fuselage top'),
        dict(model=plane.id, paint=paint_ids[1], purpose='Trim stripes'),
        dict(model=plane.id, paint=paint_ids[2], purpose='Anti-glare panel'),
        dict(model=boat.id, paint=paint_ids[5], purpose='Hull above waterline'),
        dict(model=boat.id, paint=paint_ids[2], purpose='Boot stripe'),
    ])

# ------------------------------------------------------------------------ urls
seed('url', [
    dict(url='https://www.rcgroups.com/forums/showthread.php?t=1234567',
         model=plane.id, notes='Build thread'),
    dict(url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
         model=plane.id, notes='Maiden flight video'),
    dict(url='https://www.align.com.tw/', model=heli.id, notes='Manufacturer site'),
    dict(url='https://betaflight.com/docs/wiki', model=quad.id, notes='Firmware docs'),
])

# ----------------------------------------------- legacy (v1) switch assignments
legacy_ids = seed('switch', [
    dict(switch='SA', model=plane.id, switchtype=sw_types[0], purpose='Flight modes'),
    dict(switch='SD', model=plane.id, switchtype=sw_types[1], purpose='Throttle cut'),
])
if legacy_ids:
    seed('switch_position', [
        dict(switch=legacy_ids[0], pos=_lookup('pos', 3, 'Up'), func='Normal rates'),
        dict(switch=legacy_ids[0], pos=_lookup('pos', 1, 'Middle'), func='Mid rates'),
        dict(switch=legacy_ids[0], pos=_lookup('pos', 4, 'Down'), func='High rates'),
        dict(switch=legacy_ids[1], pos=_lookup('pos', 3, 'Up'), func='Motor armed'),
        dict(switch=legacy_ids[1], pos=_lookup('pos', 4, 'Down'), func='Motor cut'),
    ])

# -------------------------------------------------- v2 model switch assignments
tx_switches = db(db.transmitter_switch).select()
ms_rows = []
if tx_switches:
    ms_rows = [
        dict(model=plane.id, transmitter_switch=tx_switches[0].id,
             purpose='Flight modes', notes='3 rate settings'),
        dict(model=plane.id, transmitter_switch=tx_switches[2].id,
             purpose='Retracts'),
        dict(model=heli.id, transmitter_switch=tx_switches[1].id,
             purpose='Idle up'),
        dict(model=quad.id, transmitter_switch=tx_switches[3].id,
             purpose='Arm'),
        # one deliberately unlinked, to cover the free-text branch
        dict(model=boat.id, name='Aux 1', switchtype=sw_types[1],
             purpose='Bilge pump', notes='Wired direct, not on the transmitter'),
    ]
ms_ids = seed('model_switch', ms_rows)
if ms_ids:
    seed('model_switch_position', [
        dict(model_switch=ms_ids[0], pos=_lookup('pos', 3, 'Up'), func='Beginner'),
        dict(model_switch=ms_ids[0], pos=_lookup('pos', 1, 'Middle'), func='Sport'),
        dict(model_switch=ms_ids[0], pos=_lookup('pos', 4, 'Down'), func='Advanced'),
        dict(model_switch=ms_ids[1], pos=_lookup('pos', 3, 'Up'), func='Gear up'),
        dict(model_switch=ms_ids[1], pos=_lookup('pos', 4, 'Down'), func='Gear down'),
        dict(model_switch=ms_ids[2], pos=_lookup('pos', 3, 'Up'), func='Idle up 1'),
        dict(model_switch=ms_ids[2], pos=_lookup('pos', 4, 'Down'), func='Throttle hold'),
        dict(model_switch=ms_ids[3], pos=_lookup('pos', 3, 'Up'), func='Armed'),
        dict(model_switch=ms_ids[3], pos=_lookup('pos', 4, 'Down'), func='Disarmed'),
        dict(model_switch=ms_ids[4], pos=_lookup('pos', 3, 'Up'), func='Pump on'),
    ])

# -------------------------------------------------------------------- wishlist
seed('wishlist', [
    dict(item='Balsa USA Fokker D.VII', notes='1/4 scale, needs a big engine',
         modeltype='Airplane', modelcategory='Dynamic'),
    dict(item='Graupner Vector 40', notes='Classic F3A pattern ship',
         modeltype='Airplane', modelcategory='Dynamic'),
    dict(item='Robbe Atlantis', notes='Semi-scale trawler',
         modeltype='Boat', modelcategory='Dynamic'),
    dict(item='Estes Saturn V', notes='Display build',
         modeltype='Rocket', modelcategory='Static'),
    dict(item='Yaesu FT-991A', notes='All band all mode base rig',
         modeltype='Experimental', modelcategory='Non-Model'),
])

# ------------------------------------------------------------ library articles
tag_ids = [t.id for t in db(db.tag).select()]
art_types = [_lookup('articletype', i, 'Article') for i in range(3)]
seed('article', [
    dict(name='Covering film without wrinkles', articletype=art_types[0],
         author='R. Fielding', articlesource='Model Aviation, Mar 2024',
         summary='Iron temperature and shrink order for tricky compound curves.',
         notes="Work from the centre out.\n\nSeal edges first, then shrink panels.",
         tags=tag_ids[:1],
         img=_upload('article', 'img', 'art1', (190, 170, 140))),
    dict(name='Basic Aeronautics for Modellers', articletype=art_types[1],
         author='M. Simons', summary='Reference text on wing sections and stability.',
         notes='Chapter 6 covers dihedral and spiral stability.',
         tags=tag_ids[:2],
         attachment=_upload('article', 'attachment', 'art2', (200, 200, 210))),
    dict(name='Soldering XT60 connectors cleanly', articletype=art_types[0],
         author='Unknown', articlesource='Forum post',
         summary='Tinning order that avoids melted housings.',
         notes='Clamp the shell, tin the cup, then flow the wire in.',
         tags=tag_ids[1:2] if len(tag_ids) > 1 else tag_ids),
    dict(name='Scale cockpit idea - resin pilot bust', articletype=art_types[2],
         summary='Cast a lightweight pilot from a 3D printed master.',
         notes='Print master, silicone mould, pour hollow.',
         tags=tag_ids[2:3] if len(tag_ids) > 2 else tag_ids),
])

# ---------------------------------------------------------------------- report
db.commit()

print('\n=== seeded ===')
for t in sorted(added):
    print('  %-28s +%d' % (t, added[t]))
print('\n=== already had rows, left alone ===')
print('  ' + ', '.join(sorted(skipped)) if skipped else '  (none)')

print('\n=== final row counts ===')
empty = []
for t in sorted(db.tables):
    if t.startswith('auth_'):
        continue
    n = db(db[t]).count()
    if not n:
        empty.append(t)
    print('  %-26s %d' % (t, n))
print('\nstill empty: %s' % (', '.join(empty) if empty else 'none'))
