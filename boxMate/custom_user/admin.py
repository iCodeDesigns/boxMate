from django.contrib.admin import site

from custom_user.models import User
site.register(User)
