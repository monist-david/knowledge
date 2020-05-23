from django.contrib import admin

from .models import Progress, News, Source, Country, Rating, Children, Parent, keyInformation

admin.site.register(Progress)
admin.site.register(News)
admin.site.register(Source)
admin.site.register(Country)
admin.site.register(Rating)
admin.site.register(Children)
admin.site.register(Parent)
admin.site.register(keyInformation)