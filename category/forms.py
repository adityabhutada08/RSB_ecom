from django import forms
from .models import category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = category
        fields = ['category_name', 'slug', 'category_description', 'category_img']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter slug (unique)'}),
            'category_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter category description'}),
            'category_img': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_category_name(self):
        name = self.cleaned_data.get('category_name')
        if len(name) < 3:
            raise forms.ValidationError("Category name must be at least 3 characters long.")
        return name
