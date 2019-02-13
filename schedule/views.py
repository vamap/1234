from django.shortcuts import render

from django.shortcuts import get_object_or_404
from django.views.generic import View,ListView,DetailView,CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils import timezone
# Create your views here.
from .models import Working,WorkingCode
from .forms import WorkingForm
from department.models import Department
from employee.models import User
from department.models import Section
import datetime


from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView


class PassRequestToFormViewMixin:
	def get_form_kwargs(self):
		kwargs = super(PassRequestToFormViewMixin, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

class WorkingCreate(PassRequestToFormViewMixin,LoginRequiredMixin,CreateView):
	model 		= Working
	form_class 	= WorkingForm
	success_url = reverse_lazy('schedule:list')

	def get_form(self, form_class=None):
		"""
		Returns an instance of the form to be used in this view.
		"""
		form = super(WorkingCreate, self).get_form(form_class)
		# user = Section.objects.get(name=self.kwargs['section'])
		form.fields['workingcode'].queryset = WorkingCode.objects.filter(section__name=self.kwargs['section'])
		form.fields['user'].queryset = User.objects.filter(en=self.kwargs['en'])
		return form

	def get_initial(self):
		print ('CreateView-get_initial')
		initial = super().get_initial()
		# cpf - it's the name of the field on your current form
		# self.args will be filled from URL. I'd suggest to use named parameters
		# so you can access e.g. self.kwargs['cpf_initial']
		year = self.request.GET.get('year', None)
		month = self.request.GET.get('month', None)
		day = self.request.GET.get('day', None)
		initial['working_date'] = datetime.date(int(year),int(month),int(day))
		initial['user'] = User.objects.get(en =self.kwargs['en'])
		return initial

	def form_valid(self, form):
		# form.instance.user = self.request.user
		# print ('On form_valid %s' % self.request.user)
		s = super(WorkingCreate, self).form_valid(form)
		form.instance.logs.create(note= ('[ work code : %s] %s ' %(form.instance.workingcode.name,form.instance.note)) ,
							user=self.request.user,log_type='ADD')
		return s

	def get_context_data(self, **kwargs):
		context = super(WorkingCreate, self).get_context_data(**kwargs)        
		# year = self.request.GET.get('year', None)
		# month = self.request.GET.get('month', None)
		# day = self.request.GET.get('day', None)
		# context['working_date'] = datetime.date(int(year),int(month),int(day))
		context['title'] = 'Create Working Schedule'
		return context

class WorkingUpdate(UpdateView):
	model = Working
	fields = ['workingcode','note']
	pk_url_kwarg = 'pk'
	success_url = reverse_lazy('schedule:list')
	
	def get_context_data(self, **kwargs):
		context = super(WorkingUpdate, self).get_context_data(**kwargs)        
		context['title'] = 'Update Working Schedule'
		return context

	def get_form(self, form_class=None):
		"""
		Returns an instance of the form to be used in this view.
		"""
		self.object = self.get_object()
		form = super(WorkingUpdate, self).get_form(form_class)
		# print (self.object.user.section)
		form.fields['workingcode'].queryset = WorkingCode.objects.filter(section=self.object.user.section)
		return form

	def form_valid(self, form):
		# form.instance.user = self.request.user
		# print ('On form_valid %s' % self.request.user)
		s = super(WorkingUpdate, self).form_valid(form)
		form.instance.logs.create(note= ('[ work code : %s] %s ' %(form.instance.workingcode.name,form.instance.note)) ,
							user=self.request.user,log_type='CHG')
		return s

class WorkingDelete(DeleteView):
	model = Working
	success_url = reverse_lazy('schedule:list')

class WorkingListView(LoginRequiredMixin,ListView):
	model = Working
	# template_name = 'schedule/bayplan_voy_detail.html'

	def get_context_data(self, **kwargs):
		context     = super().get_context_data(**kwargs)
		user 		= self.request.user
		section 	= user.section
		department 	= section.department
		# print(user.groups.all())
		year = self.request.GET.get('year', None)
		month = self.request.GET.get('month', None)

		# display mode (mode=None --> show Working Code(default) , mode=Status -->show status mode)
		mode = self.request.GET.get('mode', None)

		if year and month:
			report_date 	= datetime.date(int(year),int(month),1)
		else:
			report_date 	= timezone.now()

		context['now'] 	= report_date

		if user.groups.filter(name__in=['HR staff']).exists():
			# print ('HR Staff')
			if 'department' in self.kwargs:
				department 	= self.kwargs['department']
				# print (department)
				context['section_list'] = list(Section.objects.filter(department__name = department))
				context['working_list'] = list(Working.objects.filter(
										user__section__department__name = department,
										working_date__year = report_date.year,
										working_date__month = report_date.month))
				context['department'] = department
				print('finished on View')
			else:
				context['section_list'] 	= None
				context['working_list'] 	= None

			context['department_list']	= list(Department.objects.all())
			context['hr_staff']			= True
		else :
			context['section_list'] = list(Section.objects.filter(department = section.department))
			context['working_list'] = list(Working.objects.filter(
										user__section__department = department,
										working_date__year = report_date.year,
										working_date__month = report_date.month))
		if mode :
			context['mode'] = mode

		
		return context

	def get_queryset(self):
		user 		= self.request.user
		section 	= user.section
		department 	= section.department
		if user.groups.filter(name__in=['HR staff']).exists():
			working = Working.objects.all()
		else:
			working = Working.objects.filter(user__section__department = department)
		return working

class WorkingSectionListView(LoginRequiredMixin,ListView):
	model = Working
	# self.kwargs['lab']
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['department'] ='TEst depart'
		user 		= self.request.user
		section 	= user.section
		context['now'] = timezone.now()
		context['section_list'] = Section.objects.filter(department = section.department)
		return context