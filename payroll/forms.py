from django import forms
from django.forms import ModelForm
from payroll.models import Payroll
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Button, Field, Div
from crispy_forms.bootstrap import FormActions, AppendedText
from profiles.models import Profile

class Row(Div):
    css_class = "form-row"


class PayrollEntryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(PayrollEntryForm, self).__init__(*args, **kwargs)
        self.fields['employee'].queryset = Profile.objects.filter(wage__isnull=False).prefetch_related('user')
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-PayrollForm'
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-8'
        self.helper.layout = Layout(
            Field('employee'),
            Field('pay_period_start', autocomplete='off'),
            Field('pay_period_end', autocomplete='off'),
            'hours',
            FormActions(
                Submit('save', 'Save', css_class='btn-primary'),
                Submit('cancel', 'Cancel', css_class='btn btn-danger', formnovalidate='formnovalidate'),
            )
        )
        if self.user.profile.wage:
            del self.fields['employee']

    class Meta:
        model = Payroll
        fields = ['employee', 'pay_period_start', 'pay_period_end', 'hours']


class PayrollReviewForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PayrollReviewForm, self).__init__(*args, **kwargs)

        self.fields['employee'].queryset = Profile.objects.filter(wage__isnull=False).prefetch_related('user')

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Field('employee', wrapper_class='col-md-8'),
            ),
            Row(
                Field('pay_period_start', wrapper_class='col-md-4'),
                Field('pay_period_end', wrapper_class='col-md-4'),
                Field('hours', wrapper_class='col-md-4'),
            ),
            Row(
                    Field('paid'),
            ),
            FormActions(
                Submit('submit', 'Save', css_class='btn-default'),
                Submit('cancel', 'Cancel', css_class='btn-danger', formnovalidate='formnovalidate')
            )
        )

    class Meta:
        model = Payroll
        fields = ['employee', 'pay_period_start', 'pay_period_end', 'hours', 'paid']