import cv2
import numpy as np
import glob

#图像颜色特征：颜色矩
# Compute low order moments(1,2,3)
class PreColorHSV():
    # is pretreating flag
    isPretreating = False

    def __init__(self, data_filename):
        self.file_output(data_filename)

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
    
    # TODO 添加写入数据函数
    def file_output(self, data_filename):
        file = open('./Repository/' + data_filename, "w+")
        imgset = glob.glob("./dataset/*/*.jpg")
        # 设置为正在预处理
        self.isPretreating = True
        for i in imgset:
            # 判断是否需要终止
            if (self.isPretreating == False):
                break
            list = self.color_moments(i)
            # print(list)
            file.write(i + "\n" + str(list[0]) + "," + str(list[1]) + "," + str(list[2]) +  
                       "," + str(list[3]) + "," + str(list[4]) + "," + str(list[5]) + 
                       "," + str(list[6]) + "," + str(list[7]) + "," + str(list[8]) +"\n") 
        file.close()
        self.isPretreating = False


if __name__ == "__main__":
    pre_colorHSV = PreColorHSV('ColorHSVData')