
# =============================================================================
# SEARCH FIELD REGISTRY  (models/m_search.py)
# =============================================================================
# Defines every field available in the advanced QueryBuilder search.
# The controller and view are fully driven from SEARCH_FIELDS — you never
# need to touch either to add a new field.
#
# HOW TO ADD A NEW FIELD
# ----------------------
# 1. Append one dict to SEARCH_FIELDS (see template below).
# 2. Restart the app.  That's it.
#
# FIELD DICT TEMPLATE
# -------------------
# {
#   'id'       : str  — unique key; appears in the saved JSON rule tree
#   'label'    : str  — shown in the QueryBuilder dropdown
#   'group'    : str  — optgroup header (e.g. 'Model', 'Components')
#   'type'     : str  — 'string' | 'integer' | 'double' | 'boolean' | 'date'
#   'input'    : str  — 'text' | 'select' | 'radio' | 'number' | 'checkbox'
#   'operators': list — QB operator names, or None to use QB type defaults
#   'values'   : dict | callable | None
#                  dict      → {value: label, ...}  (static)
#                  callable  → called at request time, returns same dict
#                  None      → no values (free-text / numeric inputs)
#   'table'    : str  — db table name the field lives on (e.g. 'component')
#   'field'    : str  — field name on that table
#   'join'     : None | dict — see JOIN TYPES below
# }
#
# JOIN TYPES
# ----------
# join=None
#   Direct field on db.model.  Condition applied straight to model query.
#
# join={'bridge': ..., 'bridge_fk': ..., 'bridge_model_fk': ..., 'target': ...}
#   Cross-table via a bridge (join) table, e.g. model_component.
#   bridge          — bridge table name  (e.g. 'model_component')
#   bridge_fk       — field on bridge pointing to target.id
#   bridge_model_fk — field on bridge pointing to model.id
#   target          — target table name  (e.g. 'component')
#   extra_condition — optional callable returning an extra DAL condition on
#                     the target table (e.g. filter by componenttype)
#
# join={'direct_model_fk': True, 'model_fk_field': ..., 'target': ...}
#   Target table has its own direct FK back to model (no bridge needed).
#   model_fk_field  — field on the target table pointing to model.id
#   target          — target table name  (e.g. 'propeller')
#
# join={'model_fk': ..., 'target': ...}
#   db.model itself holds a FK to the target table (e.g. model.transmitter).
#   model_fk        — field name on db.model  (e.g. 'transmitter')
#   target          — target table name
#
# join={'existence_check': True, 'bridge': ..., 'bridge_model_fk': ...,
#       'condition_fn': callable | None}
#   Boolean presence test: "does this model have at least one related row?"
#   condition_fn    — optional callable returning extra DAL filter on bridge
#                     (e.g. lambda: db.todo.complete == False)
# =============================================================================

import json as _json

# ---------------------------------------------------------------------------
# Value helpers — return callables so DB is hit at request time, not import
# ---------------------------------------------------------------------------

def _lookup_vals(category):
    """Values from db.lookup for a given category."""
    def fn():
        rows = db(db.lookup.category == category).select(
            db.lookup.name, orderby=db.lookup.sort_order)
        return {r.name: r.name for r in rows}
    return fn

def _table_vals(tbl_name, name_field, order_field=None):
    """Values from any table."""
    def fn():
        tbl = db[tbl_name]
        orderby = tbl[order_field] if order_field else tbl[name_field]
        rows = db().select(tbl[name_field], orderby=orderby)
        return {r[name_field]: r[name_field] for r in rows}
    return fn

_YES_NO = {'1': 'Yes', '0': 'No'}

# ---------------------------------------------------------------------------
# SEARCH_FIELDS — the single source of truth for the search UI
# ---------------------------------------------------------------------------

