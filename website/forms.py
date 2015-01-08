from django import forms

from website.models import *
from spoken_auth.models import TutorialDetails, TutorialResources, FossCategory
from django.db.models import Q
tutorials = (
    ("", "Select a Tutorial"),
)
minutes = (
    ("", "min"),
)
seconds= (
    ("", "sec"),
)

class NewQuestionForm(forms.Form):
    category = forms.ChoiceField(choices = [('', 'Select a Category'),] + list(TutorialResources.objects.filter(Q(status = 1) | Q(status = 2), language__name = 'English').values('tutorial_detail__foss__foss').order_by('tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'tutorial_detail__foss__foss').distinct()), widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'State field is required.'})
    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        super(NewQuestionForm, self).__init__(*args, **kwargs)
        tutorial_choices = (
            ("", "Select a Tutorial"),
        )
        if not category and args and 'category' in args[0] and args[0]['category']:
            category = args[0]['category']
        if FossCategory.objects.filter(foss=category).exists():
            self.fields['category'].initial = category
            tutorials = TutorialDetails.objects.using('spoken').filter(foss__foss=category)
            for tutorial in tutorials:
                tutorial_choices += ((tutorial.tutorial, tutorial.tutorial),)
            self.fields['tutorial'] = forms.CharField(widget=forms.Select(choices=tutorial_choices))
        else:
            self.fields['tutorial'] = forms.CharField(widget=forms.Select(choices=tutorial_choices))

    minute_range = forms.CharField(widget=forms.Select(choices=minutes))
    second_range = forms.CharField(widget=forms.Select(choices=seconds))
    title = forms.CharField(max_length=200)
    body = forms.CharField(widget=forms.Textarea())

class AnswerQuesitionForm(forms.Form):
    question = forms.IntegerField(widget=forms.HiddenInput())
    body = forms.CharField(widget=forms.Textarea())
