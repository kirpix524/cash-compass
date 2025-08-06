from django import forms

from finances.models import WalletGroup


class CurrencyUploadForm(forms.Form):
    file: forms.FileField = forms.FileField(
        label="JSON файл",
        help_text="Выберите JSON-файл с валютами",
    )

class CategoryUploadForm(forms.Form):
    file: forms.FileField = forms.FileField(
        label="JSON файл",
        help_text="Выберите JSON-файл с категориями",
    )

class WalletUploadForm(forms.Form):
    file = forms.FileField(
        label='Файл с кошельками (JSON)',
        help_text='Загрузите .json с данными из вашего приложения',
        widget=forms.ClearableFileInput(attrs={'accept': '.json'})
    )

class WalletGroupForm(forms.ModelForm):
    class Meta:
        model = WalletGroup
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название группы'}),
        }