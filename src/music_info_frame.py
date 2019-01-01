# -*- encoding:utf-8 -*-

#音乐信息,歌手,歌名,歌词
from PyQt4 import QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import lrc_shower

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

class MusicInfoFrame(QFrame):

    def __init__(self, main, parent=None):
        QFrame.__init__(self, parent)
        self.main = main
        self._playingIndex = -1
        self._mediaObject = main.mediaObject
        #获取主体框架的大小
        rect = parent.rect()

        #设计歌曲信息模块的大小
        self.setGeometry(0, 60, rect.width() - 300, rect.height() - 120)

        #歌曲名称
        self.titleLabel = QLabel()
        self.titleLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.titleLabel.setMaximumWidth(rect.width() - 300)
        self.titleLabel.setWordWrap(True)
        titleFont = QFont("Microsoft YaHei", 15, 75)  #字体形状
        self.titleLabel.setFont(titleFont)
        self.titleLabel.setAlignment(Qt.AlignCenter)  #居中显示

        #歌手名称
        self.artistLabel = QLabel()
        self.artistLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.artistLabel.setMaximumWidth(rect.width() - 300)
        self.artistLabel.setAlignment(Qt.AlignCenter)

        #歌词self.main作为parent参数
        self.lrcShower = lrc_shower.LRCShower(self.main)

        #QVBoxLayout类将各部件垂直排列
        vLayout = QtGui.QVBoxLayout(self)
        vLayout.addWidget(self.titleLabel)
        vLayout.addWidget(self.artistLabel)
        vLayout.addWidget(self.lrcShower)

        #设定了titleLabe,artistLabel与lrcShower比例为1:10
        vLayout.addStretch()
        vLayout.setStretchFactor(self.titleLabel, 1)
        vLayout.setStretchFactor(self.artistLabel, 1)
        vLayout.setStretchFactor(self.lrcShower, 10)


    #当播放状态有变化的时候会更新歌曲信息,在main_player_widget里面调用
    def updateInfo(self):
        #两个的index不一样
        if self._playingIndex != self.main.playingIndex:
            #更新歌词信息
            self.lrcShower.updateMusic()

            #当切换歌曲,导致两个歌曲的index不同的时候,
            if self.main.playingIndex != -1:
                #更新索引,名称,歌手名
                self._playingIndex = self.main.playingIndex
                self.titleLabel.setText(self.main.playingMusic.title)
                self.artistLabel.setText(self.main.playingMusic.artist)
            #如果停止播放了歌曲,导致index为-1,那么将两个Label元素全都置空
            else:
                self.titleLabel.setText(QString())
                self.artistLabel.setText(QString())

