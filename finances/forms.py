from django import forms

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