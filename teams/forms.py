from crispy_forms.layout import Submit, Layout, Row
from django import forms
from crispy_forms.helper import FormHelper

# ChoiceField must be tuple - (Data, Display)
from teams.models import Human_Player_Match

DRIVETRAINS = (
    ("Swerve", "Swerve"),
    ("WestCoast", "WestCoast"),
    ("Mechanum","Mechanum"),
    ("Omni", "Omni"),
    ("Tank", "Tank")
)

INTAKE_LOCATION = (
    ("Source", "Source"),
    ("Ground", "Ground"),
    ("None :(", "None :("))

SCORING_LOCATION = (
    ("L1", "L1"),
    ("L2", "L2"),
    ("L3", "L3"),
    ("L4", "L4"),
    ("Net", "Net"),
    ("Processor", "Processor")
)

INTAKE_DESIGN = (
    ("Over Bumper", "Over Bumper"),
    ("Under Bumper", "Under Bumper"),
    ("Other", "Other")
)

AUTO_POSITIONS = (
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5")
)

PREFERRED_CAGE_POSITION = (
    ("Shallow", "Shallow"),
    ("Deep", "Deep")
)

BOOLEAN_VALUES = (
    ("Yes", "Yes"),
    ("No", "No")
)


class NewPitScoutingData(forms.Form):
    drivetrain = forms.ChoiceField(choices=DRIVETRAINS,
                                   widget=forms.RadioSelect)
    weight = forms.IntegerField()
    length = forms.IntegerField()
    width = forms.IntegerField()
    intake_design = forms.ChoiceField(choices=INTAKE_DESIGN, 
                                              widget=forms.RadioSelect)
    intake_locations = forms.MultipleChoiceField(choices=INTAKE_LOCATION,
                                                 widget=forms.CheckboxSelectMultiple)
    scoring_locations = forms.MultipleChoiceField(choices=SCORING_LOCATION,
                                                  widget=forms.CheckboxSelectMultiple)
    auto_positions = forms.MultipleChoiceField(choices=AUTO_POSITIONS, 
                                               widget=forms.CheckboxSelectMultiple)
    # Change this to MultipleChoiceField
    cage_positions = forms.MultipleChoiceField(
        choices=PREFERRED_CAGE_POSITION,
        widget=forms.CheckboxSelectMultiple,  # Change to CheckboxSelectMultiple
        required=True
    )
    under_shallow_coral = forms.ChoiceField(
        choices=BOOLEAN_VALUES,
        widget=forms.RadioSelect,
        required=True
    )
    removeable = forms.ChoiceField(
        choices=BOOLEAN_VALUES,
        widget=forms.RadioSelect
    )
    auto_leave = forms.ChoiceField(
        choices=BOOLEAN_VALUES, 
        widget=forms.RadioSelect,
        required=True
    )
    auto_total_notes = forms.IntegerField()
    auto_coral_notes = forms.IntegerField()
    robot_picture = forms.ImageField()
    additional_info = forms.CharField(
        max_length=512,
        required=False,
        widget=forms.Textarea
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.attrs = {"novalidate": ''}
        self.helper.layout = Layout(
            'drivetrain',
            'weight',
            'length',
            'width',
            'intake_design',
            'intake_locations',
            'scoring_locations',
            'cage_positions',
            'under_shallow_coral',
            'removeable',
            'auto_leave',
            'auto_positions',
            'auto_total_notes',
            'auto_coral_notes',
            'robot_picture',
            'additional_info',
            Submit('submit', 'Submit')
        )


class NewHumanScoutingData(forms.ModelForm):
    class Meta:
        model = Human_Player_Match
        fields = ["match_number", "human_player_comment"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"novalidate": ''}
        self.helper.layout = Layout(
            'match_number',
            'human_player_comment',
            Submit('submit', 'Submit'))
