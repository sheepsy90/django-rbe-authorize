import logging
import uuid

import django.contrib.auth as djauth

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.urls import reverse

from rbe_authorize.api.api import get_user_identity
from rbe_authorize.api.tokens import get_token
from rbe_authorize.models import Profile, Token

rbe_authorize = logging.getLogger('rbe_authorize')


@login_required(login_url=settings.LOGIN_URL)
def logout(request):
    """ When logging out the user gets logged out and is redirected to the landing page """
    rc = RequestContext(request)
    djauth.logout(request)
    return HttpResponseRedirect(reverse('landing'), rc)


def auth_callback(request):
    """ Handles the auth callback from the RBE Network """
    rbe_authorize.info('Retrieved authorization callback')

    # Check if there is an error and if so respond with the error template
    error = request.GET.get('error')
    if error:
        rbe_authorize.info('Authorization callback had error {}'.format(error))
        return render_to_response('authorization_error.html', {'error': error})

    # Get the state to make sure we initialized the request
    state = request.GET.get('state')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        rbe_authorize.info('Authorization callback state was not initialized by us {}'.format(state))
        return render_to_response('authorization_error.html', {'error': 'invalid_state'})

    # Get the code from the request
    code = request.GET.get('code')
    rbe_authorize.info('Authorization callback cde was {}'.format(state))

    # Next step is to use the code to retrieve an api token which we can then use to get the information the user
    token_response = get_token(code)

    if not token_response:
        rbe_authorize.info('Authorization callback could not retrieve token for state {}'.format(state))
        return render_to_response('authorization_error.html', {'error': 'could_not_retrieve_token'})

    # Get the users identity
    user_identity = get_user_identity(token_response.access_token)
    if not user_identity:
        rbe_authorize.info('Authorization callback could not retrieve user identity {}'.format(state))
        return render_to_response('authorization_error.html', {'error': 'could_not_retrieve_user_identity'})

    # Retrieve and update the profile based on identity response or create one
    try:
        profile = Profile.objects.get(uid=user_identity.uid)
        profile.code = code
        profile.user.username = user_identity.username
        profile.user.email = user_identity.email
        profile.save()
    except Profile.DoesNotExist:
        made_up_password = str(uuid.uuid4())
        u = User.objects.create_user(username=user_identity.username, email=user_identity.email, password=made_up_password)
        profile = Profile(uid=user_identity.uid, user=u, password=made_up_password, code=code)
        profile.save()

    # Make sure the token is saved to database such that we can make additional API calls
    Token.save_token_from_response(profile, token_response)

    # Log the user in
    user = djauth.authenticate(username=profile.user.username, password=profile.password)
    djauth.login(request, user)

    return HttpResponseRedirect(settings.AFTER_LOGIN_URL)


def authorize(request):
    """ Call this function to start the authorization at the RBE Network core"""
    return HttpResponseRedirect(make_authorization_url())


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    from uuid import uuid4
    state = str(uuid4())
    save_created_state(state)
    REDIRECT_URI = settings.CLIENT_URL + reverse('auth_callback')

    params = {"client_id": settings.CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI,
              "duration": "temporary",
              "scope": settings.CLIENT_SCOPE}
    import urllib
    url = "{}/authorize?".format(settings.SITE_URL) + urllib.urlencode(params)
    print url
    return url

def save_created_state(state):
    """ Save the state in a db model to verify that the request came from us """
    # TODO Needs implementation
    pass

def is_valid_state(state):
    """ Check the state in a db model to verify that the request came from us """
    # TODO Needs implementation
    return True



