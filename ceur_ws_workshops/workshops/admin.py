from django.contrib import admin
from .models import Workshop, Author, Editor, Paper
from django.forms import TextInput, Textarea, EmailInput, URLInput
from django.db import models
from django import forms
from django.db.models import Q

overrides = {
    models.CharField: {'widget': TextInput(attrs={'size': '20'})},
    models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': '40'})},
    models.URLField: {'widget': URLInput(attrs={'size': '50'})},  
    models.UUIDField: {'widget': TextInput(attrs={'size': '36'})}, 
    models.EmailField: {'widget': EmailInput(attrs={'size': '30'})},  
}

class WorkshopAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Workshop._meta.fields] + ['get_editors']
    list_display_links = ('workshop_short_title',)
    formfield_overrides = overrides
    search_fields = [field.name for field in Workshop._meta.fields]

    def get_editors(self, obj):
        return ", ".join(editor.editor_name for editor in obj.editors.all())
    get_editors.short_description = 'Editors'

    def get_editor_search_result(self, request, queryset, search_term):
        queryset, use_distinct = super().get_editor_search_result(request, queryset, search_term)
        if search_term:
            editor_query = Q(editors__name__icontains=search_term)
            queryset |= self.model.objects.filter(editor_query)
            use_distinct = True  
        return queryset, use_distinct
    
class PaperAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in Paper._meta.fields] + ['get_authors']
    list_display_links = ('paper_title',)
    search_fields = ['paper_title']
    formfield_overrides = overrides

    def get_authors(self, obj):
        return ", ".join(author.author_name for author in obj.authors.all())
    get_authors.short_description = 'Authors'

    def get_workshop(self, obj):
        return ", ".join(workshop.workshop_short_title for workshop in obj.workshop.all())
    get_workshop.short_description = 'Workshop'
    def get_author_search_result(self, request, queryset, search_term):
        queryset, use_distinct = super().get_author_search_result(request, queryset, search_term)
        if search_term:
            editor_query = Q(authors__author_name__icontains=search_term)
            queryset |= self.model.objects.filter(editor_query)
            use_distinct = True  
        return queryset, use_distinct

class AuthorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Author._meta.fields]
    search_fields = ['author_name']
    formfield_overrides = overrides

class EditorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Editor._meta.fields]
    list_display_links = ('editor_name',)
    search_fields = ['editor_name']
    formfield_overrides = overrides

admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Editor, EditorAdmin)
admin.site.register(Paper, PaperAdmin)