#-*- encoding: UTF-8 -*-

import logging
from PyQt4.QtCore import *
import urllib2, json, os

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _toUtf8 = QString.toUtf8
except AttributeError:
    def _toUtf8(s):
        return s

class LRCDownloaderThread(QThread):
    def __init__(self, args):
        QThread.__init__(self)
        self.args = args # 0-music 1-artist
        url = QString('http://geci.me/api/lyric')
        for arg in args:
            if isinstance(arg, QString):
                url = url.append(QString('/'))
                url = url.append(arg)
        self.url = unicode(url).encode('utf-8')   #获得一首歌的歌词的网页完整路径
        self.lrcUrl = ''   #一个歌词的路径,没有其他东西
        self.lrcPath = QString()    #歌词的本地路径

    def run(self):
        self.getDownloadUrl()

    def getDownloadUrl(self):
        try:
            response = urllib2.urlopen(self.url)  #打开url
            if response:
                jsonStr = response.read()  # ,读取网页源码
                data = json.loads(jsonStr)  #将源码的类型转换为json
                if data.has_key('result') and len(data['result']) \
                        and data['result'][0]['lrc']:   #如果lrc存在,那么对应的是纯歌词的地址
                    self.lrcUrl = data['result'][0]['lrc']   
                    self.downloadLRCFile()   #下载歌词文件
                else:
                    self.emit(SIGNAL("complete(bool)"), False)  #如果下载失败,抛出信号,被music_file_object接受
            else:
                self.emit(SIGNAL("complete(bool)"), False)
        except:
            self.emit(SIGNAL("complete(bool)"), False)

    #下载歌词文件
    def downloadLRCFile(self):
        try:
            if self.lrcUrl:
                if isinstance(self.lrcUrl, unicode):  #检查url的编码方式
                    self.lrcUrl = self.lrcUrl.encode('utf-8')   #转化成utf-8编码
                f = urllib2.urlopen(self.lrcUrl)   #打开url
                path = 'lrc/'  #本地存储歌词位置
                if not os.path.exists(path):  #没有这个位置就创建一个
                    os.mkdir(path)
                #一个歌词的完整路径
                path = path + unicode(self.args[0]) + '_' + unicode(self.args[1]) + '.lrc'
                data = f.read()
                if data:
                    with open(path, "wb+") as code:
                        code.write(data)  #讲仅有歌词的文件的网址里面的内容写入本地文件里面
                    code.close()
                    self.lrcPath = QString(path)
                    self.emit(SIGNAL("complete(bool)"), True)   #发送成功的信号
                else:
                    self.emit(SIGNAL("complete(bool)"), False)  #下载失败就抛出false
        except:
            self.emit(SIGNAL("complete(bool)"), False)
