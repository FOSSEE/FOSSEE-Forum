from django import forms
from website.models import *
#from spoken_auth.models import TutorialDetails
from django.db.models import Q
import re
class NewQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('title')
    category = forms.ModelChoiceField(widget = forms.Select(attrs = {}), 
                        queryset = FossCategory.objects.order_by('name'), 
                        empty_label = "Select a Foss category", 
                        required = True,
                        error_messages = {'required':'Select a category.'})
                        
    title = forms.CharField(widget=forms.TextInput(),
                        required = True,
                        error_messages = {'required':'Title field required.'})
                        
    body = forms.CharField(widget=forms.Textarea(),
            required = True,
            error_messages = {'required':'Question field required.'})
    
    def clean_title(self):
        title = self.cleaned_data['title']
        # if title.strip():
        #    raise forms.ValidationError("Title Can not be only Spaces")
        if len(title) < 12:
            raise forms.ValidationError("Title should be longer than 12 characteres")
        if Question.objects.filter(title=title).exists():
            raise forms.ValidationError("This title already exist.")
        # temp = title.replace(" ", '')
        # for e in str(temp):
        #     if not e.isalnum():
        #         raise forms.ValidationError("Only Alphanuemaric")
        return title
    
    def clean_body(self):
        body_list = []
        body = self.cleaned_data['body']
        if len(body) < 12:
            raise forms.ValidationError("Body should be min. 12 characters long")
        body = body.replace('&nbsp;', ' ')
        body = body.replace('<br>', '\n')
        if body.isspace():
            raise forms.ValidationError("Body Can not be only Spaces")
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
    def clean_body(self):
        body = self.cleaned_data['body']
        body = body.replace('&nbsp;', ' ')
        body = body.replace('<br>', '\n')
        if body.isspace():
            raise forms.ValidationError("Body Can not be only Spaces")
        return body

    class Meta:
        model = Question
        fields = ['question', 'body']

class AnswerCommentForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(),required = True,
        error_messages = {'required':'Comment field required.'})

    # def clean_body(self):
    #     body = self.cleaned_data['body']
    #     body = body.replace('&nbsp;', ' ')
    #     body = body.replace('<br>', '\n')
    #     if body.isspace():
    #         raise forms.ValidationError("Body Can not be only Spaces")
    #     return body

