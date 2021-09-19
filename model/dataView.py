# -*- coding: utf-8 -*-
# 2021/07/9
# author:钟军
# e-mail:junzhong0917@163.com
import os
import time

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QTableView, QAbstractItemView, QMenu, QFrame, QHeaderView
from PyQt5.QtCore import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QCursor, QIcon
from model.Thread import PlotThread, PlotAllThread_test, manager_Pool, pg_plot_thread
from model.canvas import MplWidget, pyqtgraph_widget


class FileSystemTableView(QTableView):
    """
    继承：QTableView
    文件管理器类，实现文件列表、右键绘图入口
    """

    def __init__(self, parent=None, uiMain=None):
        """

        :param parent:
        :param uiMain:
        """
        super().__init__(parent=parent)
        self.myUi = uiMain
        self.mainwind = parent
        # plotOBJ = self.myUi.plotObj
        self.qcanvas = None
        self.setStyleSheet(("QTableView{\n"
                                          "     border-color: rgb(223,223,223);\n"
                                          "     border-radius: 9px;\n"
                                          "}"))
        self.tabWidget = self.myUi.mainWidgetsObj.tabWidget
        self.myModel = self.createModel(self)  # 设置模型
        self.setModel(self.myModel)  # 给QTableView添加模型
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.setColumnWidth(0, 200)  # 行宽
        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 180)
        
        self.setMaximumWidth(230)
        # self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.resizeColumnsToContents()
        self.setFrameShape(QFrame.NoFrame)  # 边框类型为无边框
        # self.stackedWidget = self.myUi.mainWidgetsObj.stackedWidget  # stackedWidget对象
        # 添加右键菜单
        self.setContextMenuPolicy(
            Qt.CustomContextMenu)  # 右键菜单，如果不设为CustomContextMenu,无法使用customContextMenuRequested
        self.customContextMenuRequested.connect(self.contextMenuEvent)
        self.canvas_fluent_count = 1  # 画布刷新的计数标志

    def createModel(self, parent):
        """

        创建模型
        :param parent:
        :return:
        """
        model = QStandardItemModel(0, 2, parent)
        model.setHorizontalHeaderLabels(['状态', '文件名'])
        return model

    def addData(self, model, FileNameList, folderDir):
        """

        将文件添加到tableview，并初始化画布、进度条，创建线程池
        :param model:
        :param FileNameList:
        :param folderDir:
        :return:
        """
        row = 0  # 行数，等于文件数
        self.lst_checkBox = []  # 存放复选框变量
        self.mplWidget_list = []  # matplotlib类对象列表
        self.FileNameList = FileNameList  # 文件名
        self.folderDir = folderDir  # 文件夹目录
        for filename in FileNameList:  # 初始化模型model数据，插入文件名
            model.insertRow(row)
            model.setData(model.index(row, 1), filename)
            row = row + 1
        for i in range(row):
            item_checked = QStandardItem()
            item_checked.setCheckState(Qt.Checked)
            item_checked.setCheckable(True)
            model.setItem(i, 0, item_checked)
            self.lst_checkBox.append(item_checked)  # 添加到列表中
        # 创建一个管理线程池的Qthread对象
        self.poolManager = manager_Pool(row)

    def contextMenuEvent(self, pos):
        """

        右键菜单
        :param pos:
        :return:
        """
        self.contextMenu = QMenu()
        self.action_pgPlot_point = self.contextMenu.addAction(
            QIcon("./icons/logo.ico"), u'| 使用PyqtGraph绘制散点图')
        self.action_pgPlot_circle = self.contextMenu.addAction(
            QIcon("./icons/logo.ico"), u'| 使用PyqtGraph绘制圆图')
        self.action_plotCircle = self.contextMenu.addAction(
            QIcon("./icons/plot.ico"), u'| 使用matplotlib绘制二维圆图')
        self.action_plotPoint = self.contextMenu.addAction(
            QIcon("./icons/plotPoint.png"), u'| 使用matplotlib绘制散点图')
        self.action_clear_dataView = self.contextMenu.addAction(
            QIcon("./icons/clear.ico"), u'| 清除数据与图像')
        self.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
        self.action_plotCircle.triggered.connect(self.plotAllSlot_circle)
        self.action_plotPoint.triggered.connect(self.plotAllSlot_point)
        ballStyle_point = 'point'
        ballStyle_circle = 'circle'
        self.action_pgPlot_point.triggered.connect(self.pg_plot_point)
        self.action_pgPlot_circle.triggered.connect(self.pg_plot_circle)

        font = QtGui.QFont()
        font.setFamily("黑体")
        font.setPointSize(10)
        font.setBold(True)
        self.action_pgPlot_point.setFont(font)
        self.action_pgPlot_circle.setFont(font)
        self.action_clear_dataView.triggered.connect(self.clear_dataView)
        self.contextMenu.show()

    def plotSlot(self, row):
        """

        绘图单图，主线程实例化类对象，开辟子线程画图，主线程刷新画布（否则卡）
        :param row:
        :return:
        """
        select_filePath = os.path.join(
            self.folderDir, self.FileNameList[row])  # 选择的文件的绝对路径
        # 开启一个子线程，进行数据读取和绘图。注意到这里是先创建了绘图类的实例化对象，子线程执行相应的方法。
        self.newPlotThread = PlotThread(
            self.plotOBJ, self.qcanvas, select_filePath)
        self.newPlotThread.start()

    def pg_plot(self):
        """
        绘制全部，全部在一个线程中————————弃用！
        :param row:
        :return:
        """
        
        self.init_tableWidget_pg()
        self.filePathList = []
        for i in range(len(self.list_select_files)):
            filePath = os.path.join(self.folderDir, self.list_select_files[i])
            self.filePathList.append(filePath)
        self.pgPlotThread = pg_plot_thread(self.pgWidgetList, self.filePathList, self.myUi,paramList=None)
        self.pgPlotThread.start()

    def pg_setThread(self,ballstyle):

        self.init_tableWidget_pg()
        self.absulotePathList = []
        print('开始创建对象')
        for i in range(len(self.list_select_files)):  # 循环创建多个线程对象，添加到线程池
            filePath = os.path.join(self.folderDir, self.list_select_files[i])
            self.absulotePathList.append(filePath)
            PlotALLThread = PlotThread(
                self.pgWidgetList[i], filePath, self.myUi, i, ballstyle,None,'pyqtgraph')
            self.poolManager.addThread(PlotALLThread)  # 添加到线程池
            PlotALLThread.autoDelete()  # 线程执行完毕自动删除
        self.poolManager.start()  # 所有的绘图子线程已经添加到线程池，start开启执行

        # self.ThreadPool.waitForDon()  # 等待任务执行完毕。！！！添加这行代码会导致界面卡死
        print('线程已经全部加入线程池！！！！！！！')
        self.myUi.ProgressBar.statusLabel.setText("绘图中，请稍后...")






    def plotAllSlot_2(self, row):
        """

        绘制全部方法2，每张图开辟一个QThread子线程，储存在线程类对象数组中，通过循环依次start
        :param row:
        :return:
        """
        self.myUi.mainWidgetsObj.select_comBox.addItems(self.FileNameList)
        threads = []
        for i in range(len(self.FileNameList)):
            filePath = os.path.join(
                self.folderDir, self.FileNameList[i])  # 拼接成绝对路径
            # self.filePath.append(filePath)
            PlotALLThread = PlotAllThread_test(
                self.mplWidget_list[i], filePath, self.myUi, i)
            PlotALLThread.plotObj_test.updata_canvas_signal.connect(
                self.updataCanvas)
            threads.append(PlotALLThread)
        for t in threads:
            t.start()
            print('线程' + str(t) + '已开启')

    def plotAllSlot_3(self, row):
        """

        绘制全部图方法3：采取线程池实现多线程（QRunable类）绘图。这种方法会造成界面卡死！！！
        :param row:
        :return:
        """
        self.myUi.mainWidgetsObj.select_comBox.addItems(
            self.FileNameList)  # 初始化文件选择下拉框控件
        # 创建线程池，并设置最大线程数
        self.ThreadPool = QThreadPool()
        self.ThreadPool.globalInstance()  # 全局线程池
        self.ThreadPool.setMaxThreadCount(row)  # 设置最大线程数，等于文件数
        for i in range(len(self.FileNameList)):  # 循环创建多个线程对象，添加到线程池开启子线程
            filePath = os.path.join(self.folderDir, self.FileNameList[i])
            # PlotALLThread = PlotAllThread_test2(self.mplWidget_list[i], filePath, self.myUi, i)
            # PlotALLThread.plotObj_test.updata_canvas_signal.connect(self.updataCanvas)
            # self.ThreadPool.start(PlotALLThread)
        # self.ThreadPool.waitForDone()  # 等待任务执行完毕。！！！添加这行代码会导致界面卡死

    def Get_checkFile(self):
        """获取当前选择的文件

        Returns:
            [type]: 当前选择的文件列表
        """
        if self.FileNameList == None:
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, '警告', '请导入文件')
            msg_box.exec_()
        else:
            list_selcetFiles = []
            self.list_filesID = []
            for i in range(len(self.lst_checkBox)):
                if (self.lst_checkBox[i].checkState() == Qt.Checked):
                    list_selcetFiles.append(self.FileNameList[i])
                    self.list_filesID.append(i + 1)
            return list_selcetFiles

    def plotAllSlot(self, ballStyle):
        """
        绘制全部图方法4：
        采用单独的Qthread线程专门管理线程池对象,然后采取类似方法3线程池实现多线程绘图
        TODO：目前还是会造成多线程绘图时GUI界面卡死

        :param str ballStyle:
        :return:
        """
        self.absulotePathList = []
        self.init_tableWidget()
        print('定时器开始')
        self.timer = QTimer()  # 初始化一个定时器
        self.timer.singleShot(5000, lambda: self.setThread(ballStyle))
        print('定时器结束')
        # self.list_select_files = self.Get_checkFile()
        # canvasWidgets_list, self.mplWidget_list = self.init_tableWidget(len(self.list_select_files))  # 初始化tablewidget的界面，即创建row个画布对象
        # self.myUi.mainWidgetsObj.select_comBox.addItems(self.list_select_files)  # 初始化文件选择下拉框控件
        # 创建线程池，并设置最大线程数

    def setThread(self, ballStyle):

        print('开始创建对象')
        for i in range(len(self.list_select_files)):  # 循环创建多个线程对象，添加到线程池
            filePath = os.path.join(self.folderDir, self.list_select_files[i])
            self.absulotePathList.append(filePath)
            PlotALLThread = PlotThread(
                self.mplWidget_list[i], filePath, self.myUi, i, ballStyle,'matplotlib')
            PlotALLThread.plot_object.updata_canvas_signal.connect(
                self.updataCanvas)
            PlotALLThread.plot_object.begin_plot_signal.connect(
                self.beginPlot_labelupdata)
            self.poolManager.addThread(PlotALLThread)  # 添加到线程池
            PlotALLThread.autoDelete()  # 线程执行完毕自动删除
        self.poolManager.start()  # 所有的绘图子线程已经添加到线程池，start开启执行

        # self.ThreadPool.waitForDon()  # 等待任务执行完毕。！！！添加这行代码会导致界面卡死
        print('线程已经全部加入线程池！！！！！！！')
        self.myUi.ProgressBar.statusLabel.setText("绘图中，请稍后...")

    def plotAllSlot_point(self):
        """

        绘制点图
        :param row:
        :return:
        """
        self.plotAllSlot('point')

    def plotAllSlot_circle(self):
        """

        绘制二维圆图
        :param row:
        :return:
        """
        self.plotAllSlot('circle')

    def pg_plot_point(self):
        self.pg_setThread('point')

    def pg_plot_circle(self):
        self.pg_setThread('circle')


    def init_tableWidget(self):
        """

        初始化tablewidget界面，创建num个canvas画布对象
        :param num:
        :return:
        """
        self.tabWidget.clear()
        widgetsObj_list = []
        self.mplWidget_list = []
        self.QCanvas_list = []
        self.list_select_files = self.Get_checkFile()
        num = len(self.list_select_files)
        for i in range(num):
            tab = QtWidgets.QWidget()
            tab.setObjectName(str(i))
            verticalLAYOUT = QtWidgets.QVBoxLayout(tab)
            verticalLAYOUT.setObjectName('verticalLAYOUT' + str(num))
            canvas_widget = QtWidgets.QWidget(tab)
            canvas_widget.setObjectName('canvas_Widget' + str(num))
            verticalLAYOUT.addWidget(canvas_widget)
            filePrefix = os.path.splitext(self.list_select_files[i])[0]
            mpl_widget = MplWidget(canvas_widget, filePrefix)
            verticalLAYOUT2 = QtWidgets.QVBoxLayout(canvas_widget)
            verticalLAYOUT2.setObjectName('verticalLAYOUT' + str(num))
            verticalLAYOUT2.addWidget(mpl_widget)
            self.tabWidget.addTab(tab, '编号：' + str(self.list_filesID[i]))
            widgetsObj_list.append(canvas_widget)
            self.mplWidget_list.append(mpl_widget)
            self.QCanvas_list.append(mpl_widget.qCanvas)
            widgetNum = self.tabWidget.count()
            print("第" + str(widgetNum) + "个画布控件已创建")
        self.myUi.ProgressBar.setBar_plotAll(
            len(self.list_select_files))  # 初始化进度条
        self.myUi.mainWidgetsObj.select_comBox.addItems(
            self.list_select_files)  # 初始化文件选择下拉框控件


    def init_tableWidget_pg(self):
        """
        TODO:创建pyqtgraph部件
        初始化tablewidget界面，创建num个canvas画布对象
        :param num:
        :return:
        """
        self.tabWidget.clear()
        widgetsObj_list = []
        self.QWidget_list = []
        self.pgWidgetList = []
        self.QCanvas_list = []
        self.list_select_files = self.Get_checkFile()
        num = len(self.list_select_files)
        for i in range(num):
            tab = QtWidgets.QWidget()
            tab.setObjectName(str(i))
            verticalLAYOUT = QtWidgets.QVBoxLayout(tab)
            verticalLAYOUT.setObjectName('verticalLAYOUT' + str(num))
            verticalLAYOUT.setContentsMargins(0,0,0,0)
            #
            pg_mainWidget = QtWidgets.QWidget(tab)
            pg_mainWidget.setObjectName('canvas_Widget' + str(num))
            pg_mainLayout = QtWidgets.QVBoxLayout(pg_mainWidget)
            pg_mainLayout.setObjectName('pg_mainLayout')
            pg_mainLayout.setContentsMargins(0,0,0,0)
            verticalLAYOUT.addWidget(pg_mainWidget)
            # 
            pg_widget = pyqtgraph_widget(pg_mainWidget)
            pg_mainLayout.addWidget(pg_widget)
            #
            self.tabWidget.addTab(tab, '编号：' + str(self.list_filesID[i]))
            
            # widgetsObj_list.append(canvas_widget)
            self.QWidget_list.append(pg_widget)
            self.pgWidgetList.append(pg_widget.plot_widget)
            # self.QCanvas_list.append(mpl_widget.qCanvas)
            widgetNum = self.tabWidget.count()
            print("第" + str(widgetNum) + "个绘图控件已创建")
        self.myUi.ProgressBar.setBar_plotAll(
            len(self.list_select_files))  # 初始化进度条
        self.myUi.mainWidgetsObj.select_comBox.addItems(
            self.list_select_files)  # 初始化文件选择下拉框控件

    def clear_dataView(self):
        """清空文件管理器
        """
        self.myModel.removeRows(0,self.myModel.rowCount())  # 删除所有行
        self.tabWidget.clear()  # 清空绘图区窗口

    def updataCanvas(self, id):
        """

        在主线程刷新matplotlib画布canvas，若在子线程刷新会造成短暂卡顿！！！
        :param id:
        :return:
        """
        # self.mplWidget_list[id].qCanvas.figs.canvas.draw()  # 这里注意是画布重绘，figs.canvas
        # self.mplWidget_list[id].qCanvas.figs.canvas.flush_events()  # 刷新画布
        print('画布' + str(id + 1) + '已刷新')
        self.myUi.ProgressBar.updataBar_plotAll(id)
        # 状态栏label信息显示 x/x
        if self.canvas_fluent_count != len(self.list_select_files):
            self.myUi.ProgressBar.plotAllLabel.setText(
                "画布刷新中..." + str(self.canvas_fluent_count) + '/' + str(len(self.list_select_files)))
            self.canvas_fluent_count = self.canvas_fluent_count + 1
        else:
            self.myUi.ProgressBar.plotAllLabel.setText("画布刷新完成！")
            self.canvas_fluent_count = 1

    def beginPlot_labelupdata(self, id):
        """
        信息传递：线程开始画布
        :param id:
        :return:
        """
        self.myUi.ProgressBar.beginPlotLabel.setText(
            '线程' + str(id + 1) + '开始绘图')
        print('线程' + str(id + 1) + '开始绘图')
