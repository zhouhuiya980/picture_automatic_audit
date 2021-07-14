import json
# 导入json头文件
import shutil
import os, sys

class JsonReGenerator(object):

    '''
    比较同一张图片的两个json文件，找出bbox与label均相同的部分写入新的json文件并保存
    input：jsonA jsonB
    output：new json
    '''

    def __init__(self,json_A,json_B,dst_path):
        self.json_a = json_A
        self.json_b = json_B
        self.dst_path = dst_path

    def calIOU(self,box_0, box_1):
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


    def jsonReGenerator(self):

        '''
        input：两个json文件
        output：将生成的json文件输出到一个新的文件夹中
        '''

        labels_long = json.load(open(self.json_a))
        labels_short = json.load(open(self.json_b))



        if len(labels_short['shapes']) == 0 or len(labels_long['shapes']) == 0:
             #表示json文件中shapes包含的label数为空
            print('one json file is Null')
            return

        newJson_dir = self.dst_path
        if not os.path.exists(newJson_dir):
            os.mkdir(newJson_dir)

        # 比较两个标注列表长度，外层for循环遍历长的，里层for选好遍历短的,这样确保两个人的box都能遍历到
        if len(labels_short['shapes']) > len(labels_long['shapes']):
            labels_long, labels_short = labels_short, labels_long
            #默认拷贝长label的json文件
            jsonFile = shutil.copy(self.json_b,newJson_dir)
        else:
            jsonFile = shutil.copy(self.json_a,newJson_dir)


        # newJson = json.load(open(jsonFile))

        # 两层for循环
        '''
        1对于json_a中的每一个label，算出其与json_b中的每一个label的iou值，取最大值，记录【i，j】
        2对于json_b中的每一个label，算出其与json_a中的每一个label的iou值，取最大值，记录【i，j】
        两次循环匹配考虑到了重叠情况
        '''
        # 用一个list来记录第一次匹配的情况 （i，j）：i：长label列表 j：短label列表
        match_id_list1 = []
        for i in range(len(labels_long['shapes'])):
            x0 = labels_long['shapes'][i]['points'][0][0]
            y0 = labels_long['shapes'][i]['points'][0][1]
            x1 = labels_long['shapes'][i]['points'][1][0]
            y1 = labels_long['shapes'][i]['points'][1][1]

            if x0 > x1 and y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0

            box_1 = [x0, y0, x1, y1]

            label_2_item_iou = {}

            for j in range(len(labels_short['shapes'])):
                m0 = labels_short['shapes'][j]['points'][0][0]
                n0 = labels_short['shapes'][j]['points'][0][1]
                m1 = labels_short['shapes'][j]['points'][1][0]
                n1 = labels_short['shapes'][j]['points'][1][1]

                if m0 > m1 and n0 > n1:
                    m0, n0, m1, n1 = m1, n1, m0, n0

                box_2 = [m0, n0, m1, n1]

                # 计算IOU值
                iou = self.calIOU(box_1, box_2)
                #检验iou值
                if iou < 0 or iou > 1:
                    print('wrong')

                # 记录iou与索引之间的之间的关系
                label_2_item_iou[iou] = j
            max_iou = max(label_2_item_iou.keys())
            # 这里没有考虑最大iou为0的情况，是因为要进行二次匹配
            match_id_list1.append((i, label_2_item_iou[max_iou]))
            # # 若iou值大于0.7，说明重合面积占框面积80%以上，说明bbox对应上了
            # if max_iou > 0.5:
            #     match_id_list1.append((i, label_2_item_iou[max_iou]))
            # else:
            #     # 否则用-1来表示没匹配上，这里可以调控一下iou阈值
            #     match_id_list1.append((i, -1))

        # 第二次循环
        # 用于记录第二次匹配的情况，（i，j）：i：短label列表 j：长label列表
        match_id_list2 = []
        for i in range(len(labels_short['shapes'])):
            m0 = labels_short['shapes'][i]['points'][0][0]
            n0 = labels_short['shapes'][i]['points'][0][1]
            m1 = labels_short['shapes'][i]['points'][1][0]
            n1 = labels_short['shapes'][i]['points'][1][1]

            if m0 > m1 and n0 > n1:
                m0, n0, m1, n1 = m1, n1, m0, n0

            box_1 = [m0, n0, m1, n1]

            label_2_item_iou = {}
            for j in range(len(labels_long['shapes'])):
                x0 = labels_long['shapes'][j]['points'][0][0]
                y0 = labels_long['shapes'][j]['points'][0][1]
                x1 = labels_long['shapes'][j]['points'][1][0]
                y1 = labels_long['shapes'][j]['points'][1][1]

                if x0 > x1 and y0 > y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0

                box_2 = [x0, y0, x1, y1]

                # 计算IOU值
                iou = self.calIOU(box_1, box_2)
                if iou < 0 or iou > 1:
                    print('wrong')

                # 记录iou与索引之间的之间的关系
                label_2_item_iou[iou] = j
            max_iou = max(label_2_item_iou.keys())
            # if max_iou > 0.5:
            #     match_id_list2.append((i, label_2_item_iou[max_iou]))
            # else:
            #     # 否则用-1来表示没匹配上，这里可以调控一下iou阈值
            #     match_id_list2.append((i, -1))
            match_id_list2.append((i, label_2_item_iou[max_iou]))


        flag1 = []
        with open(jsonFile, 'r+') as file:
            newJson = json.load(file)
            # print(len(newJson['shapes']))
            for (i, j) in match_id_list1:
                # print(i, j)
                if (j, i) in match_id_list2 and labels_long['shapes'][i]['label'] == labels_short['shapes'][j]['label']:
                    flag1.append(0)
                else:
                    flag1.append(1)
                    # print(i)
                    d = labels_long['shapes'][i]
                    newJson['shapes'].remove(d)
            # 下面的两个命令是用于清空文件的，若无，会出错
            file.seek(0, 0)
            file.truncate()
            # 将修改后的内容保存到newJon文件中
            file.write(json.dumps(newJson))












