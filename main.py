# -*- coding:utf-8 -*-
import ReadWriteRankList
import time
import Setting

# 这里是主文件。用 python main.py 运行这个脚本
while True:
    readWriteRankList = ReadWriteRankList.ReadRankList()
    readWriteRankList.run()
    if Setting.can_loop is False:
        break
    else:
        time.sleep(Setting.interval_time)
