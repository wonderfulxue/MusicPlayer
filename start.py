# -*- encoding:utf-8 -*-
from PyQt4 import QtGui

from src import music_player_widget
import music_system_tray_icon
import sys, os

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = music_player_widget.MainWindow()
    path = os.path.join(os.getcwd(), 'res')
    icon = QtGui.QIcon(QtGui.QPixmap(os.path.join(path, 'heart.ico')))

    # 必须是 app.setWindowIcon
    app.setWindowIcon(icon)
    window.show()

    taskIcon = music_system_tray_icon.MusicSystemTray(window)
    window.mediaObject.stateChanged.connect(taskIcon.updateMenu)
    taskIcon.activated.connect(window.trayIconActived)
    taskIcon.setIcon(icon)
    taskIcon.show()

    sys.exit(app.exec_())