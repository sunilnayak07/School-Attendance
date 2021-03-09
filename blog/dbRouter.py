# DB router for app1

class BlogDBRouter(object):
	"""
	A router to control app1 db operations
	"""

	def db_for_read(self, model, **hints):
		"""Point all operations on app1 models to 'db_blog'"""
		from django.conf import settings
		if 'db_blog' not in settings.DATABASES:
			return None
		if model._meta.app_label == 'blog':
			return 'db_blog'
		return None

	def db_for_write(self, model, **hints):
		"""Point all operations on app1 models to 'db_blog'"""
		from django.conf import settings
		if 'db_blog' not in settings.DATABASES:
			return None
		if model._meta.app_label == 'blog':
			return 'db_blog'
		return None

	def allow_relation(self, obj1, obj2, **hints):
		"""Allow any relation if a model in app1 is involved"""
		from django.conf import settings
		if 'db_blog' not in settings.DATABASES:
			return None
		if obj1._meta.app_label == 'blog' or obj2._meta.app_label == 'blog':
			return True
		return None

	def allow_syncdb(self, db, model):
		"""Make sure the app1 app only appears on the 'app1' db"""
		from django.conf import settings
		if 'db_blog' not in settings.DATABASES:
			return None
		if db == 'db_blog':
			return model._meta.app_label == 'blog'
		elif model._meta.app_label == 'blog':
			return False
		return None
