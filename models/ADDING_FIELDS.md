# Adding a Field to `db.model` or `db.component`

These two tables have the most field-driven code in the app. Follow this checklist
to make sure a new field is wired up everywhere it needs to be.

---

## Step 1 — Define the field in `models/db.py`

**For `db.model`** — inside `db.define_table('model', ...)` (~line 347):

```python
Field('attr_plane_mycharprop', type='string', label='My Char Prop',
      comment='Explain what this is'),

Field('attr_plane_mymmprop', type='double', label='My Prop (mm)',
      widget=lambda field, value: SQLFORM.widgets.double.widget(
          field, value, _type='number', _step='any', _class='generic-widget form-control')),
```

**Then add `.extra` for measurement fields** (after the `define_table` block, ~line 590):

```python
db.model.attr_plane_mymmprop.extra = {'measurement': 'mm'}
```

Supported measurement keys: `mm`, `oz`, `dm2`, `sqin`, `cc`.

**For `db.component`** — inside `db.define_table('component', ...)` (~line 747), same
pattern. Add `.extra` after that block (~line 815).

---

## Step 2 — Control which model types/categories show it

**`modeltype_hide_attribs`** (~line 651): add the field name to any model type where it
should be hidden. Leave a type's list empty to show it for all models of that type.

**`modelcategory_hide_attribs`** (~line 672): same, keyed by category
(Dynamic, Static, Non-Model).

> These dicts only **seed** new DB rows. For existing rows the admin UI is the live
> source of truth — changes here won't overwrite what the admin has already saved.

---

## Step 3 — Add it to the admin field-group list

**`controllers/admin.py` — `_MODEL_FIELD_GROUPS`** (~line 85): add the field name to
the appropriate group tuple so it appears in the admin "Fields to Hide" editor.
Without this the field cannot be toggled per model type through the UI.

For `db.component` fields, update **`_COMPONENT_ATTR_GROUPS`** in the same file.

---

## Step 4 — Wire it to the component type *(component fields only)*

The attribute list per component type is stored in `db.componenttype.attrs` and is
**editable through the admin UI** at `/admin/componenttype/<name>`. The runtime
`component_attribs` dict is loaded from the DB at startup, so changes in the admin
take effect immediately on the next request.

To make the new field available for assignment in the admin UI, add it to
**`_COMPONENT_ATTR_GROUPS`** in `controllers/admin.py` (~line 129) under the
appropriate group. Without this it won't appear as a checkbox option.

If this is a brand-new `db.componenttype` row (i.e. a new component type), also add
the default attr list to the hardcoded `component_attribs` dict in `models/db.py`
(~line 832) — this dict seeds `db.componenttype.attrs` on first insert only.

---

## Step 5 — Add it to the model update view *(model fields only, if type-specific)*

`attr_*` fields on `db.component` render automatically via a loop in
`views/component/update.html` — nothing to add there.

For `db.model`:

- **General attrs** (`attr_construction`, `attr_covering`, etc.) auto-appear in the
  Attributes collapsible section — nothing to add.
- **Type-specific attrs** (Airplane-only, Boat-only, etc.) need an explicit call in the
  matching collapsible section of `views/model/update.html` (~line 115):

```html
{{=makeFormField(form, 'attr_plane_mymmprop', FormFieldType.COLUMNS, columns=6)}}
```

---

## Step 6 — Register it in search

**`models/m_search.py` — `SEARCH_FIELDS`** list (~line 92): append a dict.

**Direct `db.model` field:**

```python
{
    'id'       : 'attr_plane_mymmprop',
    'label'    : 'My Prop (mm)',
    'group'    : 'Airplane',        # optgroup header in the query-builder dropdown
    'type'     : 'double',          # 'string' | 'integer' | 'double' | 'boolean'
    'input'    : 'number',          # 'text' | 'select' | 'number' | 'radio'
    'operators': ['equal', 'greater', 'greater_or_equal', 'less', 'less_or_equal',
                  'between', 'is_null', 'is_not_null'],
    'values'   : None,
    'table'    : 'model',
    'field'    : 'attr_plane_mymmprop',
    'join'     : None,              # None = column lives directly on db.model
}
```

**`db.component` field reachable from a model** (bridge join via `model_component`):

```python
{
    ...
    'table' : 'component',
    'field' : 'attr_motor_kv',
    'join'  : {
        'bridge'          : 'model_component',
        'bridge_fk'       : 'component',
        'bridge_model_fk' : 'model',
        'target'          : 'component',
    },
}
```

---

## Optional steps

| Situation | What to do |
|---|---|
| Field needs a computed or reformatted display value | Add a `Field.Method` on `db.model` after `define_table` (~line 424 in `db.py`) |
| Field should appear in the component export card | Add it explicitly to `renderexport()` in `controllers/component.py` (~line 403); use `ConvertMeasurementField()` for measurement fields |
| Field takes values from a lookup table | Set `requires=IS_IN_SET(...)` or `IS_EMPTY_OR(IS_IN_SET(...))` on the field, and use `'input': 'select'` + `'values': _lookup_vals('category_name')` in SEARCH_FIELDS |

---

## What is automatic — no extra steps needed

- `makeFormField()` reads `.label`, `.comment`, and `.extra['measurement']` directly
  from the DAL definition and renders the unit-converter button automatically.
- `ConvertMeasurementField()` works for any field that has `.extra['measurement']`.
- The component update form auto-renders all `attr_*` fields via a loop —
  only physical dimensions (`attr_length`, `attr_width`, `attr_height`, `attr_weight_oz`)
  are listed explicitly.

---

## Quick checklist

- [ ] Field defined in `db.define_table(...)` with `label` and `comment`
- [ ] `.extra = {'measurement': '...'}` added if applicable
- [ ] `modeltype_hide_attribs` / `modelcategory_hide_attribs` updated
- [ ] `_MODEL_FIELD_GROUPS` (or `_COMPONENT_ATTR_GROUPS`) updated in `admin.py`
- [ ] *(component only)* field added to `_COMPONENT_ATTR_GROUPS` in `admin.py` so it appears in the admin UI
- [ ] *(component only, new component type only)* default attr list added to hardcoded `component_attribs` in `db.py` for seeding
- [ ] *(model, type-specific only)* `makeFormField()` call added to `update.html`
- [ ] Entry added to `SEARCH_FIELDS` in `m_search.py`
