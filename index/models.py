from django.utils import timezone

from django.db import models
import json


class Progress(models.Model):
    daily_news = models.ForeignKey('News', on_delete=models.CASCADE)

    def __str__(self):
        return self.daily_news


class News(models.Model):
    authors = models.ManyToManyField('Author')
    title = models.CharField(max_length=20)
    href = models.URLField(max_length=100)
    time = models.DateTimeField(default=timezone.now, null=True)
    content = models.TextField()
    keywords = models.ManyToManyField('keyInformation')
    summary = models.TextField()

    def __str__(self):
        return self.title

class Author(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return self.name


class keyInformation(models.Model):
    key_information = models.CharField(max_length=200, blank=True, default='')
    news_link = models.ManyToManyField('News')

    def __str__(self):
        return self.key_information


class Source(models.Model):
    name = models.CharField(max_length=10)
    country = models.OneToOneField('Country', on_delete=models.CASCADE)
    rating = models.OneToOneField('Rating', on_delete=models.CASCADE)

    def __str__(self):
        return self.name + str(self.country) + str(self.rating)


class Country(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Rating(models.Model):
    overall_reliability = models.FloatField(max_length=10)
    comment = models.TextField()

    def __str__(self):
        return str(self.overall_reliability) + " " + self.comment


class Parent(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField(max_length=100, blank=True, null=True)
    child = models.ManyToManyField('Children', blank=True, null=True)

    def __str__(self):
        return self.name


class Children(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField(max_length=100, blank=True, null=True)
    child = models.ManyToManyField('Children', blank=True, null=True)

    def __str__(self):
        return self.name


class ScrapyItem(models.Model):
    unique_id = models.CharField(max_length=100, null=True)
    data = models.TextField()  # this stands for our crawled data
    date = models.DateTimeField(default=timezone.now)

    # This is for basic and custom serialisation to return it to client as a JSON.
    @property
    def to_dict(self):
        data = {
            'data': json.loads(self.data),
            'date': self.date
        }
        return data

    def __str__(self):
        return self.unique_id
