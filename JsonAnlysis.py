import json
# 导入json头文件
import shutil
import os, sys


class JsonAnlysis(object):
    '''
    比较同一张图片的两个json文件，找出jsonfile文件中与交集json文件中不同、匹配不上的部分，重新生成json文件
    input：json_interSection, jsonB
    output：new json
    '''

    def __init__(self, jsonfile, json_interSection, dst_path):

        self.json_a = jsonfile
        self.json_b = json_interSection
        self.dst_path = dst_path

    def calIOU(self, box_0, box_1):
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
            S1 = (box_0[2] - box_0[0]) * (box_0[3] - box_0[1])
            S2 = (box_1[2] - box_1[0]) * (box_1[3] - box_1[1])
            S_cross = (down_row_min - up_row_max) * (right_column_min - left_column_max)
            return S_cross / (S1 + S2 - S_cross)

    def jsonAnlysis(self):

        '''
        input：两个json文件
        output：将生成的json文件输出到一个新的文件夹中
        '''

        labels_long = json.load(open(self.json_a))
        labels_short = json.load(open(self.json_b))

        newJson_dir = self.dst_path
        if not os.path.exists(newJson_dir):
            os.mkdir(newJson_dir)

        if len(labels_short['shapes']) == 0 or len(labels_long['shapes']) == 0:
            print('json file is null')
            return

        # 比较两个标注列表长度，外层for循环遍历长的，里层for选好遍历短的,这样确保两个人的box都能遍历到
        if len(labels_short['shapes']) > len(labels_long['shapes']):
            labels_long, labels_short = labels_short, labels_long
            # 默认拷贝长label的json文件
            jsonFile = shutil.copy(self.json_b, newJson_dir)
        else:
            jsonFile = shutil.copy(self.json_a, newJson_dir)


        newJson = json.load(open(jsonFile))
        #
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
            print('bbox1',box_1)
            label_2_item_iou = {}

            print(len(labels_long['shapes']))

            for j in range(len(labels_short['shapes'])):
                m0 = labels_short['shapes'][j]['points'][0][0]
                n0 = labels_short['shapes'][j]['points'][0][1]
                m1 = labels_short['shapes'][j]['points'][1][0]
                n1 = labels_short['shapes'][j]['points'][1][1]

                if m0 > m1 and n0 > n1:
                    m0, n0, m1, n1 = m1, n1, m0, n0

                box_2 = [m0, n0, m1, n1]
                print('bbox2',box_2)
                # 计算IOU值
                iou = self.calIOU(box_1, box_2)
                print(iou)
                # 记录iou与索引之间的之间的关系
                label_2_item_iou[iou] = j
            print(label_2_item_iou.keys())
            max_iou = max(label_2_item_iou.keys())
            # 这里没有考虑最大iou为0的情况，是因为要进行二次匹配
            match_id_list1.append((i, label_2_item_iou[max_iou]))
            # # 若iou值大于0.7，说明重合面积占框面积80%以上，说明bbox对应上了
            # if max_iou > 0.5:
            #     match_id_list1.append((i, label_2_item_iou[max_iou]))
            # else:
            #     # 否则用-1来表示没匹配上，这里可以调控一下iou阈值
            #     match_id_list1.append((i, -1))
        print('-------------')
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

                # 记录iou与索引之间的之间的关系
                label_2_item_iou[iou] = j
            print(len(label_2_item_iou.keys()))
            max_iou = max(label_2_item_iou.keys())
            # if max_iou > 0.5:
            #     match_id_list2.append((i, label_2_item_iou[max_iou]))
            # else:
            #     # 否则用-1来表示没匹配上，这里可以调控一下iou阈值
            #     match_id_list2.append((i, -1))
            match_id_list2.append((i, label_2_item_iou[max_iou]))

        '''
        与JsonReGenerator不同的地方在于，将能匹配上的部分删掉，保留有问题的bbox
        
        '''
        flag1 = []
        with open(jsonFile, 'r+') as file:
            newJson = json.load(file)
            a = len(newJson['shapes'])
            # print(len(newJson['shapes']))
            # for (i,j) in match_id_list2:
            #     d = labels_long['shapes'][j]
            #     if d in newJson['shapes']:
            #
            #         newJson['shapes'].remove(d)
            for (i, j) in match_id_list1:
                # print(i, j)
                if (j, i) in match_id_list2 and labels_long['shapes'][i]['label'] == labels_short['shapes'][j]['label']:
                    flag1.append(0)
                    d = labels_long['shapes'][i]
                    newJson['shapes'].remove(d)
                else:
                    flag1.append(1)
                    # print(i)

        # for (i, j) in match_id_list1:
        #     # print(i, j)
        #     if (j, i) in match_id_list2 and labels_long['shapes'][i]['label'] == labels_short['shapes'][j]['label']:
        #         flag1.append(0)
        #         d = labels_long['shapes'][i]
        #         newJson['shapes'].remove(d)
        #     else:
        #         flag1.append(1)
            b = len(newJson['shapes'])

            # 下面的两个命令是用于清空文件的，若无，会出错
            file.seek(0, 0)
            file.truncate()
            # 将修改后的内容保存到newJon文件中
            file.write(json.dumps(newJson))


if __name__ == '__main__':

    file_InterSection = r'./img1000_reJson'
    file_A = r'./img1000_onceMore_A'
    file_B = r'./img1000_onceMore_B'
    dst_A = r'./img1000_onceMore_A_test'
    dst_B = r'./img1000_onceMore_B_test'

    # 生成json文件，没匹配上的部分
    for file in os.listdir(file_A):
        fiA = os.path.join(file_A, file)
        if file in os.listdir(file_InterSection):
            fi_InterSection = os.path.join(file_InterSection, file)
            JsonAnlysis(fiA, fi_InterSection, dst_A).jsonAnlysis()
    for file in os.listdir(file_B):
        fiA = os.path.join(file_B, file)
        if file in os.listdir(file_InterSection):
            fi_InterSection = os.path.join(file_InterSection, file)
            JsonAnlysis(fiA, fi_InterSection, dst_B).jsonAnlysis()


