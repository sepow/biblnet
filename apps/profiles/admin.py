from django.contrib import admin
from profiles.models import Profile, Affiliation, Occupation

admin.site.register(Profile)
admin.site.register(Affiliation)
admin.site.register(Occupation)
