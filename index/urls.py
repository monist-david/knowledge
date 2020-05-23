from django.urls import path
from .views import HomeView, FocusView, NetworkView, NetworkView2

app_name = 'index'
urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('focus_<str:name>/', FocusView.as_view(), name='focus'),
    path('2/', NetworkView.as_view(), name='network'),
    path('3/', NetworkView2.as_view(), name='network2'),
]