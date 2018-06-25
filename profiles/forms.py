from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit, Button
from crispy_forms.bootstrap import FormActions, StrictButton

class Row(Div):
    css_class = "form-row"


class ProfileSignupForm(UserCreationForm):
    # Manually define Password1 to suppress help text.
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(ProfileSignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-ProfileForm'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Field('username', wrapper_class='col-md-4'),
                Field('password1', wrapper_class='col-md-4'),
                Field('password2', wrapper_class='col-md-4'),
            ),
            Row(
                Field('first_name', wrapper_class='col-md-4'),
                Field('last_name', wrapper_class='col-md-4'),
                Field('email', wrapper_class='col-md-4'),
            ),
            Submit('save', 'Save', css_class='btn-primary'),
            Submit('cancel', 'Cancel', css_class='btn-danger', formnovalidate='formnovalidate'),
        )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'email']
