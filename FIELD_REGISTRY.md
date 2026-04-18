# Field Registry

Tracks metadata for all database fields across the app.

## Column Key

| Column | Meaning |
|--------|---------|
| **Searchable** | Candidate for QueryBuilder advanced search. `direct` = on the model table. `via:X` = cross-table join through X (e.g. searching *models* whose components match). |
| **MT Hide** | Currently in `modeltype_hide_attribs` — admin can hide per model type |
| **Cat Hide** | Currently in `modelcategory_hide_attribs` — admin can hide per category |
| **Important** | Currently supported in admin Important Fields feature (type ∩ category) |
| **Help** | Has entry in `models/help.py` |
| **Measure** | Has `extra['measurement']` converter |

Blank cell = no / not applicable. `?` = uncertain, needs verification.

---

## db.model

| Field                             | Label                | Type        |      Searchable       | MT Hide | Cat Hide | Important | Help | Measure |
| --------------------------------- | -------------------- | ----------- | :-------------------: | :-----: | :------: | :-------: | :--: | :-----: |
| name                              | Name                 | string      |        direct         |         |          |           |      |         |
| modeltype                         | Type                 | ref lookup  |        direct         |         |          |           |      |         |
| modelcategory                     | Category             | ref lookup  |        direct         |         |          |           |  ✓  |         |
| modelstate                        | State                | ref lookup  |        direct         |         |          |           |  ✓  |         |
| modelorigin                       | Origin               | ref lookup  |                       |         |          |           |  ✓  |         |
| manufacturer                      | Manufacturer         | string      |        direct         |         |          |           |      |         |
| kitnumber                         | Kit Number           | string      |                       |         |          |           |      |         |
| kitlocation                       | Kit/Plan Location    | string      |                       |         |          |           |  ✓  |         |
| description                       | Description          | string      |                       |         |          |           |      |         |
| notes                             | Details              | text        |                       |         |          |           |      |         |
| fieldnotes                        | Field Notes          | text        |                       |         |          |           |      |         |
| diagram                           | Diagram Code         | text        |                       |         |          |           |      |         |
| img                               | Picture              | upload      |                       |         |          |           |      |         |
| configbackup                      | Radio Config         | upload      |        direct         |   ✓    |    ✓    |           |      |         |
| controltype                       | Control              | ref lookup  |        direct         |   ✓    |    ✓    |           |      |         |
| powerplant                        | Power Plant          | ref lookup  |        direct         |   ✓    |    ✓    |           |      |         |
| transmitter                       | Transmitter          | reference   | via:model_transmitter |   ✓    |    ✓    |           |      |         |
| protocol                          | Protocol             | reference   |        direct         |   ✓    |    ✓    |           |      |         |
| subjecttype                       | Model Subject        | ref lookup  |        direct         |         |          |           |  ✓  |         |
| haveplans                         | Has Plans            | boolean     |        direct         |         |          |           |  ✓  |         |
| havekit                           | Have Kit/Model       | boolean     |        direct         |         |          |           |  ✓  |         |
| selected                          | Mark Selected        | boolean     |                       |         |          |           |      |         |
| final_disposition                 | Final Disposition    | string      |                       |         |          |           |  ✓  |         |
| final_value                       | Reasonable Value     | double      |                       |         |          |           |      |         |
| attr_scale                        | Model Scale          | string      |        direct         |         |          |           |      |         |
| attr_flight_timer                 | Flight Timer         | double      |        direct         |   ✓    |    ✓    |    ✓     |      |         |
| attr_construction                 | Construction         | ref lookup  |        direct         |         |          |           |      |         |
| attr_cog                          | CoG                  | string      |                       |   ✓    |    ✓    |    ✓     |      |         |
| attr_length                       | Length               | double      |        direct         |         |          |           |      |   mm    |
| attr_width                        | Width/Beam           | double      |        direct         |         |          |           |      |   mm    |
| attr_height                       | Height               | double      |        direct         |         |          |           |      |   mm    |
| attr_weight_oz                    | Weight               | double      |        direct         |         |          |    ✓     |      |   oz    |
| attr_covering                     | Covering             | ref lookup  |        direct         |   ✓    |          |           |      |         |
| attr_plane_rem_wings              | Removable Wings?     | boolean     |        direct         |   ✓    |    ✓    |           |      |         |
| attr_plane_rem_wing_tube          | Removable Wing Tube? | boolean     |        direct         |   ✓    |    ✓    |           |      |         |
| attr_plane_rem_struts             | Removable Struts?    | boolean     |        direct         |   ✓    |    ✓    |           |      |         |
| attr_plane_wingspan_mm            | Wingspan             | double      |        direct         |   ✓    |          |    ✓     |      |   mm    |
| attr_plane_wingarea               | Wing Area            | double      |        direct         |   ✓    |          |    ✓     |      |  sqin   |
| attr_plane_throw_aileron          | Aileron Throw        | string      |                       |   ✓    |    ✓    |           |      |         |
| attr_plane_throw_elevator         | Elevator Throw       | string      |                       |   ✓    |    ✓    |           |      |         |
| attr_plane_throw_rudder           | Rudder Throw         | string      |                       |   ✓    |    ✓    |           |      |         |
| attr_plane_throw_flap             | Flap Throw           | string      |                       |   ✓    |    ✓    |           |      |         |
| attr_rocket_parachute             | Parachute            | string      |                       |   ✓    |    ✓    |           |      |         |
| attr_rocket_body_tube             | Body Tube            | string      |                       |   ✓    |    ✓    |           |      |         |
| attr_rocket_motors                | Motors               | list:string |        direct         |   ✓    |    ✓    |           |      |         |
| attr_boat_draft                   | Draft                | double      |        direct         |   ✓    |    ✓    |    ✓     |      |   mm    |
| attr_sub_ballast                  | Ballast Type         | string      |        direct         |   ✓    |    ✓    |           |      |         |
| attr_copter_headtype              | Head Type            | ref lookup  |        direct         |   ✓    |          |           |      |         |
| attr_copter_swashplate_type       | Swashplate Type      | ref lookup  |        direct         |   ✓    |    ✓    |    ✓     |      |         |
| attr_copter_size                  | Heli Size            | integer     |        direct         |   ✓    |          |    ✓     |      |         |
| attr_copter_blade_count           | Blade Count          | integer     |                       |   ✓    |          |           |      |         |
| attr_copter_tailrotor_blade_count | Tail Blade Count     | integer     |                       |   ✓    |          |           |      |         |
| attr_copter_mainrotor_length      | Main Rotor Length    | double      |        direct         |   ✓    |          |    ✓     |      |   mm    |
| attr_copter_tailrotor_span        | Tail Rotor Length    | double      |                       |   ✓    |          |           |      |   mm    |
| attr_copter_tailrotor_drive       | Tail Rotor Drive     | ref lookup  |                       |   ✓    |    ✓    |           |      |         |
| attr_multi_rotor_count            | Rotor Count          | integer     |        direct         |   ✓    |          |    ✓     |      |         |
| attr_car_scale                    | Vehicle Scale        | string      |        direct         |   ✓    |          |           |      |         |
| attr_car_drive                    | X Wheel Drive        | ref lookup  |        direct         |   ✓    |    ✓    |           |      |         |
| attr_car_drivetrain               | Drivetrain           | ref lookup  |        direct         |   ✓    |    ✓    |           |      |         |
| attr_car_bodystyle                | Body Style           | ref lookup  |        direct         |   ✓    |          |           |      |         |
| attr_car_wheelbase                | Wheelbase            | double      |        direct         |   ✓    |          |    ✓     |      |   mm    |

