from django import forms

class UploadFileForm(forms.Form):
    # file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    urls = forms.CharField(label="urls", widget=forms.Textarea(attrs={"rows":50, "cols":100}))