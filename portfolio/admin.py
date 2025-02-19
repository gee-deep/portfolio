from django.contrib import admin
from .models import Book, Show, LifeEvent, About

admin.site.register(Book)
admin.site.register(Show)
admin.site.register(LifeEvent)
admin.site.register(About) 