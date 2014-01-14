from datetime import timedelta
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django import forms
from django.views.decorators.csrf import csrf_exempt
#from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as auth_login, logout as auth_logout
import httplib2

from dbtrade.apps.trader.models import TickerHistory
from dbtrade.utils.apiclient import CoinBaseAPI, coinbase_client


@csrf_exempt
def access_fee(request):
    if request.method == 'POST':
        #: TODO: must have access code: ONE_TIME_ACCESS_FEE
        with open('/tmp/last_request.txt', 'w') as f:
            f.write(str(request.body))
    
    return HttpResponse('{"status": "ok"}', mimetype='application/json')
    #env = {}
    #return render_to_response('about.html', RequestContext(request, env))


@login_required
def connect_coinbase(request):
    coinbase_callback_redirect_to = request.GET.get('redirect_to', None)
    request.session['coinbase_callback_redirect_to'] = coinbase_callback_redirect_to
    return HttpResponse(coinbase_client.step1_get_authorize_url())
    return HttpResponseRedirect(coinbase_client.step1_get_authorize_url())


@login_required
def connect_coinbase_callback(request):
    oauth_code = request.GET.get('code', None)
    if oauth_code == None:
        raise Http404
    
    http = httplib2.Http(ca_certs='/etc/ssl/certs/ca-certificates.crt')
    token = coinbase_client.step2_exchange(oauth_code, http=http)
    
    request.user.usersettings.coinbase_oauth_token = token
    request.user.usersettings.save()
    
    coinbase_callback_redirect_to = request.session.get('coinbase_callback_redirect_to', '/')
    return HttpResponseRedirect(coinbase_callback_redirect_to)
