import logging

from django.conf import settings

import requests
import requests.auth

rbe_authorize = logging.getLogger('rbe_authorize')


class UserIdentityResponse(object):

    def __init__(self, params):
        self.params = params

    @property
    def uid(self):
        return self.params.get('uid')

    @property
    def username(self):
        return self.params.get('username')

    @property
    def email(self):
        return self.params.get('email')


def get_user_identity(access_token):
    """ """
    try:
        # TODO if 401 refresh and retry
        headers = {"Authorization": "Bearer " + access_token}
        response = requests.get("{}/core/api/identity?token={}".format(settings.SITE_URL, access_token), headers=headers)
        if response.status_code != 200:
            rbe_authorize.error("Get username response, status_code={} content={}".format(response.status_code,
                                                                                          response.content))
        else:
            return UserIdentityResponse(response.json())
    except Exception as e:
        rbe_authorize.exception(e)