import os, shutil
import conf

from django.http.response import HttpResponse
from django import forms


def write_to_file(file, lines, mod='w'):
    if file is None or lines is None:
        return None
    try:
        f = open(file, mod)
    except OSError as e:
        print('File write error: ' + e.msg)
        return False
    f.writelines(lines)
    f.close()
    return True


def mv_file(src, dst):
    if os.path.isfile(src):
        shutil.move(src, dst)
        return True
    else:
        return False


class UploadFileForm(forms.Form):
    # title = forms.CharField(max_length=5)
    file = forms.FileField()


def handle_uploaded_file(file, cid):
    try:
        path = conf.settings_autotestfile_location + cid
        if not os.path.exists(path):
            os.mkdir(path)
        if path[:-1] != '/':
            path += '/'
        file_name = path + file.name
        destination = open(file_name, 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
    except Exception as e:
        return HttpResponse(u'上传失败：' + str(e))
    else:
        pass
