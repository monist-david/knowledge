from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render
from newspaper import Article

from .forms import UploadFileForm
from searching.views import SearchView

# Create your views here.
from django.views.generic import TemplateView
from index.models import News, Author, Parent, Children, keyInformation
from . import forms


class UploadView(TemplateView):
    template_name = "upload/index.html"

    def handle_uploaded_file(f):
        with open('some/file/name.txt', 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def get(self, request):
        form = UploadFileForm()
        return render(request, self.template_name)

    def post(self, request):
        form = UploadFileForm(request.POST)
        # files = request.FILES.getlist('file_field')
        if form.is_valid():
            urls = form.cleaned_data['urls']
            urls = urls.split(',')
            for url in urls:
                article = Article(url, language="zh")
                article.download()
                SearchView.scrapy(self, article)

        #     for f in files:
        #         ...  # Do something with each file.
            return render(request, self.template_name)
        else:
            return render(request, self.template_name)
