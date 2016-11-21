from __future__ import unicode_literals

import logging
import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from rbe_authorize.api.tokens import refresh, get_token

rbe_authorize = logging.getLogger('rbe_authorize')


class Profile(models.Model):
    user = models.OneToOneField(User)
    uid = models.IntegerField(help_text="The unique user id from the RBE Network")
    password = models.CharField(max_length=128, help_text="The dummy password for log in")
    code = models.CharField(max_length=128, help_text="The code to retrieve an api token with.")

    def __str__(self):
        return "Profile<id: {} username: {}>".format(self.uid, self.user)

    @staticmethod
    def get_token(profile):
        assert isinstance(profile, Profile), "Parameter profile not of instance models.Profile"
        # Try to get token from profile

        try:
            token = Token.objects.get(belongs_to=profile, token_expires_in__gt=timezone.now())
            if token.token_expires_in > timezone.now():
                return token
            else:
                token.refresh()
                return token
        except Token.DoesNotExist:
            rbe_authorize.info("Profile {} has no tokens, need to request one.".format(profile))

        # Try to create token by calling the RBE Network
        token_response = get_token(profile.code)
        if not token_response:
            raise EnvironmentError("Could not create API token.")

        # Save the token and return it
        return Token.save_token_from_response(profile, token_response)


class Token(models.Model):

    belongs_to = models.OneToOneField(Profile)
    access_token = models.CharField(max_length=128, help_text="The code to retrieve an api token with.")
    token_type = models.CharField(max_length=128, help_text="The code to retrieve an api token with.")
    expires_in = models.DateTimeField(help_text="The code to retrieve an api token with.")
    refresh_token = models.CharField(max_length=128, help_text="The code to retrieve an api token with.")
    id_token = models.CharField(max_length=512, help_text="The code to retrieve an api token with.")

    def __str__(self):
        return "Token <{}, {}, {}, {}>".format(self.belongs_to, self.access_token, self.refresh_token, self.id_token)

    @staticmethod
    def save_token_from_response(profile, token_response):
        """ Saves the api token to the database """
        try:
            token = Token.objects.get(belongs_to=profile)
            token.access_token = token_response.access_token
            token.token_type = token_response.token_type
            token.expires_in = timezone.now() + datetime.timedelta(seconds=token_response.expires_in)
            token.refresh_token = token_response.refresh_token
            token.id_token = token_response.id_token
            token.save()
        except Token.DoesNotExist:
            token = Token(
                belongs_to=profile,
                access_token=token_response.access_token,
                token_type=token_response.token_type,
                expires_in=timezone.now() + datetime.timedelta(seconds=token_response.expires_in),
                refresh_token=token_response.refresh_token,
                id_token=token_response.id_token
            )
            token.save()
        return token

    def refresh(self):
        token_response = refresh(self.refresh_token)

        if not token_response:
            token = Token.save_token_from_response(self.belongs_to, token_response)
            return token