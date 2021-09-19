
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QThreadPool, QRunnable, QObject
from model import plot


class _PlotThread(QThread):
    """
    绘制单图线程，注意是已经在主线程实例化绘图类对象
    """
    updata_fig = pyqtSignal(int)

    def __init__(self, plotObject=None, canvasObject=None, filename=None):
        """

        :param plotObject:
        :param canvasObject:
        :param filename:
        """
        super().__init__()
        self.plotObject = plotObject
        self.canvasObject = canvasObject
        self.filename = filename

    def run(self):
        """

        :return:
        """
        self.plotObject.readData(self.filename)
        self.plotObject.plotJPG(self.canvasObject)
        print("plot success!!!")


class pg_plot_thread(QThread):
    """

    """
    updata_fig = pyqtSignal(int)

    def __init__(self, pg_Widgets_list=None, filePathList=None, myUi=None,paramList=None):
        """

        :param plotAllObj:
        :param canvasWidgets_list:
        :param filePath:
        :param myUi:
        """
        super().__init__()
        
        self.pg_Widgets_list = pg_Widgets_list
        self.myUi = myUi
        self.filePathList = filePathList
        if (paramList == None):  # 未传入参数表时使用默认参数表
            self.paramList = [0.0, 0.0, None, None, None, None, '', True, 0.8, 'ZDEMColor', '', 12, '', 9, '', 9,
                              10000.0, 1000.0, True, True, True, True, 1000]
            self.paramList[6] = 'point'
        else:
            self.paramList = paramList  # 接收参数表
        


    def run(self):
        """
        BUG:QObject::startTimer: Timers cannot be started from another thread
        :return:
        """
        for i in range(len(self.pg_Widgets_list)):
            plot_obj = plot.pg_plot(self.paramList,self.pg_Widgets_list[i],self.filePathList[i])
            plot_obj.updata_progressbar_signal.connect(self.myUi.ProgressBar.updataBar_plotAll_pg)
            plot_obj.updata_pg_circle_signal.connect(self.myUi.dataView.QWidget_list[i].update_circle)
            plot_obj.updata_pg_wall_signal.connect(self.myUi.dataView.QWidget_list[i].update_circle)
            plot_obj.readData()
            plot_obj.plot_circle(id=i)
            # plot_obj.plot_scatter(id=i)
            self.myUi.ProgressBar.plotAllLabel.setText('  已完成' + str(i + 1) + '/' + str((len(self.pg_Widgets_list))) + '  ')
            print('  已完成' + str(i + 1) + '/' + str((len(self.pg_Widgets_list))) + '  ')
        print("all success!!!!!!!!!!!!!!!!")
        

# 每个绘图开一个线程
Qclock = QMutex()  # Qt线程锁


class PlotAllThread_test(QThread):
    """
    每张图开辟一个QThread子线程(在子线程实例化绘图类对象，线程结束后释放资源)，储存在线程类对象数组中，通过循环依次start
    """
    updata_fig = pyqtSignal(int)

    def __init__(self, canvasWidgets=None, fileName=None, myUi=None, id=None):
        """

        :param canvasWidgets:
        :param fileName:
        :param myUi:
        :param id:
        """
        super().__init__()
        self.canvasWidgets = canvasWidgets
        self.fileName = fileName
        self.myUi = myUi
        self.id = id
       #self.plotObj_test = plot.plotAll(self.myUi.mainWidgetsObj.stackedWidget)

    def run(self):
        """

        :return:
        """
        # Qclock.lock()
        self.plotObj_test.readData(self.fileName)
        self.plotObj_test.plotJPG(self.canvasWidgets, self.id)
        print(str(id) + ("plot success!"))
        # Qclock.unlock()


# QRunnable只是namespace,没有继承QT的信号机制,所以需要另外继承QObject来使用信号
class Signal(QObject):
    """
    将qt信号进行封装
    """
    updata_canvas_signal = pyqtSignal(int)


class PlotThread(QRunnable):
    """

    """

    def __init__(self, Widgets=None, fileName=None, myUi=None, id=None, ballStyle=None, paramList=None,plot_way = None):
        """

        :param Widgets:
        :param fileName:
        :param myUi:
        :param id:
        """
        super().__init__()
        self.Widgets = Widgets
        self.fileName = fileName
        self.myUi = myUi
        self.id = id
        self.plot_way = plot_way
        if (paramList == None):  # 未传入参数表时使用默认参数表
            self.paramList = [0.0, 0.0, None, None, None, None, '', True, 0.8, 'ZDEMColor', '', 12, '', 9, '', 9,
                              10000.0, 1000.0, True, True, True, True, 1000]
            self.paramList[6] = ballStyle
        else:
            self.paramList = paramList  # 接收参数表
        if self.plot_way == 'matplotlib':
            self.plot_object = plot.Plot(self.paramList, self.Widgets, self.fileName)
        if self.plot_way == 'pyqtgraph':
            self.plot_object = plot.pg_plot(self.paramList, self.Widgets, self.fileName)
            self.plot_object.updata_progressbar_signal.connect(self.myUi.ProgressBar.updataBar_plotAll_pg)
            self.plot_object.updata_pg_circle_signal.connect(self.myUi.dataView.QWidget_list[id].update_circle)
            self.plot_object.updata_pg_wall_signal.connect(self.myUi.dataView.QWidget_list[id].update_wall)
        self.signal = Signal()

    def run(self):
        """

        :return:
        """
        if self.plot_way == 'matplotlib':
            self.plot_object.readData()
            self.plot_object.plotJPG(self.id )
        if self.plot_way == 'pyqtgraph':
            self.plot_object.readData()
            if self.paramList[6] == 'circle':
                self.plot_object.plot_circle(self.id)
            if self.paramList[6] == 'point':
                self.plot_object.plot_scatter(self.id)
        print(str(self.id) + "plot success!")


class Thread_Pool(QObject):
    '''线程池类'''
    thread_list = []

    def __init__(self, max_thread_num):
        """

        :param max_thread_num:
        """
        super(Thread_Pool, self).__init__()
        # 创建线程池
        self.ThreadPool = QThreadPool()
        self.ThreadPool.globalInstance()  # 全局线程池
        self.ThreadPool.setMaxThreadCount(max_thread_num)  # 最大线程数

    def addThread(self, _thread):
        """

        :param _thread:
        :return:
        """
        self.thread_list.append(_thread)

    def Start(self):
        """

        :return:
        """
        for i in self.thread_list:
            self.ThreadPool.start(i)  # 遍历开启线程start

        #self.ThreadPool.waitForDone()  # 等待全部线程结束
        self.thread_list.clear()  # 清空


class manager_Pool(QThread):
    '''
    创建一个Qthread线程，单独管理线程池类Thread_Pool，否则会造成ui界面卡顿
    '''

    def __init__(self, maxThreadNum):
        """

        :param maxThreadNum:
        """
        super(manager_Pool, self).__init__()
        # 创建线程池类Tasks的实例对象，默认最大线程数为8线程
        self.threadPool = Thread_Pool(maxThreadNum)

    def run(self):
        '''
        启动线程池
        :return:
        '''
        self.threadPool.Start()

    def addThread(self, _thread):
        """

        :param _thread:
        :return:
        """
        self.threadPool.addThread(_thread)
