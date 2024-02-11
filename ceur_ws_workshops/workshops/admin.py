from django.contrib import admin
from .models import Workshop, Author, Editor, Paper

class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('workshop_title', 'publication_year', 'volume_number')
    search_fields = ['workshop_title']

class PaperAdmin(admin.ModelAdmin):
    list_display = ('paper_title', 'workshop')
    search_fields = ['paper_title', 'author__author']

class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['author']
# Register your models here.
admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Editor)
admin.site.register(Paper, PaperAdmin)