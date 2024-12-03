from django.contrib import admin
from django.contrib.auth.models import Group
from django.apps import apps

admin.site.unregister(Group)

models = apps.get_app_config('accounts').get_models()

for model in models:
    admin.site.register(model)
