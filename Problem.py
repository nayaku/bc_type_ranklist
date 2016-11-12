# -*- coding:utf-8 -*-
import Setting


######
#   问题类
######
class Problem:
    def __init__(self):
        # 实例成员
        self.link = u''  # 题目链接
        self.mark = Setting.default_mark  # 题目的分数
        self.name = u''  # 题号
        self.ac_number = 0 # AC人数
        self.submit_number = 0 # 提交次数
