# -*- coding: utf-8 -*-
# 2021/07/13
# author:钟军
# e-mail:junzhong0917@163.com

from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg  # pyqt5的画布
import io
import cv2
import matplotlib
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QWidget
import pyqtgraph as pg
matplotlib.use("Qt5Agg")  # 声明使用pyqt5



class MatplotlibFigure(FigureCanvasQTAgg):
    """
    创建一个画布类，并把画布放到FigureCanvasQTAgg
    """

    def __init__(self, parent=None, filePrefix=None):
        """
        
        :param parent:
        :param filePrefix:
        """
        self.figs = Figure(figsize=(10, 8), dpi=300)
        super(MatplotlibFigure, self).__init__(self.figs)  # 在父类中激活self.fig
        self.setParent(parent)
        self.filePrefix = filePrefix
        self.axes = self.figs.add_subplot(111)
        self.axes.patch.set_alpha(1)  # 设置ax区域背景颜色透明度
        # self.figs.canvas.setStyleSheet("background-color:transparent;")
        FigureCanvasQTAgg.setSizePolicy(
            self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # 用于告知包含该widget的layout：该widget的size hint已发生变化，layout会自动进行调整。
        FigureCanvasQTAgg.updateGeometry(self)

    def saveFig(self):
        """保存图片，使用二进制字节流存储，opencv读取
        """
        # FIXME:保存的图片大小不正确，无法显示全部
        buffer = io.BytesIO()
        self.figs.canvas.print_png(buffer)
        data = buffer.getvalue()
        buffer.write(data)
        img = Image.open(buffer)
        img = np.asarray(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imwrite("./temp save files/" + self.filePrefix + ".png", img)

    def saveFig2(self):
        """
        FIXME:需要优化保存图片的速度
        """
        self.figs.savefig("./temp save files/" + self.filePrefix +
                          ".jpg", dpi=144, bbox_inches="tight")


class MplWidget(QWidget):
    """Qt控件，用于嵌入matplotlib画布和工具栏

    Args:
        QWidget ([type]): [description]
    """

    def __init__(self, parent=None, filePrefix=None):
        """

        :param parent:
        """
       
        QWidget.__init__(self, parent)
        self.qCanvas = MatplotlibFigure(parent, filePrefix)
        self.mpl_toolbar = NavigationToolbar(self.qCanvas, self)  # 创建工具条
        # 创建布局，把画布类组件对象和工具条对象添加到QWidget控件中
        self.vbl = QtWidgets.QVBoxLayout(self)
        self.vbl.addWidget(self.qCanvas)
        self.vbl.addWidget(self.mpl_toolbar)



class pyqtgraph_widget(QWidget):
    """将pyqtgraph嵌入到pyqt界面中

    Args:
        QWidget ([type]): 基于QWidget组件
    """

    def __init__(self, parent=None):
        """

        :param parent: 父组件
        """
       
        QWidget.__init__(self, parent)
        # 创建垂直布局
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setObjectName('layout')
        self.layout.setContentsMargins(0,0,0,0)
        # 修改背景颜色
        pg.setConfigOption('background', '#FFFFFF')
        pg.setConfigOption('foreground', 'k')
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        self.plot_widget.setAspectLocked()  # 坐标轴等比例缩放
        
    def update_circle(self,circle_list):
        for circle in circle_list:
            self.plot_widget.addItem(circle)
        print('============颗粒更新完成===========')

    def update_wall(self,wall_list):
        for wall in wall_list:
            self.plot_widget.addItem(wall)
        print('============墙更新完成===========')