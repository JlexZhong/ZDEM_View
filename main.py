# -*- coding: utf-8 -*-
# 2021/07/9
# author:钟军
# e-mail:junzhong0917@163.com
import sys
from PyQt5.QtGui import QIcon
import qdarkstyle
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication,  QMainWindow
from UI import wMain
import cgitb

# 这句放在所有程序开始前，这样就可以正常打印异常了
cgitb.enable(format="text")

if __name__ == '__main__':

    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myMainWindow = wMain.myMainWindow()
    
    with open('./QSS/myQSS.qss', encoding='utf-8') as f:
        qss = f.read()
    app.setStyleSheet(qss)  # 设置主题
    # qdarkstyle
    # 设置qdarkstyle
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    myUi = wMain.Ui_MainWindow()
    myUi.setupUi(myMainWindow)
    myMainWindow.setWindowTitle('ZDEMViewer    离散元数值模拟可视化程序')
    myMainWindow.setWindowIcon(QIcon("./icons/logo.ico"))
    myMainWindow.show()
    sys.exit(app.exec_())
   