---

## db.component

Join path to models: `model_component.model` where `model_component.component = component.id`

| Field                 | Label              | Type              |     Searchable      | Help | Measure |
| --------------------- | ------------------ | ----------------- | :-----------------: | :--: | :-----: |
| name                  | Name               | string            | via:model_component |      |         |
| componenttype         | Type               | ref componenttype | via:model_component |  ✓  |         |
| componentsubtype      | Subtype            | string            | via:model_component |      |         |
| manufacturer          | Manufacturer       | string            | via:model_component |  ✓  |         |
| model                 | Model              | string            | via:model_component |  ✓  |         |
| significantdetail     | Significant Detail | string            |                     |  ✓  |         |
| storedat              | Location           | string            |                     |  ✓  |         |
| ownedcount            | Count              | integer           |                     |      |         |
| serial                | Serial Number      | string            |                     |      |         |
| diagramname           | Diagram Name       | string            |                     |  ✓  |         |
| customdot             | Custom .dot Code   | string            |                     |  ✓  |         |
| notes                 | Notes              | text              |                     |      |         |
| img                   | Picture            | upload            |                     |      |         |
| attachment            | Attachment         | upload            |                     |      |         |
| attr_length           | Length             | double            | via:model_component |      |   mm    |
| attr_width            | Width/Beam         | double            | via:model_component |      |   mm    |
| attr_height           | Height             | double            | via:model_component |      |   mm    |
| attr_weight_oz        | Weight             | double            | via:model_component |      |   oz    |
| attr_channel_count    | Channel Count      | integer           | via:model_component |      |         |
| attr_telemetry_port   | Telemetry Port     | boolean           | via:model_component |      |         |
| attr_sbus_port        | SBUS Port          | boolean           | via:model_component |      |         |
| attr_pwr_port         | Power Port         | boolean           | via:model_component |      |         |
| attr_protocol         | Protocol           | reference         | via:model_component |      |         |
| attr_gear_type        | Gear Type          | string            | via:model_component |      |         |
| attr_amps_in          | Rated Amps In      | double            | via:model_component |      |         |
| attr_amps_out         | Rated Amps Out     | double            | via:model_component |      |         |
| attr_torque           | Rated Torque       | string            | via:model_component |      |         |
| attr_switch_type      | Switch Type        | string            | via:model_component |      |         |
| attr_displacement_cc  | Displacement       | double            | via:model_component |      |   cc    |
| attr_motor_kv         | Motor KV           | integer           | via:model_component |      |         |
| attr_voltage_in       | Max Voltage In     | double            | via:model_component |      |         |
| attr_voltage_out      | Max Voltage Out    | double            | via:model_component |      |         |
| attr_num_turns        | Number of Turns    | integer           |                     |      |         |
| attr_watts_in         | Max Watts In       | double            | via:model_component |      |         |
| attr_watts_out        | Max Watts Out      | double            | via:model_component |      |         |
| attr_pump_type        | Pump Type          | ref lookup        |                     |      |         |
| attr_travel           | Travel             | double            |                     |      |   mm    |
| attr_model_scale      | Model Scale        | string            |                     |      |         |
| attr_firmware_version | Firmware Version   | string            |                     |      |         |

