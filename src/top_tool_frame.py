# -*- encoding:utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os

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


class TopToolFrame(QFrame):

    def __init__(self, main, parent=None):
        QFrame.__init__(self, parent)
        self.main = main
        self.setStyleSheet(
        '''
        border-image: url(res/bgColor.png);
        background-repeat: no-repeat;
        ''')
        #用来标注是否可以拖动
        self.isDraging = False
        self.setGeometry(0, 0, 800, 60)  #设置顶部的开始坐标还有宽度和高度
        #增加一个机器人的动态图
        self.addRobotLogo(main)
        #增加关闭和最小化按钮
        self.addButtons(self)

        #音乐播放器的标题
        titelText = QLabel(self)
        titelText.setGeometry(370, 10, 120, 40)
        titleFont = QFont("Microsoft YaHei", 20, 35)
        titelText.setFont(titleFont)
        titelText.setStyleSheet("color: rgb(221, 160, 221)")
        titelText.setText(u'️M~Player')

        #在音乐播放器上的一个小图标
        titleLabel = QPushButton(main)
        titleLabel.setIcon(QIcon(QPixmap('res/icon.png')))
        titleLabel.setGeometry(330, 80, 30, 30)

        #右下角有一个+号可以导入歌曲
        addButton = QPushButton(main)
        addButton.setIcon(QIcon(QPixmap('res/add.png')))
        addButton.setGeometry(780, 518, 20, 20)
        addButton.clicked.connect(self.main.addMusics)   #点击后产生的动作
        addButton.setToolTip(u'导入歌曲')   #鼠标放在上面的提示信息

    def addRobotLogo(self, main):
        btn = QPushButton(main)
        btn.setObjectName("btnSpecial")
        btn.setStyleSheet(
            '''
            QPushButton#btnSpecial {
            border-image: url(res/robot_1.png);
            background-repeat: no-repeat;
            }
            QPushButton#btnSpecial:hover {
            border-image: url(res/robot_2.png);
            background-repeat: no-repeat;
            }
            QPushButton#btnSpecial:pressed {
            border-image: url(res/robot_3.png);
            background-repeat: no-repeat;
            }
            ''')
        btn.setGeometry(20, 70, 54, 47)

    def addButtons(self, main):
        closeButton = PushButton(main)
        closeButton.loadPixmap('res/close.png')
        closeButton.setGeometry(770, 10, 16, 16)
        closeButton.clicked.connect(self.main.close)   #当点击的时候发送信号,调用main里面的clodse函数

        miniButton = PushButton(main)
        miniButton.loadPixmap('res/mini.png')
        miniButton.setGeometry(740, 10, 16, 16)
        miniButton.clicked.connect(self.main.showMinimized)


    #鼠标拖动界面的实现逻辑
    def mousePressEvent(self, event):
        self.isDraging = True
        self.main.dragPostion = event.globalPos() - self.main.pos()

    def mouseReleaseEvent(self, event):
        self.isDraging = False

    def mouseMoveEvent(self, event):
        if self.isDraging:
            self.main.move(event.globalPos() - self.main.dragPostion)


class PushButton(QPushButton):
    def __init__(self, parent=None):
        super(PushButton, self).__init__(parent)

        self.status = 1

    #按键的尺寸
    def loadPixmap(self, pic_name):
        self.pixmap = QPixmap(pic_name)
        self.btn_width = self.pixmap.width() / 4
        self.btn_height = self.pixmap.height()

    # def enterEvent(self, event):
    #     if not self.isChecked() and self.isEnabled():
    #         self.status = 0
    #         self.update()

    #设置按键不可用
    # def setDisabled(self, bool):
    #     super(PushButton, self).setDisabled(bool)
    #     if not self.isEnabled():
    #         self.status = 2
    #         self.update()
    #     else:
    #         self.status = 1
    #         self.update()

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.status = 2
    #         self.update()

    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.clicked.emit(True)
    #     if not self.isChecked():
    #         self.status = 3
    #     if self.menu():
    #         self.menu().exec_(event.globalPos())
    #     self.update()

    # def leaveEvent(self, event):
    #     if not self.isChecked() and self.isEnabled():
    #         self.status = 1
    #         self.update()

    #画图标
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(self.rect(),
                           self.pixmap.copy(self.btn_width * self.status, 0, self.btn_width, self.btn_height))
        painter.end()

    def addMusic(self):
        pass
