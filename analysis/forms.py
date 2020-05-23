from django import forms


class AnalysisForm(forms.Form):
    article = forms.CharField(widget=forms.Textarea, label='article')
