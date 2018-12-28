# -*- encoding:utf-8 -*-
from PyQt4 import QtGui
import sys, os
from src import music_player_widget
from src import music_system_tray_icon

if __name__ == "__main__":
    #每个PyQt4程序必须创建一个application对象,sys.argv 参数是命令行中的一组参数
    app = QtGui.QApplication(sys.argv)
    window = music_player_widget.MainWindow()
    path = os.path.join(os.getcwd(), 'res')
    #程序图标的路径
    icon = QtGui.QIcon(QtGui.QPixmap(os.path.join(path, 'heart.ico')))   

    # 必须是 app.setWindowIcon,设置应用程序的图标
    app.setWindowIcon(icon)
    #显示主体窗口
    window.show()    

    #taskIcon = music_system_tray_icon.MusicSystemTray(window)
    #当media对象的状态改变的时候,调用taskIcon.updateMenu
    #window.mediaObject.stateChanged.connect(taskIcon.updateMenu)
    #taskIcon.activated.connect(window.trayIconActived)
    # taskIcon.setIcon(icon)
    # taskIcon.show()

    sys.exit(app.exec_())
