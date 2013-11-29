from datetime import timedelta
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django import forms
#from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as auth_login, logout as auth_logout

from dbtrade.apps.trader.models import TickerHistory


def access_fee(request):
    if request.method == 'POST':
        #: TODO: must have access code: ONE_TIME_ACCESS_FEE
        with open('/tmp/last_request.txt', 'w') as f:
            f.write(str(request.body))
    
    return HttpResponse('{"status": "ok"}', mimetype='application/json')
    #env = {}
    #return render_to_response('about.html', RequestContext(request, env))
