import logging

from django.conf import settings
from django.urls import reverse

import requests
import requests.auth

rbe_authorize = logging.getLogger('rbe_authorize')


class TokenResponse(object):

    def __init__(self, params):
        self.params = params
        print params

    @property
    def access_token(self):
        return self.params['access_token']

    @property
    def token_type(self):
        return self.params['token_type']

    @property
    def expires_in(self):
        return self.params['expires_in']

    @property
    def refresh_token(self):
        return self.params['refresh_token']

    @property
    def id_token(self):
        return self.params['id_token']


def get_token(code):
    try:
        redirect_uri = settings.CLIENT_URL + reverse('auth_callback')
        client_auth = requests.auth.HTTPBasicAuth(settings.CLIENT_ID, settings.CLIENT_SECRET)
        post_data = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri}
        response = requests.post("{}/token".format(settings.SITE_URL), auth=client_auth, data=post_data)
        if response.status_code != 200:
            rbe_authorize.error("Get token response, status_code={} content={}".format(response.status_code,
                                                                                       response.content))
        else:
            return TokenResponse(response.json())
    except Exception as e:
        rbe_authorize.exception(e)


def refresh(refresh_token):
    try:
        client_auth = requests.auth.HTTPBasicAuth(settings.CLIENT_ID, settings.CLIENT_SECRET)
        headers = {'Cache-Control': 'no-cache', 'Content-Type': 'application/x-www-form-urlencoded'}
        post_data = {"client_id": settings.CLIENT_ID, "grant_type": 'refresh_token', "refresh_token": refresh_token}
        response = requests.post("{}/token".format(settings.SITE_URL), auth=client_auth, data=post_data, headers=headers)
        if response.status_code != 200:
            rbe_authorize.error("Get token response, status_code={} content={}".format(response.status_code,
                                                                                       response.content))
        else:
            return TokenResponse(response.json())
    except Exception as e:
        rbe_authorize.exception(e)
