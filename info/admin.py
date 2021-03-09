from datetime import timedelta, datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.urls import path

from .models import Class, Student, Attendance, Teacher, AssignClassTeacher, AttendanceClass
from .models import User, AttendanceRange


def daterange(start_date, end_date):
	for n in range(int((end_date - start_date).days)):
		yield start_date + timedelta(n)


class ClassInline(admin.TabularInline):
	model = Class
	extra = 0


class StudentInline(admin.TabularInline):
	model = Student
	extra = 0

	def has_add_permission(self, request, obj):
		return False


class ClassAdmin(admin.ModelAdmin):
	list_display = ('id', 'class_name', 'section')
	search_fields = ('id', 'class_name', 'section')
	ordering = ['id', 'class_name', 'section']
	inlines = [StudentInline]


class StudentAdmin(admin.ModelAdmin):
	list_display = ('roll_no', 'name', 'class_id')
	search_fields = ('roll_no', 'name', 'class_id__id')
	ordering = ['class_id__id', 'roll_no']
	list_filter = ['class_id']


class TeacherAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	ordering = ['name']


class AssignClassTeacherAdmin(admin.ModelAdmin):
	list_display = ('class_id', 'teacher')
	search_fields = ('class_id__id', 'teacher__name')
	ordering = ['teacher__name', 'class_id__id']
	raw_id_fields = ['class_id', 'teacher']


class AttendanceInline(admin.TabularInline):
	model = Attendance
	fields = ['student', 'status']
	readonly_fields = ['student']
	extra = 0

	def has_add_permission(self, request, obj):
		return False

	def has_delete_permission(self, request, obj=None):
		return False


class AttendanceClassAdmin(admin.ModelAdmin):
	list_display = ('assign_ct', 'date', 'status')
	ordering = ['assign_ct', 'date']
	# change_list_template = 'admin/attendance/attendance_change_list.html'
	list_filter = ['date', 'assign_ct__class_id', 'assign_ct__teacher_id']
	inlines = [AttendanceInline]


class AttendanceRangeAdmin(admin.ModelAdmin):
	list_display = ('start_date', 'end_date')
	change_list_template = 'admin/attendance/attendance_change_list.html'

	def has_add_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return False

	def get_urls(self):
		urls = super().get_urls()
		my_urls = [
			path('reset_attd/', self.reset_attd, name='reset_attd'),
		]
		return my_urls + urls

	def reset_attd(self, request):

		start_date = datetime.strptime(request.POST['startdate'], '%Y-%m-%d').date()
		end_date = datetime.strptime(request.POST['enddate'], '%Y-%m-%d').date()

		try:
			a = AttendanceRange.objects.all()[:1].get()
			a.start_date = start_date
			a.end_date = end_date
			a.save()
		except AttendanceRange.DoesNotExist:
			a = AttendanceRange(start_date=start_date, end_date=end_date)
			a.save()

		Attendance.objects.all().delete()
		AttendanceClass.objects.all().delete()

		for asst in AssignClassTeacher.objects.all():
			for single_date in daterange(start_date, end_date + timedelta(days=1)):
				if single_date.isoweekday() != 7:
					try:
						AttendanceClass.objects.get(date=single_date.strftime("%Y-%m-%d"), assign_ct=asst)
					except AttendanceClass.DoesNotExist:
						a = AttendanceClass(date=single_date.strftime("%Y-%m-%d"), assign_ct=asst)
						a.save()

		self.message_user(request, "Attendance Dates reset successfully!")
		return HttpResponseRedirect("../")


# Common
admin.site.register(User, UserAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)

# Attendance
admin.site.register(AssignClassTeacher, AssignClassTeacherAdmin)
admin.site.register(AttendanceClass, AttendanceClassAdmin)
admin.site.register(AttendanceRange, AttendanceRangeAdmin)
