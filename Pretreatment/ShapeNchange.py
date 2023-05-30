# hu不变矩
# https://blog.csdn.net/qq_23926575/article/details/80624630
import glob
import cv2

class PreShapeNchange():
    # is pretreating flag
    isPretreating = False

    def __init__(self, data_filename):
        self.file_output(data_filename)

    def test(self, img):
        moments = cv2.moments(img)
        humoments = cv2.HuMoments(moments)
        return humoments

    def file_output(self, data_filename):
        f = open("./Repository/" + data_filename, 'w+')
        imgset = glob.glob("./dataset/*/*.jpg")
        self.isPretreating = True
        for i in imgset:
            if (self.isPretreating == False):
                break
            img = cv2.imread(i)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # out = "{" + str(i) + "}\n" + str(test(img_gray)) + "\n"
            # TODO 修改了生成数据的格式规则
            out = str(i) + "\n" + str(self.test(img_gray)) + "\n"
            f.write(out)
        f.close()
        self.isPretreating = False

if __name__ == "__main__":
    pre_shape_Nchange = PreShapeNchange("ShapeNchangeData")