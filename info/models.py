from django.db import models
import math
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from datetime import timedelta

sex_choice = (
	('Male', 'Male'),
	('Female', 'Female')
)


class User(AbstractUser):
	@property
	def is_student(self):
		if hasattr(self, 'student'):
			return True
		return False

	@property
	def is_teacher(self):
		if hasattr(self, 'teacher'):
			return True
		return False


# -----------------
#   Common Models
# -----------------
class Class(models.Model):
	id = models.PositiveIntegerField(primary_key='True')
	class_name = models.CharField(max_length=50)
	section = models.CharField(max_length=100)

	class Meta:
		verbose_name_plural = 'classes'

	def __str__(self):
		return '%s : %s' % (self.class_name, self.section)


class Student(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
	class_id = models.ForeignKey(Class, on_delete=models.CASCADE, default=1, verbose_name='Class')
	roll_no = models.CharField(primary_key='True', max_length=100)
	name = models.CharField(max_length=200)
	sex = models.CharField(max_length=50, choices=sex_choice, default='Male')
	DOB = models.DateField(default='1998-01-01')

	def __str__(self):
		return self.name


class Teacher(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
	id = models.CharField(primary_key=True, max_length=100)
	name = models.CharField(max_length=100)
	sex = models.CharField(max_length=50, choices=sex_choice, default='Male')
	DOB = models.DateField(default='1980-01-01')

	def __str__(self):
		return self.name


# --------------------
#  Attendance Models
# --------------------
class AssignClassTeacher(models.Model):
	class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
	teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

	class Meta:
		unique_together = (('class_id', 'teacher'),)
		verbose_name_plural = 'Class Teachers'

	def __str__(self):
		cl = Class.objects.get(id=self.class_id_id)
		te = Teacher.objects.get(id=self.teacher_id)
		return '%s : %s' % (te.name, cl)


class AttendanceClass(models.Model):
	assign_ct = models.ForeignKey(AssignClassTeacher, on_delete=models.CASCADE, verbose_name='Class Teacher')
	date = models.DateField()
	status = models.IntegerField(default=0, help_text='2=holiday',
	                             validators=[MinValueValidator(0), MaxValueValidator(2)])

	class Meta:
		verbose_name = 'Attendance'
		verbose_name_plural = 'Attendance'


class Attendance(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	attendanceclass = models.ForeignKey(AttendanceClass, on_delete=models.CASCADE, default=1)
	date = models.DateField(default='2018-10-23')
	status = models.BooleanField(default='True')

	def __str__(self):
		s = Student.objects.get(name=self.student)
		return '%s' % (s.roll_no,)


class AttendanceTotal(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)

	class Meta:
		unique_together = (('student',),)

	@property
	def att_class(self):
		stud = Student.objects.get(name=self.student)
		att_class = Attendance.objects.filter(student=stud, status='True').count()
		return att_class

	@property
	def total_class(self):
		stud = Student.objects.get(name=self.student)
		total_class = Attendance.objects.filter(student=stud).count()
		return total_class

	@property
	def attendance(self):
		stud = Student.objects.get(name=self.student)
		total_class = Attendance.objects.filter(student=stud).count()
		att_class = Attendance.objects.filter(student=stud, status='True').count()
		if total_class == 0:
			attendance = 0
		else:
			attendance = round(att_class / total_class * 100, 2)
		return attendance

	@property
	def classes_to_attend(self):
		stud = Student.objects.get(name=self.student)
		total_class = Attendance.objects.filter(student=stud).count()
		att_class = Attendance.objects.filter(student=stud, status='True').count()
		cta = math.ceil((0.75 * total_class - att_class) / 0.25)
		if cta < 0:
			return 0
		return cta


class AttendanceRange(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()

	class Meta:
		verbose_name = 'Session Date'


# ---------------
#     Triggers
# ---------------

def daterange(start_date, end_date):
	for n in range(int((end_date - start_date).days)):
		yield start_date + timedelta(n)


def create_attendance(sender, instance, **kwargs):
	if kwargs['created']:
		start_date = AttendanceRange.objects.all()[:1].get().start_date
		end_date = AttendanceRange.objects.all()[:1].get().end_date
		for single_date in daterange(start_date, end_date + timedelta(days=1)):
			if single_date.isoweekday() != 7:
				try:
					AttendanceClass.objects.get(date=single_date.strftime("%Y-%m-%d"), assign_ct=instance)
				except AttendanceClass.DoesNotExist:
					a = AttendanceClass(date=single_date.strftime("%Y-%m-%d"), assign_ct=instance)
					a.save()


post_save.connect(create_attendance, sender=AssignClassTeacher)
