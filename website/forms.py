from django import forms

from website.models import *

categories = (
    ("None", "Select a Category"),
    ("General", "General"),
    ('Advanced-C++', 'Advanced-C++'),
    ('BASH', 'BASH'),
    ('Blender', 'Blender'),
    ('C-and-C++', 'C-and-C++'),
    ('CellDesigner', 'CellDesigner'),
    ('Digital-Divide', 'Digital-Divide'),
    ('Drupal', 'Drupal'),
    ('Firefox', 'Firefox'),
    ('GChemPaint', 'GChemPaint'),
    ('Geogebra', 'Geogebra'),
    ('GeoGebra-for-Engineering-drawing', 'GeoGebra-for-Engineering-drawing'),
    ('GIMP', 'GIMP'),
    ('GNS3', 'GNS3'),
    ('GSchem', 'GSchem'),
    ('Inkscape', 'Inkscape'),
    ('Java', 'Java'),
    ('Java-Business-Application', 'Java-Business-Application'),
    ('KiCad', 'KiCad'),
    ('KTouch', 'KTouch'),
    ('KTurtle', 'KTurtle'),
    ('LaTeX', 'LaTeX'),
    ('LibreOffice-Suite-Base', 'LibreOffice-Suite-Base'),
    ('LibreOffice-Suite-Calc', 'LibreOffice-Suite-Calc'),
    ('LibreOffice-Suite-Draw', 'LibreOffice-Suite-Draw'),
    ('LibreOffice-Suite-Impress', 'LibreOffice-Suite-Impress'),
    ('LibreOffice-Suite-Math', 'LibreOffice-Suite-Math'),
    ('LibreOffice-Suite-Writer', 'LibreOffice-Suite-Writer'),
    ('Linux', 'Linux'),
    ('Netbeans', 'Netbeans'),
    ('Ngspice', 'Ngspice'),
    ('OpenFOAM', 'OpenFOAM'),
    ('Orca', 'Orca'),
    ('Oscad', 'Oscad'),
    ('PERL', 'PERL'),
    ('PHP-and-MySQL', 'PHP-and-MySQL'),
    ('Python', 'Python'),
    ('Python-Old-Version', 'Python-Old-Version'),
    ('QCad', 'QCad'),
    ('R', 'R'),
    ('Ruby', 'Ruby'),
    ('Scilab', 'Scilab'),
    ('Selenium', 'Selenium'),
    ('Single-Board-Heater-System', 'Single-Board-Heater-System'),
    ('Spoken-Tutorial-Technology', 'Spoken-Tutorial-Technology'),
    ('Step', 'Step'),
    ('Thunderbird', 'Thunderbird'),
    ('Tux-Typing', 'Tux-Typing'),
    ('What-is-Spoken-Tutorial', 'What-is-Spoken-Tutorial'),
    ('Xfig', 'Xfig')
)
tutorials = (
    ("None", "Select a Tutorial"),
)
minutes = (
    ("None", "min"),
)
seconds= (
    ("None", "sec"),
)

class NewQuestionForm(forms.Form):
    #fix dirty code
    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        super(NewQuestionForm, self).__init__(*args, **kwargs)
        self.fields['category'] = forms.CharField(widget=forms.Select(choices=categories))
        self.fields['category'].initial = category
        
        tutorial_choices = (
            ("None", "Select a Tutorial"),
        )
        if (category, category) in categories:
            tutorials = TutorialDetails.objects.using('spoken').filter(foss_category=category)
            for tutorial in tutorials:
                tutorial_choices += ((tutorial.tutorial_name, tutorial.tutorial_name),)
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
