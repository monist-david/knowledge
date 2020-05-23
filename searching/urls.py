from django.urls import path
from .views import SearchView, ResultsView

app_name = 'searching'
urlpatterns = [
    path('', SearchView.as_view(), name='searching'),
    path('results/', ResultsView.as_view(), name='results'),
]