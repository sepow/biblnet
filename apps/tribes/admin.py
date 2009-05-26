from django.contrib import admin
from tribes.models import Tribe, Topic, TribeMember

class TribeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created', 'deleted')  

class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', )
    
class TribeMemberAdmin(admin.ModelAdmin):
    pass

admin.site.register(Tribe, TribeAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(TribeMember, TribeMemberAdmin)
