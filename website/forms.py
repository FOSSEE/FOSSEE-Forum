from django import forms

from website.models import *
#from spoken_auth.models import TutorialDetails
from django.db.models import Q
class NewQuestionForm(forms.ModelForm):
    category = forms.ModelChoiceField(widget = forms.Select(attrs = {}), 
    					queryset = FossCategory.objects.order_by('name'), 
    					empty_label = "Select a category", 
    					error_messages = {'required':'Categoty field required.'})
    					
    '''tutorial = forms.ModelChoiceField(widget = forms.Select(attrs = {}), q
    					ueryset = Issue.objects.order_by('name'), 
    					empty_label = "Select a Issue", 
    					error_messages = {'required':'Issue field required.'})'''
    '''class Meta:
        model = Question
        fields = ['category', 'tutorial', 'title', 'body']'''
        
    class Meta:
        model = Question
        fields = ['category', 'title', 'body']

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        super(NewQuestionForm, self).__init__(*args, **kwargs)
        
class AnswerQuesitionForm(forms.Form):
    question = forms.IntegerField(widget=forms.HiddenInput())
    body = forms.CharField(widget=forms.Textarea(),
    		required = True
    		)
