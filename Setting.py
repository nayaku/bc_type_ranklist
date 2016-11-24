# -*- coding:utf-8 -*-

######
#   设置区域
######
# MNNUOJ网址
MNNU_url = 'http://acm.mnnu.edu.cn'
# Content id 地址

# Contest RANKLIST 网址
url = 'http://acm.mnnu.edu.cn/Contest/ranklist/cid/2027.htm'
# 重试时间
time_out = 60
# 默认分数
default_mark = 1000
# 每题的分数，如果未指定为默认分数
mark_list = [500, 500, 500, 900, 1000, 1200, 1200, 1500, 2000]
# 每题最大随时间而减少的分数比率
max_decrease_with_time = 1.0 / 2.0
# 每分钟减少的分数
decrease_mark_each_minute = 4
# 每次错误减少的分数
decrease_mark_each_error = 50
# 每题保底比率
base_mark = 2.0 / 5.0
# 排名文件名
rank_list_file_name = 'RankList.html'
# 临时排名文件名
temp_rank_list_file_name = '~RankList.html'
# 能否循环执行
can_loop = False
# 如果循环执行，循环的间隔时间(s)
interval_time = 120
