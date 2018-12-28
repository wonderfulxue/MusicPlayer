# -*- encoding:utf-8 -*-

import ConfigParser
import logging
import os
import random

from PyQt4 import QtGui

import bottom_tool_frame  #窗口底部控件视图设计
import music_info_frame   
import music_player_main_frame   #音乐播放器背景设计,进度条添加
import top_tool_frame  # 音乐播放器顶部布局设计
from music_file_object import *  #一个音乐文件对象
from music_tableview import *   #播放器菜单栏(播放列表,收藏列表)布局设计

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

# 主窗口布局，核心类

class MainWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # player
        self.mediaObject = Phonon.MediaObject(self)  # 实例化一个媒体对象
        self.audioOutput = Phonon.AudioOutput(Phonon.VideoCategory, self)#实例化音频输出
        Phonon.createPath(self.mediaObject, self.audioOutput)  #将上面的媒体对象作为音频来源并对接到音频输出
        self.playingIndex = -1   #正在播放音乐在列表中的索引
        self.playingList = None  #正在播放的列表
        self.playingMusic = None #正在播放的音乐
        self.playingOrder = 0    #播放形式 顺序,随机,单曲
        self.tabIndex = 0        #侧边窗口索引

        self.musicList = []    #播放列表
        self.favList = []      #收藏列表
        path = os.path.abspath(os.path.join(os.getcwd(), '..'))
        self.lastOpenedPath = QString(path)  #上一次打开的路径,下一次导入的时候大打开这个路径
        self.lastLRCOpenedPath = QString(path)
        self.musicToLrcDict = {}
        self.isImporting = False    #是否正在导入歌曲

        self.resize(800, 600)     #整体窗口
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 需tableView已初始化，musicInfoFrame未初始化
        self.importConfig()

        # 主窗口，窗口顶部Frame，窗口底部Frame，音乐信息Frame 构建
        self.mainFrame = music_player_main_frame.MusicPlayerMainFrame(self)
        #窗口底部,顶部,音乐信息全都要继承主窗口
        self.topToolFrame = top_tool_frame.TopToolFrame(self, self.mainFrame)
        self.bottomToolFrame = bottom_tool_frame.BottomToolFrame(self, self.mainFrame)
        self.musicInfoFrame = music_info_frame.MusicInfoFrame(self, self.mainFrame)
        rect = self.mainFrame.rect()   #获得主窗口的尺寸

        # 音乐栏窗口构建
        self.tableView = MusicTableView('all', self)  #播放列表窗口
        self.tableViewFav = MusicTableView('fav', self)  #收藏列表窗口
        #在mainframe里面放一个音乐栏窗口组件
        self.tabWidget = QTabWidget(self.mainFrame)
        #设置音乐栏窗口大小
        self.tabWidget.setGeometry(rect.right() - 300, 60, 301, rect.bottom() - 118)
        self.tabWidget.setStyleSheet(
            '''
            QTabWidget:pane {border-top:0px solid #e8f3f9; background:transparent;}
            QTabBar:tab {width:150px; height:25px}
            ''')  #设置"播放列表"收藏列表"这几个字所占得宽度和高度,还有播放列表和收藏列表窗口的样式
        self.tabWidget.addTab(self.tableView, u'播放列表')
        self.tabWidget.addTab(self.tableViewFav, u'我的收藏')
        self.tabWidget.setCurrentIndex(0)   #设置默认打开的时候为播放列表,改成1,则为收藏列表

        # 为各个组件（widget）connect function
        # 以下代码: self.connect(QObject, SIGNAL(function), slot)
        # 此时QObject的SIGNAL(function)和slot相关联
        # 当特定事件发生时，对应的信号被发出，和SIGNAL关联的slot会被调用

        #音乐栏的动作,分为播放列表和收藏列表分别进行信号的接收
        self.connect(self.tableView, SIGNAL("addMusics()"), self.addMusics)
        self.connect(self.tableViewFav, SIGNAL("addMusics()"), self.addMusics)
        self.connect(self.tableView, SIGNAL("update()"), self.updateTableView)
        self.connect(self.tableViewFav, SIGNAL("update()"), self.updateTableView)
        self.connect(self.tableView, SIGNAL("playMusic(int)"), self.playMusicAtIndex)
        self.connect(self.tableViewFav, SIGNAL("playMusic(int)"), self.playMusicAtIndex)

        #底部框架的动作,接受来自底部框架的消信号
        self.connect(self.bottomToolFrame, SIGNAL(
            "lastMusic()"), self.lastMusic)  # 上一首
        self.connect(self.bottomToolFrame, SIGNAL(
            "nextMusic()"), self.nextMusic)  # 下一首
        self.connect(self.bottomToolFrame, SIGNAL(
            "playControl()"), self.playControl)  # 播放控制,暂停或开始
        self.connect(self.bottomToolFrame, SIGNAL("stop()"), self.stop)  # 停止
        self.connect(self.bottomToolFrame, SIGNAL(
            "changeOrder(int)"), self.changeOrder)  # 改变播放方式

        #当播放状态改变的时候
        self.mediaObject.stateChanged.connect(self.bottomToolFrame.updateButtons)#更新底部按键
        #self.mediaObject.stateChanged.connect(self.tableView.updatePlayingItem)
        self.mediaObject.stateChanged.connect(self.tableView.updatePlayingItem)   #更新播放曲目颜色等特征
        self.mediaObject.stateChanged.connect(self.musicInfoFrame.updateInfo)  #更新歌曲信息

        self.mediaObject.finished.connect(self.finished)  #当一首歌播放完成时

        self.mediaObject.tick.connect(self.bottomToolFrame.updateTimeLabel) #更新进度条
        self.mediaObject.tick.connect(self.musicInfoFrame.lrcShower.updateLRC)  #歌词滚动

        self.tabWidget.currentChanged.connect(self.tabChanged)   #侧边窗口播放和收藏之间的相互转换

    # 重构closeEvent，显示退出窗口信息
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit?', 'Are you sure you want to close?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QtGui.qApp.quit()
        else:
            try:
                event.ignore()
            except AttributeError:
                pass

    # 打开指定文件夹，批量加载音乐
    def addMusics(self, filePaths=[], favFilePaths=[]):
        #如果没有正在导入音乐
        if not self.isImporting:  
            #选择要导入的音乐的路径
            filePaths = QFileDialog.getOpenFileNames(self, u'打开',
                                                     self.lastOpenedPath, u'音频文件 (*.mp3 *.wma)')
        #如果正在导入,则退出
        elif self.isImporting:   
            self.isImporting = False

        if len(filePaths):
            #给要导入的文件进行排序
            filePaths.sort()
            for filePath in filePaths:
                #避免重复导入音乐
                if all(filePath != music.filePath for music in self.musicList) and os.path.exists(unicode(filePath)):
                    #创建一个音乐对象,传入音乐的路径
                    musicFile = MusicFile(filePath)
                    #下一次导入的时候,从这个地方打开
                    self.lastOpenedPath = musicFile.absoluteDirPath()
                    #讲要添加的音乐加入到音乐列表里
                    self.musicList.append(musicFile)
                    #在音乐栏添加歌曲
                    itemList = [QStandardItem(musicFile.title),
                                QStandardItem(musicFile.artist),
                                QStandardItem(musicFile.timeString)]
                    itemList[2].setTextAlignment(Qt.AlignCenter)
                    self.tableView.model.appendRow(itemList)  

                    #?
                    if filePath in favFilePaths:
                        self.favList.append(musicFile)
                        itemListFav = [QStandardItem(musicFile.title),
                                       QStandardItem(musicFile.artist),
                                       QStandardItem(musicFile.timeString)]
                        itemList[2].setTextAlignment(Qt.AlignCenter)
                        self.tableViewFav.model.appendRow(itemListFav)


    def updateTableView(self):
        #清空两个列表显示出来的内容
        self.tableView.model.clear()
        self.tableViewFav.model.clear()

        #再在列表中遍历重新显示
        for musicFile in self.musicList:
            itemList = [QStandardItem(musicFile.title),
                        QStandardItem(musicFile.artist),
                        QStandardItem(musicFile.timeString)]
            itemList[2].setTextAlignment(Qt.AlignCenter)
            self.tableView.model.appendRow(itemList)
        for musicFile in self.favList:
            itemList = [QStandardItem(musicFile.title),
                        QStandardItem(musicFile.artist),
                        QStandardItem(musicFile.timeString)]
            itemList[2].setTextAlignment(Qt.AlignCenter)
            self.tableViewFav.model.appendRow(itemList)

    def exportConfig(self):
        config = ConfigParser.ConfigParser()
        config.add_section('Player')
        config.set('Player', 'lastOpenedPath', _toUtf8(self.lastOpenedPath).data())
        musicPathList = []
        favPathList = []
        for music in self.musicList:
            musicPathList.append(_toUtf8(music.filePath).data())
        for music in self.favList:
            favPathList.append(_toUtf8(music.filePath).data())
        config.set('Player', 'musicList', musicPathList)
        config.set('Player', 'favList', favPathList)
        config.set('Player', 'lastLRCOpenedPath', _toUtf8(self.musicInfoFrame.lrcShower.lastOpenedPath).data())
        config.set('Player', 'musicToLRCDict', self.musicToLrcDict)
        try:
            path = os.path.join(os.getcwd(), 'setting.ini')
            configFile = open(path, 'w+')
            config.write(configFile)
        except Exception as e:
            raise ValueError(e)


    def importConfig(self):
        path = os.path.join(os.getcwd(), 'setting.ini')
        self.isImporting = True
        config = ConfigParser.ConfigParser()
        try:
            config.read(path)
            if config:
                self.lastOpenedPath = _fromUtf8(config.get('Player', 'lastOpenedPath'))
                musicList = eval(config.get('Player', 'musicList'))
                qMusicList = [QString.fromUtf8(music) for music in musicList]
                favList = eval(config.get('Player', 'favList'))
                qFavList = [QString.fromUtf8(music) for music in favList]
                self.lastLRCOpenedPath = _fromUtf8(config.get('Player', 'lastLRCOpenedPath'))
                self.addMusics(qMusicList, qFavList)
                self.musicToLrcDict = eval(config.get('Player', 'musicToLRCDict'))

        except Exception as e:
            logging.debug(e.message)
            config.add_section('Player')
            config.set('Player', 'lastOpenedPath',
                       _toUtf8(self.lastOpenedPath).data())
            musicPathList = []
            favPathList = []
            for music in self.musicList:
                musicPathList.append(_toUtf8(music.filePath).data())
            for music in self.favList:
                favPathList.append(_toUtf8(music.filePath).data())
            config.set('Player', 'musicList', [])
            config.set('Player', 'favList', [])
            config.set('Player', 'lastLRCOpenedPath', '')
            config.set('Player', 'musicToLRCDict', {})
            self.isImporting = False
            try:
                configFile = open(path, 'w+')
                config.write(configFile)
            except Exception as e:
                logging.debug(e.message)
            finally:
                self.isImporting = False
                configFile.close()

    #按照索引来播放
    def playMusicAtIndex(self, i):
        #看播放的是播放列表还是收藏列表
        self.playingList = self.musicList if self.tabWidget.currentIndex() == 0 else self.favList
        self.playingMusic = self.playingList[i]
        self.playingIndex = i

        self.playMusic(self.playingMusic)

    #播放音乐
    def playMusic(self, musicFile):
        #如果不是音乐类的文件,直接返回
        if not isinstance(musicFile, MusicFile):
            return
        self.mediaObject.setCurrentSource(musicFile.getMediaSource())
        self.mediaObject.play()

    def playControl(self):
        #如果现在有音乐正在播放(可以是暂停或者播放)
        if self.playingMusic:
            #如果正在播放
            if self.mediaObject.state() == 2:
                self.mediaObject.pause()
            #如果正在暂停
            else:
                self.mediaObject.play()
        #如果没有音乐在播放
        else:
            #列表是播放列表还是收藏列表
            self.playingList = self.musicList if self.tabIndex == 0 else self.favList
            #当前窗口
            tableView = self.tableView if self.tabIndex == 0 else self.tableViewFav
            #获得播放列表中被选中的的音乐
            selectedRows = tableView.selectionModel().selectedRows()
            #如果不是空
            if len(selectedRows):
                #播放的歌曲在整个列表中的索引
                self.playingIndex = tableView.model.itemFromIndex(selectedRows[0]).row()
            else:
                self.playingIndex = 0
            if len(self.playingList) > self.playingIndex:
                self.playingMusic = self.playingList[self.playingIndex]
                self.playMusic(self.playingMusic)

    #停止播放音乐,不是暂停
    def stop(self):
        if self.playingMusic:
            self.mediaObject.stop()
            self.playingList = self.musicList if self.tabIndex == 0 else self.favList
            self.playingIndex = -1
            self.playingMusic = None

    #上一首
    def lastMusic(self):
        #顺序播放
        if (self.playingIndex - 1 >= 0) and self.playingOrder == 0:
            self.playingIndex -= 1
            self.playingMusic = self.playingList[self.playingIndex]
            self.playMusic(self.playingMusic)
        elif (self.playingIndex == 0) and self.playingOrder == 0:
            self.playingIndex = len(self.playingList - 1)
            self.playingMusic = self.playingList[self.playingIndex]
            self.playMusic(self.playingMusic)
        #随机播放
        elif self.playingOrder == 1:
            self.randMusic()
        #单曲循环
        elif self.playingOrder == -1:
            self.playMusic(self.playingMusic)

    def nextMusic(self):
        #没有歌曲在播放
        if not self.playingList or not len(self.playingList) or self.playingIndex == -1:
            return
        #顺序播放
        if (len(self.playingList) > self.playingIndex + 1) and self.playingOrder == 0:
            self.playingIndex += 1
            self.playingMusic = self.playingList[self.playingIndex]
            self.playMusic(self.playingMusic)
        elif (len(self.playingList) == self.playingIndex + 1) and self.playingOrder == 0:
            self.playingIndex = 0
            self.playingMusic = self.playingList[self.playingIndex]
            self.playMusic(self.playingMusic)
        #随机播放
        elif self.playingOrder == 1:
            self.randMusic()
        #单曲循环
        elif self.playingOrder == -1:
            self.playMusic(self.playingMusic)

        else:
            self.stop()

    #随机播放
    def randMusic(self):
        self.playingIndex = int(random.randint(0, len(self.playingList) - 1))
        self.playingMusic = self.playingList[self.playingIndex]
        self.playMusic(self.playingMusic)

    #改变播放的形式
    def changeOrder(self, order):
        self.playingOrder = order

    #当一首歌曲播放完了
    def finished(self):
        # if self.playingOrder = 0, 顺序播放
        if not self.playingOrder:
            self.nextMusic()

        # 随机播放
        elif self.playingOrder == 1:
            self.randMusic()

        # 单曲循环
        else:
            self.playMusic(self.playingMusic)

    #改变右边音乐栏是播放列表还是收藏列表
    def tabChanged(self, i):
        self.tabIndex = i

    def trayIconActived(self, reason):
        self.activateWindow()
