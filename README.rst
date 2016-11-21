====================
Django RBE Authorize
====================

The Django RBE Authorize is a simple app that once enabled in the
installed apps allows the authentication through the RBE Network Core.

Quick start
-----------

1. Add "rbe_authorize" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'rbe_authorize',
    ]

2. Include the rbe_authorize URLconf in your project urls.py like this::

    url(r'^', include('rbe_authorize.urls')),

3. Run `python manage.py migrate` to create the rbe_authorize models.

4. Configure the settings.py to set the configurations for
    * SITE_URL = 'https://rbe-network.org'
    * CLIENT_ID = The client id that you get from the RBE Network
    * CLIENT_SECRET = The client secret you get from the RBE Network
    * CLIENT_SCOPE = The client scope you need for your app eg. ('identity')
    * CLIENT_URL = Your page url eg. ('http://localhost:9090')

4. Start the development server and put a page in place that you can visit

5. Put the snippet `{% include 'rbe_authorize.html' %}` in the template and include bootstrap or style the link

6. Click the link and see how you are forwarded and redirected back to your page

7. You should be redirected to the AFTER_LOGIN_URL and can use the User, Profile and Token model to build the experience
