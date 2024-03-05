from django.contrib import admin
from .models import Workshop, Author, Editor, Paper

class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('workshop_title', 'publication_year')
    search_fields = ['workshop_title']

class PaperAdmin(admin.ModelAdmin):
    list_display = ('paper_title', 'pages')
    search_fields = ['paper_title', 'author__author']

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'id')
    search_fields = ['author_name']

class EditorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ['name']
    
# Register your models here.
admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Editor, EditorAdmin)
admin.site.register(Paper, PaperAdmin)