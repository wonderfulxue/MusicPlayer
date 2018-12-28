# -*- encoding:utf-8 -*-

from PyQt4.phonon import Phonon
from PyQt4.QtGui import *
from PyQt4.QtCore import *

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


class BottomToolFrame(QFrame):

    def __init__(self, main, parent=None):
        QFrame.__init__(self, parent)
        self.main = main
        #使用主体窗口的媒体和音频对象
        self._mediaObject = main.mediaObject
        self._audioOutput = main.audioOutput
        #获得正在播放的音乐
        self._playingMusic = main.playingMusic
        #播放模式
        self.playingOrder = 0
        self.count = 0

        #底部模块的背景
        self.setStyleSheet(
        '''
        BottomToolFrame{
        border-image: url(res/box.png);
        background-repeat: no-repeat;
        }
        ''')
        rect = parent.rect()

        #各个按钮的位置和形状

        #上一曲
        self.setGeometry(0, rect.height() - 60, rect.width(), 60)
        self.lastButton = QPushButton()
        self.lastButton.setMinimumSize(40, 40)
        self.lastButton.setObjectName("btnSpecial")
        self.lastButton.setStyleSheet(
        '''
        QPushButton#btnSpecial {
        border-image: url(res/last.png);
        background-repeat: no-repeat;
        }
        QPushButton#btnSpecial:pressed {
        border-image: url(res/last_press.png);
        background-repeat: no-repeat;
        }
        ''')

        #播放
        self.playButton = QPushButton()
        # self.playButton.setText(u"播放")
        self.playButton.setMinimumSize(40, 40)
        self.playButton.setObjectName("btnSpecial")
        self.playButton.setStyleSheet(
        '''
        QPushButton#btnSpecial {
        border-image: url(res/play.png);
        background-repeat: no-repeat;
        }
        QPushButton#btnSpecial:pressed {
        border-image: url(res/play_press.png);
        background-repeat: no-repeat;
        }
        ''')

        #下一曲
        self.nextButton = QPushButton()
        self.nextButton.setMinimumSize(40, 40)
        self.nextButton.setObjectName("btnSpecial")
        self.nextButton.setStyleSheet(
        '''
        QPushButton#btnSpecial {
        border-image: url(res/next.png);
        background-repeat: no-repeat;
        }
        QPushButton#btnSpecial:pressed {
        border-image: url(res/next_press.png);
        background-repeat: no-repeat;
        }
        ''')

        #播放顺序
        self.orderButton = QPushButton()
        #初始的播放模式为顺序播放
        self.orderButton.setText(u"顺序播放")
        #用来确定是什么播放模式
        self.orderButton.clicked.connect(self.updateCount)

        self.seekSlider = Phonon.SeekSlider()
        self.seekSlider.setMediaObject(self._mediaObject)

        #时间进度条
        self.curTimeInt = -1

        self.timeString = QString('00:00/00:00')   #初始值
        self.timeLabel = QLabel(self.timeString)
        self.timeLabel.setAlignment(Qt.AlignCenter)
        self.timeLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        #声音模块
        self.volumeSlider = Phonon.VolumeSlider()
        self.volumeSlider.setAudioOutput(self._audioOutput)

        #将各个模块横向排列
        hLayout = QHBoxLayout(self)
        hLayout.addWidget(self.lastButton)
        hLayout.addWidget(self.playButton)
        hLayout.addWidget(self.nextButton)
        hLayout.addWidget(self.orderButton)
        hLayout.addWidget(self.seekSlider)
        hLayout.addWidget(self.timeLabel)
        hLayout.addWidget(self.volumeSlider)
        hLayout.addStretch()
        hLayout.setStretchFactor(self.lastButton, 1)
        hLayout.setStretchFactor(self.playButton, 1)
        hLayout.setStretchFactor(self.nextButton, 1)
        hLayout.setStretchFactor(self.orderButton, 1)
        hLayout.setStretchFactor(self.seekSlider, 10)
        hLayout.setStretchFactor(self.timeLabel, 1)
        hLayout.setStretchFactor(self.volumeSlider, 5)

        #将各个按钮连接到相应的函数,这些函数都在music_player_widget里面
        self.lastButton.clicked.connect(self.lastMusic)
        self.playButton.clicked.connect(self.playControl)
        self.nextButton.clicked.connect(self.nextMusic)
        self.orderButton.clicked.connect(self.changeOrder)

    def lastMusic(self):
        self.emit(SIGNAL("lastMusic()"))

    def nextMusic(self):
        self.emit(SIGNAL("nextMusic()"))

    def playControl(self):
        self.emit(SIGNAL("playControl()"))

    def stop(self):
        self.emit(SIGNAL("stop()"))

    def updateCount(self):
        self.count += 1

    def changeOrder(self):

        if self.count % 3 == 0:
            self.orderButton.setText(u'顺序播放')
            self.playingOrder = 0
        elif (self.count - 1) % 3 ==0:
            self.orderButton.setText(u'随机播放')
            self.playingOrder = 1
        elif (self.count - 2) % 3 == 0:
            self.orderButton.setText(u'单曲循环')
            self.playingOrder = -1

        #在底部框架修改完之后,还要在主体函数来更改播放的顺序,来保证播放列表是对的
        self.emit(SIGNAL("changeOrder(int)"), self.playingOrder)

    #更新时间进度条  #ms的意义是啥
    def updateTimeLabel(self, ms):
        time = ms/1000
        if not self.main.playingMusic:  #如果没有正在播放的音乐
            self.timeLabel.setText('00:00/00:00')  #初始化显示的字符串
        elif self.curTimeInt != time:
            self.curTimeInt = time
            h = self.curTimeInt / 3600
            m = self.curTimeInt % 3600 / 60
            s = self.curTimeInt % 3600 % 60
            curTime = QTime(h, m, s)
            totTime = self.main.playingMusic.time
            curTimeString = curTime.toString("mm:ss") if not totTime.hour() else curTime.toString("hh:mm:ss")
            strList = QStringList()
            strList.append(curTimeString)  #当前时间
            strList.append(self.main.playingMusic.timeString)   #这首歌的总时间
            self.timeString = strList.join('/')   #两个时间用/连接起来
            self.timeLabel.setText(self.timeString)

    #更改按钮的状态,当状态是播放的时候,为暂停按钮,为暂停或者停止的时候,是播放按钮
    #这个函数在music_player_widget里面被调用
    def updateButtons(self):  
        state = self.main.mediaObject.state()  #获得播放器的当前状态
        if state == Phonon.PlayingState:
            self.playButton.setStyleSheet(
                '''
                QPushButton#btnSpecial {
                border-image: url(res/pause.png);
                background-repeat: no-repeat;
                }
                QPushButton#btnSpecial:pressed {
                border-image: url(res/pause_press.png);
                background-repeat: no-repeat;
                }
                ''')
        elif state == Phonon.PausedState or state == Phonon.StoppedState:
            self.playButton.setStyleSheet(
                '''
                QPushButton#btnSpecial {
                border-image: url(res/play.png);
                background-repeat: no-repeat;
                }
                QPushButton#btnSpecial:pressed {
                border-image: url(res/play_press.png);
                background-repeat: no-repeat;
                }
                ''')
import os
print os.getcwd()
