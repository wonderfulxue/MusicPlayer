# -*- encoding:utf-8 -*-
#音乐播放器图标设计
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.phonon import Phonon

#返回使用UTF-8字符串str初始化的QString。
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

class MusicSystemTray(QSystemTrayIcon):
    def __init__(self, parent=None):
        QSystemTrayIcon.__init__(self, parent)
        self._parent = parent

        #建立一个菜单
        menu = QMenu()
        #建立操作的Action
        self.showAction = QAction(u'打开主界面', self)
        self.playAction = QAction(u'播放', self)
        self.lastAction = QAction(u'上一首', self)
        self.nextAction = QAction(u'下一曲', self)
        self.stopAction = QAction(u'停止播放', self)
        self.stopAction.setEnabled(False)
        self.exitAction = QAction(u'退出', self)

        #将Action添加进Menu
        menu.addAction(self.showAction)
        menu.addSeparator()
        menu.addAction(self.playAction)
        menu.addSeparator()
        menu.addAction(self.lastAction)
        menu.addSeparator()
        menu.addAction(self.nextAction)
        menu.addSeparator()
        menu.addAction(self.stopAction)
        menu.addSeparator()
        menu.addAction(self.exitAction)
        
        #回调函数,当点击某一个Action的时候,调用相应的函数
        self.connect(self.showAction, SIGNAL('triggered()'), parent.showNormal)
        self.connect(self.playAction, SIGNAL('triggered()'), parent.playControl)
        self.connect(self.lastAction, SIGNAL('triggered()'), parent.lastMusic)
        self.connect(self.nextAction, SIGNAL('triggered()'), parent.nextMusic)
        self.connect(self.stopAction, SIGNAL('triggered()'), parent.stop)
        self.connect(self.exitAction, SIGNAL('triggered()'), parent.close)

        #将Menu 关联上TrayIcon
        self.setContextMenu(menu)

    def updateMenu(self):
        #获取当前播放器的状态
        state = self._parent.mediaObject.state()
        #如果正在播放,暂停可用
        if state == Phonon.PlayingState:
            self.playAction.setText(u"暂停")
            self.stopAction.setEnabled(True)
        #如果正在暂停,播放可用
        elif state == Phonon.PausedState:
            self.playAction.setText(u"播放")
            self.stopAction.setEnabled(True)
        #如果正停止,播放可用,停止不可用
        elif state == Phonon.StoppedState:
            self.playAction.setText(u"播放")
            self.stopAction.setEnabled(False)

