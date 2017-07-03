from django import forms
from website.models import *
from .models import *
from taggit.forms import *
from django.db.models import Q
import re

class Category(forms.ModelForm):

	class Meta:
		model = FossCategory
		fields = "__all__"
		field_args = {
            "username" : {
                "error_messages" : {
                    "required" : "Please let us know what to call you!"
                }
            }
        }


class Emails(forms.ModelForm):

	class Meta:
		model = NotificationEmail
		fields = "__all__"



