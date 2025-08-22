# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

icon_size = '24px'

response.menu = [
    # (T('Home'), False, URL('default', 'index'), []),
    (T('ATF'), False, URL('model', 'atthefield'), []),
    (T('Calendar'), False, URL('activity', 'calendar'), []),
    (T('Library'), False, URL('library', 'index'), []),
    (T('Packing List'), False, URL('packinglist', 'select')),

    # (T('|'), False, '#'),
    (T('List'), False, '#', [

        (DIV(IMG(_src=URL('static', 'icons/plane.png'), _width=icon_size,
                 _height=icon_size), ' Model'), False, URL('model', 'listview')),
        (DIV(IMG(_src=URL('static', 'icons/icons8-gearbox-64.png'), _width=icon_size,
                 _height=icon_size), ' Component'), False, URL('component', 'listview.html')),
        (DIV(IMG(_src=URL('static', 'icons/icons8-low-battery-80.png'), _width=icon_size,
                 _height=icon_size), ' Battery'), False, URL('battery', 'listview')),
        (DIV(IMG(_src=URL('static', 'icons/boat-48.svg'), _width=icon_size,
                 _height=icon_size), ' Sailing Rigs'), False, URL('sailrig', 'listview')),
        (DIV(IMG(_src=URL('static', 'icons/icons8-wrench-50.png'), _width=icon_size,
                 _height=icon_size), ' Tool'), False, URL('tool', 'listview')),
        (DIV(IMG(_src=URL('static', 'icons/icons8-calendar-50.png'), _width=icon_size,
                 _height=icon_size), ' Activity'), False, URL('activity', 'listview')),
        (DIV(IMG(_src=URL('static', 'icons/icons8-checklist-50.png'), _width=icon_size,
                 _height=icon_size), ' Todo'), False, URL('todo', 'listview')),
        (DIV(IMG(_src=URL('static', 'icons/briefcase.png'), _width=icon_size,
                 _height=icon_size), ' Packing Item'), False, URL('packinglist', 'allitems')),
        (DIV(IMG(_src=URL('static', 'icons/gamepad.png'), _width=icon_size,
                 _height=icon_size), ' Transmitters'), False, URL('transmitter', 'listview')),
        (DIV(IMG(_src=URL('static', 'icons/image.png'), _width=icon_size, 
                 _height=icon_size), ' Images'), False, URL('image', 'index')),
        (DIV(IMG(_src=URL('static', 'icons/003-tasks.png'), _width=icon_size, 
                 _height=icon_size), ' Inventory'), False, URL('component', 'inventory')),
        (DIV(IMG(_src=URL('static', 'icons/003-tasks.png'), _width=icon_size, 
                 _height=icon_size), ' Protocols'), False, URL('protocol', 'index')),
    ]),
    (T('Dash'), False, URL('default', 'setui', args=['dashboard'])),
]


response.menu_buttons = [
    ('New Model', False, URL('model', 'update'),
     IMG(_src=URL('static', 'icons/plane.png'),
         _alt='New Model', _title='New Model', _width=icon_size, _height=icon_size)),
    ('New Component', False, URL('component', 'update'),
     IMG(_src=URL('static', 'icons/icons8-gearbox-64.png'),
         _alt='New Component', _title='New Component', _width=icon_size, _height=icon_size)),
    ('New Battery', False, URL('battery', 'update'),
     IMG(_src=URL('static', 'icons/icons8-low-battery-80.png'),
         _alt='New Battery', _title='New Battery', _width=icon_size, _height=icon_size)),
    ('New Tool', False, URL('tool', 'update'),
     IMG(_src=URL('static', 'icons/icons8-wrench-50.png'),
         _alt='New Tool', _title='New Tool', _width=icon_size, _height=icon_size)),
    ('New Activity', False, URL('activity', 'update'),
     IMG(_src=URL('static', 'icons/icons8-calendar-50.png'),
         _alt='New Activity', _title='New Activity', _width=icon_size, _height=icon_size)),
    ('New Todo', False, URL('todo', 'update'),
     IMG(_src=URL('static', 'icons/icons8-checklist-50.png'),
         _alt='New Todo', _title='New Todo', _width=icon_size, _height=icon_size)),
    ('New Transmitter', False, URL('transmitter', 'update'), IMG(_src=URL('static', 'icons/gamepad.png'), _alt='New Transmitter', _title='New Transmitter', _width=icon_size, _height=icon_size)),
]
# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. you can remove everything below in production
# ----------------------------------------------------------------------------------------------------------------------

# if not configuration.get('app.production'):
#    _app = request.application
