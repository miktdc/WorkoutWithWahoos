from django.contrib import admin
from .models import Profile
from .models import Session
from .models import SessionFile

admin.site.register(Profile)
admin.site.register(Session)
@admin.register(SessionFile)
class SessionFileAdmin(admin.ModelAdmin):
    list_display = ('file_title', 'session', 'uploaded_at')
    list_filter = ('session', 'uploaded_at')
    search_fields = ('file_title', 'session__topic')