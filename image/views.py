from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Image
from .forms import ImageAddForm, ImageEditForm
import urllib3
import PIL
import io
import uuid
from django.conf import settings
import os
from django.http import Http404

@login_required
def image_list(request):
	images = Image.objects.filter(user=request.user)
	return render(request, 'image_list.html', {'images': images})
@login_required
def image_add(request):
	if request.method == 'POST':
		form = ImageAddForm(request.POST, request.FILES)
		if form.is_valid():
			if form.cleaned_data.get('file'):
				print(form)
				print(form.cleaned_data['file'])
				Image.objects.create(user=request.user, name=form.cleaned_data.get('file'), base_image=form.cleaned_data.get('file'))
				return redirect('/')
			else:
				http = urllib3.PoolManager()
				r = http.request('GET', form.cleaned_data.get('link'))
				if r.status in range(200, 300):
					image = PIL.Image.open(io.BytesIO(r.data))
					if image:
						'''path = os.path.join(settings.MEDIA_ROOT, str(uuid.uuid4())+'.gif')
						image.save(path, format='GIF')'''
						path = os.path.join(settings.MEDIA_ROOT, str(uuid.uuid4())+'.'+form.cleaned_data.get('link').split('.')[-1])
						image.save(path)
						Image.objects.create(user=request.user, base_image=path.split('/')[-1], name=form.cleaned_data.get('link'))
						return redirect('/')
					else:
						form.add_error('link', "Файл повреждён или имеет недопустимый формат")
				else:
					form.add_error('link', "Не удалось загрузить файл")
	else:
		form = ImageAddForm()
	return render(request, 'image_add.html', {'form': form})
@login_required
def image_edit(request, id):
	try:
		image = Image.objects.get(user=request.user, pk=id)
	except:
		raise Http404("Файл не найден или доступ запрещён")
	if request.method == 'POST':
		form = ImageEditForm(request.POST)
		if form.is_valid():
			width = form.cleaned_data.get('width', '0')
			height = form.cleaned_data.get('height', '0')

			if width and not height:
				rate = width/image.base_image.width
			elif height and not width:
				rate = height/image.base_image.height
			elif width and height:
				x_rate = width/image.base_image.width
				y_rate = height/image.base_image.height
				rate = x_rate if x_rate<y_rate else y_rate

			img = PIL.Image.open(image.base_image.path)
			w, h = img.size
			img = img.resize((int(w*rate), int(h*rate)))
			path = os.path.join(settings.MEDIA_ROOT, str(uuid.uuid4())+'.'+image.base_image.path.split('.')[-1]) if not image.resize_image else image.resize_image.path
			img.save(path)
			#new_image = Image.objects.create(user=request.user, image=path.split('/')[-1])
			image.resize_image = path.split('/')[-1]
			image.save()
			return redirect("/edit/"+str(image.pk))

	else:
		form = ImageEditForm(initial={'width': image.get_image().width, 'height': image.get_image().height})

	return render(request, 'image_edit.html', {'form': form, 'image': image.get_image().url, 'name': image.name})