---

## db.model_component  *(join table)*

| Field     | Label     | Type      |     Searchable      |
| --------- | --------- | --------- | :-----------------: |
| model     | Model     | reference |          —          |
| component | Component | reference |          —          |
| purpose   | Purpose   | string    | via:model_component |
| channel   | Channel   | integer   |                     |

---

## db.battery

Join path to models: `model_battery.model` where `model_battery.battery = battery.id`

| Field      | Label             | Type          |    Searchable     |
| ---------- | ----------------- | ------------- | :---------------: |
| cellcount  | Cell Count        | integer       |                   |
| mah        | mAh               | integer       |                   |
| chemistry  | Chemistry         | ref chemistry |                   |
| crating    | C Rating          | integer       |                   |
| ownedcount | Number Owned      | integer       |                   |
| .format    | The "unique" name | string        | via:model_battery |

---

## db.activity

Join path to models: `activity.model`

| Field            | Label          | Type       |  Searchable  |
| ---------------- | -------------- | ---------- | :----------: |
| activitytype     | Type           | ref lookup | via:activity |
| activitydate     | Date           | date       | via:activity |
| duration         | Duration (min) | double     | via:activity |
| activitylocation | Location       | string     | via:activity |
| notes            | Notes          | text       |              |
| img              | Picture        | upload     |              |

---

## db.transmitter

Join path to models: `model.transmitter`

| Field          | Label               | Type           |      Searchable       | Help |
| -------------- | ------------------- | -------------- | :-------------------: | :--: |
| name           | Name                | string         | via:model.transmitter |      |
| nickname       | Nickname            | string         | via:model.transmitter |  ✓  |
| manufacturer   | Manufacturer        | string         | via:model.transmitter |      |
| model          | Model               | string         | via:model.transmitter |      |
| os             | Operating System    | string         |                       |  ✓  |
| protocol       | Protocols Supported | list:reference | via:model.transmitter |  ✓  |
| serial         | Serial Number       | string         |                       |      |
| radio_firmware | Radio Firmware      | string         | via:model.transmitter |      |
| processor      | Processor           | string         |                       |      |
| notes          | Notes               | text           |                       |      |
| img            | Picture             | upload         |                       |      |
| attachment     | Manual              | upload         |                       |      |

---

## db.protocol

Join path to models: `model.protocol` or via `transmitter.protocol`

| Field       | Label       | Type   |                   Searchable                   | Help |
| ----------- | ----------- | ------ | :--------------------------------------------: | :--: |
| name        | Name        | string | via:model.protocol OR via:transmitter.protocol |  ✓  |
| description | Description | text   |                                                |      |

---

## db.sailrig

Join path to models: `sailrig.model`

| Field               | Label              | Type    | Searchable | Help | Measure |
| ------------------- | ------------------ | ------- | :--------: | :--: | :-----: |
| rigname             | Name               | string  |            |  ✓  |         |
| mast_length_mm      | Mast Length        | integer |            |      |   mm    |
| mast_material       | Mast Material      | string  |            |      |         |
| main_boom_length_mm | Main Boom Length   | integer |            |      |   mm    |
| main_boom_material  | Main Boom Material | string  |            |      |         |
| main_sail_area_dm2  | Main Sail Area     | double  |            |      |   dm2   |
| main_sail_material  | Main Sail Material | string  |            |      |         |
| jib_boom_length_mm  | Jib Boom Length    | integer |            |      |   mm    |
| jib_boom_material   | Jib Boom Material  | string  |            |      |         |
| jib_sail_area_dm2   | Jib Sail Area      | double  |            |      |   dm2   |
| jib_sail_material   | Jib Sail Material  | string  |            |      |         |
| notes               | Notes              | text    |            |      |         |
| img                 | Picture            | upload  |            |      |         |

