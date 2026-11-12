from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-e=ouwc_u(v5b0u#van@9&g8=n_nvuph2euaow3rbo^x-5fz@t0"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += [
    "django_browser_reload",
]

# Dev-only middleware — must be at the END of the middleware list
MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

try:
    from .local import *
except ImportError:
    pass
