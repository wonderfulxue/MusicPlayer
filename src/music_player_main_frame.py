# -*- encoding:utf-8 -*-

from PyQt4.QtGui import *

class MusicPlayerMainFrame(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
        self.setStyleSheet(   #主窗口的样式
        '''
        MusicPlayerMainFrame{
        border-image: url(res/bg.png);
        background-repeat: no-repeat;
        }
        ''')
        #setGeometry() 方法干了两件事，它定义了窗体在屏幕上的位置，并设置窗体的大小。
        #开始的两个参数是窗体的x和y的位置，第三个是宽度，第四个是高度
        self.setGeometry(0, 67, 800, 533)


