import datetime

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect, Http404
from django.db.models import Sum, F
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.template.loader import render_to_string, get_template
from django.template import Context
from django.conf import settings

from braces import views

from .forms import PayrollEntryForm, PayrollReviewForm
from .models import Payroll


# Create your views here.
class PayrollListView(views.LoginRequiredMixin,
                      views.MultiplePermissionsRequiredMixin,
                      ListView):
    permissions = {
        'any': ('payroll.add_payroll', 'payroll.approve_payroll')
    }
    model = Payroll
    template_name = 'payroll/payroll_list.html'

    def get_queryset(self):
        queryset = super(PayrollListView, self).get_queryset()
        if self.request.user.groups.filter(name='Nanny').exists():
            queryset = queryset.filter(employee=self.request.user.profile)\
                .annotate(
                employer_taxes=F('employer_social_security') + F('employer_medicare') + F('futa') + F('wa_uta'),)\
                .prefetch_related('employee__user')
        else:
            queryset = queryset.annotate(
                employer_taxes=F('employer_social_security') + F('employer_medicare') + F('futa') + F('wa_uta'),)\
                .prefetch_related('employee__user')
        return queryset


class PayrollDetailView(views.LoginRequiredMixin,
                        views.MultiplePermissionsRequiredMixin,
                        DetailView):
    permissions = {
        'any': ('payroll.add_payroll', 'payroll.approve_payroll')
    }
    model = Payroll
    template_name = 'payroll/payroll_detail.html'

    def get_object(self):
        # Ensures that only those on the invoice and approvers can see invoices.
        object = get_object_or_404(Payroll, pk=self.kwargs['pk'])
        if self.request.user.profile == object.employee or self.request.user.has_perm('payroll.approve_payroll'):
            return object
        else:
            raise Http404('You are not authorized to view this invoice.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_taxes'] = self.object.employee_medicare + self.object.employee_social_security
        context['employer_taxes'] =  self.object.employer_medicare + \
                                     self.object.employer_social_security + self.object.futa + self.object.wa_uta
        context['combined_taxes'] = context['employee_taxes'] + context['employer_taxes']
        context['total_cost'] = self.object.gross_total + context['employer_taxes']
        context['net_pay'] = self.object.gross_total - context['employee_taxes']
        context['ytd'] = Payroll.objects\
            .filter(employee=self.object.employee, pay_period_end__year=self.object.pay_period_end.year)\
            .exclude(pay_period_start__gt=self.object.pay_period_start)\
            .aggregate(gross_total=Sum('gross_total'),employer_medicare=Sum('employer_medicare'),
                       employer_social_security=Sum('employer_social_security'), futa=Sum('futa'), wa_uta=Sum('wa_uta'),
                       employee_medicare=Sum('employee_medicare'), employee_social_security=Sum('employee_social_security'),
                       )
        context['ytd']['employer_taxes'] = \
            context['ytd']['employer_medicare'] + context['ytd']['employer_social_security'] + context['ytd']['futa'] + context['ytd']['wa_uta']
        context['ytd']['employee_taxes'] = context['ytd']['employee_medicare'] + context['ytd']['employee_social_security']
        context['ytd']['net_pay'] = context['ytd']['gross_total'] - context['ytd']['employee_taxes']
        context['ytd']['total_cost'] = context['ytd']['gross_total'] + context['ytd']['employer_taxes']
        context['ytd']['combined_taxes'] = context['ytd']['employer_taxes'] + context['ytd']['employee_taxes']
        return context


class PayrollEntryView(views.LoginRequiredMixin,
                       views.MultiplePermissionsRequiredMixin,
                       CreateView):
    permissions = {
        'any': ('payroll.add_payroll', 'payroll.approve_payroll')
    }
    model = Payroll
    form_class = PayrollEntryForm
    template_name = 'payroll/payroll_entry.html'

    def get_success_url(self):
        return reverse_lazy('payroll:list')

    def get_form_kwargs(self):
        kwargs = super(PayrollEntryView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse_lazy('payroll:list'))
        else:
            return super(PayrollEntryView, self).post(self, request, *args, **kwargs)

    def send_email(self, obj):
        subject = '[Sébastien] Time Card Submitted'
        from_email = settings.DEFAULT_FROM_EMAIL
        context = {
            'employee': obj.employee.user.first_name,
            'pay_period_end': obj.pay_period_end,
            'id': obj.pk,
            'site_url': self.request.META['HTTP_HOST']
        }
        payroll_email_employer = render_to_string('payroll/payroll_entered_for_employer.html', context)
        approver_emails = [a.email for a in User.objects.all() if a.has_perm('payroll.approve_payroll')]
        if obj.employee.user.email:
            payroll_email_employee = render_to_string('payroll/payroll_entered_for_employee.html', context)
            send_mail(
                subject,
                'Your timecard for pay period ending {0} has been submitted for review.'.format(context['pay_period_end']),
                from_email,
                [obj.employee.user.email, ],
                fail_silently=True,
                html_message=payroll_email_employee,
            )
        send_mail(subject,
                  '{0} has entered a timecard for pay period ending {1}. Please go to sebastien.site to review and approve it.'.format(context['employee'], context['pay_period_end']),
                  from_email,
                  approver_emails,
                  fail_silently=True,
                  html_message=payroll_email_employer)

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.employee:
            obj = form.save()
            # self.send_email(obj)
            return super(PayrollEntryView, self).form_valid(form)
        else:
            employee = self.request.user
            if not employee.profile.wage:
                messages.add_message(self.request, messages.ERROR,
                                     'Your account is not set up to enter time cards. Please contact an administrator.')
                return HttpResponseRedirect(reverse_lazy('payroll:list'))
            else:
                obj.employee = employee.profile
                obj.save()
                # self.send_email(obj)
                return super(PayrollEntryView, self).form_valid(form)


