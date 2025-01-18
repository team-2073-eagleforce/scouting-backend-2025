from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout

class NewPitScoutingData(forms.Form):
    # Your form fields here...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'  # Add this line
        self.helper.form_enctype = 'multipart/form-data'  # Add this line
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
            Submit('submit', 'Submit'))
