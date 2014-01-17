from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django import forms
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from dbtrade.utils.utils import get_user_cb_api


@login_required(login_url='/#login-form')
def home(request):
    template = 'trade_home.html'
    
    env = {}
    return render_to_response(template, RequestContext(request, env))


@login_required(login_url='/#login-form')
def login(request):
    template = 'trade_login.html'
    CB_API = get_user_cb_api(request.user)
    if CB_API != None:
        return HttpResponseRedirect('/trade/')
    
    ref = request.GET.get('ref', '/trade/')
    env = {'ref': ref}
    return render_to_response(template, RequestContext(request, env))


@login_required(login_url='/#login-form')
def buy(request):
    template = 'trade_order.html'
    CB_API = get_user_cb_api(request.user)
    if CB_API == None:
        return HttpResponseRedirect('/trade/login/?ref=/trade/buy/')
    
    env = {}
    return render_to_response(template, RequestContext(request, env))


@login_required(login_url='/#login-form')
def sell(request):
    template = 'trade_order.html'
    CB_API = get_user_cb_api(request.user)
    if CB_API == None:
        return HttpResponseRedirect('/trade/login/?ref=/trade/sell/')
    
    env = {}
    return render_to_response(template, RequestContext(request, env))

