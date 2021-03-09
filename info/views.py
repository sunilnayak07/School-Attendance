from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Class, Student, Attendance, Teacher, AssignClassTeacher, AttendanceClass, AttendanceTotal
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
import datetime


@login_required()
def index(request):
	if request.user.is_teacher:
		return render(request, 'info/t_homepage.html')
	if request.user.is_student:
		return render(request, 'info/homepage.html')
	return render(request, 'info/logout.html')


# --------------------
#   Attendance Views
# --------------------

# Student Attendance
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def attendance(request, stud_id):
	if request.method == "POST":
		try:
			from_date = request.POST.get('from_date')
			to_date = request.POST.get('to_date')
			search_result = Attendance.objects.raw(
				'select * from info_attendance where student_id = %s AND date between "' + from_date + '" and "' + to_date + '" ORDER BY date',
				[stud_id])
			return render(request, 'info/attendance.html', {'att_list': search_result,
			                                                'from_date': datetime.datetime.strptime(from_date,
			                                                                                        "%Y-%m-%d").date(),
			                                                'to_date': datetime.datetime.strptime(to_date,
			                                                                                      "%Y-%m-%d").date()})
		except ValueError:
			today = datetime.date.today()
			last_seven = today - datetime.timedelta(days=7)
			search_result = Attendance.objects.raw(
				'select * from info_attendance where student_id = %s AND date between "' + str(
					last_seven) + '" and "' + str(today) + '" ORDER BY date DESC', [stud_id])
			return render(request, 'info/attendance.html', {'att_list': search_result,
			                                                'from_date': last_seven,
			                                                'to_date': today})
	else:
		today = datetime.date.today()
		last_seven = today - datetime.timedelta(days=7)
		search_result = Attendance.objects.raw(
			'select * from info_attendance where student_id = %s AND date between "' + str(last_seven) + '" and "' + str(
				today) + '" ORDER BY date DESC', [stud_id])
		return render(request, 'info/attendance.html', {'att_list': search_result,
		                                                'from_date': last_seven,
		                                                'to_date': today})


