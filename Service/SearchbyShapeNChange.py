import cv2

class SearchByShapeNChange():
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
        self.data_filename = "ShapeNchangeData"
        self.inputpath = ""
        self.loss_threshold = loss_threshold

        print("Search by Shape Nchange loss threshold: " + str(self.loss_threshold))


    def set_content(self, inputpath, data_filename):
        self.data_filename = data_filename
        self.inputpath = inputpath


    def ft(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        moments = cv2.moments(img_gray)
        humoments = cv2.HuMoments(moments)
        return humoments


    def cal(self, input, data):
        ans = 0
        for i in range(0,6):
            if input[i] == 0:
                continue
            ans += abs(input[i] - data[i])/abs(input[i])
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
        inlist = self.ft(inputimg)

        i = 0
        linelist = []
        outputlist = []
        outacc = []
        flag = 0
        loop = 0
        while 1:
            line = file.readline()
            if not line:
                break
            i += 1
            case = i % 8
            if case == 1:
                # TODO 修改文件读取规则
                # name = line[1:-2]
                name = line[:-1]
            elif case != 1 and case != 0:
                linelist.append(float(line[2:-2]))
            elif case == 0:
                linelist.append(float(line[2:-3]))

            # print(name)
            # print(linelist)
            if case == 0 and len(linelist) == 7:
                num = self.cal(inlist, linelist)
                if flag == 1 and num < self.loss_threshold:
                    outputlist.append(name)
                    outacc.append(num)
                if num < 0.1 and flag == 0:
                    outputlist.append(name)
                    outacc.append(num)
                    flag = 1
            if case == 0 and len(linelist) == 7:
                linelist = []

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
    search_by_shapeNchange = SearchByShapeNChange()
    search_by_shapeNchange.set_content("test_imgs/image_0014.jpg", "ShapeNchangeData")
    search_by_shapeNchange.process_func()
    (outputlist, outacc) = search_by_shapeNchange.get_output()
    print(outputlist)
    print(outacc)