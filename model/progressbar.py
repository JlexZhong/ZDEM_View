# -*- coding: utf-8 -*-
# 2021/07/9
# author:钟军
# e-mail:junzhong0917@163.com

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QProgressBar, QLabel, QSlider


class ProgressBar(object):
    """
    进度条
    """

    def __init__(self, myUi=None):
        """

        :param myUi:
        """
        self.myUi = myUi
        self.initBar()
        self.nowPlotNum = 0

    def initBar(self):
        """

        创建进度条
        :return:
        """
        self.pBar = QProgressBar()
        self.pBar.setInvertedAppearance(False)

        self.pBar.setVisible(False)  # 设置进度条不可见
        self.pBar.setRange(0, 100)
        self.pBar.setValue(0)
        self.pBar.setMaximumWidth(400)
        self.barStep = 0
        self.barVaule = 0  # 每次赋给进度条的值，第一次为step
        self.statusWidget = QtWidgets.QWidget()
        # FIXME:需要优化状态栏的信息显示功能，目前很杂乱！
        # 添加控件
        font = QtGui.QFont()
        font.setFamily("黑体")
        #font.setPointSize(8)
        font.setBold(False)
        
        self.myUi.statusBar.setMaximumHeight(30)
        self.statusWidget.setMaximumHeight(30)
        self.statusLabel = QLabel(self.statusWidget)
        self.statusLabel.setText(u'  准备  ')
        self.statusLabel.setFont(font)
        self.statusLabel.setStyleSheet("color:white")  # 字体颜色为白色
        #self.statusLabel.setFont(QFont("Roman times",6,QFont.Bold))
        self.statusLabel.setMaximumHeight(30)
        self.plotAllLabel = QLabel(self.statusWidget)
        self.plotAllLabel.setText(u' 暂未执行画图功能 ')
        self.plotAllLabel.setMaximumHeight(30)
        self.plotAllLabel.setFont(font)
        self.plotAllLabel.setStyleSheet("color:white")  # 字体颜色为白色
        self.beginPlotLabel = QLabel(self.statusWidget)
        self.beginPlotLabel.setText(u' 暂无线程工作 ')
        self.beginPlotLabel.setMaximumHeight(30)
        self.beginPlotLabel.setFont(font)
        self.beginPlotLabel.setStyleSheet("color:white")  # 字体颜色为白色
        self.statusLayout = QtWidgets.QHBoxLayout(self.statusWidget)
        self.statusLayout.setObjectName("statusLayout")
        self.statusLayout.setContentsMargins(0,0,0,0)
        self.myUi.statusBar.addWidget(self.statusWidget,1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.statusLayout.addWidget(self.statusLabel)
        self.statusLayout.addWidget(self.plotAllLabel)
        self.statusLayout.addWidget(self.beginPlotLabel)
        self.statusLayout.addWidget(self.pBar)
        self.statusLayout.addItem(spacerItem)



    def updata_PBar(self, num):
        """

        更新进度条(绘制单图)
        :param num:
        :return:
        """
        self.pBar.setVisible(True)
        if num == 0:
            # self.AllNum = int(self.myUi.plotObj.BallNum) + 1 + 3 + 1
            # self.barStep = 100 // self.AllNum
            # self.barVaule = self.barStep
            # self.pBar.setRange(0, self.AllNum)

            self.pBar.setValue(5)
            # self.barVaule = self.barVaule + 1
            self.barVaule = 7
            self.statusLabel.setText('  读取数据成功  ')
        if num == 1:
            self.pBar.setValue(self.barVaule)
            self.barVaule = self.barVaule + 2
            self.statusLabel.setText('  绘制颗粒中  ')
        if num == 2:
            self.pBar.setValue(self.barVaule)
            self.statusLabel.setText('  绘制墙和坐标轴中  ')
        if num == 3:
            self.pBar.setValue(100)
            self.pBar.setVisible(False)
            self.statusLabel.setText('  绘图成功  ')

    def setBar_plotAll(self, num):
        """

        初始化进度条，设置进度条的参数
        :param num:
        :return:
        """
        self.nowPlotNum = 0
        self.maxNum = num
        self.pBar.setVisible(True)
        self.pBar.setRange(1, self.maxNum)  # 设置进度条的值域，这里是从1到maxNUm

    def updataBar_plotAll_mp(self, id):
        """
        更新进度条（绘制多图时）,matplotlib
        :param id:
        :return:
        """
        self.nowPlotNum = self.nowPlotNum + 1
        self.pBar.setValue(self.nowPlotNum)
        if self.nowPlotNum != self.maxNum:
            self.statusLabel.setText('绘图中，请稍后...' + str(self.nowPlotNum) + '/' + str(self.maxNum))
        else:
            self.statusLabel.setText(str(self.maxNum) + '张图片已经绘制成功！')
            self.nowPlotNum = 0
            
            axisRangeList = self.myUi.dataView.mplWidget_list[0].qCanvas.axes.axis()
            xMin = axisRangeList[0]
            xMax = axisRangeList[1]
            yMin = axisRangeList[2]
            yMax = axisRangeList[3]
            self.myUi.leftBar.xmax_lineEdit.setText(str(xMax))
            self.myUi.leftBar.xmin_lineEdit.setText(str(xMin))
            self.myUi.leftBar.ymax_lineEdit.setText(str(yMax))
            self.myUi.leftBar.ymin_lineEdit.setText(str(yMin))
            



    def updataBar_plotAll_pg(self, id):
        """
        更新进度条（绘制多图时）,pyqtgraph
        :param id:
        :return:
        """
        self.nowPlotNum = self.nowPlotNum + 1
        self.pBar.setValue(self.nowPlotNum)
        if self.nowPlotNum != self.maxNum:
            self.statusLabel.setText('绘图中，请稍后...' + str(self.nowPlotNum) + '/' + str(self.maxNum))
        else:
            # TODO: pyqtgraph绘图时，更新侧边栏的min、max信息
            self.statusLabel.setText(str(self.maxNum) + '张图片已经绘制成功！')
            self.nowPlotNum = 0
            
            