class PayrollReviewView(views.LoginRequiredMixin,
                        views.PermissionRequiredMixin,
                        UpdateView):
    permission_required = 'payroll.approve_payroll'
    model = Payroll
    form_class = PayrollReviewForm
    template_name = 'payroll/payroll_review.html'

    def get_success_url(self):
        return reverse_lazy('payroll:list')

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse_lazy('payroll:list'))
        else:
            return super(PayrollReviewView, self).post(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_taxes'] = self.object.employee_medicare + self.object.employee_social_security
        context['employer_taxes'] =  self.object.employer_medicare + self.object.employer_social_security + self.object.futa + self.object.wa_uta
        context['combined_taxes'] = context['employee_taxes'] + context['employer_taxes']
        context['total_cost'] = self.object.gross_total + context['employer_taxes']
        context['net_pay'] = self.object.gross_total - context['employee_taxes']
        context['ytd'] = Payroll.objects\
            .filter(employee=self.object.employee, pay_period_end__year=self.object.pay_period_end.year)\
            .exclude(pay_period_start__gt=self.object.pay_period_start)\
            .aggregate(gross_total=Sum('gross_total'),employer_medicare=Sum('employer_medicare'),
                       employer_social_security=Sum('employer_social_security'), futa=Sum('futa'), wa_uta=Sum('wa_uta'),
                       employee_medicare=Sum('employee_medicare'), employee_social_security=Sum('employee_social_security'),
                       )
        context['ytd']['employer_taxes'] = \
            context['ytd']['employer_medicare'] + context['ytd']['employer_social_security'] + context['ytd']['futa'] + context['ytd']['wa_uta']
        context['ytd']['employee_taxes'] = context['ytd']['employee_medicare'] + context['ytd']['employee_social_security']
        context['ytd']['net_pay'] = context['ytd']['gross_total'] - context['ytd']['employee_taxes']
        context['ytd']['total_cost'] = context['ytd']['gross_total'] + context['ytd']['employer_taxes']
        context['ytd']['combined_taxes'] = context['ytd']['employer_taxes'] + context['ytd']['employee_taxes']
        return context

    def send_email(self, obj):
        subject = '[Sébastien] Time Card Approved'
        from_email = settings.DEFAULT_FROM_EMAIL
        context = {
            'employee': obj.employee.user.first_name,
            'pay_period_end': obj.pay_period_end,
            'id': obj.pk,
            'site_url': self.request.META['HTTP_HOST']
        }
        approver_emails = [a.email for a in User.objects.all() if a.has_perm('payroll.approve_payroll')]
        payroll_email_employer = render_to_string('payroll/payroll_approved_for_employer.html', context)
        if obj.employee.user.email:
            payroll_email_employee = render_to_string('payroll/payroll_approved_for_employee.html', context)
            send_mail(subject,
                      'Your timecard for pay period ending {0} has been approved. Visit sebastien.site to review the invoice'.format(context['pay_period_end']),
                      from_email,
                      [obj.employee.user.email],
                      fail_silently=True,
                      html_message=payroll_email_employee)
        send_mail(subject,
                  'The timecard for pay period ending {0} for {1} has been approved. Visit sebastien.site to review the invoice.'.format(context['pay_period_end'], context['employee']),
                  from_email,
                  approver_emails,
                  fail_silently=True,
                  html_message=payroll_email_employer)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.paid = True
        obj.date_paid = datetime.datetime.now()
        obj.save()
        # self.send_email(obj)
        return super(PayrollReviewView, self).form_valid(form)


class PayrollDeleteView(views.LoginRequiredMixin,
                        views.PermissionRequiredMixin,
                        DeleteView):
    permission_required = 'payroll.approve_payroll'
    model = Payroll
    success_url = reverse_lazy('payroll:list')
