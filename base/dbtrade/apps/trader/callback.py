from datetime import timedelta
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django import forms
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
#from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as auth_login, logout as auth_logout
import httplib2

from dbtrade.apps.trader.models import TickerHistory, UserSettings, User
from dbtrade.utils.apiclient import CoinBaseAPI, coinbase_oauth_client
#from dbtrade.utils.utils import get_user_cb_api


@csrf_exempt
def access_fee(request):
    if request.method == 'POST':
        #: TODO: must have access code: ONE_TIME_ACCESS_FEE
        with open('/tmp/last_request.txt', 'w') as f:
            f.write(str(request.body))
    
    return HttpResponse('{"status": "ok"}', mimetype='application/json')
    #env = {}
    #return render_to_response('about.html', RequestContext(request, env))


#@login_required(login_url='/#login-form')
def connect_coinbase(request):
    coinbase_callback_redirect_to = request.GET.get('redirect_to', None)
    request.session['coinbase_callback_redirect_to'] = coinbase_callback_redirect_to
    return HttpResponseRedirect(coinbase_oauth_client.step1_get_authorize_url())


#@login_required(login_url='/#login-form')
def connect_coinbase_callback(request):
    #: oauth_code is the whole reason we're here
    oauth_code = request.GET.get('code', None)
    if oauth_code == None:
        raise Http404
    
    #: Secret handshake time
    http = httplib2.Http(ca_certs='/etc/ssl/certs/ca-certificates.crt')
    token = coinbase_oauth_client.step2_exchange(oauth_code, http=http)
    
    #: Get user details according to Coinbase
    CB_API = CoinBaseAPI(oauth2_credentials=token.to_json())
    cb_user_details = CB_API.get_user_details()
    
    if request.user.is_authenticated():
        #: Occasionally the user will already be logged in.  This is the simplest handling
        user = request.user
        user_settings = user.usersettings
        if user_settings.coinbase_user_id and user_settings.coinbase_user_id != cb_user_details.id:
            #: You're not allowed to change your coinbase id once it's set
            raise HttpResponseForbidden
        do_login = False
    else:
        #: If we're not logged in, we either find the existing user, or create a new one
        do_login = True
        try:
            #: Find existing user
            user_settings = UserSettings.objects.get(coinbase_user_id=cb_user_details.id)
        except UserSettings.DoesNotExist:
            try:
                #: Edge cases may cause user settings to not exist, but coinbase username to exist.  If we can, retrieve.
                user = User.objects.get(username=cb_user_details.id)
            except User.DoesNotExist:
                #: Create new user, which can only be logged into through coinbase.
                user = User.objects.create_user(cb_user_details.id, email=cb_user_details.email)
            #: Create new user settings.  Save is below.
            user_settings = UserSettings(user=user)
        else:
            #: Existing user, use existing settings
            user = user_settings.user
    
    if not user.email:
        #: Email may or may not already exist
        user.email = cb_user_details.email
        user.save()
    
    #: Update or insert settings
    user_settings.coinbase_oauth_token = token.to_json()
    user_settings.coinbase_user_id = cb_user_details.id
    user_settings.save()
    
    #: Determine redirect location
    coinbase_callback_redirect_to = request.session.get('coinbase_callback_redirect_to', '/')
    if coinbase_callback_redirect_to == None:
        coinbase_callback_redirect_to = '/'
    
    if do_login:
        #: If we're not logged in already, do so
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
    
    #: Finally, redirect to where we're going
    return HttpResponseRedirect(coinbase_callback_redirect_to)
