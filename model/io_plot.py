# -*- coding: utf-8 -*-
# 2021/01/23
# author:钟军
# e-mail:2678091501@qq.com
# 离散元数值模拟后处理系统 v1.0

# 导入numpy库
import io
import os
import sys
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import cv2
from PIL import Image
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QWidget
import PyQt5.QtWidgets as QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, FormatStrFormatter
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from matplotlib.ticker import MultipleLocator
import  matplotlib.pyplot as plt
import pyqtgraph as pg
from pyqtgraph.functions import mkBrush






class MatplotlibFigure(FigureCanvasQTAgg):
    """
    创建一个画布类，并把画布放到FigureCanvasQTAgg
    """

    def __init__(self, parent=None):
        """

        :param parent:
        :param filePrefix:
        """
        self.figs = Figure(figsize=(10, 8), dpi=300)
        super(MatplotlibFigure, self).__init__(self.figs)  # 在父类中激活self.fig
        self.setParent(parent)
        self.axes = self.figs.add_subplot(111)
        filepath = "E:\\Study\\Data_Visualization ui_pyqt5\\Data_Visualization\\V2.0\\example\\easyData\\all_0000003600.dat"
        self.mpl_plot(filepath, xmove=-1000, ymove=-1000)
        FigureCanvasQTAgg.setSizePolicy(
            self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # 用于告知包含该widget的layout：该widget的size hint已发生变化，layout会自动进行调整。
        FigureCanvasQTAgg.updateGeometry(self)

    def readData(self,filepath=None, xmove=0, ymove=0):
        """读取.dat格式文件内容
        """
        flag = 0
        WALL = []
        BALL = []
        CurrentStep = 0
        BallNum = 0
        ZDEM_File = open(filepath, 'r')
        for line in ZDEM_File:  # 逐行读取文件
            if "current_step" in line:  # 当前所在步数
                step = line.split()  # 将该行（list）以空格“ ”进行切片
                CurrentStep = step[-1]  # 取step的最后一个元素作为步数

            if "ball num" in line:  # 获取颗粒个数
                ball_num = line.split()
                BallNum = ball_num[-1]

            if "     index         id      P1[0]" in line:  # 标记wall数据开始
                flag = 1
                continue
            if "     index         id         xF" in line:  # 当读取到此行时，含wall坐标的数据结束
                flag = 0
            if "     index         id                    x" in line:  # 标记ball数据开始
                flag = 2
                continue
            if "     index         id            m" in line:  # 当读取到此行时，含ball坐标的数据结束
                flag = 0
            if flag == 0:
                continue
            if flag == 1:
                wall = line.split()  # 将该行（list）以空格“ ”进行切片
                # 读取第3到第6列，并用for循环把字符串转变为浮点型
                wall = [float(i) for i in wall[2:6]]
                WALL.append(wall)  # wall两点p1、p2的x、y坐标
            if flag == 2:
                ball = line.split()  # 将该行（list）以空格“ ”进行切片
                ball = [float(i) for i in ball[2:6]]
                BALL.append(ball)  # ball的x、y坐标以及半径、颜色
        del WALL[-1]  # 删除最后的空行
        del BALL[-1]  # 删除最后的空行
        ZDEM_File.close()  # 关闭对象，避免占用过多资源
        # self.updata_progressbar_signal.emit(0)
        WALL, BALL, CurrentStep = np.array(
            WALL), np.array(BALL), np.array(CurrentStep)
        # ZDEM颜色的RGB列表
        ZDEMColor_num = np.array([[0.85, 0.85, 0.85],
                                  [0.00, 1.00, 0.00],
                                  [1.00, 1.00, 0.00],
                                  [1.00, 0.00, 0.00],
                                  [0.90, 0.90, 0.90],
                                  [0.15, 0.15, 0.15],
                                  [0.50, 0.50, 0.50],
                                  [0.00, 0.00, 1.00],
                                  [0.00, 1.00, 1.00],
                                  [1.00, 0.00, 1.00]])
        ZDEMColor_code = ['#D9D9D9',
                          '#00FF00',
                          '#FFFF00',
                          '#FF0000',
                          '#F5F5F5',
                          '#262626',
                          '#808080',
                          '#0000FF',
                          '#00FFFF',
                          '#FF00FF']
        # 读取数组对应需要的元素
        BALL_x = BALL[:, 0]
        BALL_y = BALL[:, 1]
        BALL_r = BALL[:, 2]
        BALL_c = BALL[:, 3]
        WALL_P1_x = WALL[4:7, 0]
        WALL_P1_y = WALL[4:7, 1]
        WALL_P2_x = WALL[4:7, 2]
        WALL_P2_y = WALL[4:7, 3]
        # 进行偏移量修改
        for i in range(len(WALL_P1_x)):
            WALL_P1_x[i] = WALL_P1_x[i] + xmove
            WALL_P1_y[i] = WALL_P1_y[i] + ymove
            WALL_P2_x[i] = WALL_P2_x[i] + xmove
            WALL_P2_y[i] = WALL_P2_y[i] + ymove
        for i in range(len(BALL_x)):
            BALL_x[i] = BALL_x[i] + xmove
            BALL_y[i] = BALL_y[i] + ymove

        # begin_plot_signal.emit(id)  # 发送信号：开始绘图

        ball_c = []  # 颜色 #xxxxxx格式
        for i in range(len(BALL_x)):
            color_num = BALL_c[i]
            color_num = int(color_num)
            ballColor = ZDEMColor_num[color_num]
            ball_c.append(ballColor)
        return BALL_x, BALL_y, BALL_r, ball_c, WALL_P1_x, WALL_P1_y, WALL_P2_x, WALL_P2_y

    def mpl_plot(self,filepath=None, xmove=0, ymove=0):
        BALL_x, BALL_y, BALL_r, BALL_c, WALL_P1_x, WALL_P1_y, WALL_P2_x, WALL_P2_y = self.readData(filepath, xmove, ymove)
        self.axes.cla()
        for i in range(len(BALL_x)):
            ball_x = BALL_x[i]
            ball_y = BALL_y[i]
            ball_r = BALL_r[i]
            ball_c = BALL_c[i]
            # 绘图
            cir = Circle(xy=(ball_x, ball_y),
                         radius=ball_r, facecolor=ball_c)
            self.axes.add_patch(cir)
            print('ball id:', i)
        self.draw()




class MplWidget(QWidget):
    """Qt控件，用于嵌入matplotlib画布和工具栏

    Args:
        QWidget ([type]): [description]
    """

    def __init__(self, parent=None):
        """

        :param parent:
        """

        QWidget.__init__(self, parent)
        self.qCanvas = MatplotlibFigure(parent)
        self.mpl_toolbar = NavigationToolbar(self.qCanvas, self)  # 创建工具条
        # 创建布局，把画布类组件对象和工具条对象添加到QWidget控件中
        self.vbl = QtWidgets.QVBoxLayout(self)
        self.vbl.addWidget(self.qCanvas)
        self.vbl.addWidget(self.mpl_toolbar)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    ui = MplWidget()

    ui.show()

    sys.exit(app.exec_())