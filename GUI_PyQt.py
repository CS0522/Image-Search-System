"""
@Author: Chen Shi
"""

import sys
from PyQt5 import uic
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from functools import partial

from Service.ShowPicWidget import ShowPicWidget

from Pretreatment.ColorHSV import PreColorHSV
from Pretreatment.GreyMatrix import PreGreyMatrix
from Pretreatment.ShapeHistogram import PreShapeHist
from Pretreatment.ShapeNchange import PreShapeNchange

# 存储在 Repository 里的 data_filename
colorHSV_data = "ColorHSVData"
greyMatrix_data = "GreyMatrixData"
shapeHist_data = "ShapeHistogramData"
shapeNchange_data = "ShapeNchangeData"

# 建立字典
data_file_dict = {"1": colorHSV_data, "2": greyMatrix_data,
                  "3": shapeHist_data, "4": shapeNchange_data}


class ImageSearchSystemWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.method = 0

        self.currentProgress = 0
        self.progressing = "Pretreating...... " + str(self.currentProgress) + "/4"
        self.progress_finish = "Success!"
        self.lbl_progress = QLabel("")

        self.btn_preTreat = QPushButton("Pretreat")

        self.thread1 = ColorHSVThread()
        self.thread2 = GreyMatrixThread()
        self.thread3 = ShapeHistThread()
        self.thread4 = ShapeNchangeThread()
        
        # 绑定线程内信号与函数
        self.thread1.colorHSV_finish_signal.connect(self.change_lbl_progress)
        self.thread2.greyMatrix_finish_signal.connect(self.change_lbl_progress)
        self.thread3.shapeHist_finish_signal.connect(self.change_lbl_progress)
        self.thread4.shapeNchange_finish_signal.connect(self.change_lbl_progress)

        self.setUi()

    
    # 修改 lbl_progress 文本的函数
    def change_lbl_progress(self):
        self.currentProgress += 1
        # 都结束，显示 success
        if (self.currentProgress == 4):
            self.lbl_progress.setText(self.progress_finish)
            self.currentProgress = 0
            # btn_preTreat 还原
            self.btn_preTreat.setEnabled(True)
            self.btn_preTreat.setText("Pretreat")

        else:
            self.progressing = "Pretreating...... " + str(self.currentProgress) + "/4"
            self.lbl_progress.setText(self.progressing)

    # 设置 UI 界面
    def setUi(self):
        # create new button
        btn_HSV = QPushButton("Search by Color: HSV")
        btn_greyMatrix = QPushButton("Search by Texture: Grey Matrix")
        btn_histogram = QPushButton("Search by Shape: Histogram")
        btn_Nchange = QPushButton("Search by Shape: No Change")

        # create label
        lbl_name = QLabel("Content Based Image Search System")
        lbl_name.setAlignment(QtCore.Qt.AlignHCenter)

        # connect to slot function
        btn_HSV.clicked.connect(partial(self.getImageFileAndInputThreshold, 1))
        btn_greyMatrix.clicked.connect(partial(self.getImageFileAndInputThreshold, 2))
        btn_histogram.clicked.connect(partial(self.getImageFileAndInputThreshold, 3))
        btn_Nchange.clicked.connect(partial(self.getImageFileAndInputThreshold, 4))
        
        self.btn_preTreat.clicked.connect(self.preTreat)

        # create layout
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(btn_HSV)
        self.vlayout.addStretch(1)
        self.vlayout.addWidget(btn_greyMatrix)
        self.vlayout.addStretch(1)
        self.vlayout.addWidget(btn_histogram)
        self.vlayout.addStretch(1)
        self.vlayout.addWidget(btn_Nchange)
        self.vlayout.addStretch(2)
        self.vlayout.addWidget(self.lbl_progress)
        self.vlayout.addWidget(self.btn_preTreat)
        self.vlayout.addStretch(2)
        self.vlayout.addWidget(lbl_name)
        self.setLayout(self.vlayout)

        # set window attribute
        # set window title
        self.setWindowTitle("Image Search System")
        # set window size
        self.resize(350, 375)
        self.setMinimumSize(300, 300)
        self.setMaximumSize(400, 450)
        # no maximum button
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

    # 获取图片
    def getImageFileAndInputThreshold(self, method):
        self.method = method
        # 获取 image 文件路径
        """
        getOpenFileName(): 返回值是一个 pair，第一个是路径，第二个是过滤器
        第一个参数: 用于指定父组件
        第二个参数: QFileDialog 对话框标题
        第三个参数: 指定打开的路径
        第四个参数: 文件扩展名过滤器
        """
        self.image_file,_ = QFileDialog.getOpenFileName(self, "Choose an image file", 
                                                        "./test_imgs", "Image Files (*.jpg *.png)")
        # 未读取到文件
        if (len(self.image_file) == 0):
            return
        
        # 输入调整参数
        self.input_threshold_dialog = InputThresHoldDialog(self.method)
        # bind signal
        self.input_threshold_dialog.accept_signal.connect(self.do_accept)
        self.input_threshold_dialog.reject_signal.connect(self.do_reject)
        
        self.input_threshold_dialog.show()

    # reject signal
    def do_reject(self):
        self.input_threshold_dialog.close()

    # accept signal 
    def do_accept(self, loss_threshold):
        self.searchImg(loss_threshold, self.method)

    # search
    def searchImg(self, loss_threshold, method):
        self.input_threshold_dialog.close()
        self.show_pic_widget = ShowPicWidget(loss_threshold)
        self.show_pic_widget.set_img_and_data_file(self.image_file, data_file_dict[str(method)])
        self.show_pic_widget.search_process(method)
        # self.show_pic_widget.show()
    
    # 修改全局变量 data_filename
    def setDataFilename(self, method, new_filename):
        if (method == 1):
            colorHSV_data = new_filename
        elif (method == 2):
            greyMatrix_data = new_filename
        elif (method == 3):
            shapeHist_data = new_filename
        elif (method == 4):
            shapeNchange_data = new_filename
        
        # 更新字典
        data_file_dict[str(method)] = new_filename


    # 执行预处理
    # 尝试多线程同时执行
    def preTreat(self):
        # lbl_progress 标签进行更新
        self.lbl_progress.setText(self.progressing)
        # 更新 btn_preTreat
        self.btn_preTreat.setText("Preteating")
        self.btn_preTreat.setEnabled(False)

        self.thread1.start()
        self.thread2.start()
        self.thread3.start()
        self.thread4.start()



