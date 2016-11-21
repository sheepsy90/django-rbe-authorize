from django.conf.urls import url

from rbe_authorize.views import authorize, auth_callback, logout

urlpatterns = [
    # The admin urls and the standard index page url
    url(r'^authorize', authorize, name='authorize_at_core'),
    url(r'^auth_callback', auth_callback, name='auth_callback'),
    url(r'^logout', logout, name='logout'),
]
