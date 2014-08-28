# coding=utf-8
"""Views of the apps."""
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse
from django.contrib.auth import (
    login as django_login,
    authenticate,
    logout as django_logout)

from user_map.forms import UserForm, LoginForm
from user_map.models import User
from user_map.app_settings import USER_ICONS


def index(request):
    """Index page of user map.

    :param request: A django request object.
    :type request: request

    :returns: Response will be a nice looking map page.
    :rtype: HttpResponse
    """
    information_modal = loader.render_to_string(
        'user_map/information_modal.html')
    data_privacy_content = loader.render_to_string('user_map/data_privacy.html')
    user_menu = dict(
        add_user=True,
        download=True,
        reminder=True
    )
    user_menu_button = loader.render_to_string(
        'user_map/user_menu_button.html',
        dictionary=user_menu
    )
    legend_template = loader.get_template('user_map/legend.html')
    legend_context = Context({'user_icons': USER_ICONS})
    legend = legend_template.render(legend_context)

    context = {
        'data_privacy_content': data_privacy_content,
        'information_modal': information_modal,
        'user_menu': user_menu,
        'user_menu_button': user_menu_button,
        'user_icons': USER_ICONS,
        'legend': legend
    }
    return render(request, 'user_map/index.html', context)


def get_users(request):
    """Return a json document of users with given role.

    This will only fetch users who have approved by email and still active.

    :param request: A django request object.
    :type request: request
    """
    # Get data:
    user_role = int(request.GET['user_role'])

    # Get user
    users = User.objects.filter(
        role=user_role,
        is_approved=True,
        is_active=True)
    json_users_template = loader.get_template('user_map/users.json')
    context = Context({'users': users})
    json_users = json_users_template.render(context)

    users_json = (
        '{'
        ' "users": %s'
        '}' % json_users
    )
    # Return Response
    return HttpResponse(users_json, mimetype='application/json')


def register(request):
    """User registration view.

    :param request: A django request object.
    :type request: request
    """
    if request.method == 'POST':
        form = UserForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect(reverse('user_map:index'))
    else:
        form = UserForm()
    return render_to_response(
        'user_map/user_form.html',
        {'form': form},
        context_instance=RequestContext(request)
    )


def login(request):
    """Login view.

    :param request: A django request object.
    :type request: request
    """
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(
                email=request.POST['email'],
                password=request.POST['password']
            )
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    return HttpResponseRedirect(reverse('user_map:index'))
    else:
        form = LoginForm()
    return render_to_response(
        'user_map/login.html',
        {'form': form},
        context_instance=RequestContext(request))


def logout(request):
    """Log out view.

    :param request: A django request object.
    :type request: request
    """
    django_logout(request)
    return HttpResponseRedirect(reverse('user_map:index'))
