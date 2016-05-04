from django import forms
from django.contrib.auth import login, logout, authenticate
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinLengthValidator, MinValueValidator, \
RegexValidator, URLValidator
from captcha.fields import ReCaptchaField
from django.contrib.auth.models import User
from captcha.fields import ReCaptchaField

from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinLengthValidator, MinValueValidator, \
RegexValidator, URLValidator
from django.template.defaultfilters import filesizeformat
from website.models import Profile
import re
from django.utils.translation import ugettext_lazy as _


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username')
        print username
        password = cleaned_data.get('password')
        print password
        if username is None or password is None:
            raise forms.ValidationError("Invalid username or password")
        user = authenticate(username=username, password=password)
        
        if not user:
            raise forms.ValidationError("Invalid username or password")
        if not user.is_active:
            raise forms.ValidationError("User is blocked")
        cleaned_data['user'] = user
        return cleaned_data
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'confirmation_code']

    # def clean_picture(self):
    #    if 'picture' in self.cleaned_data and not \
    #        self.cleaned_data['picture']:
    #         raise forms.ValidationError("Profile picture required!")

    first_name = forms.CharField()
    last_name = forms.CharField()
    


    def __init__(self, user, *args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]
        if 'user' in kwargs:
            user = kwargs["user"]
            del kwargs["user"]
            
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
          
     
class RegisterForm(forms.Form):
	username = forms.RegexField(
	    regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Username"), error_messages={ 
	    'invalid': _("This value must contain only letters, numbers and underscores.") })

	password = forms.CharField(
		label = _("Password"),
		widget = forms.PasswordInput(render_value = False),
		min_length = 8,
	)
	
	password_confirm = forms.CharField(
		label = _("Password (again)"),
		widget = forms.PasswordInput(render_value = False),
		min_length = 8,
	)
	email = forms.EmailField(
		label = _("Email"),
		widget = forms.TextInput(),
		required=True
	)
	captcha = ReCaptchaField()
	
	
	def clean_username(self):
		try:
			User.objects.get(username=self.cleaned_data['username'])
			raise forms.ValidationError(_("This username has already existed."))
		except User.DoesNotExist:
			pass
			
			
	def clean_email(self):
		try:
			User.objects.get(email=self.cleaned_data['email'])
			raise forms.ValidationError(_("This email is already taken."))
		except User.DoesNotExist:
			pass	
			
	
	# def clean(self):
 #        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
 #            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
 #                raise forms.ValidationError(_("The two password fields did not match."))
 #        return self.cleaned_data


        