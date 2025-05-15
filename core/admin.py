from django.apps import apps
from django.contrib import admin

# Register your models here.
models = apps.get_app_config('core').get_models()

for model in models:
    admin.site.register(model)
