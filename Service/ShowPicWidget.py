import sys

from PyQt5 import uic
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import time

from Service.SearchbyColorHSV import SearchByColorHSV
from Service.SearchbyTextureGreyMatrix import SearchByTextureGreyMatrix
from Service.SearchbyShapeHist import SearchByShapeHist
from Service.SearchbyShapeNChange import SearchByShapeNChange

# from SearchbyColorHSV import SearchByColorHSV
# from SearchbyTextureGreyMatrix import SearchByTextureGreyMatrix
# from SearchbyShapeHist import SearchByShapeHist
# from SearchbyShapeNChange import SearchByShapeNChange

class ShowPicWidget(QWidget):
    input_img = ""
    data_file = ""
    # output 最多显示数目
    max_num = 20
    # 计时器
    # 单位: 毫秒 ms
    search_timer = 0.000

    def __init__(self, loss_threshold):
        super().__init__()
        print("initializing the output page......")
        # 字典 (键值对)
        # outputlist(name):outacc(loss)
        self.output_dict = {}
        # outputlist & outacc
        self.outputlist = []
        self.outacc = []
        # loss threshold
        self.loss_threshold = loss_threshold

        # 设置窗口属性
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        # 设置禁止拉伸
        # self.setFixedSize(self.width(), self.height())
        # 设置窗口置顶
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        # 关闭后立即销毁
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)


    # 设置图像文件
    def set_img_and_data_file(self, input_img, data_file):
        self.input_img = input_img
        self.data_file = data_file


    # 执行相应的检索方法
    """
    method: 用来判断是哪一个检索方法，实例化相应的类
    """
    def search_process(self, method):
        # SearchByColorHSV
        if (method == 1):   
            search_by_colorHSV = SearchByColorHSV(self.loss_threshold)
            search_by_colorHSV.set_content(self.input_img, self.data_file)
            # start time count
            time_start = time.perf_counter()

            search_by_colorHSV.process_func()

            # end time count
            time_end = time.perf_counter()
            # calculate time
            self.search_timer = (time_end - time_start) * 1000
            
            colorHSV_error = search_by_colorHSV.get_error()
            # 如果出现错误
            if (colorHSV_error != -1):
                if (colorHSV_error == 0):
                    QMessageBox.critical(self, "Error", "Data file not found!")
                elif (colorHSV_error == 1):
                    QMessageBox.critical(self, "Error", "The image is not in the database!")
                return
            # 没有出现错误，获取 outputlist & outacc
            self.outputlist, self.outacc = search_by_colorHSV.get_output()

        # SearchByGreyMatrix
        elif (method == 2):
            search_by_greyMatrix = SearchByTextureGreyMatrix(self.loss_threshold)
            search_by_greyMatrix.set_content(self.input_img, self.data_file)
            # start time count
            time_start = time.perf_counter()

            search_by_greyMatrix.process_func()

            # end time count
            time_end = time.perf_counter()
            # calculate time
            self.search_timer = (time_end - time_start) * 1000
            
            greyMatrix_error = search_by_greyMatrix.get_error()
            # 如果出现错误
            if (greyMatrix_error != -1):
                if (greyMatrix_error == 0):
                    QMessageBox.critical(self, "Error", "Data file not found!")
                elif (greyMatrix_error == 1):
                    QMessageBox.critical(self, "Error", "The image is not in the database!")
                return
            # 没有出现错误，获取 outputlist & outacc
            self.outputlist, self.outacc = search_by_greyMatrix.get_output()

        # SearchByShapeHist
        elif (method == 3):
            search_by_shapeHist = SearchByShapeHist(self.loss_threshold)
            search_by_shapeHist.set_content(self.input_img, self.data_file)
            # start time count 
            time_start = time.perf_counter()

            search_by_shapeHist.process_func()

            # end time count
            time_end = time.perf_counter()
            # calculate time
            self.search_timer = (time_end - time_start) * 1000
            
            shapeHist_error = search_by_shapeHist.get_error()
            # 如果出现错误
            if (shapeHist_error != -1):
                if (shapeHist_error == 0):
                    QMessageBox.critical(self, "Error", "Data file not found!")
                elif (shapeHist_error == 1):
                    QMessageBox.critical(self, "Error", "The image is not in the database!")
                return
            # 没有出现错误，获取 outputlist & outacc
            self.outputlist, self.outacc = search_by_shapeHist.get_output()

        # SearchByShapeNchange
        elif (method == 4):
            search_by_shapeNchange = SearchByShapeNChange(self.loss_threshold)
            search_by_shapeNchange.set_content(self.input_img, self.data_file)
            # start time count
            time_start = time.perf_counter()

            search_by_shapeNchange.process_func()

            # end time count
            time_end = time.perf_counter()
            # calculate time
            self.search_timer = (time_end - time_start) * 1000
            
            shapeNchange_error = search_by_shapeNchange.get_error()
            # 如果出现错误
            if (shapeNchange_error != -1):
                if (shapeNchange_error == 0):
                    QMessageBox.critical(self, "Error", "Data file not found!")
                elif (shapeNchange_error == 1):
                    QMessageBox.critical(self, "Error", "The image is not in the database!")
                return
            # 没有出现错误，获取 outputlist & outacc
            self.outputlist, self.outacc = search_by_shapeNchange.get_output()
        
        # print("in show pic widget: ")
        # print("outputlist length: " + str(len(self.outputlist)))
        # print("outacc length: " + str(len(self.outacc)))
        print("elapsed time: " + str(self.search_timer) + " ms")

        # set content (output_dict)
        self.set_content(method)
        # set ui
        self.set_ui()
        # show
        self.show()


    """
    method: 用来判断是哪一个检索方法。不同的检索方法 outputlist 不一样
    """
    def set_content(self, method):
        if (len(self.outacc) != len(self.outputlist)):
            QMessageBox.critical(self, "Error", "Output is invalid!")
            return
        
        for i in range(len(self.outacc)):
            # 最多 10 个
            # if (i == self.max_num):
            #     break
            if (method == 1): # ColorHSVData 格式问题
                # insert into dictionary
                self.output_dict.update({str(self.outputlist[i][0:-1]): float(self.outacc[i])})
            elif (method == 2 or method == 3 or method == 4):
                # insert into dictionary
                self.output_dict.update({str(self.outputlist[i]): float(self.outacc[i])})

        # loss 从小到大排序
        sorted_output_list = sorted(self.output_dict.items(), key=lambda x:x[1])
        self.output_dict = dict(sorted_output_list)
        # print(sorted_output_list)


    # set ui
    def set_ui(self):
        # label and pixmap
        lbl_input = QLabel()
        pm_input = QPixmap(self.input_img)
        # display picture on the label
        lbl_input.setPixmap(pm_input)
        # set alignment center
        lbl_input.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        
        # 一个 vlayout，vlayout 中有两个 groupbox
        vlayout_out = QVBoxLayout()
        
        # input groupbox and hlayout
        groupbox_input = QGroupBox()
        hlayout_input = QHBoxLayout()

        hlayout_input.addWidget(lbl_input)
        groupbox_input.setTitle("Input Image")
        groupbox_input.setLayout(hlayout_input)

        # output groupbox and hlayout
        # 加入横向滚动条
        scollarea_output = QScrollArea()

        groupbox_output = QGroupBox()
        hlayout_output = QHBoxLayout()

        # 内部还有多个 groupbox (内部有 vlayout)
        # groupbox 需要添加进 hlayout_output
        # 根据字典的元素个数 for 循环生成
        # 第一个是 loss 最小的 output，也就是 best
        # 记录当前是第几个元素
        count = 0    
        # 用于计算前 i 个样本 (也就是显示出来的) 平均 loss
        loss_total = 0   
        for key_list, value_acc in self.output_dict.items():
            # 最多 20 个
            if (count == self.max_num):
                break
            # label and pixmap
            lbl_output = QLabel()
            lbl_output_acc = QLabel()
            if (count == 0):   # 如果是第一个
                lbl_output_acc.setText("best: loss = " + str('{:.6f}'.format(value_acc)))
            else:
                lbl_output_acc.setText("candidate " + str(count) + ": loss = " + str('{:.6f}'.format(value_acc)))
            
            pm_output = QPixmap(key_list)
            # display picture on the label
            lbl_output.setPixmap(pm_output)
            # set alignment center
            lbl_output.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            lbl_output_acc.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

            # groupbox and vlayout
            groupbox_item = QGroupBox()
            vlayout_item = QVBoxLayout()
            
            vlayout_item.addWidget(lbl_output)
            vlayout_item.addWidget(lbl_output_acc)

            groupbox_item.setLayout(vlayout_item)
            # set groupbox_item as no border
            groupbox_item.setStyleSheet("border:none")

            hlayout_output.addWidget(groupbox_item)
            # 步长++
            count += 1
            # loss_average += value_acc
            loss_total += value_acc

        
        # 显示 output 总数
        groupbox_output.setTitle("Output Images: " + str(len(self.output_dict)) + 
                                 "  |  Loss Average (shown below): " + str('{:.3f}'.format(loss_total / count)) + 
                                 "  |  Elapsed Time: " + str('{:.3f}'.format(self.search_timer)) + " ms  ")
        # groupbox_output.setTitle("Output Images: " + str(i))
        groupbox_output.setLayout(hlayout_output)

        scollarea_output.setWidget(groupbox_output)

        # 最外层 vlayout
        vlayout_out.addWidget(groupbox_input)
        # vlayout_out.addWidget(groupbox_output)
        vlayout_out.addWidget(scollarea_output)
        self.setLayout(vlayout_out)
        self.setWindowTitle('Output Result')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    show_pic_widget = ShowPicWidget()
    show_pic_widget.set_img_and_data_file("test_imgs/airplane_image_0007.jpg", "ColorHSVData")
    show_pic_widget.search_process(1)
    # show_pic_widget.show()

    app.exec_()