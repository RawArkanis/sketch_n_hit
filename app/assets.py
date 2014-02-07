from flask.ext.assets import Bundle

from . import wa

js_libs = Bundle('js/libs/jquery.min.js',
                 'js/libs/bootstrap.min.js',
                 'js/libs/lodash.min.js',
                 filters='jsmin',
                 output='js/libs.js')

js_board = Bundle('js/libs/drawingboard.min.js',
                 filters='jsmin',
                 output='js/board.js')

js_main = Bundle('js/main.js',
                 filters='jsmin',
                 output='js/snh.js')

css_main = Bundle('css/bootstrap.min.css',
                  'css/font-awesome.min.css',
                  'css/main.css',
                  filters='cssmin',
                  output='css/snh.css')

css_board = Bundle('css/drawingboard.min.css',
                  filters='cssmin',
                  output='css/board.css')

wa.register('js_libs', js_libs)
wa.register('js_board', js_libs)
wa.register('js_main', js_main)
wa.register('css_main', css_main)
wa.register('css_board', css_main)
