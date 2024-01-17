from django.contrib import admin
from .models import Workshop, Author, Editor, Paper
# Register your models here.
admin.site.register(Workshop)
admin.site.register(Author)
admin.site.register(Editor)
admin.site.register(Paper)