# -*- coding: utf-8 -*-
# 2021/01/23
# author:钟军
# e-mail:2678091501@qq.com
# 离散元数值模拟后处理系统 v1.0

# 导入numpy库
import io
import os
import cv2
from PIL import Image
from PyQt5.QtCore import pyqtSignal, QObject
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, FormatStrFormatter
import numpy as np
from matplotlib.patches import Circle
from matplotlib.ticker import MultipleLocator
import pyqtgraph as pg
from pyqtgraph.functions import mkBrush

"""
    读取和绘图文件，负责读取文件和图像的绘制
"""


class _plot(object):
    updata_progressbar_signal = pyqtSignal(int)

    def __init__(self):
        # self.wMain = myUi

        super().__init__()
        self.WALL = []
        self.BALL = []
        self.CurrentStep = 0
        self.BallNum = 0
        self.xmove = 0
        self.ymove = 0
        self.wallShow = "true"
        self.units = 1
        self.canvasObj = None
        self.pagesize = 14

    def readData(self, filepath):
        filename = os.path.split(filepath)[1]
        self.filePrefix = os.path.splitext(filename)[0]
        flag = 0
        self.WALL = []
        self.BALL = []
        self.CurrentStep = 0
        self.BallNum = 0
        ZDEM_File = open(filepath, 'r')
        for line in ZDEM_File:  # 逐行读取文件
            if "current_step" in line:  # 当前所在步数
                step = line.split()  # 将该行（list）以空格“ ”进行切片
                self.CurrentStep = step[-1]  # 取step的最后一个元素作为步数

            if "ball num" in line:  # 获取颗粒个数
                ball_num = line.split()
                self.BallNum = ball_num[-1]

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
                self.WALL.append(wall)  # wall两点p1、p2的x、y坐标
            if flag == 2:
                ball = line.split()  # 将该行（list）以空格“ ”进行切片
                ball = [float(i) for i in ball[2:6]]
                self.BALL.append(ball)  # ball的x、y坐标以及半径、颜色
        del self.WALL[-1]  # 删除最后的空行
        del self.BALL[-1]  # 删除最后的空行
        ZDEM_File.close()  # 关闭对象，避免占用过多资源
        self.updata_progressbar_signal.emit(0)

    def plotJPG(self, canvasObj):
        self.canvasObj = canvasObj
        self.xmove = 0
        self.ymove = 0
        self.wallShow = 'true'
        self.units = 1

        self.canvasObj.axes.cla()  # 清理画布后必须重新添加绘图区
        # 转换为numpy数组，便于处理
        self.WALL, self.BALL, self.CurrentStep = np.array(
            self.WALL), np.array(self.BALL), np.array(self.CurrentStep)
        # ZDEM颜色的RGB列表
        Color = np.array([[0.85, 0.85, 0.85],
                          [0.00, 1.00, 0.00],
                          [1.00, 1.00, 0.00],
                          [1.00, 0.00, 0.00],
                          [0.90, 0.90, 0.90],
                          [0.15, 0.15, 0.15],
                          [0.50, 0.50, 0.50],
                          [0.00, 0.00, 1.00],
                          [0.00, 1.00, 1.00],
                          [1.00, 0.00, 1.00]])
        ZDEM_color = ['#D9D9D9',
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
        BALL_x = self.BALL[:, 0]
        BALL_y = self.BALL[:, 1]
        BALL_r = self.BALL[:, 2]
        BALL_c = self.BALL[:, 3]
        WALL_P1_x = self.WALL[4:7, 0]
        WALL_P1_y = self.WALL[4:7, 1]
        WALL_P2_x = self.WALL[4:7, 2]
        WALL_P2_y = self.WALL[4:7, 3]
        # 获取x、y轴偏移量，并对ball、wall的坐标修改
        # xmove = min(min(WALL_P1_x),min(WALL_P2_x))
        # ymove = min(min(WALL_P1_y),min(WALL_P2_y))
        for i in range(len(WALL_P1_x)):
            WALL_P1_x[i] = WALL_P1_x[i] + self.xmove
            WALL_P1_y[i] = WALL_P1_y[i] + self.ymove
            WALL_P2_x[i] = WALL_P2_x[i] + self.xmove
            WALL_P2_y[i] = WALL_P2_y[i] + self.ymove
        for i in range(len(BALL_x)):
            BALL_x[i] = BALL_x[i] + self.xmove
            BALL_y[i] = BALL_y[i] + self.ymove
            # 通过循环获取每个颗粒的坐标和半径、颜色，用matplotlib库的Circle绘制颗粒
        # 先设置坐标轴max、min
        b_xmax = max(BALL_x)
        b_ymax = max(BALL_y)
        w_p1_xmax = max(WALL_P1_x)
        w_p2_xmax = max(WALL_P2_x)
        w_p1_ymax = max(WALL_P1_y)
        w_p2_ymax = max(WALL_P2_y)
        w_xmax = max(w_p1_xmax, w_p2_xmax)
        w_ymax = max(w_p1_ymax, w_p2_ymax)
        xmax = max(b_xmax, w_xmax)
        ymax = max(b_ymax, w_ymax)

        b_xmin = min(BALL_x)
        b_ymin = min(BALL_y)
        w_p1_xmin = min(WALL_P1_x)
        w_p2_xmin = min(WALL_P2_x)
        w_p1_ymin = min(WALL_P1_y)
        w_p2_ymin = min(WALL_P2_y)
        w_xmin = min(w_p1_xmin, w_p2_xmin)
        w_ymin = min(w_p1_ymin, w_p2_ymin)
        xmin = min(b_xmin, w_xmin)
        ymin = min(b_ymin, w_ymin)

        self.canvasObj.axes.set_xlim(0, xmax)
        self.canvasObj.axes.set_ylim(0, ymax)
        ball_c = []
        for i in range(len(BALL_x)):
            color_num = BALL_c[i]
            color_num = int(color_num)
            ballColor = ZDEM_color[color_num]
            ball_c.append(ballColor)

        ballNUM = len(BALL_r)
        # 绘制点图，转换坐标
        rr_pix = (self.canvasObj.axes.transData.transform(np.vstack([BALL_r, BALL_r]).T) -

                  self.canvasObj.axes.transData.transform(np.vstack([np.zeros(ballNUM), np.zeros(ballNUM)]).T))

        rpix, _ = rr_pix.T

        size_pt = (2 * rpix / self.canvasObj.figs.dpi * 72) ** 2
        scat = self.canvasObj.axes.scatter(BALL_x, BALL_y, s=size_pt, c=ball_c)

        for i in range(len(BALL_x)):
            ball_x = BALL_x[i]
            ball_y = BALL_y[i]
            ball_r = BALL_r[i]
            # .dat文件的颜色为0-7，要对应到相应的RGB值
            # color_num = BALL_c[i]
            # color_num = int(color_num)
            # ball_c = Color[color_num]
            # 绘图
            # cir = Circle(xy=(ball_x, ball_y), radius=ball_r, facecolor=ball_c)
            # self.canvasObj.axes.add_patch(cir)
            BallNum_45 = (int(self.BallNum) // 45)
            for n in range(45):
                if i == (BallNum_45 * (n + 1)):
                    self.updata_progressbar_signal.emit(1)
                    n = 0

        if (self.wallShow == 'true'):
            for n in range(len(WALL_P1_x)):
                p1x = WALL_P1_x[n]
                p1y = WALL_P1_y[n]
                p2x = WALL_P2_x[n]
                p2y = WALL_P2_y[n]
                p12x = [p1x, p2x]
                p12y = [p1y, p2y]
                self.canvasObj.axes.plot(p12x, p12y, c='k')
                line1 = [(p1x, p1y), (p2x, p2y)]
                (line1_xs, line1_ys) = zip(*line1)
                # 创建两条线，并添加
                self.canvasObj.axes.add_line(
                    Line2D(line1_xs, line1_ys, linewidth=1, color='black'))
        self.updata_progressbar_signal.emit(2)
        # plt.plot(VBOXx,VBOXy,'.')
        """for i in range(len(wp1x)):
            # 两条line的数据
            line1 = [(wp1x[i], wp1y[i]), (wp2x[i], wp2y[i])]
            (line1_xs, line1_ys) = zip(*line1)
            # 创建两条线，并添加
            self.canvasObj.axes.add_line(Line2D(line1_xs, line1_ys, linewidth=1, color='black'))"""

        self.canvasObj.axes.axis('scaled')

        def unitsformat(x, pos):
            return '{:n}'.format(x / self.units)

        xmajorformatter = FuncFormatter(unitsformat)
        self.canvasObj.axes.xaxis.set_major_formatter(xmajorformatter)
        ymajorformatter = FuncFormatter(unitsformat)
        self.canvasObj.axes.yaxis.set_major_formatter(ymajorformatter)

        # 修改次刻度
        xminorLocator = MultipleLocator(1000)
        yminorLocator = MultipleLocator(1000)
        self.canvasObj.axes.xaxis.set_minor_locator(xminorLocator)
        self.canvasObj.axes.yaxis.set_minor_locator(yminorLocator)
        '''
        b_xmax = BALL_x[0]
        for i in range(len(BALL_x)):
            b_xmax = max(BALL_x[i],b_xmax)
            '''
        b_xmax = max(BALL_x)
        b_ymax = max(BALL_y)
        w_p1_xmax = max(WALL_P1_x)
        w_p2_xmax = max(WALL_P2_x)
        w_p1_ymax = max(WALL_P1_y)
        w_p2_ymax = max(WALL_P2_y)
        w_xmax = max(w_p1_xmax, w_p2_xmax)
        w_ymax = max(w_p1_ymax, w_p2_ymax)
        xmax = max(b_xmax, w_xmax)
        ymax = max(b_ymax, w_ymax)

        b_xmin = min(BALL_x)
        b_ymin = min(BALL_y)
        w_p1_xmin = min(WALL_P1_x)
        w_p2_xmin = min(WALL_P2_x)
        w_p1_ymin = min(WALL_P1_y)
        w_p2_ymin = min(WALL_P2_y)
        w_xmin = min(w_p1_xmin, w_p2_xmin)
        w_ymin = min(w_p1_ymin, w_p2_ymin)
        xmin = min(b_xmin, w_xmin)
        ymin = min(b_ymin, w_ymin)

        wi = xmax - xmin
        hi = ymax - ymin
        wcm = self.pagesize
        winch = wcm / 2.54
        hinch = winch / wi * hi

        self.canvasObj.axes.set_xlim(0, xmax)
        self.canvasObj.axes.set_ylim(0, ymax)
        self.canvasObj.figs.set_size_inches(w=winch, h=hinch)

        self.canvasObj.figs.canvas.draw()  # 这里注意是画布重绘，figs.canvas
        self.canvasObj.figs.canvas.flush_events()  # 画布刷新self.figs.canvas
        self.canvasObj.figs.savefig(
            "./temp save files/" + self.filePrefix + ".jpg", dpi=100, bbox_inches="tight")

        self.updata_progressbar_signal.emit(3)


class Plot(QObject):
    updata_progressbar_signal = pyqtSignal(int)
    updata_canvas_signal = pyqtSignal(int)
    begin_plot_signal = pyqtSignal(int)

    def __init__(self, param_list, canvasObj, filepath):
        super().__init__()
        self.canvasObj = canvasObj
        self.param_list = param_list
        self.filepath = filepath
        # 绘图参数
        self.xmove = self.param_list[0]
        self.ymove = self.param_list[1]
        self.xmin = self.param_list[2]
        self.xmax = self.param_list[3]
        self.ymin = self.param_list[4]
        self.ymax = self.param_list[5]
        self.ballStyle = self.param_list[6]
        self.wallShow = self.param_list[7]
        self.wallLineSize = self.param_list[8]
        self.colorStyle = self.param_list[9]
        self.titleText = self.param_list[10]
        self.titleTextFontSize = self.param_list[11]
        self.xText = self.param_list[12]
        self.xTextFontSize = self.param_list[13]
        self.yText = self.param_list[14]
        self.yTextFontSize = self.param_list[15]
        self.mainTickInterval = self.param_list[16]
        self.minorTickInterval = self.param_list[17]
        self.isShowTop = self.param_list[18]
        self.isShowBottom = self.param_list[19]
        self.isShowLeft = self.param_list[20]
        self.isShowRight = self.param_list[21]
        self.units = self.param_list[22]
        # 图片尺寸
        self.pagesize = 14

    def readData(self):
        filename = os.path.split(self.filepath)[1]
        self.filePrefix = os.path.splitext(filename)[0]
        flag = 0
        self.WALL = []
        self.BALL = []
        self.CurrentStep = 0
        self.BallNum = 0
        ZDEM_File = open(self.filepath, 'r')
        for line in ZDEM_File:  # 逐行读取文件
            if "current_step" in line:  # 当前所在步数
                step = line.split()  # 将该行（list）以空格“ ”进行切片
                self.CurrentStep = step[-1]  # 取step的最后一个元素作为步数

            if "ball num" in line:  # 获取颗粒个数
                ball_num = line.split()
                self.BallNum = ball_num[-1]

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
                self.WALL.append(wall)  # wall两点p1、p2的x、y坐标
            if flag == 2:
                ball = line.split()  # 将该行（list）以空格“ ”进行切片
                ball = [float(i) for i in ball[2:6]]
                self.BALL.append(ball)  # ball的x、y坐标以及半径、颜色
        del self.WALL[-1]  # 删除最后的空行
        del self.BALL[-1]  # 删除最后的空行
        ZDEM_File.close()  # 关闭对象，避免占用过多资源
        # self.updata_progressbar_signal.emit(0)

    def plotJPG(self, id):
        # 初始化
        self.canvasObj.qCanvas.axes.clear()  # 清理画布
        # 转换为numpy数组
        self.WALL, self.BALL, self.CurrentStep = np.array(
            self.WALL), np.array(self.BALL), np.array(self.CurrentStep)
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
        self.BALL_x = self.BALL[:, 0]
        self.BALL_y = self.BALL[:, 1]
        self.BALL_r = self.BALL[:, 2]
        self.BALL_c = self.BALL[:, 3]
        self.WALL_P1_x = self.WALL[4:7, 0]
        self.WALL_P1_y = self.WALL[4:7, 1]
        self.WALL_P2_x = self.WALL[4:7, 2]
        self.WALL_P2_y = self.WALL[4:7, 3]
        # 进行偏移量修改
        for i in range(len(self.WALL_P1_x)):
            self.WALL_P1_x[i] = self.WALL_P1_x[i] + self.xmove
            self.WALL_P1_y[i] = self.WALL_P1_y[i] + self.ymove
            self.WALL_P2_x[i] = self.WALL_P2_x[i] + self.xmove
            self.WALL_P2_y[i] = self.WALL_P2_y[i] + self.ymove
        for i in range(len(self.BALL_x)):
            self.BALL_x[i] = self.BALL_x[i] + self.xmove
            self.BALL_y[i] = self.BALL_y[i] + self.ymove
        self.plot_axis()
        self.begin_plot_signal.emit(id)  # 发送信号：开始绘图

        ball_c = []  # 颜色 #xxxxxx格式
        for i in range(len(self.BALL_x)):
            color_num = self.BALL_c[i]
            color_num = int(color_num)
            ballColor = ZDEMColor_code[color_num]
            ball_c.append(ballColor)

        if self.ballStyle == 'point':  # 绘制散点图
            ballNUM = len(self.BALL_r)
            # 绘制点图，转换坐标数据
            rr_pix = (self.canvasObj.qCanvas.axes.transData.transform(np.vstack([self.BALL_r, self.BALL_r]).T) -
                      self.canvasObj.qCanvas.axes.transData.transform(
                          np.vstack([np.zeros(ballNUM), np.zeros(ballNUM)]).T))
            rpix, _ = rr_pix.T
            size_pt = (rpix / self.canvasObj.qCanvas.figs.dpi * 72) ** 2
            scat = self.canvasObj.qCanvas.axes.scatter(
                self.BALL_x, self.BALL_y, s=size_pt, c=ball_c)
        if self.ballStyle == 'circle':  # 绘制二维圆图
            for i in range(len(self.BALL_x)):
                ball_x = self.BALL_x[i]
                ball_y = self.BALL_y[i]
                ball_r = self.BALL_r[i]
                # .dat文件的颜色为0-7，要对应到相应的RGB值
                color_num = self.BALL_c[i]
                color_num = int(color_num)
                ball_c = ZDEMColor_num[color_num]
                # 绘图
                cir = Circle(xy=(ball_x, ball_y),
                             radius=ball_r, facecolor=ball_c)
                self.canvasObj.qCanvas.axes.add_patch(cir)

        if (self.wallShow == True):
            for n in range(len(self.WALL_P1_x)):
                p1x = self.WALL_P1_x[n]
                p1y = self.WALL_P1_y[n]
                p2x = self.WALL_P2_x[n]
                p2y = self.WALL_P2_y[n]
                p12x = [p1x, p2x]
                p12y = [p1y, p2y]
                line1 = [(p1x, p1y), (p2x, p2y)]
                (line1_xs, line1_ys) = zip(*line1)
                # 创建两条线，并添加
                self.canvasObj.qCanvas.axes.add_line(
                    Line2D(line1_xs, line1_ys, linewidth=self.wallLineSize, color='black'))

        # self.canvasObj.qCanvas.axes.margins(0,0)
        # self.canvasObj.qCanvas.axes.tick_params(which='both', width=0.5, pad=1)
        # self.canvasObj.qCanvas.axes.set_xlim(xmin, xmax)
        # self.canvasObj.qCanvas.axes.set_ylim(xmin, ymax)
        # self.canvasObj.qCanvas.axes.tick_params(bottom=True, top=False, width=1, colors='black')
        # self.canvasObj.qCanvas.axes.tick_params(left=True, right=False, width=1, colors='black')

        # self.canvasObj.qCanvas.axes.tick_params(top='off',bottom='on',left='on',right='off')

        # top和right轴标签默认不显示
        # self.canvasObj.qCanvas.axes.tick_params(bottom=False,top = False,left=True, right=False)
        self.updata_canvas_signal.emit(id)
        self.canvasObj.qCanvas.figs.canvas.draw_idle()
        # self.canvasObj.qCanvas.figs.canvas.draw()
        # self.canvasObj.qCanvas.figs.canvas.flush_events()  # 画布刷新self.figs.canvas
        # self.canvasObj.qCanvas.figs.savefig("./temp save files/"+self.filePrefix+".png",dpi=100,bbox_inches="tight")

    def plot_axis(self):
        """
        BUG: 绘图数过多时报错Traceback (most recent call last):
                        File "e:\Study\Data_Visualization ui_pyqt5\Data_Visualization\V2.0\model\Thread.py", line 145, in run
                            self.plotObj_test.plotJPG(self.id )
                        File "e:\Study\Data_Visualization ui_pyqt5\Data_Visualization\V2.0\model\plot.py", line 408, in plotJPG
                            self.plot_axis()
                        File "e:\Study\Data_Visualization ui_pyqt5\Data_Visualization\V2.0\model\plot.py", line 479, in plot_axis
                            w_p1_xmax = max(self.WALL_P1_x)
                        ValueError: max() arg is an empty sequence
                        """
        # 坐标轴
        if (self.xmin == None) & (self.xmax == None) & (self.ymin == None) & (self.ymax == None):  # 若未传入min、max参数，进行计算
            # 计算xmax、ymax
            b_xmax = max(self.BALL_x)
            b_ymax = max(self.BALL_y)
            w_p1_xmax = max(self.WALL_P1_x)
            w_p2_xmax = max(self.WALL_P2_x)
            w_p1_ymax = max(self.WALL_P1_y)
            w_p2_ymax = max(self.WALL_P2_y)
            w_xmax = max(w_p1_xmax, w_p2_xmax)
            w_ymax = max(w_p1_ymax, w_p2_ymax)
            self.xmax = max(b_xmax, w_xmax)
            self.ymax = max(b_ymax, w_ymax)
            # 计算xmin、ymin
            b_xmin = min(self.BALL_x)
            b_ymin = min(self.BALL_y)
            w_p1_xmin = min(self.WALL_P1_x)
            w_p2_xmin = min(self.WALL_P2_x)
            w_p1_ymin = min(self.WALL_P1_y)
            w_p2_ymin = min(self.WALL_P2_y)
            w_xmin = min(w_p1_xmin, w_p2_xmin)
            w_ymin = min(w_p1_ymin, w_p2_ymin)
            self.xmin = min(b_xmin, w_xmin)
            self.ymin = min(b_ymin, w_ymin)
        # 坐标轴等比例缩放
        self.canvasObj.qCanvas.axes.axis('scaled')
        # 设置 x轴、y轴范围
        self.canvasObj.qCanvas.axes.set_xlim(self.xmin, self.xmax)
        self.canvasObj.qCanvas.axes.set_ylim(self.xmin, self.ymax)

        # 单位
        def unitsformat(x, pos):
            return '{:n}'.format(x / self.units)

        xmajorformatter = FuncFormatter(unitsformat)
        self.canvasObj.qCanvas.axes.xaxis.set_major_formatter(xmajorformatter)
        ymajorformatter = FuncFormatter(unitsformat)
        self.canvasObj.qCanvas.axes.yaxis.set_major_formatter(ymajorformatter)
        # 修改主刻度
        xmajorLocator = MultipleLocator(
            self.mainTickInterval)  # 将x主刻度标签设置为20的倍数
        # xmajorFormatter = FormatStrFormatter('%5.1f')  # 设置x轴标签文本的格式
        ymajorLocator = MultipleLocator(
            self.mainTickInterval)  # 将y轴主刻度标签设置为0.5的倍数
        # ymajorFormatter = FormatStrFormatter('%1.1f')  # 设置y轴标签文本的格式
        # 设置主刻度标签的位置,标签文本的格式
        self.canvasObj.qCanvas.axes.xaxis.set_major_locator(xmajorLocator)
        # self.canvasObj.qCanvas.axes.xaxis.set_major_formatter(xmajorFormatter)
        self.canvasObj.qCanvas.axes.yaxis.set_major_locator(ymajorLocator)
        # self.canvasObj.qCanvas.axes.yaxis.set_major_formatter(ymajorFormatter)
        # 修改次刻度
        xminorLocator = MultipleLocator(self.minorTickInterval)
        yminorLocator = MultipleLocator(self.minorTickInterval)
        self.canvasObj.qCanvas.axes.xaxis.set_minor_locator(xminorLocator)
        self.canvasObj.qCanvas.axes.yaxis.set_minor_locator(yminorLocator)
        # 设置标签label的字体大小
        self.canvasObj.qCanvas.axes.tick_params(
            axis='x', labelsize=self.xTextFontSize)
        self.canvasObj.qCanvas.axes.tick_params(
            axis='y', labelsize=self.yTextFontSize)
        # 坐标轴边框显示/隐藏
        self.canvasObj.qCanvas.axes.spines['top'].set_visible(self.isShowTop)
        self.canvasObj.qCanvas.axes.spines['right'].set_visible(
            self.isShowRight)
        self.canvasObj.qCanvas.axes.spines['bottom'].set_visible(
            self.isShowBottom)
        self.canvasObj.qCanvas.axes.spines['left'].set_visible(self.isShowLeft)
        # 计算图片尺寸
        wi = self.xmax - self.xmin
        hi = self.ymax - self.ymin
        wcm = self.pagesize
        winch = wcm / 2.54
        hinch = (winch) / wi * hi
        self.canvasObj.qCanvas.figs.set_size_inches(w=winch, h=hinch)




class pg_plot(QObject):
    updata_progressbar_signal = pyqtSignal(int)
    updata_canvas_signal = pyqtSignal(int)
    begin_plot_signal = pyqtSignal(int)
    updata_pg_circle_signal = pyqtSignal(list)
    updata_pg_wall_signal = pyqtSignal(list)

    def __init__(self, param_list, plot_widget, filepath):
        super().__init__()
        self.plot_widget = plot_widget
        self.param_list = param_list
        self.filepath = filepath
        # 绘图参数
        self.xmove = self.param_list[0]
        self.ymove = self.param_list[1]
        self.xmin = self.param_list[2]
        self.xmax = self.param_list[3]
        self.ymin = self.param_list[4]
        self.ymax = self.param_list[5]
        self.ballStyle = self.param_list[6]
        self.wallShow = self.param_list[7]
        self.wallLineSize = self.param_list[8]
        self.colorStyle = self.param_list[9]
        self.titleText = self.param_list[10]
        self.titleTextFontSize = self.param_list[11]
        self.xText = self.param_list[12]
        self.xTextFontSize = self.param_list[13]
        self.yText = self.param_list[14]
        self.yTextFontSize = self.param_list[15]
        self.mainTickInterval = self.param_list[16]
        self.minorTickInterval = self.param_list[17]
        self.isShowTop = self.param_list[18]
        self.isShowBottom = self.param_list[19]
        self.isShowLeft = self.param_list[20]
        self.isShowRight = self.param_list[21]
        self.units = self.param_list[22]
        # 图片尺寸
        self.pagesize = 14

    def readData(self):
        filename = os.path.split(self.filepath)[1]
        self.filePrefix = os.path.splitext(filename)[0]
        flag = 0
        self.WALL = []
        self.BALL = []
        self.CurrentStep = 0
        self.BallNum = 0
        ""
        ZDEM_File = open(self.filepath, 'r')
        for line in ZDEM_File:  # 逐行读取文件
            if "current_step" in line:  # 当前所在步数
                step = line.split()  # 将该行（list）以空格“ ”进行切片
                self.CurrentStep = step[-1]  # 取step的最后一个元素作为步数

            if "ball num" in line:  # 获取颗粒个数
                ball_num = line.split()
                self.BallNum = ball_num[-1]

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
                self.WALL.append(wall)  # wall两点p1、p2的x、y坐标
            if flag == 2:
                ball = line.split()  # 将该行（list）以空格“ ”进行切片
                ball = [float(i) for i in ball[2:6]]
                self.BALL.append(ball)  # ball的x、y坐标以及半径、颜色
        del self.WALL[-1]  # 删除最后的空行
        del self.BALL[-1]  # 删除最后的空行
        ZDEM_File.close()  # 关闭对象，避免占用过多资源
        # 转换为numpy数组
        self.WALL, self.BALL, self.CurrentStep = np.array(
            self.WALL), np.array(self.BALL), np.array(self.CurrentStep)
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
        self.BALL_x = self.BALL[:, 0]
        self.BALL_y = self.BALL[:, 1]
        self.BALL_r = self.BALL[:, 2]
        self.BALL_c = self.BALL[:, 3]
        self.WALL_P1_x = self.WALL[4:7, 0]
        self.WALL_P1_y = self.WALL[4:7, 1]
        self.WALL_P2_x = self.WALL[4:7, 2]
        self.WALL_P2_y = self.WALL[4:7, 3]
        # 进行偏移量修改
        for i in range(len(self.WALL_P1_x)):
            self.WALL_P1_x[i] = self.WALL_P1_x[i] + self.xmove
            self.WALL_P1_y[i] = self.WALL_P1_y[i] + self.ymove
            self.WALL_P2_x[i] = self.WALL_P2_x[i] + self.xmove
            self.WALL_P2_y[i] = self.WALL_P2_y[i] + self.ymove
        for i in range(len(self.BALL_x)):
            self.BALL_x[i] = self.BALL_x[i] + self.xmove
            self.BALL_y[i] = self.BALL_y[i] + self.ymove
        
        # self.begin_plot_signal.emit(id)  # 发送信号：开始绘图

        self.ball_c = []  # 颜色 #xxxxxx格式
        for i in range(len(self.BALL_x)):
            color_num = self.BALL_c[i]
            color_num = int(color_num)
            ballColor = ZDEMColor_code[color_num]
            self.ball_c.append(ballColor)

    def plot_circle(self,id):
        """
        使用QGraphicsEllipseItem绘制圆

        Args:
            id ([type]): [description]
        """
        self.plot_axis()
        circle_list = []
        wall_list = []
        
        # 颗粒
        for i in range(len(self.BALL_x)):
            x = self.BALL_x[i]
            y = self.BALL_y[i]
            r = self.BALL_r[i]
            color = self.ball_c[i]
            circle = pg.QtGui.QGraphicsEllipseItem(x - r, y - r, 2 * r, 2 * r)
            circle.setPen(pg.mkPen(color=color,width=0))
            circle.setBrush(pg.mkBrush(color))
            circle_list.append(circle)
            self.plot_widget.addItem(circle)
        # self.updata_pg_circle_signal.emit(circle_list)
        # 绘制墙
        if (self.wallShow == True):
            for n in range(len(self.WALL_P1_x)):
                p1x = self.WALL_P1_x[n]
                p1y = self.WALL_P1_y[n]
                p2x = self.WALL_P2_x[n]
                p2y = self.WALL_P2_y[n]
                p12x = [p1x, p2x]
                p12y = [p1y, p2y]
                # plot_wall_item = pg.PlotItem(x=p12x,y=p12y,pen=pg.mkPen(width=3,color='k'))
                self.plot_widget.plot(x=p12x,y=p12y,pen=pg.mkPen(width=3,color='k'))  #线条粗细为2
                # wall_list.append(plot_wall_item)
        # self.updata_pg_wall_signal.emit(wall_list)
        # 发送信号，绘图结束
        self.updata_progressbar_signal.emit(id)



    def plot_scatter(self,id):

        self.plot_axis()
        self.plot_item = pg.ScatterPlotItem(
                    size=5,            
                    pen=pg.mkPen(None),
                    )   
        self.plot_item.addPoints(
                                x=self.BALL_x,
                                y=self.BALL_y,
                                brush=self.ball_c
                                )
        self.plot_widget.addItem(self.plot_item)
        # 绘制墙
        if (self.wallShow == True):
            for n in range(len(self.WALL_P1_x)):
                p1x = self.WALL_P1_x[n]
                p1y = self.WALL_P1_y[n]
                p2x = self.WALL_P2_x[n]
                p2y = self.WALL_P2_y[n]
                p12x = [p1x, p2x]
                p12y = [p1y, p2y]
                self.plot_widget.plot(x=p12x,y=p12y,pen=pg.mkPen(width=2))  #线条粗细为2
        # 发送信号，绘图结束
        self.updata_progressbar_signal.emit(id)

        
    def plot_axis(self):
        
        if (self.xmin == None) & (self.xmax == None) & (self.ymin == None) & (self.ymax == None):  # 若未传入min、max参数，进行计算
            # 计算xmax、ymax
            b_xmax = max(self.BALL_x)
            b_ymax = max(self.BALL_y)
            w_p1_xmax = max(self.WALL_P1_x)
            w_p2_xmax = max(self.WALL_P2_x)
            w_p1_ymax = max(self.WALL_P1_y)
            w_p2_ymax = max(self.WALL_P2_y)
            w_xmax = max(w_p1_xmax, w_p2_xmax)
            w_ymax = max(w_p1_ymax, w_p2_ymax)
            self.xmax = max(b_xmax, w_xmax)
            self.ymax = max(b_ymax, w_ymax)
            # 计算xmin、ymin
            b_xmin = min(self.BALL_x)
            b_ymin = min(self.BALL_y)
            w_p1_xmin = min(self.WALL_P1_x)
            w_p2_xmin = min(self.WALL_P2_x)
            w_p1_ymin = min(self.WALL_P1_y)
            w_p2_ymin = min(self.WALL_P2_y)
            w_xmin = min(w_p1_xmin, w_p2_xmin)
            w_ymin = min(w_p1_ymin, w_p2_ymin)
            self.xmin = min(b_xmin, w_xmin)
            self.ymin = min(b_ymin, w_ymin)
        self.plot_widget.setXRange(self.xmin, self.xmax,padding=0)
        self.plot_widget.setYRange(self.ymin, self.ymax,padding=0)
        self.plot_widget.showAxis('right')
        self.plot_widget.showAxis('top')
        