SEARCH_FIELDS = [

    # =========================================================================
    # GROUP: Model
    # =========================================================================
    {
        'id': 'name', 'label': 'Name', 'group': 'Model',
        'type': 'string', 'input': 'text',
        'operators': ['contains', 'not_contains', 'equal', 'begins_with',
                      'is_empty', 'is_not_empty'],
        'values': None, 'table': 'model', 'field': 'name', 'join': None,
    },
    {
        'id': 'modeltype', 'label': 'Type', 'group': 'Model',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal', 'in', 'not_in'],
        'values': _lookup_vals('modeltype'),
        'table': 'model', 'field': 'modeltype', 'join': None,
    },
    {
        'id': 'modelcategory', 'label': 'Category', 'group': 'Model',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal'],
        'values': _lookup_vals('modelcategory'),
        'table': 'model', 'field': 'modelcategory', 'join': None,
    },
    {
        'id': 'modelstate', 'label': 'State', 'group': 'Model',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal', 'in', 'not_in'],
        'values': _table_vals('modelstate', 'name'),
        'table': 'model', 'field': 'modelstate', 'join': None,
    },
    {
        'id': 'modelorigin', 'label': 'Origin', 'group': 'Model',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal', 'is_empty', 'is_not_empty'],
        'values': _lookup_vals('modelorigin'),
        'table': 'model', 'field': 'modelorigin', 'join': None,
    },
    {
        'id': 'manufacturer', 'label': 'Manufacturer', 'group': 'Model',
        'type': 'string', 'input': 'text',
        'operators': ['contains', 'equal', 'begins_with', 'is_empty', 'is_not_empty'],
        'values': None, 'table': 'model', 'field': 'manufacturer', 'join': None,
    },
    {
        'id': 'controltype', 'label': 'Control Type', 'group': 'Model',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal', 'is_empty', 'is_not_empty'],
        'values': _lookup_vals('controltype'),
        'table': 'model', 'field': 'controltype', 'join': None,
    },
    {
        'id': 'powerplant', 'label': 'Power Plant', 'group': 'Model',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal', 'is_empty', 'is_not_empty'],
        'values': _lookup_vals('powerplant'),
        'table': 'model', 'field': 'powerplant', 'join': None,
    },
    {
        'id': 'subjecttype', 'label': 'Subject Type', 'group': 'Model',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal', 'is_empty', 'is_not_empty'],
        'values': _lookup_vals('subjecttype'),
        'table': 'model', 'field': 'subjecttype', 'join': None,
    },
    {
        'id': 'haveplans', 'label': 'Has Plans', 'group': 'Model',
        'type': 'boolean', 'input': 'radio',
        'operators': ['equal'], 'values': _YES_NO,
        'table': 'model', 'field': 'haveplans', 'join': None,
    },
    {
        'id': 'havekit', 'label': 'Have Kit/Model', 'group': 'Model',
        'type': 'boolean', 'input': 'radio',
        'operators': ['equal'], 'values': _YES_NO,
        'table': 'model', 'field': 'havekit', 'join': None,
    },
    {
        'id': 'kitlocation', 'label': 'Kit/Plan Location', 'group': 'Model',
        'type': 'string', 'input': 'text',
        'operators': ['contains', 'equal', 'is_empty', 'is_not_empty'],
        'values': None, 'table': 'model', 'field': 'kitlocation', 'join': None,
    },

    # =========================================================================
    # GROUP: Model Attributes
    # =========================================================================
    {
        'id': 'attr_scale', 'label': 'Scale', 'group': 'Model Attributes',
        'type': 'string', 'input': 'text',
        'operators': ['equal', 'contains', 'is_empty', 'is_not_empty'],
        'values': None, 'table': 'model', 'field': 'attr_scale', 'join': None,
    },
    {
        'id': 'attr_weight_oz', 'label': 'Weight (oz)', 'group': 'Model Attributes',
        'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'between', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_weight_oz', 'join': None,
    },
    {
        'id': 'attr_length', 'label': 'Length (mm)', 'group': 'Model Attributes',
        'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'between', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_length', 'join': None,
    },
    {
        'id': 'attr_width', 'label': 'Width/Beam (mm)', 'group': 'Model Attributes',
        'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'between', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_width', 'join': None,
    },
    {
        'id': 'attr_height', 'label': 'Height (mm)', 'group': 'Model Attributes',
        'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'between', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_height', 'join': None,
    },
    {
        'id': 'attr_flight_timer', 'label': 'Flight Timer (min)',
        'group': 'Model Attributes', 'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_flight_timer', 'join': None,
    },
    {
        'id': 'attr_construction', 'label': 'Construction', 'group': 'Model Attributes',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal', 'is_empty', 'is_not_empty'],
        'values': _lookup_vals('attr_construction'),
        'table': 'model', 'field': 'attr_construction', 'join': None,
    },
    {
        'id': 'attr_covering', 'label': 'Covering', 'group': 'Model Attributes',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal', 'is_empty', 'is_not_empty'],
        'values': _lookup_vals('attr_covering'),
        'table': 'model', 'field': 'attr_covering', 'join': None,
    },

    # =========================================================================
    # GROUP: Airplane
    # =========================================================================
    {
        'id': 'attr_plane_wingspan_mm', 'label': 'Wingspan (mm)', 'group': 'Airplane',
        'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'between', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_plane_wingspan_mm', 'join': None,
    },
    {
        'id': 'attr_plane_wingarea', 'label': 'Wing Area (sqin)', 'group': 'Airplane',
        'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'between', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_plane_wingarea', 'join': None,
    },
    {
        'id': 'attr_plane_rem_wings', 'label': 'Removable Wings', 'group': 'Airplane',
        'type': 'boolean', 'input': 'radio',
        'operators': ['equal'], 'values': _YES_NO,
        'table': 'model', 'field': 'attr_plane_rem_wings', 'join': None,
    },

    # =========================================================================
    # GROUP: Helicopter / Multirotor
    # =========================================================================
    {
        'id': 'attr_copter_size', 'label': 'Heli Size',
        'group': 'Helicopter / Multirotor', 'type': 'integer', 'input': 'number',
        'operators': ['equal', 'not_equal', 'greater', 'less', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_copter_size', 'join': None,
    },
    {
        'id': 'attr_copter_mainrotor_length', 'label': 'Main Rotor Length (mm)',
        'group': 'Helicopter / Multirotor', 'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_copter_mainrotor_length', 'join': None,
    },
    {
        'id': 'attr_multi_rotor_count', 'label': 'Rotor Count',
        'group': 'Helicopter / Multirotor', 'type': 'integer', 'input': 'number',
        'operators': ['equal', 'not_equal', 'greater', 'less', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_multi_rotor_count', 'join': None,
    },

    # =========================================================================
    # GROUP: Boat / Submarine
    # =========================================================================
    {
        'id': 'attr_boat_draft', 'label': 'Draft (mm)', 'group': 'Boat / Submarine',
        'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_boat_draft', 'join': None,
    },

    # =========================================================================
    # GROUP: Car
    # =========================================================================
    {
        'id': 'attr_car_bodystyle', 'label': 'Body Style', 'group': 'Car',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal', 'is_empty', 'is_not_empty'],
        'values': _lookup_vals('attr_car_bodystyle'),
        'table': 'model', 'field': 'attr_car_bodystyle', 'join': None,
    },
    {
        'id': 'attr_car_wheelbase', 'label': 'Wheelbase (mm)', 'group': 'Car',
        'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'is_null', 'is_not_null'],
        'values': None, 'table': 'model', 'field': 'attr_car_wheelbase', 'join': None,
    },

    # =========================================================================
    # GROUP: Components
    # Cross-table via model_component bridge.
    # =========================================================================
    {
        'id': 'component_type', 'label': 'Component Type', 'group': 'Components',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal', 'in', 'not_in'],
        'values': _table_vals('componenttype', 'name', 'sort_order'),
        'table': 'component', 'field': 'componenttype',
        'join': {'bridge': 'model_component', 'bridge_fk': 'component',
                 'bridge_model_fk': 'model', 'target': 'component'},
    },
    {
        'id': 'component_manufacturer', 'label': 'Component Manufacturer',
        'group': 'Components', 'type': 'string', 'input': 'text',
        'operators': ['contains', 'equal', 'begins_with', 'is_empty', 'is_not_empty'],
        'values': None, 'table': 'component', 'field': 'manufacturer',
        'join': {'bridge': 'model_component', 'bridge_fk': 'component',
                 'bridge_model_fk': 'model', 'target': 'component'},
    },
    {
        'id': 'component_amps_in', 'label': 'Component Rated Amps In',
        'group': 'Components', 'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'is_null', 'is_not_null'],
        'values': None, 'table': 'component', 'field': 'attr_amps_in',
        'join': {'bridge': 'model_component', 'bridge_fk': 'component',
                 'bridge_model_fk': 'model', 'target': 'component'},
    },
    {
        'id': 'component_motor_kv', 'label': 'Motor KV',
        'group': 'Components', 'type': 'integer', 'input': 'number',
        'operators': ['equal', 'not_equal', 'greater', 'greater_or_equal',
                      'less', 'less_or_equal', 'is_null', 'is_not_null'],
        'values': None, 'table': 'component', 'field': 'attr_motor_kv',
        'join': {'bridge': 'model_component', 'bridge_fk': 'component',
                 'bridge_model_fk': 'model', 'target': 'component'},
    },
    {
        'id': 'component_voltage_in', 'label': 'Component Max Voltage In',
        'group': 'Components', 'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'is_null', 'is_not_null'],
        'values': None, 'table': 'component', 'field': 'attr_voltage_in',
        'join': {'bridge': 'model_component', 'bridge_fk': 'component',
                 'bridge_model_fk': 'model', 'target': 'component'},
    },
    {
        'id': 'component_channel_count', 'label': 'Component Channel Count',
        'group': 'Components', 'type': 'integer', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less', 'less_or_equal'],
        'values': None, 'table': 'component', 'field': 'attr_channel_count',
        'join': {'bridge': 'model_component', 'bridge_fk': 'component',
                 'bridge_model_fk': 'model', 'target': 'component'},
    },
    {
        'id': 'component_displacement_cc', 'label': 'Engine Displacement (cc)',
        'group': 'Components', 'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'is_null', 'is_not_null'],
        'values': None, 'table': 'component', 'field': 'attr_displacement_cc',
        'join': {'bridge': 'model_component', 'bridge_fk': 'component',
                 'bridge_model_fk': 'model', 'target': 'component'},
    },
    {
        'id': 'component_watts_in', 'label': 'Component Max Watts In',
        'group': 'Components', 'type': 'double', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less',
                      'less_or_equal', 'is_null', 'is_not_null'],
        'values': None, 'table': 'component', 'field': 'attr_watts_in',
        'join': {'bridge': 'model_component', 'bridge_fk': 'component',
                 'bridge_model_fk': 'model', 'target': 'component'},
    },

    # =========================================================================
    # GROUP: Battery  (via model_battery bridge)
    # =========================================================================
    {
        'id': 'battery_chemistry', 'label': 'Battery Chemistry', 'group': 'Battery',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal'],
        'values': _table_vals('chemistry', 'name'),
        'table': 'battery', 'field': 'chemistry',
        'join': {'bridge': 'model_battery', 'bridge_fk': 'battery',
                 'bridge_model_fk': 'model', 'target': 'battery'},
    },
    {
        'id': 'battery_cellcount', 'label': 'Battery Cell Count (S)',
        'group': 'Battery', 'type': 'integer', 'input': 'number',
        'operators': ['equal', 'not_equal', 'greater', 'greater_or_equal',
                      'less', 'less_or_equal'],
        'values': None, 'table': 'battery', 'field': 'cellcount',
        'join': {'bridge': 'model_battery', 'bridge_fk': 'battery',
                 'bridge_model_fk': 'model', 'target': 'battery'},
    },
    {
        'id': 'battery_mah', 'label': 'Battery Capacity (mAh)',
        'group': 'Battery', 'type': 'integer', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less', 'less_or_equal'],
        'values': None, 'table': 'battery', 'field': 'mah',
        'join': {'bridge': 'model_battery', 'bridge_fk': 'battery',
                 'bridge_model_fk': 'model', 'target': 'battery'},
    },
    {
        'id': 'battery_crating', 'label': 'Battery C Rating',
        'group': 'Battery', 'type': 'integer', 'input': 'number',
        'operators': ['equal', 'greater', 'greater_or_equal', 'less', 'less_or_equal'],
        'values': None, 'table': 'battery', 'field': 'crating',
        'join': {'bridge': 'model_battery', 'bridge_fk': 'battery',
                 'bridge_model_fk': 'model', 'target': 'battery'},
    },

    # =========================================================================
    # GROUP: Transmitter / Protocol
    # db.model holds a direct FK (model.transmitter, model.protocol).
    # =========================================================================
    {
        'id': 'transmitter_name', 'label': 'Transmitter',
        'group': 'Transmitter / Protocol', 'type': 'string', 'input': 'text',
        'operators': ['contains', 'equal', 'begins_with', 'is_empty', 'is_not_empty'],
        'values': None, 'table': 'transmitter', 'field': 'name',
        'join': {'model_fk': 'transmitter', 'target': 'transmitter'},
    },
    {
        'id': 'transmitter_manufacturer', 'label': 'Transmitter Manufacturer',
        'group': 'Transmitter / Protocol', 'type': 'string', 'input': 'text',
        'operators': ['contains', 'equal', 'is_empty', 'is_not_empty'],
        'values': None, 'table': 'transmitter', 'field': 'manufacturer',
        'join': {'model_fk': 'transmitter', 'target': 'transmitter'},
    },
    {
        'id': 'protocol_name', 'label': 'Protocol',
        'group': 'Transmitter / Protocol', 'type': 'string', 'input': 'text',
        'operators': ['contains', 'equal', 'is_empty', 'is_not_empty'],
        'values': None, 'table': 'protocol', 'field': 'name',
        'join': {'model_fk': 'protocol', 'target': 'protocol'},
    },

    # =========================================================================
    # GROUP: Tools  (via model_tool bridge)
    # =========================================================================
    {
        'id': 'tool_name', 'label': 'Tool Name', 'group': 'Tools',
        'type': 'string', 'input': 'text',
        'operators': ['contains', 'equal', 'is_empty', 'is_not_empty'],
        'values': None, 'table': 'tool', 'field': 'name',
        'join': {'bridge': 'model_tool', 'bridge_fk': 'tool',
                 'bridge_model_fk': 'model', 'target': 'tool'},
    },
    {
        'id': 'tool_type', 'label': 'Tool Type', 'group': 'Tools',
        'type': 'string', 'input': 'select',
        'operators': ['equal', 'not_equal'],
        'values': _lookup_vals('tooltype'),
        'table': 'tool', 'field': 'tooltype',
        'join': {'bridge': 'model_tool', 'bridge_fk': 'tool',
                 'bridge_model_fk': 'model', 'target': 'tool'},
    },

    # =========================================================================
    # GROUP: Propeller
    # propeller has a direct model FK (propeller.model).
    # =========================================================================
    {
        'id': 'propeller', 'label': 'Propeller', 'group': 'Propeller',
        'type': 'string', 'input': 'text',
        'operators': ['contains', 'equal', 'begins_with', 'is_empty', 'is_not_empty'],
        'values': None, 'table': 'propeller', 'field': 'item',
        'join': {'direct_model_fk': True, 'model_fk_field': 'model', 'target': 'propeller'},
    },

    # =========================================================================
    # GROUP: Has / Don't Have
    # Existence checks — value '1' = has at least one, '0' = has none.
    # =========================================================================
    {
        'id': 'has_attachment', 'label': 'Has Attachment',
        'group': "Has / Don't Have", 'type': 'boolean', 'input': 'radio',
        'operators': ['equal'], 'values': _YES_NO,
        'table': 'attachment', 'field': 'id',
        'join': {'existence_check': True, 'bridge': 'attachment',
                 'bridge_model_fk': 'model', 'condition_fn': None},
    },
    {
        'id': 'has_open_todo', 'label': 'Has Open To-Do',
        'group': "Has / Don't Have", 'type': 'boolean', 'input': 'radio',
        'operators': ['equal'], 'values': _YES_NO,
        'table': 'todo', 'field': 'id',
        'join': {'existence_check': True, 'bridge': 'todo',
                 'bridge_model_fk': 'model',
                 'condition_fn': lambda: db.todo.complete == False},
    },
]

# ---------------------------------------------------------------------------
# QueryBuilder JS config builder
# ---------------------------------------------------------------------------

def get_qb_field_config():
    """
    Build the jQuery QueryBuilder `filters` array (as a JSON string) from
    SEARCH_FIELDS.  Called once per search page request.
    """
    filters = []
    optgroups = {}
    for f in SEARCH_FIELDS:
        cfg = {
            'id':       f['id'],
            'label':    f['label'],
            'type':     f['type'],
            'input':    f['input'],
            'optgroup': f['group'],
        }
        if f.get('operators'):
            cfg['operators'] = f['operators']
        vals = f.get('values')
        if callable(vals):
            vals = vals()
        if vals:
            cfg['values'] = vals
        filters.append(cfg)
        optgroups[f['group']] = f['group']

    return _json.dumps({'filters': filters, 'optgroups': optgroups})


# ---------------------------------------------------------------------------
# DAL query parser
# ---------------------------------------------------------------------------

def parse_search_query(rules_dict):
    """
    Recursively parse a QueryBuilder JSON rule tree into a single web2py DAL
    condition on db.model.  Returns None if the tree is empty or invalid.

    Usage in a controller:
        condition = parse_search_query(json.loads(request.vars.q))
        rows = db(condition).select(db.model.ALL) if condition else []
    """
    if not rules_dict or 'rules' not in rules_dict:
        return None

    condition = rules_dict.get('condition', 'AND').upper()
    parts = []

    for rule in rules_dict.get('rules', []):
        if 'condition' in rule:
            sub = parse_search_query(rule)
            if sub is not None:
                parts.append(sub)
        else:
            expr = _build_rule_condition(rule)
            if expr is not None:
                parts.append(expr)

    if not parts:
        return None
    result = parts[0]
    for p in parts[1:]:
        result = (result | p) if condition == 'OR' else (result & p)
    return result


def _build_rule_condition(rule):
    """Translate one QueryBuilder rule dict into a DAL condition on db.model."""
    fdef = next((f for f in SEARCH_FIELDS if f['id'] == rule.get('id')), None)
    if not fdef:
        return None

    join = fdef.get('join')
    dal_field = db[fdef['table']][fdef['field']]
    operator  = rule.get('operator', 'equal')
    value     = rule.get('value')

    # --- Existence check ---
    if join and join.get('existence_check'):
        bridge     = db[join['bridge']]
        model_fk   = bridge[join['bridge_model_fk']]
        cond_fn    = join.get('condition_fn')
        base       = cond_fn() if cond_fn else (bridge.id > 0)
        model_ids  = db(base).select(model_fk, distinct=True)
        if value in ('1', True, 1):
            return db.model.id.belongs(model_ids)
        else:
            return ~db.model.id.belongs(model_ids)

    # Build condition on the target table
    target_cond = _apply_operator(dal_field, operator, value, fdef)
    if target_cond is None:
        return None

    # --- Direct model field ---
    if join is None:
        return target_cond

    # --- Bridge (join) table ---
    if 'bridge' in join:
        bridge   = db[join['bridge']]
        tgt      = db[join['target']]
        extra_fn = join.get('extra_condition')
        q        = (target_cond & extra_fn()) if extra_fn else target_cond
        tgt_ids  = db(q).select(tgt.id)
        model_ids = db(bridge[join['bridge_fk']].belongs(tgt_ids)).select(
                        bridge[join['bridge_model_fk']], distinct=True)
        return db.model.id.belongs(model_ids)

    # --- Direct FK on target table back to model ---
    if join.get('direct_model_fk'):
        tgt       = db[join['target']]
        model_ids = db(target_cond).select(tgt[join['model_fk_field']], distinct=True)
        return db.model.id.belongs(model_ids)

    # --- FK on db.model pointing to target ---
    if 'model_fk' in join:
        tgt      = db[join['target']]
        tgt_ids  = db(target_cond).select(tgt.id)
        return db.model[join['model_fk']].belongs(tgt_ids)

    return None


def _apply_operator(field, operator, value, fdef):
    """Map a QueryBuilder operator string to a DAL expression."""
    ftype = fdef.get('type', 'string')
    # Coerce value to the right Python type
    try:
        if ftype == 'integer':
            if isinstance(value, list):
                value = [int(v) for v in value]
            else:
                value = int(value)
        elif ftype == 'double':
            if isinstance(value, list):
                value = [float(v) for v in value]
            else:
                value = float(value)
        elif ftype == 'boolean':
            value = value in ('1', 'true', True, 1)
    except (TypeError, ValueError):
        return None

    ops = {
        'equal':            lambda f, v: f == v,
        'not_equal':        lambda f, v: f != v,
        'contains':         lambda f, v: f.contains(v),
        'not_contains':     lambda f, v: ~f.contains(v),
        'begins_with':      lambda f, v: f.startswith(v),
        'ends_with':        lambda f, v: f.endswith(v),
        'greater':          lambda f, v: f > v,
        'greater_or_equal': lambda f, v: f >= v,
        'less':             lambda f, v: f < v,
        'less_or_equal':    lambda f, v: f <= v,
        'is_null':          lambda f, v: f == None,
        'is_not_null':      lambda f, v: f != None,
        'is_empty':         lambda f, v: (f == None) | (f == ''),
        'is_not_empty':     lambda f, v: (f != None) & (f != ''),
        'in':               lambda f, v: f.belongs(v if isinstance(v, list) else [v]),
        'not_in':           lambda f, v: ~f.belongs(v if isinstance(v, list) else [v]),
        'between':          lambda f, v: (f >= v[0]) & (f <= v[1]),
    }
    fn = ops.get(operator)
    return fn(field, value) if fn else None
