from django import forms
from .models import DropboxReceipt

class DropboxReceiptForm(forms.ModelForm):
    class Meta:
        model = DropboxReceipt
        fields = ['file_name']

    file_name = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        files = kwargs.pop('files', [])
        super().__init__(*args, **kwargs)

        print(files)
        self.fields['file_name'].choices = [(file['path'], file['name']) for file in files]
