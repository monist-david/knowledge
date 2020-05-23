from django.urls import path
from .views import GraphView

app_name = 'graph'
urlpatterns = [
    path('', GraphView.as_view(), name='graph'),
]