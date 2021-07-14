import os
import json


def calIOU(box_0, box_1):
    '''
    计算IOU
    ：param gt_ox: ground truth [x0,y0,w0,h0] (x0,y0)为左上角坐标（x1，y1）为右下角坐标
    ：param b_box:bounding box
    :return
    '''
    '''
    IOU计算原理
    ground truth(目标所在的真实框）bounding box(算法预测目标所在的框)
    bbox文件（x，y，w，h）表示的是两个点的坐标，顾名思义w-x为这个框的宽，h-y表示这个框的高
    W = w0 + w1 - (max((x0 + w0) , (x1 + w1)) - min (x0, x1))
    H = h0 + h1 - (max((y0 + h0) , (y1 + h1)) - min (y0, y1))
    Intersection = W * H
    Union = w0 * h0 + w1 * h1 - Intersection
    '''
    """
       计算两个矩形框的交并比。
       :param box1: (x0,y0,x1,y1)      (x0,y0)代表矩形左上的顶点，（x1,y1）代表矩形右下的顶点。下同。
       :param box2: (x0,y0,x1,y1)
       :return: 交并比IOU.
       """
    left_column_max = max(box_0[0], box_1[0])
    right_column_min = min(box_0[2], box_1[2])
    up_row_max = max(box_0[1], box_1[1])
    down_row_min = min(box_0[3], box_1[3])
    # 两矩形无相交区域的情况
    if left_column_max >= right_column_min or down_row_min <= up_row_max:
        return 0
    # 两矩形有相交区域的情况
    else:
        S1 = abs((box_0[2] - box_0[0])) * abs((box_0[3] - box_0[1]))
        S2 = abs((box_1[2] - box_1[0])) * abs((box_1[3] - box_1[1]))
        S_cross = (down_row_min - up_row_max) * (right_column_min - left_column_max)
        return S_cross / (S1 + S2 - S_cross)






pathA = './img1000_A'
pathB = './img1000_B'
path = './img1000_reJson'

for file in os.listdir(path):
    if file[-5:] == '.json':
        filepath = os.path.join(path,file)
        data = json.load(open(filepath))
        print(len(data['shapes']))

# for file in os.listdir(pathA):
#     if file[-5:] == '.json':
#         fileA = os.path.join(pathA,file)
#         if file in os.listdir(pathB):
#             fileB = os.path.join(pathB,file)
#             dataA = json.load(open(fileA))
#             dataB = json.load(open(fileB))
#             for i in range(len(dataA['shapes'])):
#                 x0 = dataA['shapes'][i]['points'][0][0]
#                 y0 = dataA['shapes'][i]['points'][0][1]
#                 x1 = dataA['shapes'][i]['points'][1][0]
#                 y1 = dataA['shapes'][i]['points'][1][1]
#                 # print(x0,y0,x1,y1)
#                 #防止右下左上的情况# 348.9672131147541 31.557377049180328 253.47540983606558 0.819672131147541
#                 if x0 > x1 and y0 > y1:
#                     x0,y0,x1,y1 = x1,y1,x0,y0
#                 bbox_1 = [x0,y0,x1,y1]
#                 for j in range(len(dataB['shapes'])):
#                     m0 = dataB['shapes'][j]['points'][0][0]
#                     n0 = dataB['shapes'][j]['points'][0][1]
#                     m1 = dataB['shapes'][j]['points'][1][0]
#                     n1 = dataB['shapes'][j]['points'][1][1]
#
#                     if m0 > m1 and n0 > n1 :
#                         m0,n0,m1,n1 = m1,n1,m0,n0
#                     bbox_2 = [m0,n0,m1,n1]
#
#                     iou = calIOU(bbox_1,bbox_2)
#                     print(iou)
#             print('-----------------')


                # if x0 > x1







