from django import forms
from .models import Product, ReviewRating

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_name', 'slug', 'description', 'price',
            'weight', 'images', 'stock', 'is_available', 'category'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={
                'placeholder': 'Enter product name *', 'class': 'form-control'
            }),
            'slug': forms.TextInput(attrs={
                'placeholder': 'Unique slug *', 'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Short description *', 'class': 'form-control', 'rows': 3
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': 'Price (₹) *', 'class': 'form-control'
            }),
            'weight': forms.Textarea(attrs={
                'placeholder': 'Weight as per your requirement(in Kg or in Quintal) *', 'class': 'form-control'
            }),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={
                'placeholder': 'Available stock *', 'class': 'form-control'
            }),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
