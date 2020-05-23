from django.urls import path
from .views import UploadView

app_name = 'upload'
urlpatterns = [
    path('', UploadView.as_view(), name='upload'),
]