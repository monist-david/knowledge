from django.urls import path
from .views import AnalysisView

app_name = 'analysis'
urlpatterns = [
    path('', AnalysisView.as_view(), name='analysis'),
]