---

## db.wtc  *(Water Tight Cylinder)*

Join path to models: `model_wtc.model`

| Field                  | Label            | Type   |  Searchable   | Measure |
| ---------------------- | ---------------- | ------ | :-----------: | :-----: |
| name                   | Name             | string | via:model_wtc |         |
| make                   | Make             | string | via:model_wtc |         |
| model                  | Model            | string | via:model_wtc |         |
| attr_length_mm         | Length           | double | via:model_wtc |   mm    |
| attr_outer_diameter_mm | Outer Diameter   | double | via:model_wtc |   mm    |
| attr_width_mm          | Width/Beam       | double |               |   mm    |
| attr_height_mm         | Height           | double |               |   mm    |
| attr_weight_oz         | Weight           | double |               |   oz    |
| attr_ballast_capacity  | Ballast Capacity | double |               |   oz    |
| notes                  | Notes            | text   |               |         |
| img                    | Picture          | upload |               |         |

---

## db.hardware  *(per-model, no join table)*

Join path to models: `hardware.model`

| Field        | Label                    | Type       |  Searchable  |
| ------------ | ------------------------ | ---------- | :----------: |
| hardwaretype | Type                     | ref lookup |              |
| diameter     | Size/Dimensions          | string     |              |
| length_mm    | Length                   | double     |              |
| purpose      | Purpose                  | string     |              |
| quantity     | Quantity                 | integer    |              |
| .format      | The "unique" description | string     | via:hardware |
---

## db.tool / db.model_tool

Join path to models: `model_tool.model` where `model_tool.tool = tool.id`
Use case: find models that share the same tool, or find models requiring a specific tool type.

| Field    | Label   | Type       | Searchable      |
|----------|---------|------------|:---------------:|
| name     | Name    | string     | via:model_tool  |
| tooltype | Type    | ref lookup | via:model_tool  |
| notes    | Notes   | text       |                 |
| img      | Picture | upload     |                 |
| *model_tool.purpose* | Purpose | string | via:model_tool |

---

## db.propeller

Join path to models: `propeller.model`
Use case: find models sharing a specific propeller spec.

| Field | Label     | Type      | Searchable       |
|-------|-----------|-----------|:----------------:|
| item  | Propeller | string    | via:propeller    |

---

## db.wishlist

Stand-alone search target (not a model join).
Use case: search wishlist when considering a new kit purchase alongside model search.

| Field         | Label    | Type       | Searchable |
|---------------|----------|------------|:----------:|
| item          | Item     | string     | direct     |
| modeltype     | Type     | ref lookup | direct     |
| modelcategory | Category | ref lookup | direct     |
| notes         | Notes    | string     |            |

---

## db.article

Stand-alone search target, also surfaced alongside model search results.
Use case: "models with retractable gear" also returns articles about retractable gear installation/maintenance.

| Field         | Label   | Type            | Searchable |
|---------------|---------|-----------------|:----------:|
| name          | Name    | string          | direct     |
| articletype   | Type    | ref lookup      | direct     |
| summary       | Summary | string          | direct     |
| author        | Author  | string          |            |
| articlesource | Source  | string          |            |
| tags          | Tags    | list:reference  | direct     |
| notes         | Content | text            |            |

---

## Has / Don't Have  *(boolean presence check, no field-level search)*

These tables are searched only as "does this model have at least one?" or "does this model have none?".
No individual fields are exposed to the QueryBuilder.

| Table          | Check label              |
|----------------|--------------------------|
| db.attachment  | Has attachment           |
| db.todo        | Has open to-do items     |
| db.images      | Has images               |

---

## Tables Not Included in Search Scope

| Table                                                       | Reason                                                          |
|-------------------------------------------------------------|-----------------------------------------------------------------|
| db.eflite_time                                              | Very little search value; efficiency records are view-only      |
| db.supportitem                                              | Per-model support notes, not search criteria                    |
| db.paint / db.model_paint                                   | Low search demand                                               |
| db.switch / db.switch_position                              | Configuration detail, low search demand                         |
| db.url                                                      | Links, not searchable                                           |
| db.lookup / db.modelstate / db.chemistry / db.componenttype | Reference/config tables                                         |
| db.migrations / db.tag                                      | System tables                                                   |

## Activity Search — Potential Separate Feature

`db.activity` has its own search shape (date ranges, type, location, duration) that doesn't map cleanly onto a model-centric QueryBuilder. Suggested as a future stand-alone search page rather than part of the main model search.
