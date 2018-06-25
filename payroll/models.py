import datetime

from django.db import models
from django.db.models import Sum, F

from profiles.models import Profile, Role

# Create your models here.
class Payroll(models.Model):
    employee = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, related_name='employee_paystubs')
    current_wage = models.DecimalField(blank=True, max_digits=6, decimal_places=2)
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    date_paid = models.DateField(blank=True, null=True)
    paid = models.BooleanField(default=False)
    # the following taxes are calculated on save
    employee_medicare = models.DecimalField(blank=True, max_digits=6, decimal_places=2)
    employee_social_security = models.DecimalField(blank=True, max_digits=6, decimal_places=2)
    employer_medicare = models.DecimalField(blank=True, max_digits=6, decimal_places=2)
    employer_social_security = models.DecimalField(blank=True, max_digits=6, decimal_places=2)
    futa = models.DecimalField(blank=True, max_digits=6, decimal_places=2)
    wa_uta = models.DecimalField(blank=True, max_digits=6, decimal_places=2)
    gross_total = models.DecimalField(blank=True, max_digits=6, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calculate whether FUTA should be withheld and, if so, how much.
        # FUTA is only withheld on the first $7,000 in wages.
        self.current_wage = self.employee.wage
        current_year = datetime.datetime.now().year
        if Payroll.objects.filter(employee=self.employee):
            current_year_payroll_hours = Payroll.objects.filter(employee=self.employee).exclude(
                pay_period_end__year__lt=current_year, pay_period_end__year__gt=current_year).aggregate(
                Sum('hours'))
            if current_year_payroll_hours['hours__sum'] * self.current_wage < 7000:
                self.futa = float((self.hours * self.current_wage)) * .006
            else:
                self.futa = 0
        else:
            self.futa = float((self.hours * self.current_wage)) * .006
        # Calculate other taxes.
        self.employee_medicare = self.employer_medicare = float((self.hours * self.current_wage)) * .0145
        self.employee_social_security = self.employer_social_security = float((self.hours * self.current_wage)) * .062
        self.wa_uta = float((self.hours * self.current_wage)) * .0119
        self.gross_total = float((self.hours * self.current_wage))
        return super(Payroll, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-pay_period_start',)
        permissions = (
            ('approve_payroll', 'Approve Payroll'),
        )

    def __str__(self):
        return "{0} to {1}".format(self.pay_period_start.strftime('%m/%d/%Y'), self.pay_period_end.strftime('%m/%d/%Y'))