# 定义多个线程类
class ColorHSVThread(QThread):
    # finish signal
    colorHSV_finish_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def run(self):
        print("ColorHSV is running")
        pre_thread = PreColorHSV(colorHSV_data)
        print("ColorHSV is over")
        # emit signal
        self.colorHSV_finish_signal.emit(True)


class GreyMatrixThread(QThread):
    # finish signal
    greyMatrix_finish_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def run(self):
        print("GreyMatrix is running")
        pre_thread = PreGreyMatrix(greyMatrix_data)
        print("GreyMatrix is over")
        self.greyMatrix_finish_signal.emit(True)


class ShapeHistThread(QThread):
    # finish signal
    shapeHist_finish_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def run(self):
        print("ShapeHist is running")
        pre_thread = PreShapeHist(shapeHist_data)
        print("ShapeHist is over")
        self.shapeHist_finish_signal.emit(True)


class ShapeNchangeThread(QThread):
    # finish signal
    shapeNchange_finish_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def run(self):
        print("ShapeNchange is running")
        pre_thread = PreShapeNchange(shapeNchange_data)
        print("ShapeNchange is over")
        self.shapeNchange_finish_signal.emit(True)


class InputThresHoldDialog(QWidget):
    # define two sginals
    accept_signal = pyqtSignal(float)
    reject_signal = pyqtSignal()

    def __init__(self, method):
        super().__init__()
        self.method = method
        self.setUi()

        # 设置窗口属性
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        # 设置禁止拉伸
        # self.setFixedSize(self.width(), self.height())
        # 设置窗口置顶
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        # 关闭后立即销毁
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def setUi(self):
        lbl_threshold = QLabel("Input loss threshold: ")
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("(0.0, 10.0]")
        
        # set default loss threshold
        if (self.method == 1):
            self.line_edit.setText(str(3.0))
        elif (self.method == 2):
            self.line_edit.setText(str(0.5))
        elif (self.method == 3):
            self.line_edit.setText(str(10.0))
        elif (self.method == 4):
            self.line_edit.setText(str(5.0))

        self.btn_dialog = QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        # bind signal
        self.btn_dialog.accepted.connect(self.do_accept)
        self.btn_dialog.rejected.connect(self.do_reject)

        group_box_input = QGroupBox()
        group_box_btnbox = QGroupBox()

        hlayout1 = QHBoxLayout()
        hlayout2 = QHBoxLayout()
        vlayout = QVBoxLayout()

        hlayout1.addWidget(lbl_threshold)
        hlayout1.addWidget(self.line_edit)
        hlayout2.addStretch()
        hlayout2.addWidget(self.btn_dialog)
        
        group_box_input.setLayout(hlayout1)
        group_box_btnbox.setLayout(hlayout2)
        group_box_input.setStyleSheet("QGroupBox{border: none}")
        group_box_btnbox.setStyleSheet("QGroupBox{border: none}")
        
        vlayout.addWidget(group_box_input)
        vlayout.addWidget(group_box_btnbox)

        self.setLayout(vlayout)

    # 发送 accept 信号
    def do_accept(self):
        # 先检查输入是否合规
        if (float(self.line_edit.text()) <= 0 or float(self.line_edit.text()) > 10):
            QMessageBox.information(self, "Invalid Input", "Plz input right value!")
            return
        
        self.accept_signal.emit(float(self.line_edit.text()))
    
    # 发送 reject 信号
    def do_reject(self):
        self.reject_signal.emit()


# main
if __name__ == "__main__":
    app = QApplication(sys.argv)

    ui = ImageSearchSystemWindow()
    ui.show()
    
    app.exec_()