import numpy as np
import cv2
import math

"""
这个图片颜色很多的时候，要算很久
"""

class SearchByShapeHist():
    # encounter error
    hasError = False
    # error type
    """
    -1: no error
     0: data file not found
     1: image is not in the database
    """
    errorType = -1
    
    # outputlist & outacc
    outputlist = []
    outacc = []

    def __init__(self, loss_threshold):
        super().__init__()
        self.data_filename = "ShapeHistogramData"
        self.inputpath = ""
        self.loss_threshold = loss_threshold

        print("Search by Shape Hist loss threshold: " + str(self.loss_threshold))


    def set_content(self, inputpath, data_filename):
        self.data_filename = data_filename
        self.inputpath = inputpath


    def ft(self, img):
        sigma1 = sigma2 = 1
        sum = 0

        gaussian = np.zeros([5, 5])
        for i in range(5):
            for j in range(5):
                gaussian[i, j] = math.exp(-1 / 2 * (np.square(i - 3) / np.square(sigma1)  # 生成二维高斯分布矩阵
                                                    + (np.square(j - 3) / np.square(sigma2)))) / (
                                 2 * math.pi * sigma1 * sigma2)
                sum = sum + gaussian[i, j]

        gaussian = gaussian / sum

        # print(gaussian)

        def rgb2gray(rgb):
            return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])

        # step1.高斯滤波
        gray = rgb2gray(img)
        W, H = gray.shape
        new_gray = np.zeros([W - 5, H - 5])
        for i in range(W - 5):
            for j in range(H - 5):
                new_gray[i, j] = np.sum(gray[i:i + 5, j:j + 5] * gaussian)  # 与高斯矩阵卷积实现滤波

        # plt.imshow(new_gray, cmap="gray")


        # step2.增强 通过求梯度幅值
        W1, H1 = new_gray.shape
        dx = np.zeros([W1 - 1, H1 - 1])
        dy = np.zeros([W1 - 1, H1 - 1])
        d = np.zeros([W1 - 1, H1 - 1])
        for i in range(W1 - 1):
            for j in range(H1 - 1):
                dx[i, j] = new_gray[i, j + 1] - new_gray[i, j]
                dy[i, j] = new_gray[i + 1, j] - new_gray[i, j]
                d[i, j] = np.sqrt(np.square(dx[i, j]) + np.square(dy[i, j]))  # 图像梯度幅值作为图像强度值

        # plt.imshow(d, cmap="gray")


        # setp3.非极大值抑制 NMS
        W2, H2 = d.shape
        NMS = np.copy(d)
        NMS[0, :] = NMS[W2 - 1, :] = NMS[:, 0] = NMS[:, H2 - 1] = 0
        for i in range(1, W2 - 1):
            for j in range(1, H2 - 1):

                if d[i, j] == 0:
                    NMS[i, j] = 0
                else:
                    gradX = dx[i, j]
                    gradY = dy[i, j]
                    gradTemp = d[i, j]

                    # 如果Y方向幅度值较大
                    if np.abs(gradY) > np.abs(gradX):
                        weight = np.abs(gradX) / np.abs(gradY)
                        grad2 = d[i - 1, j]
                        grad4 = d[i + 1, j]
                        # 如果x,y方向梯度符号相同
                        if gradX * gradY > 0:
                            grad1 = d[i - 1, j - 1]
                            grad3 = d[i + 1, j + 1]
                        # 如果x,y方向梯度符号相反
                        else:
                            grad1 = d[i - 1, j + 1]
                            grad3 = d[i + 1, j - 1]

                    # 如果X方向幅度值较大
                    else:
                        weight = np.abs(gradY) / np.abs(gradX)
                        grad2 = d[i, j - 1]
                        grad4 = d[i, j + 1]
                        # 如果x,y方向梯度符号相同
                        if gradX * gradY > 0:
                            grad1 = d[i + 1, j - 1]
                            grad3 = d[i - 1, j + 1]
                        # 如果x,y方向梯度符号相反
                        else:
                            grad1 = d[i - 1, j - 1]
                            grad3 = d[i + 1, j + 1]

                    gradTemp1 = weight * grad1 + (1 - weight) * grad2
                    gradTemp2 = weight * grad3 + (1 - weight) * grad4
                    if gradTemp >= gradTemp1 and gradTemp >= gradTemp2:
                        NMS[i, j] = gradTemp
                    else:
                        NMS[i, j] = 0

        # plt.imshow(NMS, cmap = "gray")


        # step4. 双阈值算法检测、连接边缘
        W3, H3 = NMS.shape
        DT = np.zeros([W3, H3])
        # 定义高低阈值
        TL = 0.2 * np.max(NMS)
        TH = 0.3 * np.max(NMS)
        for i in range(1, W3 - 1):
            for j in range(1, H3 - 1):
                if (NMS[i, j] < TL):
                    DT[i, j] = 0
                elif (NMS[i, j] > TH):
                    DT[i, j] = 1
                elif ((NMS[i - 1, j - 1:j + 1] < TH).any() or (NMS[i + 1, j - 1:j + 1]).any()
                      or (NMS[i, [j - 1, j + 1]] < TH).any()):
                    DT[i, j] = 1
        size = DT.shape

        w = size[0]
        h = size[1]
        wnew = int(w / 4)
        hnew = int(h / 4)
        # calc存放最终结果，256
        step = 0  # calcnew的下标，0~63
        start = 0  # 每次统计的开始位置
        calc = [0 for i in range(0, 16)]
        count = 0
        i = 0
        j = 0
        k = 0
        for i in range(0, w):
            for j in range(0, h):
                if i >= 0 and i <= wnew and j >= 0 and j <= hnew and DT[i][j] == 1:
                    calc[0] = calc[0] + 1
                if i >= wnew and i <= 2 * wnew and j >= 0 and j <= hnew and DT[i][j] == 1:
                    calc[1] = calc[1] + 1
                if i >= 2 * wnew and i <= 3 * wnew and j >= 0 and j <= hnew and DT[i][j] == 1:
                    calc[2] = calc[2] + 1
                if i >= 3 * wnew and i <= 4 * wnew and j >= 0 and j <= hnew and DT[i][j] == 1:
                    calc[3] = calc[3] + 1

                if i >= 0 and i <= wnew and j >= hnew and j <= 2 * hnew and DT[i][j] == 1:
                    calc[4] = calc[4] + 1
                if i >= wnew and i <= 2 * wnew and j >= hnew and j <= 2 * hnew and DT[i][j] == 1:
                    calc[5] = calc[5] + 1
                if i >= 2 * wnew and i <= 3 * wnew and j >= hnew and j <= 2 * hnew and DT[i][j] == 1:
                    calc[6] = calc[6] + 1
                if i >= 3 * wnew and i <= 4 * wnew and j >= hnew and j <= 2 * hnew and DT[i][j] == 1:
                    calc[7] = calc[7] + 1

                if i >= 0 and i <= wnew and j >= 2 * hnew and j <= 3 * hnew and DT[i][j] == 1:
                    calc[8] = calc[8] + 1
                if i >= wnew and i <= 2 * wnew and j >= 2 * hnew and j <= 3 * hnew and DT[i][j] == 1:
                    calc[9] = calc[9] + 1
                if i >= 2 * wnew and i <= 3 * wnew and j >= 2 * hnew and j <= 3 * hnew and DT[i][j] == 1:
                    calc[10] = calc[10] + 1
                if i >= 3 * wnew and i <= 4 * wnew and j >= 2 * hnew and j <= 3 * hnew and DT[i][j] == 1:
                    calc[11] = calc[11] + 1

                if i >= 0 and i <= wnew and j >= 3 * hnew and j <= 4 * hnew and DT[i][j] == 1:
                    calc[12] = calc[12] + 1
                if i >= wnew and i <= 2 * wnew and j >= 3 * hnew and j <= 4 * hnew and DT[i][j] == 1:
                    calc[13] = calc[13] + 1
                if i >= 2 * wnew and i <= 3 * wnew and j >= 3 * hnew and j <= 4 * hnew and DT[i][j] == 1:
                    calc[14] = calc[14] + 1
                if i >= 3 * wnew and i <= 4 * wnew and j >= 3 * hnew and j <= 4 * hnew and DT[i][j] == 1:
                    calc[15] = calc[15] + 1
        return calc


    def calc(self, input, data):
        res = 0
        if len(input) != 16 and len(data)!= 16:
            return 9999999
        for i in range (0,16):
            if input[i] == 0:
                continue
            res += abs(float(input[i]-data[i]))/abs(float(input[i]))
        return res
    

    # 主要处理函数
    def process_func(self):
        # 添加异常，如果出现没有存在那个文件，弹出提示框，并 return
        try:
            file = open("./Repository/" + self.data_filename)
        except FileNotFoundError:
            self.hasError = True
            self.errorType = 0
            return
        
        inputimg = cv2.imread(self.inputpath)
        inputlist = (self.ft(inputimg))

        i = 1
        outputlist = []
        outacc = []
        flag = 0
        while 1:
            line = file.readline()
            if not line:
                break
            if i % 2 == 1:
                name = line
            if i % 2 == 0:
                lstr = str(line)
                tlist = [float(x) for x in lstr[1:-2].split(',')]
                num = self.calc(inputlist, tlist)

                if flag == 1 and num <= self.loss_threshold:
                    outputlist.append(name[0:-1])
                    outacc.append(num)
                if num <= 1 and flag == 0:
                    # print([num, name])
                    outputlist.append(name[0:-1])
                    outacc.append(num)
                    flag = 1

            i+=1

        # TODO 判断 outputlist 和 outacc 是否为空
        if (len(outputlist) == 0 or len(outacc) == 0):
            self.hasError = True
            self.errorType = 1
            return
        
        self.outputlist = outputlist
        self.outacc = outacc

        # print("in search method: ")
        # print("outputlist length: " + str(len(self.outputlist)))
        # print("outacc length: " + str(len(self.outacc)))


    # get outputlist and outacc
    # Used by ShowPicWidget
    def get_output(self):
        return self.outputlist, self.outacc
    

    # 获取 error 信息
    def get_error(self):
        # 有错误并且错误代码 != -1
        if (self.hasError == True and self.errorType != -1):
            return self.errorType
        return self.errorType


if __name__ == "__main__":
    search_by_shapeHist = SearchByShapeHist()
    search_by_shapeHist.set_content("test_imgs/image_0014.jpg", "ShapeHistogramData")
    search_by_shapeHist.process_func()
    (outputlist, outacc) = search_by_shapeHist.get_output()
    print(outputlist)
    print(outacc)