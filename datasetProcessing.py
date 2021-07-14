import os
import shutil
#shutil可以让文件快速地被移动、复制、删除和修改
# import JsonMatching
from JsonMatching import TwoPersonCompareAlgo
import json
from JsonReGenerator import JsonReGenerator

'''
主要完成三件事情
1 三个人的标注结果 分成A、B两组，作为输入
2 将A B两个文件中的json文件进行对比，审核通不通过
3 针对不能一次性通过的json文件进行分类，json再生成
'''


#处理数据集，分数据
def dataDivide(source_path0,source_path1,source_path2,destination_path0,destination_path1):
    #将三个人的数据，分成两个数据集
    file_list0 = os.listdir(source_path0)
    file_list1 = os.listdir(source_path1)
    file_list2 = os.listdir(source_path2)
    file_list_A = []
    file_list_B = []

    #先将path0中的文件放到目标文件夹0中，并记录文件名
    for file in file_list0:
        a = file.split('.')[0]
        file_list_A.append(a)
        source_file = os.path.join(source_path0,file)
        shutil.copy(source_file,destination_path0)

    #对剩下的两个文件夹进行筛选，除去A中重复的，均放入B中
    for file in file_list1 :
        a = file.split('.')[0]
        source_file = os.path.join(source_path1, file)
        if a not in file_list_A:
            file_list_A.append(a)
            shutil.copy(source_file, destination_path0)
        else:
            file_list_B.append(a)
            shutil.copy(source_file, destination_path1)

    for file in file_list2:
        a = file.split('.')[0]
        source_file = os.path.join(source_path2, file)
        if a not in file_list_A:
            file_list_A.append(a)
            shutil.copy(source_file, destination_path0)
        else:
            file_list_B.append(a)
            shutil.copy(source_file, destination_path1)
    print('done~')




def JsonCheck(fileA,fileB):
    '''
    经过数据分割后，发现A与B中的json文件数目并不相等，出现了一张图片两个人标，一个标了另一个没标的情况
    input：分好的文件A 及 B
    output：不同类的list，例如 通过、图片仅标注一次（即该图片仅有一个json文件）、需二次处理的（情况较为复杂，需要重新生成json文件，处理过后才能用作最终的数据集
    '''

    file_listA = os.listdir(fileA)
    file_listB = os.listdir(fileB)

    #防止A、B两个列表不等且A比B短的情况
    if len(file_listA) < len(file_listB):
        file_listA,file_listB = file_listB,file_listA


    #label、bbox均对应上了
    Matched_list = []

    #A中有而B中无的，即该图片仅标注了一遍（或者说两个人中的一个人认为该图片中不存在我们需要的组件）
    OnlyOne_list = []

    #需二次处理的图片，bbox数目不对/bbox位置不对（这里要求IOU大于0.7,即重叠面积占80%以上才能算是匹配上了，后期可调整）/bbox对上了但label不对
    OnceMore_list = []

    for file in file_listA :
        if file[-5:] == '.json':

            # A中有而B中无的，即该图片仅标注了一遍
            if file not in file_listB:
                OnlyOne_list.append(file)

            else:
                # print(file)
                json_A = os.path.join(fileA,file)
                json_B = os.path.join(fileB,file)

                flag = TwoPersonCompareAlgo(json_A,json_B).compare_json_new()
                # print(flag)
                if flag == 'True':
                    Matched_list.append(file)
                else:
                    OnceMore_list.append(file)
    return Matched_list,OnlyOne_list,OnceMore_list


def JsonGeneratorProcess( fileA_path, fileB_path, OnceMore_list,dst_path ):
    '''
    针对标注有误的图片取交集 重新生成json文件（取json中匹配上的部分，先生成能用的数据集)
    '''
    for file in OnceMore_list:
        json_a = os.path.join(fileA,file)
        json_b = os.path.join(fileB,file)

        JsonReGenerator(json_a,json_b,dst_path).jsonReGenerator()


def StatisticAnalyse(filePath,Matched_list):
    """
    统计通过率情况
    input：每个人的标注文件路径，匹配上的list
    output：这个人的标注通过率
    """
    filelist = os.listdir(filePath)
    length = 0
    matched_num = 0
    for file in filelist:
        if file[-5:] == '.json':
            length += 1
            if file in Matched_list:
                matched_num += 1
    return matched_num / length


if __name__ == '__main__':
    #数据集分流
    # path0 = r'./img1000_1_labeled'
    # path1 = r'./img1000_2_labeled'
    # path2 = r'./img1000_3_labeled'
    #
    # obj_path_A = r'./img1000_A'
    # obj_path_B = r'./img1000_B'
    #
    # dataDivide(path0,path1,path2,obj_path_A,obj_path_B)

    fileA = r'./img1000_A'
    fileB = r'./img1000_B'
    reJson_dst_path = r'./img1000_reJson'
    print('kkk')
    Matched_list, OnlyOne_list, OnceMore_list = JsonCheck(fileA,fileB)
    print(len(Matched_list),len(OnlyOne_list),len(OnceMore_list))
    # print(OnceMore_list)
    JsonGeneratorProcess(fileA,fileB,OnceMore_list,reJson_dst_path)

    #标注情况统计
    # file_Q = r'./img1000_2_labeled'
    # file_H = r'./img1000_1_labeled'
    # file_K = r'./img1000_3_labeled'
    # Q = StatisticAnalyse(file_Q,OnceMore_list)
    # H = StatisticAnalyse(file_H, OnceMore_list)
    # K = StatisticAnalyse(file_K, OnceMore_list)
    # print('Qinglian',Q)
    # print('Hui',H)
    # print('Kai',K)


    #分数据
    # onceMore_A = r'./img1000_onceMore_A'
    # onceMore_B = r'./img1000_onceMore_B'
    # for file in OnceMore_list:
    #     if file in os.listdir(fileA):
    #         fiA = os.path.join(fileA,file)
    #         shutil.copy(fiA,onceMore_A)
    #     if file in os.listdir(fileB):
    #         fiB = os.path.join(fileB,file)
    #         shutil.copy(fiB,onceMore_B)