# Teacher Attendance
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def t_class(request, teacher_id, choice):
	if request.user.is_teacher:
		teacher1 = get_object_or_404(Teacher, id=teacher_id)
		return render(request, 'info/t_class.html', {'teacher1': teacher1, 'choice': choice})
	elif request.user.is_student:
		return render(request, 'info/homepage.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def t_class_date(request, assign_ct_id):
	if request.user.is_teacher:
		ass = get_object_or_404(AssignClassTeacher, id=assign_ct_id)
		if request.method == "POST":
			try:
				from_date = request.POST.get('from_date')
				to_date = request.POST.get('to_date')
				search_result = AttendanceClass.objects.raw('select * from info_attendanceclass where assign_ct_id = '
				                                            '%s AND date between "' + from_date + '" and "' + to_date + '" ORDER BY date',
				                                            [assign_ct_id])
				return render(request, 'info/t_class_date.html', {'att_list': search_result, 'ass': ass,
				                                                  'from_date': datetime.datetime.strptime(from_date,
				                                                                                          "%Y-%m-%d").date(),
				                                                  'to_date': datetime.datetime.strptime(to_date,
				                                                                                        "%Y-%m-%d").date()})
			except ValueError:
				today = datetime.date.today()
				last_seven = today - datetime.timedelta(days=7)
				search_result = AttendanceClass.objects.raw(
					'select * from info_attendanceclass where assign_ct_id = %s AND date between "' + str(
						last_seven) + '" and "' + str(today) + '" ORDER BY date DESC', [assign_ct_id])
				return render(request, 'info/t_class_date.html', {'att_list': search_result,
				                                                  'ass': ass,
				                                                  'from_date': last_seven,
				                                                  'to_date': today})
		else:
			today = datetime.date.today()
			last_seven = today - datetime.timedelta(days=7)
			search_result = AttendanceClass.objects.raw('select * from info_attendanceclass where assign_ct_id = %s '
			                                            'AND date between "' + str(last_seven) + '" and "' + str(today) + '" '
			                                                                                                              'ORDER BY date DESC',
			                                            [assign_ct_id])
			return render(request, 'info/t_class_date.html', {'att_list': search_result,
			                                                  'ass': ass,
			                                                  'from_date': last_seven,
			                                                  'to_date': today})
	elif request.user.is_student:
		return render(request, 'info/homepage.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def cancel_class(request, ass_c_id):
	if request.user.is_teacher:
		assc = get_object_or_404(AttendanceClass, id=ass_c_id)
		assc.status = 2
		assc.save()
		return HttpResponseRedirect(reverse('t_class_date', args=(assc.assign_ct_id,)))
	elif request.user.is_student:
		return render(request, 'info/homepage.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def t_attendance(request, ass_c_id):
	if request.user.is_teacher:
		assc = get_object_or_404(AttendanceClass, id=ass_c_id)
		ass = assc.assign_ct
		c = ass.class_id
		context = {
			'ass': ass,
			'c': c,
			'assc': assc,
		}
		return render(request, 'info/t_attendance.html', context)
	elif request.user.is_student:
		return render(request, 'info/homepage.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def edit_att(request, ass_c_id):
	if request.user.is_teacher:
		assc = get_object_or_404(AttendanceClass, id=ass_c_id)
		att_list = Attendance.objects.filter(attendanceclass=assc)
		context = {
			'assc': assc,
			'att_list': att_list,
		}
		return render(request, 'info/t_edit_att.html', context)
	elif request.user.is_student:
		return render(request, 'info/homepage.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def confirm(request, ass_c_id):
	if request.user.is_teacher:
		assc = get_object_or_404(AttendanceClass, id=ass_c_id)
		ass = assc.assign_ct
		cl = ass.class_id
		for i, s in enumerate(cl.student_set.all()):
			status = request.POST[s.roll_no]
			if status == 'present':
				status = 'True'
			else:
				status = 'False'
			if assc.status == 1:
				try:
					a = Attendance.objects.get(student=s, date=assc.date, attendanceclass=assc)
					a.status = status
					a.save()
				except Attendance.DoesNotExist:
					a = Attendance(student=s, status=status, date=assc.date, attendanceclass=assc)
					a.save()
			else:
				a = Attendance(student=s, status=status, date=assc.date, attendanceclass=assc)
				a.save()
				assc.status = 1
				assc.save()

		return HttpResponseRedirect(reverse('t_class_date', args=(ass.id,)))
	elif request.user.is_student:
		return render(request, 'info/homepage.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def t_student(request, assign_ct_id):
	if request.user.is_teacher:
		ass = AssignClassTeacher.objects.get(id=assign_ct_id)
		att_list = []
		for stud in ass.class_id.student_set.all():
			try:
				a = AttendanceTotal.objects.get(student=stud)
			except AttendanceTotal.DoesNotExist:
				a = AttendanceTotal(student=stud)
				a.save()
			att_list.append(a)
		return render(request, 'info/t_students.html', {'att_list': att_list})
	elif request.user.is_student:
		return render(request, 'info/homepage.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def t_attendance_detail(request, stud_id):
	if request.user.is_teacher:
		stud = get_object_or_404(Student, roll_no=stud_id)
		if request.method == "POST":
			try:
				from_date = request.POST.get('from_date')
				to_date = request.POST.get('to_date')
				search_result = Attendance.objects.raw('select * from info_attendance where student_id = %s AND date '
				                                       'between "' + from_date + '" and "' + to_date + '" ORDER BY date',
				                                       [stud_id])
				return render(request, 'info/t_att_detail.html', {'att_list': search_result, 'stud': stud,
				                                                  'from_date': datetime.datetime.strptime(from_date, "%Y-%m-%d").date(),
				                                                  'to_date': datetime.datetime.strptime(to_date, "%Y-%m-%d").date()})
			except ValueError:
				today = datetime.date.today()
				att_list = Attendance.objects.filter(student=stud, date__month=today.month).order_by('date')
				return render(request, 'info/t_att_detail.html', {'att_list': att_list,
				                                                  'stud': stud,
				                                                  'from_date': today.replace(day=1),
				                                                  'to_date': today})
		else:
			today = datetime.date.today()
			att_list = Attendance.objects.filter(student=stud, date__month=today.month).order_by('date')
			return render(request, 'info/t_att_detail.html', {'att_list': att_list,
			                                                  'stud': stud,
			                                                  'from_date': today.replace(day=1),
			                                                  'to_date': today})
	elif request.user.is_student:
		return render(request, 'info/homepage.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def change_att(request, att_id):
	if request.user.is_teacher:
		a = get_object_or_404(Attendance, id=att_id)
		a.status = not a.status
		a.save()
		return HttpResponseRedirect(reverse('t_attendance_detail', args=(a.student.roll_no,)))
	elif request.user.is_student:
		return render(request, 'info/homepage.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def t_extra_class(request, assign_ct_id):
	if request.user.is_teacher:
		ass = get_object_or_404(AssignClassTeacher, id=assign_ct_id)
		c = ass.class_id
		context = {
			'ass': ass,
			'c': c,
		}
		return render(request, 'info/t_extra_class.html', context)
	elif request.user.is_student:
		return render(request, 'info/homepage.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/accounts/login/')
def e_confirm(request, assign_ct_id):
	if request.user.is_teacher:
		ass = get_object_or_404(AssignClassTeacher, id=assign_ct_id)
		cl = ass.class_id
		assc = ass.attendanceclass_set.create(status=1, date=request.POST['date'])
		assc.save()

		for i, s in enumerate(cl.student_set.all()):
			status = request.POST[s.roll_no]
			if status == 'present':
				status = 'True'
			else:
				status = 'False'
			date = request.POST['date']
			a = Attendance(student=s, status=status, date=date, attendanceclass=assc)
			a.save()

		return HttpResponseRedirect(reverse('t_class', args=(ass.teacher_id, 1)))
	elif request.user.is_student:
		return render(request, 'info/homepage.html')
# ------------------------
#   End Attendance Views
# ------------------------
