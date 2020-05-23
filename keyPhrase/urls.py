from django.urls import path
from .views import ChineseExtractionView, EnglishExtractionView

app_name = 'keyPhrase'
urlpatterns = [
    path('chinese/', ChineseExtractionView.as_view(), name='chineseKeyPhrase'),
    path('english/', EnglishExtractionView.as_view(), name='englishKeyPhrase'),
]