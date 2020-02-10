from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from tiantian.settings import NGINX_URL, FDFS_CONF


class FDFSStorage(Storage):

    def __init__(self):
        self.fdfs_conf = FDFS_CONF
        self.nginx_url = NGINX_URL

    def open(self, name, mode='rb'):
        """打开文件的时候使用"""
        pass

    def save(self, name, content, max_length=None):
        """
                保存文件的时候使用
        :param name: 文件的名字
        :param content: 文件的内容，是一个文件对象，可以使用read()
        :param max_length:
        :return:
        """
        client_fdfs = Fdfs_client(self.fdfs_conf)
        dict_r = client_fdfs.upload_by_buffer(content.read())
        if dict_r.get('Status') != 'Upload successed.':
            raise Exception("file load fail")

        return dict_r.get('Remote file_id')

    def exists(self, name):
        """
            校验文件名是否可用。在django中也许不可用，但是在fdfs当中一定是可用的
        :param name: 我们上传的文件名，不是远程文件ID
        :return: 如果文件名不可用，返回True，如果文件名可用，返回False
        """
        return False

    def url(self, name):
        """

        :param name:远程文件ID
        :return: 将远程文件ID和nginx服务器的URL拼接起来。
        """
        return self.nginx_url + name
