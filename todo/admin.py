from django.contrib import admin

# Register your models here.
# First we have to import the module 'Project' into admin.py
from .models import Todo

# The following class define some readonly fields which are then reported in the
# Admin web page. In particular we are presenting the 'datecreated'
class TodoAdmin(admin.ModelAdmin):
    readonly_fields = ('datecreated',)

# Then we have to register it 
admin.site.register(Todo, TodoAdmin)




