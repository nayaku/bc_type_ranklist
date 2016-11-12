# -*- coding:utf-8 -*-

######
#   用户类
######
class User:
    def __init__(self, name = u''):
        # 实例成员
        self.name = name  # 名字
        self.url = u''  # 个人主页的地址
        self.status_url = u''  # 个人评判总状态
        self.ac_number = 0  # AC题数
        self.mark = 0  # 分数
        self.rank = 0  # 排名
        self.solution = []  # 回答问题的列表
    # 排序
    def __cmp__(self, other):
        return self.mark > other.mark and -1 or 1
    def p(self):
        print self.name , self.url
