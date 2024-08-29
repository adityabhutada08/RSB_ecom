from django import forms
from . models import Account

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'placeholder': 'Enter Password'
        }
    ))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'placeholder': 'Confirm Password'
        }
    ))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone', 'email', 'password'] 
        
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone'].widget.attrs['placeholder'] = 'Enter Your Mobile Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Your Email'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Password doesn't match!! Enter same password")


    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if Account.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone