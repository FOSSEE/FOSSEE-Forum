from builtins import object
from django import forms
from django.conf import settings
from antispam.honeypot.forms import HoneypotField
from bs4 import BeautifulSoup
from ckeditor.widgets import CKEditorWidget
from website.models import *

tutorials = (
    ("Select a Tutorial", "Select a Tutorial"),
)

class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = 'forums/templates/clearable_file_input.html'

class NewQuestionForm(forms.ModelForm):

    category = forms.ModelChoiceField(widget = forms.Select(attrs = {}),
                        queryset = FossCategory.objects.order_by('name'),
                        empty_label = "Select a Foss category",
                        required = True,
                        error_messages = {'required':'Select a category'})

    title = forms.CharField(widget = forms.TextInput(),
                        required = True,
                        error_messages = {'required':'Title field required'})

    body = forms.CharField(widget = CKEditorWidget(),
                        required = True,
                        error_messages = {'required':'Question field required'})

    is_spam = forms.BooleanField(required = False)

    spam_honeypot_field = HoneypotField()

    image = forms.ImageField(widget = CustomClearableFileInput(), help_text = "Upload image", required = False)

    def clean_title(self):
        title = str(self.cleaned_data['title'])
        title = title.replace('&nbsp;', ' ')
        title = title.replace('<br>', '\n')
        if title.isspace():
            raise forms.ValidationError("Title cannot be only spaces")
        temp = BeautifulSoup(title, 'html.parser').get_text()
        if (temp.isspace() or temp == ''):
            raise forms.ValidationError("Title cannot be only tags")
        if len(title) < 12:
            raise forms.ValidationError("Title should be longer than 12 characters")
        if Question.objects.filter(title = title).exists():
            raise forms.ValidationError("This title already exists")

        return title

    def clean_body(self):

        body = str(self.cleaned_data['body'])
        body = body.replace('&nbsp;', ' ')
        body = body.replace('<br>', '\n')
        if body.isspace():
            raise forms.ValidationError("Body cannot be only spaces")
        if len(body) < 12:
            raise forms.ValidationError("Body should be minimum 12 characters long")
        temp = BeautifulSoup(body, 'html.parser').get_text()
        if (temp.isspace() or temp == ''):
            raise forms.ValidationError("Body cannot be only tags")

        return body

    def clean_image(self):
        image = self.cleaned_data['image']

        if (image != None):
            if (image._size > settings.MAXIMUM_FILE_SIZE):
                raise forms.ValidationError('File size needs to be under {0} MB.'.format(settings.MAX_FILE_SIZE_MB))

        return image

    class Meta(object):

        model = Question
        fields = ['category', 'title', 'body', 'is_spam', 'image']

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        selecttutorial = kwargs.pop('tutorial', None)
        super(NewQuestionForm, self).__init__(*args, **kwargs)
        tutorial_choices = (
                ("Select a Sub Category", "Select a Sub Category"),
        )

        if category == '12':
            if FossCategory.objects.filter(id = category).exists():
                self.fields['category'].initial = category
                children = SubFossCategory.objects.filter(parent_id = category)

                for child in children:
                    tutorial_choices += ((child.name, child.name), )

                self.fields['tutorial'] = forms.CharField(widget = forms.Select(choices = tutorial_choices))
                if SubFossCategory.objects.filter(name = selecttutorial).exists():
                    self.fields['tutorial'].initial = selecttutorial
            else:
                self.fields['tutorial'] = forms.CharField(widget = forms.Select(choices = tutorial_choices))
        else:
            self.fields['category'].initial = category
            self.fields['tutorial'] = forms.CharField(widget = forms.Select(choices = tutorial_choices))

class AnswerQuestionForm(forms.ModelForm):

    question = forms.IntegerField(widget = forms.HiddenInput())

    body = forms.CharField(widget = CKEditorWidget(),
        required = True,
        error_messages = {'required':'Answer field required'}
    )

    image = forms.ImageField(widget = CustomClearableFileInput(), help_text = "Upload image", required = False)

    spam_honeypot_field = HoneypotField()

    def clean_body(self):

        body = str(self.cleaned_data['body'])
        body = body.replace('&nbsp;', ' ')
        body = body.replace('<br>', '\n')
        if body.isspace():
            raise forms.ValidationError("Body cannot be only spaces")
        if len(body) < 12:
            raise forms.ValidationError("Body should be minimum 12 characters long")
        temp = BeautifulSoup(body, 'html.parser').get_text()
        if (temp.isspace() or temp == ''):
            raise forms.ValidationError("Body cannot be only tags")

        return body

    def clean_image(self):
        image = self.cleaned_data['image']

        if (image != None):
            if (image._size > settings.MAXIMUM_FILE_SIZE):
                raise forms.ValidationError('File size needs to be under {0} MB.'.format(settings.MAX_FILE_SIZE_MB))

        return image

    class Meta(object):

        model = Question
        fields = ['question', 'body', 'image']

class AnswerCommentForm(forms.Form):

    body = forms.CharField(widget = forms.Textarea(), required = True,
        error_messages = {'required':'Comment field required'})
    spam_honeypot_field = HoneypotField()

    def clean_body(self):
        body = str(self.cleaned_data['body'])
        body = body.replace('&nbsp;', ' ')
        body = body.replace('<br>', '\n')
        if body.isspace():
            raise forms.ValidationError("Body cannot be only spaces")

        temp = BeautifulSoup(body, 'html.parser').get_text()
        if (temp.isspace() or temp == ''):
            raise forms.ValidationError("Body cannot be only tags")
        return body