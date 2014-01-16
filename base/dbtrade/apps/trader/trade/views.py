from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django import forms
from django.db.models import Q
from django.contrib.auth.decorators import login_required


def home(request):
    template = 'trade_home.html'
    
    env = {}
    return render_to_response(template, RequestContext(request, env))


def login(request):
    template = 'trade_login.html'
    
    env = {}
    return render_to_response(template, RequestContext(request, env))


def buy(request):
    template = 'trade_order.html'
    
    env = {}
    return render_to_response(template, RequestContext(request, env))


def sell(request):
    template = 'trade_order.html'
    
    env = {}
    return render_to_response(template, RequestContext(request, env))

