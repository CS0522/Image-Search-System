import cv2
import numpy as np

class SearchByColorHSV():
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
        self.data_filename = "ColorHSVData"
        self.inputpath = ""
        self.loss_threshold = loss_threshold

        print("Search by ColorHSV loss threshold: " + str(self.loss_threshold))


    def set_content(self, inputpath, data_filename):
        self.data_filename = data_filename
        self.inputpath = inputpath


    def color_moments(self, filename):
        img = cv2.imread(filename)
        if img is None:
            return
        # Convert BGR to HSV colorspace
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Split the channels - h,s,v
        h, s, v = cv2.split(hsv)
        # Initialize the color feature
        color_feature = []
        # N = h.shape[0] * h.shape[1]
        # The first central moment - average
        h_mean = np.mean(h)  # np.sum(h)/float(N)
        s_mean = np.mean(s)  # np.sum(s)/float(N)
        v_mean = np.mean(v)  # np.sum(v)/float(N)
        color_feature.extend([h_mean, s_mean, v_mean])
        # The second central moment - standard deviation
        h_std = np.std(h)  # np.sqrt(np.mean(abs(h - h.mean())**2))
        s_std = np.std(s)  # np.sqrt(np.mean(abs(s - s.mean())**2))
        v_std = np.std(v)  # np.sqrt(np.mean(abs(v - v.mean())**2))
        color_feature.extend([h_std, s_std, v_std])
        # The third central moment - the third root of the skewness
        h_skewness = np.mean(abs(h - h.mean())**3)
        s_skewness = np.mean(abs(s - s.mean())**3)
        v_skewness = np.mean(abs(v - v.mean())**3)
        h_thirdMoment = h_skewness**(1./3)
        s_thirdMoment = s_skewness**(1./3)
        v_thirdMoment = v_skewness**(1./3)
        color_feature.extend([h_thirdMoment, s_thirdMoment, v_thirdMoment])

        return color_feature


    def cal(self, input, data):
        ans = 0
        for i in range(0,9):
            if input[i] == 0:
                continue
            ans += abs(input[i] - data[i])/(abs(input[i]))
        return ans
    

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
        inputft = self.color_moments(self.inputpath)
        i = 0
        outputlist = []
        outacc = []
        flag = 0
        while 1:
            line = file.readline()
            if not line:
                break
            if i % 2 == 0:
                name = line
            if i % 2 == 1:
                lstr = str(line)
                try:
                    tlist = [float(x) for x in lstr.split(',')]
                except ValueError as e:
                    # print("error", e, "on line", i)
                    continue
                num = self.cal(inputft, tlist)

                if flag == 1 and num < self.loss_threshold:
                    outputlist.append(name)
                    outacc.append(num)
                if num <= 0.1 and flag == 0:
                    outputlist.append(name)
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
    search_by_colorHSV = SearchByColorHSV()
    search_by_colorHSV.set_content("test_imgs/image_0014.jpg", "ColorHSVData")
    search_by_colorHSV.process_func()
    (outputlist, outacc) = search_by_colorHSV.get_output()
    print(outputlist)
    print(outacc)