# -*- coding:utf-8 -*-

######
#   每个问题的回答类
######
class Solution:
    def __init__(self):
        self.is_solve = False # 是否解决
        self.is_first = False #是否是第一个解决
        self.solve_time = 0 # 解决所发的时间
        self.error_time = 0 # 错误的次数
        self.mark = 0 # 获得的分数
