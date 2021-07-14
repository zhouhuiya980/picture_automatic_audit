import json
import os

class TwoPersonCompareAlgo(object):
    '''
    两个人的评估算法
    input：json文件路径 eg：'/Users/edz/Desktop/test_A/0007DCB4-DBF0-4CDB-885A-D925DD1943BF.json'
    '''

    def __init__(self, person_one_algo_json, person_two_algo_json):
        self.person_one_algo_json = json.load(open(person_one_algo_json))
        self.person_two_algo_json = json.load(open(person_two_algo_json))


    def calIOU(self,box_0,box_1):
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


    def compare_json_new(self):
        '''
        input:两个json文件的路径
        返回：匹配与否等相关信息
        '''

        labels_long = self.person_one_algo_json
        labels_short = self.person_two_algo_json


        if len(labels_short['shapes']) == 0 or len(labels_long['shapes']) == 0:
            #表示生成的json文件为空
            flag = 'Null'
            return flag

        #比较两个标注列表长度，外层for循环遍历长的，里层for选好遍历短的,这样确保两个人的box都能遍历到
        if len(labels_short['shapes']) > len(labels_long['shapes']):
            labels_long, labels_short = labels_short, labels_long

        #匹配记录
        match_history = {}
        #匹配上了的个数
        matchcount = 0
        #bbox匹配上了但label不对的个数
        matchbunotcount = 0
        #没匹配上的个数
        notmatch = 0

        #两层for循环
        '''
        1对于json1中的每一个label，算出其与json2中的每一个label的iou值，取最大值，记录【i，j】
        2对于json2中的每一个label，算出其与json2中的每一个label的iou值，取最大值，记录【i，j】
        两次循环匹配考虑到了重叠情况
        '''
        #用一个list来记录第一次匹配的情况 （i，j）：i：长label列表 j：短label列表
        match_id_list1 =[]
        for i in range(len(labels_long['shapes'])):
            x0 = labels_long['shapes'][i]['points'][0][0]
            y0 = labels_long['shapes'][i]['points'][0][1]
            x1 = labels_long['shapes'][i]['points'][1][0]
            y1 = labels_long['shapes'][i]['points'][1][1]

            if x0 > x1 and y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0

            box_1 = [ x0, y0, x1, y1 ]

            label_2_item_iou = {}

            for j in range(len(labels_short['shapes'])):
                m0 = labels_short['shapes'][j]['points'][0][0]
                n0 = labels_short['shapes'][j]['points'][0][1]
                m1 = labels_short['shapes'][j]['points'][1][0]
                n1 = labels_short['shapes'][j]['points'][1][1]

                if m0 > m1 and n0 > n1:
                    m0, n0, m1, n1 = m1, n1, m0, n0

                box_2 = [ m0, n0, m1, n1 ]

                #计算IOU值
                iou = self.calIOU(box_1,box_2)
                if iou < 0 or iou > 1:
                    print('wrong')

                #记录iou与索引之间的之间的关系
                label_2_item_iou[iou] = j
            max_iou = max(label_2_item_iou.keys())
            match_id_list1.append((i, label_2_item_iou[max_iou]))
            #这里没有考虑最大iou为0的情况，是因为要进行二次匹配

            #若iou值大于0.7，说明重合面积占框面积80%以上，说明bbox对应上了
            # if max_iou > 0.6:
            #     match_id_list1.append((i,label_2_item_iou[max_iou]))
            # else:
            #     #否则用-1来表示没匹配上，这里可以调控一下iou阈值
            #     match_id_list1.append((i,-1))

            #match_label = labels_short['shapes'][label_2_item_iou[max_iou]]['label']

        #第二次循环
        #用于记录第二次匹配的情况，（i，j）：i：短label列表 j：长label列表
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

                #计算IOU值
                iou = self.calIOU(box_1, box_2)
                if iou < 0 or iou > 1:
                    print('wrong')
                # 记录iou与索引之间的之间的关系
                label_2_item_iou[iou] = j
            max_iou = max(label_2_item_iou.keys())

            match_id_list2.append((i, label_2_item_iou[max_iou]))
            # 若iou值大于0.7，说明重合面积占框面积80%以上，说明bbox对应上了
            # if max_iou > 0.6:
            #     match_id_list2.append((i, label_2_item_iou[max_iou]))
            # else:
            #     # 否则用-1来表示没匹配上，这里可以调控一下iou阈值
            #     match_id_list2.append((i, -1))

        flag = []
        for (i, j) in match_id_list2:  # list2中，短label在前，长label在后
            if (j, i) in match_id_list1 and labels_long['shapes'][j]['label'] == labels_short['shapes'][i]['label']:

                flag.append(0)
            else:
                flag.append(1)

        flag1 = []
        for (i, j) in match_id_list1:
            if (j, i) in match_id_list2 and labels_long['shapes'][i]['label'] == labels_short['shapes'][j]['label']:
                flag1.append(0)
            else:
                flag1.append(1)

        if sum(flag1) == 0 and sum(flag) == 0:
            # print('True')
            res = 'True'
            return res
        else:
            # print('False')
            res = 'False'
            return res




    @classmethod
    def is_pass_assessment(cls, labels):
        '''
        验证是否都存在匹配
        '''
        for label in labels:
            if not label.get('isMatched'):
                return False
        return True

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print("Hi, {0}".format(name))  # Press ⌘F8 to toggle the breakpoint.


if __name__ == '__main__':

    #print(os.getcwd())#/Users/edz/Desktop
    path0 = '/Users/edz/Desktop/test_A'
    path1 = '/Users/edz/Desktop/test_B'
    file_list0 = os.listdir(path0)
    file_list1 = os.listdir(path1)

    for file in file_list0:
        file1 = os.path.join(path0,file)

        if file in file_list1:
            print('hhh')
            file2 = os.path.join(path1,file)
            TwoPersonCompareAlgo(file1,file2).compare_json_new()


        # data = json.load(open(file))
        # print(len(data['shapes']))


    # file = '/Users/edz/Desktop/test_A/0007DCB4-DBF0-4CDB-885A-D925DD1943BF.json'
    # data = json.load(open(file))
    # for i in range(len(data['shapes'])):
    #     label = data['shapes'][i]['label']
    #     print(label)
    # print(data['shapes'][1]['points'])
    # print(data['shapes'][1]['points'][1])
    # print(data['shapes'][1]['points'][1][0])




