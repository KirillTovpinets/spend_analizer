from django import forms
from .models import Receipt


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result
class ReceiptForm(forms.ModelForm):
    files = MultipleFileField()

    class Meta:
        model = Receipt
        fields = ['files']

    def clean_files(self):
        files = self.cleaned_data.get('files', [])
        # Additional validation for files (optional)
        return files

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()

class CSVBofUploadForm(forms.Form):
    csv_bof_file = forms.FileField()
