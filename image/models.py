from django.db import models
from django.contrib.auth import get_user_model
import uuid
import os

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "%s.%s" % (uuid.uuid4(), ext)
	return filename

# Create your models here.
class Image(models.Model):
	user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
	name = models.TextField(verbose_name="базовое имя изображения")
	base_image = models.ImageField(verbose_name="базовое изображение")
	resize_image = models.ImageField(verbose_name="изменённое изображение", blank=True, null=True)
	class Meta:
		verbose_name = "изображение"
		verbose_name_plural = "изображения"
	def __str__(self):
		return self.name
	def get_image(self):
		if self.resize_image:
			return self.resize_image
		else:
			return self.base_image