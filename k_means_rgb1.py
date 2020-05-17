'''
使用k均值算法对图片进行颜色划分(副作用:可以压缩图片)
'''

from PIL import Image
import random
import pygame
from math import pow as power
import tools

class Mylist:
    def __init__(self):
        self.data = []
        self.f=0
    def __len__(self):
        return len(self.data)
    def __getitem__(self,n):
        return self.data[n]
    def __setitem__(self,n,v):
        self.data[n]=v
    def __iter__(self):
        return self
    def __next__(self):
        if self.f<len(self.data):
            i = self.data[self.f]
            self.f += 1
            return i
        else:
            self.f = 0
            raise StopIteration()
    def __lt__(self,other):
        return len(self.data)<len(other.data)
    def __gt__(self,other):
        return len(self.data)>len(other.data)
    def append(self,item):
        self.data.append(item)
    def clear(self):
        self.data=[]

imgfile = 'e:/img/k-means/' 
imgfile2='60.jpg'

size = Image.open(imgfile+imgfile2).size

k = 10 #将图片分为[至多]k种颜色 (经常会有质心选的太偏而抢不到任何像素点)
maxdistance = 50 #循环的出口,代表允许[质心与该类中心点的距离平方]的最大值

AUTO=True #是否采用随机选取质心 P.S.False需要你手动输入,很费事,但效果甩auto几条街
CompletelyRandom=True #是否完全随机抛点

#动态计算图片导入导出路径
tofile = imgfile+imgfile2[:-4]+'k'+str(k)+'-.png'
imgfile+=imgfile2 

#存放分组后的像素点,与means对应
groops = [Mylist() for _ in range(k)]
#存放图片全部[像素位置]信息
pixels = []

#质心列表
means = Mylist()

twin = tools.Twinlist(means,groops)
#当前为第n张图片
TEST_count=0

#对每一个k值计算5张图片,此参数为当前图片索引
Write_count = 0

#分别表示质心与平均中心点的距离是否达标,是否开始新一轮聚类
FINISH = [False,False]



#动态添加全局变量
class Setting:
    def __init__(self):
        pass
setting = Setting()

#保存位置-像素数据
class Point:
    def __init__(self,pos,color):
        self.pos = pos
        self.color = color

def loadImgColor(imgfile): #导入图片位置-像素数据
    img = Image.open(imgfile)
    x,y = img.size
    setting.img=img
    setting.size = img.size
    for col in range(y):
        for row in range(x):
            pixels.append(Point((row,col),img.getpixel((row,col))))

def createRandomMeans(num): #初始化质心
    for _ in range(num):
        rancolor=tuple([random.randint(0,255) for i in range(3)])
        means.append(Point((0,0),rancolor))

def inputFixMeans(): #手动输入图片颜色,效果较棒
    print('输入格式:\nr g b\nfor example:100 100 100')
    for i in range(k):
        fixcolor=input('请输入第%d种颜色:'%(i+1))
        fixcolor=fixcolor.strip().split(' ')
        for j in range(3):
            fixcolor[j]=int(fixcolor[j])
        means.append(Point(None,tuple(fixcolor)))

def selectMeans1(k):
    x,y=setting.size
    for _ in range(k):
        color=[0,0,0]
        for _ in range(15):
            ranpos=(random.randint(0,x-1),random.randint(0,y-1))
            color=[color[i]+setting.img.getpixel(ranpos)[i] for i in range(3)]
        color = tuple([color[i]//5 for i in range(3)])
        means.append(Point(None,color))

def selectMeans2(k):
    x,y=setting.size
    count=0
    up = 0
    while count<k:
        up+=1
        ranpos=(random.randint(0,x-1),random.randint(0,y-1))
        color=setting.img.getpixel(ranpos)
        can=True
        for i in means:
            if distance(Point(None,color),i)<10000:
                can=False
        if can:
            means.append(Point(None,tuple(color)))
            count+=1
        if up>10000:
            selectMeans1(k-count)
            break


def distance(point1,point2): #计算两点距离
    return power(point1.color[0]-point2.color[0],2)\
           +power(point1.color[1]-point2.color[1],2)\
           +power(point1.color[2]-point2.color[2],2)

def classification(k):#归类
    for i in pixels:
        minindex = 0
        d = float('inf')
        for j in range(k):
            if distance(i,means[j])<d:
                minindex = j
                d=distance(i,means[j])
        groops[minindex].append(i)
    for i in groops:
        print(len(i))

def focus(k):#计算重心
    for i in range(k):
        total=[0,0,0]
        if len(groops[i])==0:continue
        for j in range(len(groops[i])):
            point = groops[i][j]
            total[0]+=point.color[0]
            total[1]+=point.color[1]
            total[2]+=point.color[2]
        for j in range(3):
            total[j]=round(total[j]/len(groops[i]))
        if distance(means[i],Point(None,total))>=maxdistance:
            FINISH[0]=False
        print('distance',distance(means[i],Point(None,total)))
        means[i].color = tuple(total)
        print(total)

def save(tofile,k):
    img = Image.new('RGB',setting.size,(0,0,0))
    for i in range(k):
        for j in groops[i]:
            img.putpixel(j.pos,means[i].color)
    img.save(tofile)

def main(imgfile,k,tofile):
    global TEST_count,Write_count
    if not pixels:
        loadImgColor(imgfile)
    Num_img=5 if AUTO else 1
    while Write_count<Num_img:
        classcount=0
        while not FINISH[0] or not FINISH[1]:
            if not FINISH[1]:
                means.clear()
                if not AUTO: inputFixMeans()
                elif not CompletelyRandom: selectMeans1(k)
                else:createRandomMeans(k)
                print('the %d time(s)'%(TEST_count+1))
            for i in groops:
                i.clear()
            print('重新聚类次数:%d次'%classcount)
            classification(k)
            FINISH[0]=True;FINISH[1]=True
            focus(k)
            classcount+=1
            yield
        FINISH[0]=False;FINISH[1]=False
        Write_count+=1
        TEST_count+=1
        


pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption('k-means')


for i in main(imgfile,k,tofile):
    twin.sort()
    _groops = twin.orderlist
    _means = twin.mainlist
    screen.fill(_means[0].color)
    for indexj,j in enumerate(_groops[1:]):
        color=_means[indexj+1].color
        for k in j:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            screen.set_at(k.pos,color)
            pygame.display.flip()

