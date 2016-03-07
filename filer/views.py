from django.shortcuts import render

from filer.models import Filer, EncryptKey, FileUploadForm

# show the list of available files in the db
def filer_index(request):
    f=Filer.objects.all()
    return render(request, 'filer_index.html', {'file_list': f})

# upload file to db
def filer_add(request):
    if request.method=="POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # add username
            f=form.save(commit=False)
            f.upload_user=request.user
            return
        else:
            return

    upload_form=FileUploadForm()
    return render(request, 'filer_upload.html', {'form': upload_form})

# create encryption key, add
def filer_encrypt(request):
    return render(request, 'filer_index.html')

# return the raw file via http
def filer_serve(request):
    return render(request, 'filer_index.html')

# rename, delete, copy?
def filer_manage(request):
    return render(request, 'filer_index.html')
