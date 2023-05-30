import cv2
import math

class SearchByTextureGreyMatrix():
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

    #定义最大灰度级数
    gray_level = 16

    def __init__(self, loss_threshold):
        super().__init__()
        self.data_filename = "GreyMatrixData"
        self.inputpath = ""
        self.loss_threshold = loss_threshold

        print("Search by Texture GreyMatrix loss threshold: " + str(self.loss_threshold))


    def set_content(self, inputpath, data_filename):
        self.data_filename = data_filename
        self.inputpath = inputpath
    

    def maxGrayLevel(self, img):
        max_gray_level=0
        (height,width)=img.shape
        # print height,width
        for y in range(height):
            for x in range(width):
                if img[y][x] > max_gray_level:
                    max_gray_level = img[y][x]
        return max_gray_level+1


    def getGlcm(self, input, d_x, d_y):
        srcdata=input.copy()
        ret=[[0.0 for i in range(self.gray_level)] for j in range(self.gray_level)]
        (height,width) = input.shape
    
        max_gray_level = self.maxGrayLevel(input)
    
        # 若灰度级数大于gray_level，则将图像的灰度级缩小至gray_level，减小灰度共生矩阵的大小
        if max_gray_level > self.gray_level:
            for j in range(height):
                for i in range(width):
                    srcdata[j][i] = srcdata[j][i] * self.gray_level / max_gray_level
    
        for j in range(height-d_y):
            for i in range(width-d_x):
                 rows = srcdata[j][i]
                 cols = srcdata[j + d_y][i+d_x]
                 ret[rows][cols]+=1.0
    
        for i in range(self.gray_level):
            for j in range(self.gray_level):
                ret[i][j]/=float(height*width)
    
        return ret


    def feature_computer(self, p):
        Con=0.0
        Eng=0.0
        Asm=0.0
        Idm=0.0
        for i in range(self.gray_level):
            for j in range(self.gray_level):
                Con+=(i-j)*(i-j)*p[i][j]
                Asm+=p[i][j]*p[i][j]
                Idm+=p[i][j]/(1+(i-j)*(i-j))
                if p[i][j]>0.0:
                    Eng+=p[i][j]*math.log(p[i][j])
        return Asm,Con,-Eng,Idm


    def test(self, img):
        try:
            img_shape=img.shape
        except:
            print ('imread error')
            return -1

        img=cv2.resize(img, (int(img_shape[1]/2), int(img_shape[0]/2)), interpolation=cv2.INTER_CUBIC)

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        glcm_0 = self.getGlcm(img_gray, 1,0)
        # glcm_1=getGlcm(src_gray, 0,1)
        # glcm_2=getGlcm(src_gray, 1,1)
        # glcm_3=getGlcm(src_gray, -1,1)

        asm,con,eng,idm = self.feature_computer(glcm_0)

        return asm,con,eng,idm


    def calc(self, input, data):
        res = 0
        for i in range (0,4):
            if input[i] == 0:
                continue
            res += abs(float(input[i]-data[i])) / abs(float(input[i]))
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
        inputlist = (self.test(inputimg))

        i = 1
        outputlist = []
        outacc = []
        flag = 0
        while 1:
            line = file.readline()
            if i % 2 == 1:
                name = line
            if i % 2 == 0:
                if not line:
                    break
                lstr = str(line)
                length = len(lstr)
                lstr = lstr[1:length-2]
                tlist = [float(x) for x in lstr.split(',')]
                num = self.calc(inputlist, tlist)
                # print
                # TODO 修改了文件读写规则
                if flag == 1 and num <= self.loss_threshold:
                    # outputlist.append(name[1:-2])
                    outputlist.append(name[:-1])
                    outacc.append(num)
                    # TODO num: 0.001 -> 0.005 
                if num <= 0.005 and flag == 0:
                    # print([num, name])
                    # outputlist.append(name[1:-2])
                    outputlist.append(name[:-1])
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
        # print("self outacc length: " + str(len(self.outacc)))


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
    search_by_greyMatrix = SearchByTextureGreyMatrix()
    search_by_greyMatrix.set_content("test_imgs/image_0014.jpg", "GreyMatrixData")
    search_by_greyMatrix.process_func()
    (outputlist, outacc) = search_by_greyMatrix.get_output()
    print(outputlist)
    print(outacc)