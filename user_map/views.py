# coding=utf-8
"""Views of the apps."""
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader, Context
from django.forms.util import ErrorList
from django.forms.forms import NON_FIELD_ERRORS
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import (
    login as django_login,
    authenticate,
    logout as django_logout)
from django.contrib.auth.decorators import login_required

from user_map.forms import (
    UserForm, LoginForm, BasicInformationForm, PasswordForm)
from user_map.models import User
from user_map.app_settings import PROJECT_NAME, USER_ICONS, FAVICON_FILE


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
        'project_name': PROJECT_NAME,
        'app_favicon': FAVICON_FILE,
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
        'user_map/add_user.html',
        {'form': form},
        context_instance=RequestContext(request)
    )


def login(request):
    """Login view.

    :param request: A django request object.
    :type request: request
    """
    if request.method == 'POST':
        next_page = request.GET.get('next', '')
        if next_page == '':
            next_page = reverse('user_map:index')
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(
                email=request.POST['email'],
                password=request.POST['password']
            )
            if user is not None:
                if user.is_active and user.is_approved:
                    django_login(request, user)

                    return HttpResponseRedirect(next_page)
                if not user.is_active:
                    errors = form._errors.setdefault(
                        NON_FIELD_ERRORS, ErrorList())
                    errors.append(
                        'The user is not active. Please contact our '
                        'administrator to resolve this.')
                if not user.is_approved:
                    errors = form._errors.setdefault(
                        NON_FIELD_ERRORS, ErrorList())
                    errors.append(
                        'Please confirm you registration email first!')
            else:
                errors = form._errors.setdefault(
                    NON_FIELD_ERRORS, ErrorList())
                errors.append(
                    'Please enter a correct email and password. '
                    'Note that both fields may be case-sensitive.')

    else:
        form = LoginForm()
    return render_to_response(
        'user_map/login.html',
        {'form': form},
        context_instance=RequestContext(request))


@login_required(login_url='user_map:login')
def update_user(request):
    """Update user view.

    :param request: A django request object.
    :type request: request
    """
    if request.method == 'POST':
        if 'change_basic_info' in request.POST:
            anchor_id = '#basic-information'
            basic_info_form = BasicInformationForm(
                data=request.POST, instance=request.user)
            change_password_form = PasswordForm(user=request.user)
            if basic_info_form.is_valid():
                user = basic_info_form.save()
                messages.success(
                    request, 'You have succesfully changed your information!')
                return HttpResponseRedirect(
                    reverse('user_map:update_user') + anchor_id)
        elif 'change_password' in request.POST:
            anchor_id = '#security'
            change_password_form = PasswordForm(
                data=request.POST, user=request.user)
            basic_info_form = BasicInformationForm(instance=request.user)
            if change_password_form.is_valid():
                user = change_password_form.save()
                messages.success(
                    request, 'You have successfully changed your password!')
                return HttpResponseRedirect(
                    reverse('user_map:update_user') + anchor_id)

    else:
        anchor_id = '#basic-information'
        basic_info_form = BasicInformationForm(instance=request.user)
        change_password_form = PasswordForm(user=request.user)

    return render_to_response(
        'user_map/edit_user.html',
        {
            'basic_info_form': basic_info_form,
            'change_password_form': change_password_form,
            'anchor_id': anchor_id,
        },
        context_instance=RequestContext(request)
    )


def logout(request):
    """Log out view.

    :param request: A django request object.
    :type request: request
    """
    django_logout(request)
    return HttpResponseRedirect(reverse('user_map:index'))