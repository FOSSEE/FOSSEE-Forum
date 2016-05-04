from django import forms
from website.models import *
#from spoken_auth.models import TutorialDetails
from django.db.models import Q
from tinymce.widgets import TinyMCE
class NewQuestionForm(forms.ModelForm):
    category = forms.ModelChoiceField(widget = forms.Select(attrs = {}), 
                        queryset = FossCategory.objects.order_by('name'), 
                        empty_label = "Select a Foss category", 
                        required = True,
                        error_messages = {'required':'Select a category.'})
                        
    title = forms.CharField(widget=forms.TextInput(),
                        required = True,
                        error_messages = {'required':'Title field required.'})
                        
    body = forms.CharField(
            widget=TinyMCE(
                attrs={'cols': 115, 'rows': 15}))
    
    def clean_title(self):
        title = self.cleaned_data['title']
        if not title.strip():
           raise forms.ValidationError("Can not be only Spaces")
        if len(title) < 3:
            raise forms.ValidationError("Title more than 3 characters")
        return title
    
    def clean_body(self):
        body = self.cleaned_data['body']
        if not body.strip():
            raise forms.ValidationError("Can not be only Spaces")
        if len(body) < 30:
            raise forms.ValidationError("Question more than 50 characters")
        return body

    class Meta:
        model = Question
        fields = ['category', 'title', 'body']

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        super(NewQuestionForm, self).__init__(*args, **kwargs)
        
class AnswerQuestionForm(forms.ModelForm):
    question = forms.IntegerField(widget=forms.HiddenInput())
    body = forms.CharField(widget=forms.Textarea(),
            required = True,
            error_messages = {'required':'Answer field required.'}
            )
    class Meta:
        model = Question
        fields = ['question', 'body']

class AnswerCommentForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(),required = True,)

