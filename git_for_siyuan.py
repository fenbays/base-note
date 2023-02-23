import os
import sys
import threading
import time

import psutil
from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtCore import QUrl, QCoreApplication, QDateTime
from PyQt5.QtGui import QIcon, QDesktopServices, QPixmap
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QLabel, QMainWindow, QMessageBox

from gui.ui_main import Ui_MainWindow

# 适配高分屏
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.icon_type = 'mario'

        self.ui = uic.loadUi("gui/ui_main.ui", self)
        self.ui.setupUi(self)
        self.ui.setWindowTitle("思源笔记git")

        self.logAction = QAction("日志", self)
        self.logAction.setIcon(QIcon.fromTheme("document-new"))
        self.aboutAction = QAction("关于", self)
        self.aboutAction.setIcon(QIcon.fromTheme("help-about"))
        self.openAction = QAction("打开", self)
        self.openAction.setIcon(QIcon.fromTheme("media-record"))
        self.quitAction = QAction("退出", self)
        self.quitAction.setIcon(QIcon.fromTheme("application-exit"))  # 从系统主题获取图标

        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.aboutAction)
        self.trayIconMenu.addAction(self.logAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.openAction)
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = TrayIcon(self)
        # self.trayIcon.setContextMenu(self.trayIconMenu)
        self.icon_list = self.loadIcon()
        self.trayIcon.setIcon(self.icon_list[0])
        self.trayIcon.setToolTip("思源笔记git助手")
        # 左键双击打开主界面
        self.trayIcon.activated[QtWidgets.QSystemTrayIcon.ActivationReason].connect(self.openApp)
        self.trayIcon.show()

        self.initWidget()
        self.initConnect()
        self.initLog()

    def initWidget(self):
        # 居中
        desktop = QApplication.desktop()
        current_screen = desktop.screenNumber(self)  # 获取程序所在屏幕是第几个屏幕
        rect = desktop.screenGeometry(current_screen)  # 获取程序所在屏幕的尺寸
        self.move(int((rect.width() - self.width()) / 2), int((rect.height() - self.height()) / 2))

    def initConnect(self):
        self.quitAction.triggered.connect(self.quitApp)
        self.openAction.triggered.connect(self.openApp)
        self.aboutAction.triggered.connect(self.showAbout)
        self.logAction.triggered.connect(self.openLog)
        self.btnConnect.clicked.connect(self.showConnect)
        self.btnPower.clicked.connect(self.showPower)
        self.btnLogin.clicked.connect(self.showLogin)

    def initLog(self):
        currentDateTime = QDateTime.currentDateTime()
        time = currentDateTime.toString("yyyy/MM/dd HH:mm:ss")
        f = open("./log.txt", "a")
        f.write(time)
        f.close()

    def quitApp(self):
        QCoreApplication.quit()

    def openApp(self, reason):
        """
        双击任务栏时或显式调用方法时主窗口变为活动状态，防止右键任务栏图标也打开主界面
        :param reason: 
        :return:
        """
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick or reason == False:
            self.ui.showNormal()
            self.ui.activateWindow()

    def showAbout(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("关于")
        msg.setText("git helper for siyuan note\n \nCopyright © 2020-2020 JUN. \nAll Rights Reserved. ")
        msg.setIconPixmap(QPixmap(":/icon/icon.png"))
        msg.addButton("确定", QMessageBox.ActionRole)
        msg.exec()

    def openLog(self):
        QDesktopServices.openUrl(QUrl("./log.txt"))

    def closeEvent(self, event):
        """

        :param event:
        :return:
        """

    def showConnect(self):
        self.showMessage("连接", "已经连接机械手")

    def showPower(self):
        self.showMessage("上电", "机械手已上电")

    def showLogin(self):
        self.showMessage("权限", "切换权限USER1")

    def showMessage(self, title, content):
        self.trayIcon.showMessage(title, content, QSystemTrayIcon.Information, 1000)

    # 加载图标
    def loadIcon(self):
        if self.icon_type == 'mario':
            return [QIcon(f'icons/{self.icon_type}/{i}.png') for i in range(3)]
        return [QIcon(f'icons/{self.icon_type}/{i}.png') for i in range(5)]


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.monitor = 'cpu'
        self.cpu_usage = 0.2  # 初始化
        self.mem_usage = 0.2  # 初始化
        self.gpu_usage = 0.2  # 初始化

        self.icon_type = 'runcat'  # 设定默认图标，并加载
        self.icon_list = self.loadIcon()
        self.setIcon(self.icon_list[0])

        self.setVisible(True)
        self.setMenu()  # 加载菜单
        self.updateIcon()  # 更新图标

    # 加载图标
    def loadIcon(self):
        if self.icon_type == 'mario':
            return [QIcon(f'icons/{self.icon_type}/{i}.png') for i in range(3)]
        return [QIcon(f'icons/{self.icon_type}/{i}.png') for i in range(5)]

    # 设置菜单
    def setMenu(self):
        self.menu = QMenu()
        self.action_1 = QAction(QIcon(f'icons/cat.png'),
                                'Cat', self, triggered=lambda: self.changeIconType('runcat'))
        self.action_2 = QAction(QIcon(f'icons/mario/0.png'),
                                'Mario', self, triggered=lambda: self.changeIconType('mario'))

        self.action_c = QAction(QIcon(f'icons/cpu.png'),
                                'CPU', self, triggered=lambda: self.changeMonitor('cpu'))
        self.action_m = QAction(QIcon(f'icons/mem.png'),
                                'Memory', self, triggered=lambda: self.changeMonitor('mem'))
        self.action_g = QAction(QIcon(f'icons/gpu.png'),
                                'GPU', self, triggered=lambda: self.changeMonitor('gpu'))

        self.action_q = QAction(QIcon(f'icons/quit.png'),
                                'Quit', self, triggered=self.quit)

        self.action_push = QAction(QIcon(f'icons/quit.png'),"push",self, triggered=self.push)

        self.action_pull = QAction(QIcon(f'icons/quit.png'),"pull",self, triggered=self.push)

        self.menu.addAction(self.action_pull)
        self.menu.addAction(self.action_c)
        self.menu.addAction(self.action_m)
        self.menu.addAction(self.action_g)
        self.menu.addSeparator()
        self.menu.addAction(self.action_1)
        self.menu.addAction(self.action_2)
        self.menu.addSeparator()
        self.menu.addAction(self.action_push)
        self.menu.addAction(self.action_q)
        self.setContextMenu(self.menu)

    # 根据使用率更新图标，
    # 创建两个 threading：一个获取使用率，一个更新图标
    def updateIcon(self):
        threading.Timer(0.1, self.thread_get_cpu_usage, []).start()
        threading.Timer(0.1, self.thread_update_icon, []).start()

    # get cpu usage
    def thread_get_cpu_usage(self):
        while True:
            self.cpu_usage = psutil.cpu_percent(interval=1) / 100
            self.mem_usage = psutil.virtual_memory().percent / 100
            # print(self.cpu_usage)
            time.sleep(0.5)

    # update icon
    def thread_update_icon(self):
        while True:
            mon = self.cpu_usage
            if self.monitor == 'mem':
                mon = self.mem_usage
            elif self.monitor == 'gpu':
                mon = self.gpu_usage

            t = 0.18 - mon * 0.15
            # print(mon, t)
            for i in self.icon_list:
                self.setIcon(i)
                tip = f'cpu: {self.cpu_usage:.2%} \nmem: {self.mem_usage:.2%} \ngpu: {self.gpu_usage:.2%}'
                self.setToolTip(tip)
                # print(i, self.cpu_usage)
                time.sleep(t)

    # Change icon type
    def changeIconType(self, type):
        print(type)
        if type != self.icon_type:
            self.icon_type = type
            self.icon_list = self.loadIcon()
            print(f'Load {self.icon_type}({len(self.icon_list)}) icons...')

    # change monitor type
    def changeMonitor(self, monitor_type):
        print(monitor_type)
        if monitor_type != self.monitor:
            self.monitor = monitor_type

    def windowsMessage(self):
        """
        配置显示 windows 系统消息通知
        :return:
        """
        print("example")
        if self.trayIcon.supportsMessages() == True and self.trayIcon.isSystemTrayAvailable() == True:
            self.trayIcon.showMessage("title", "message", QtGui.QIcon("../amber_logo.ico"), 10000)
        else:
            print("ERROR: windowsMessage()")

    def push(self):
        """git push

        :return:
        """

    def pull(self):
        """git pull

        :return:
        """

    # 退出程序
    def quit(self):
        self.setVisible(False)
        app.quit()
        os._exit(-1)  # 完全退出程序




if __name__ == "__main__":
    # 创建活跃 app 句柄
    app = QApplication(sys.argv)
    # 关闭全部窗口后程序不退出
    QApplication.setQuitOnLastWindowClosed(False)  # 关闭最后一个窗口不退出程序
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
