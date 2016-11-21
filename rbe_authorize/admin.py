from django.contrib import admin

from rbe_authorize.models import Profile, Token

admin.site.register(Profile)
admin.site.register(Token)
