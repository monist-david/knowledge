from django.shortcuts import render
from django.views.generic import TemplateView
import sys

sys.setrecursionlimit(3000)

from . import models

import copy


class HomeView(TemplateView):
    template_name = "index/index.html"

    def parent_children_3(self, parents):
        dataset = []
        for parent in parents:
            name = parent.name
            value = parent.value
            if value != None:
                value = int(value)
            children = []
            data = ()
            data += (name, value, children)
            dataset.append(data)
        return dataset

    def parent_children_2(self, parents):
        dataset = []
        for parent in parents:
            name = parent.name
            value = parent.value
            if value != None:
                value = int(value)
            children = parent.child.all()
            data = ()
            if len(children) == 0:
                data += (name, value)
            else:
                data += (name, value, self.parent_children_3(children))
            dataset.append(data)
        return dataset


    def parent_children(self, parents):
        dataset = []
        for parent in parents:
            name = parent.name
            value = parent.value
            if value != None:
                value = int(value)
            children = parent.child.all()
            data = ()
            if len(children) == 0:
                data += (name, value)
            else:
                data += (name, value, self.parent_children_2(children))

            dataset.append(data)
        return dataset

    def get(self, request):
        parent = self.parent_children(models.Parent.objects.all())
        content = {"parent": parent}
        return render(request, self.template_name, content)

    def post(self, request):
        return render(request, self.template_name)


class FocusView(TemplateView):
    template_name = "index/index.html"

    def parent_children_3(self, parents):
        dataset = []
        for parent in parents:
            name = parent.name
            value = parent.value
            if value != None:
                value = int(value)
            children = []
            data = ()
            data += (name, value, children)
            dataset.append(data)
        return dataset

    def parent_children_2(self, parents):
        dataset = []
        for parent in parents:
            name = parent.name
            value = parent.value
            if value != None:
                value = int(value)
            children = parent.child.all()
            data = ()
            if len(children) == 0:
                data += (name, value)
            else:
                data += (name, value, self.parent_children_3(children))
            dataset.append(data)
        return dataset


    def parent_children(self, parents):
        dataset = []
        for parent in parents:
            name = parent.name
            value = parent.value
            if value != None:
                value = int(value)
            children = parent.child.all()
            data = ()
            if len(children) == 0:
                data += (name, value)
            else:
                data += (name, value, self.parent_children_2(children))

            dataset.append(data)
        return dataset

    def get(self, request, name):
        parent = self.parent_children(models.Parent.objects.all().filter(name=name))
        parent += self.parent_children(models.Children.objects.all().filter(name=name))
        content = {"parent": parent}
        return render(request, self.template_name, content)

    def post(self, request):
        return render(request, self.template_name)


class NetworkView(TemplateView):
    template_name = "index/index2.html"

    def parent_children_5(self, parents):
        dataset = []
        for parent in parents:
            name = parent.name
            value = parent.value
            if value != None:
                value = int(value)
            children = []
            data = ()
            data += (name, value, children)
            dataset.append(data)
        return dataset

    def parent_children_4(self, parents):
        dataset = []
        for parent in parents:
            name = parent.name
            value = parent.value
            if value != None:
                value = int(value)
            children = parent.child.all()
            data = ()
            if len(children) == 0:
                data += (name, value)
            else:
                data += (name, value, self.parent_children_5(children))
            dataset.append(data)
        return dataset

    def parent_children_3(self, parents):
        dataset = []
        for parent in parents:
            name = parent.name
            value = parent.value
            if value != None:
                value = int(value)
            children = parent.child.all()
            data = ()
            if len(children) == 0:
                data += (name, value)
            else:
                data += (name, value, self.parent_children_4(children))
            dataset.append(data)
        return dataset

    def parent_children_2(self, parents):
        dataset = []
        for parent in parents:
            name = parent.name
            value = parent.value
            if value != None:
                value = int(value)
            children = parent.child.all()
            data = ()
            if len(children) == 0:
                data += (name, value)
            else:
                data += (name, value, self.parent_children_3(children))
            dataset.append(data)
        return dataset


    def parent_children(self, parents):
        dataset = []
        for parent in parents:
            name = parent.name
            value = parent.value
            if value != None:
                value = int(value)
            children = parent.child.all()
            data = ()
            if len(children) == 0:
                data += (name, value)
            else:
                data += (name, value, self.parent_children_2(children))

            dataset.append(data)
        return dataset


    def get(self, request):
        parent = self.parent_children(models.Parent.objects.all())
        content = {"parent": parent}
        return render(request, self.template_name, content)

    def post(self, request):
        return render(request, self.template_name)

class NetworkView2(TemplateView):
    template_name = "index/index3.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
