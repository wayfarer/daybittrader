import sys, os

MANAGE_ROOT = os.path.dirname(os.path.realpath(os.path.dirname(__file__)))
ROOT = os.path.dirname(MANAGE_ROOT)
SUB_ROOT = os.path.dirname(ROOT)
VE_ROOT = os.path.join(SUB_ROOT, 've')

sys.path = ['', os.path.join(VE_ROOT, 'lib/python2.7/site-packages/distribute-0.6.10-py2.7.egg'),
            os.path.join(VE_ROOT, 'lib/python2.7/site-packages/pip-0.7.2-py2.7.egg'),
            os.path.join(VE_ROOT, 'lib/python2.7'),
            os.path.join(VE_ROOT, 'lib/python2.7/plat-linux2'),
            os.path.join(VE_ROOT, 'lib/python2.7/lib-tk'),
            os.path.join(VE_ROOT, 'lib/python2.7/lib-old'),
            os.path.join(VE_ROOT, 'lib/python2.7/lib-dynload'),
            '/usr/lib/python2.7', '/usr/lib64/python2.7', '/usr/lib/python2.7/plat-linux2',
            '/usr/lib/python2.7/lib-tk', '/usr/lib64/python2.7/lib-tk',
            os.path.join(VE_ROOT, 'lib/python2.7/site-packages')]


sys.path.append(ROOT)
sys.path.append(MANAGE_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dbtrade.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


class WsgiEnvironment(object):
    def __init__(self, application):
        self.application = application
        
    def __call__(self, environ, start_response):
        os.environ['DBT_SETTINGS_CONFIG'] = environ['DBT_SETTINGS_CONFIG']
        os.environ['DBT_CB_ID'] = environ['DBT_CB_ID']
        os.environ['DBT_CB_SECRET'] = environ['DBT_CB_SECRET']
        return start_response
    
application = WsgiEnvironment(application)

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
