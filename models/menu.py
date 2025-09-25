# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

icon_size = 24

response.menu = [
    # (T('Home'), False, URL('default', 'index'), []),
    (T('ATF'), False, URL('model', 'atthefield'), []),
    (T('Dash'), False, URL('default', 'setui', args=['dashboard'])),
    (T('Calendar'), False, URL('activity', 'calendar'), []),
    (T('Library'), False, URL('library', 'index'), []),
    (T('Packing List'), False, URL('packinglist', 'select')),

    # (T('|'), False, '#'),
    (T('List'), False, '#', [
        (DIV(controller_icon('model',       icon_size), ' Model'       ), False, URL('model', 'listview')),
        (DIV(controller_icon('component',   icon_size), ' Component'   ), False, URL('component', 'listview')),
        (DIV(controller_icon('battery',     icon_size), ' Battery'     ), False, URL('battery', 'listview')),
        (DIV(controller_icon('sailrig',     icon_size), ' Sailing Rigs'), False, URL('sailrig', 'listview')),
        (DIV(controller_icon('tool',        icon_size), ' Tool'        ), False, URL('tool', 'listview')),
        (DIV(controller_icon('activity',    icon_size), ' Activity'    ), False, URL('activity', 'listview')),
        (DIV(controller_icon('todo',        icon_size), ' Todo'        ), False, URL('todo', 'listview')),
        (DIV(controller_icon('packingitem', icon_size), ' Packing Item'), False, URL('packinglist', 'allitems')),
        (DIV(controller_icon('transmitter', icon_size), ' Transmitter' ), False, URL('transmitter', 'listview')),
        (DIV(controller_icon('image',       icon_size), ' Images'      ), False, URL('image', 'index')),
        (DIV(controller_icon('component',   icon_size), ' Inventory'   ), False, URL('component', 'inventory')),
        (DIV(controller_icon('protocol',    icon_size), ' Protocol'    ), False, URL('protocol', 'listview')),
        (DIV(controller_icon('wtc',         icon_size), ' WTC'         ), False, URL('wtc', 'listview')),
        (DIV(controller_icon('tag',         icon_size), ' Tags'         ), False, URL('tag', 'listview')),
    ]),
    (T('New'), False, '#', [
        (DIV(controller_icon('model',       icon_size), ' Model'       ), False, URL('model', 'update')),
        (DIV(controller_icon('component',   icon_size), ' Component'   ), False, URL('component', 'update')),
        (DIV(controller_icon('battery',     icon_size), ' Battery'     ), False, URL('battery', 'update')),
        (DIV(controller_icon('tool',        icon_size), ' Tool'        ), False, URL('tool', 'update')),
        (DIV(controller_icon('activity',    icon_size), ' Activity'    ), False, URL('activity', 'update')),
        (DIV(controller_icon('todo',        icon_size), ' Todo'        ), False, URL('todo', 'update')),
        (DIV(controller_icon('transmitter', icon_size), ' Transmitter' ), False, URL('transmitter', 'update')),
        (DIV(controller_icon('wtc',         icon_size), ' WTC'         ), False, URL('wtc', 'update')),
    ]),
]

# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. you can remove everything below in production
# ----------------------------------------------------------------------------------------------------------------------

# if not configuration.get('app.production'):
#    _app = request.application
