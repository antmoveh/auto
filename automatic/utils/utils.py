import os, time, urllib.request
import django.db
from subprocess import Popen, PIPE
from .exceptions import DeployError
# from Crypto.Cipher import AES

Java_path = [
    '/data/java/jdk1.7.0_79',
]


def get_temp_folder(prefix=''):
    cur_working_folder = os.getcwd()
    temp_up_folder = os.getcwd() + '/tmp/'
    if os.path.exists(temp_up_folder):
        if not os.path.isdir(temp_up_folder):
            os.remove(temp_up_folder)
    temp_folder = temp_up_folder + prefix + str(int(time.time() * 1000)) + '/'
    output, err = Popen(['mkdir', '-p', temp_folder], stdout=PIPE, stderr=PIPE).communicate()
    if len(err) > 0:
        raise DeployError('023', err.decode('utf-8'))
    else:
        return temp_folder


def mkdir(dir_name, err_code='000'):
    output, err = Popen(['mkdir', '-p', dir_name], stdout=PIPE, stderr=PIPE).communicate()
    if len(err) > 0:
        raise DeployError(err_code, err.decode('utf-8'))
    else:
        return True


def check_service(urls, iid=0):
    close_db()
    url_list = urls.split()
    if len(url_list) == 0:
        return True
    for i in range(0, 6):
        print('进行服务测试第' + str(i + 1) + '轮')
        time.sleep(30)
        test = True
        for url in url_list:
            try:
                r = urllib.request.urlopen(url)
            except:
                test = False
                break
            else:
                if r.status != 200:
                    test = False
                    break
        if test:
            return True
    return False


def close_db():
    try:
        # django.db.connection.abort()
        pass
    except django.db.utils.Error:
        pass
    django.db.connection.close()


# def aes_encrypt(data, key):
#     if data is None or key is None or len(key) < 6:
#         return None
#     BS = AES.block_size
#     pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
#     cipher = AES.new(key)
#     return cipher.encrypt(pad(data)).encode('hex')
#
#
# def aes_decrypt(data, key):
#     if data is None or key is None or len(key) < 6:
#         return None
#     unpad = lambda s: s[0:-ord(s[-1])]
#     cipher = AES.new(key)
#     return unpad(cipher.decrypt(data.decode))
