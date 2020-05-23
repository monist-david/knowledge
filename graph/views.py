from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

import copy
from index.models import News, Author, Parent, Children, keyInformation
import heapq


class GraphView(TemplateView):
    template_name = "searching/results.html"

    def in_keywords(self, key, keywords):
        for word in keywords:
            if key in str(word):
                return True
            else:
                pass
        return False

    def in_news(self, all_keys):
        top = heapq.nlargest(3, all_keys, key=all_keys.get)
        all_news = News.objects.all()
        top_five_parent = copy.deepcopy(top)
        for index in range(len(top)):
            if Parent.objects.filter(name=top[index]):
                top_new = Parent.objects.get(name=top[index])
                top_five_parent[index] = top_new
            else:
                top_new = Parent(name=top[index], value=all_keys[top[index]])
                top_new.save()
                top_five_parent[index] = top_new
            try:
                del all_keys[str(top_five_parent[index])]
            except:
                pass
        # print(top)
        new_top_five_children = copy.deepcopy(top_five_parent)
        new_top_five_children_change = copy.deepcopy(new_top_five_children)
        print(new_top_five_children)
        while all_keys != {} and len(new_top_five_children) != 0:
            print(len(new_top_five_children))
            for index in range(len(new_top_five_children)):
                new_top_five = {}
                try:
                    del all_keys[str(new_top_five_children[index])]
                except:
                    pass
                for news in all_news:
                    if self.in_keywords(str(new_top_five_children[index]), news.keywords.all()):
                        for keyword in news.keywords.all():
                            # if str(keyword) != new_top_five_children[index] and all_keys.get(str(keyword)):
                            if all_keys.get(str(keyword)):
                                if not new_top_five.get(str(keyword)):
                                    new_top_five[str(keyword)] = 1
                                else:
                                    new_top_five[str(keyword)] += 1
                    else:
                        pass
                new_top_five = heapq.nlargest(5, new_top_five, key=new_top_five.get)
                for top in new_top_five:
                    if Children.objects.filter(name=top):
                        new_children = Children.objects.get(name=top)
                        if new_top_five_children[index].child.filter(name=top):
                            pass
                        else:
                            new_top_five_children[index].child.add(new_children)
                    else:
                        new_children = Children(name=top, value=all_keys[top])
                        new_children.save()
                        # new_top_five_children.append(new_children)
                        new_top_five_children_change.append(new_children)
                        new_top_five_children[index].child.add(new_children)
                new_top_five_children_change.remove(new_top_five_children[index])
            new_top_five_children = copy.deepcopy(new_top_five_children_change)
            print(new_top_five_children)

    def add_child_parent(self):
        all_key = keyInformation.objects.all()
        all_news = News.objects.all()
        all_keys = {}
        for key in all_key:
            all_keys[str(key)] = 0
        for news in all_news:
            for keyword in news.keywords.all():
                all_keys[str(keyword)] += 1
        self.in_news(all_keys)
        pass

    def get(self, request):
        self.add_child_parent()
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
