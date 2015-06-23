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


class UserLoginForm(forms.Form):

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    db = forms.ChoiceField(choices=[('forum', 'forum'), ('scilab', 'scilab'), ('client2', 'client2')])

    def clean(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        db = cleaned_data.get('db')
        
        if username is None or password is None:
            raise forms.ValidationError("Invalid username or password")


        if db == 'forum':
            user = authenticate(username=username, password=password)
            print "default" , "*******************"
        else:
            user = authenticate(username=username, password=password, db=db)
            print db , "*******************"
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
	username = forms.CharField(
		label = _("Username"),
		max_length = 30,
		widget = forms.TextInput(),
		required = True,
		validators = [
		RegexValidator(
			regex = '^[a-zA-Z0-9-_+.]*$',
			message = 'Username required. 30 characters or fewer. \
			Letters, digits and @/./+/-/_ only.',
			code = 'invalid_username'
		),
		]
	)
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
		return username
