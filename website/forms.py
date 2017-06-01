from django import forms
from website.models import *
from taggit.forms import *
from django.db.models import Q
import re

tutorials = (
    ("Select a Tutorial", "Select a Tutorial"),
)


class NewQuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('title')

    category = forms.ModelChoiceField(
                      widget=forms.Select(attrs={}),
                      queryset=FossCategory.objects.order_by('name'),
                      empty_label="Select a Foss category",
                      required=True,
                      error_messages={'required': 'Select a category.'})

    title = forms.CharField(
                      widget=forms.TextInput(),
                      required=True,
                      error_messages={'required': 'Title field required.'})

    body = forms.CharField(
                      widget=forms.Textarea(),
                      required=True,
                      error_messages={'required': 'Question field required.'})

    tag = TagField(
                  required=True,
                  error_messages={'required': 'Tag field required.'})

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 12:
            raise (forms
                   .ValidationError("Title should be longer"
                                    " than 12 characteres"))
        if Question.objects.filter(title=title).exists():
            raise forms.ValidationError("This title already exist.")

        return title

    def clean_body(self):
        body_list = []
        body = self.cleaned_data['body']
        if len(body) < 12:
            raise (forms
                   .ValidationError("Body should be min. 12 characters long"))
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
        selecttutorial = kwargs.pop('tutorial', None)


        super(NewQuestionForm, self).__init__(*args, **kwargs)
        tutorial_choices = (
                ("Select a Sub Category", "Select a Sub Category"),
        )
        super(NewQuestionForm, self).__init__(*args, **kwargs)
        if category == '12':
            if FossCategory.objects.filter(id=category).exists():

                self.fields['category'].initial = category
                children = SubFossCategory.objects.filter(parent_id=category)
                for child in children:
                    tutorial_choices += ((child.name, child.name),)
                self.fields['tutorial'] = (forms
                                           .CharField(widget=forms.Select(
                                                             choices=
                                                             tutorial_choices
                                                              )))
                if SubFossCategory.objects.filter(name=selecttutorial).exists():
                    self.fields['tutorial'].initial = selecttutorial
            else:

                self.fields['tutorial'] = forms.CharField(widget=
                                                          forms.Select(
                                                               choices=
                                                               tutorial_choices
                                                                      ))
        else:
            self.fields['category'].initial = category
            self.fields['tutorial'] = forms.CharField(
                                                      widget=forms.Select(
                                                          choices=
                                                          tutorial_choices))



class AnswerQuestionForm(forms.ModelForm):
    question = forms.IntegerField(widget=forms.HiddenInput())
    body = forms.CharField(widget=forms.Textarea(),
                           required=True,
                           error_messages={'required': 'Answer field required.'}
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
    body = forms.CharField(widget=forms.Textarea(), required=True,
                           error_messages=
                           {'required': 'Comment field required.'})
