from django import forms
from .models import Account


#class RegistrationForm(form.ModelForm):
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter password',
        'class': 'form-control',
        
    }))
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Re enter password'
        
    }))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
        
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields["first_name"].widget.attrs['placeholder'] = 'enter first name'
            self.fields["last_name"].widget.attrs['placeholder'] = 'enter last nme'
            self.fields["phone_number"].widget.attrs['placeholder'] = 'enter phone number'
            self.fields["email"].widget.attrs['placeholder'] = 'enter email'
            
            
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError(
                "password does not match"
            )
            
            