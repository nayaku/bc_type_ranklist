# -*- coding:utf-8 -*-
import re
import urllib2
import codecs
import time
import shutil
import Setting
import User
import Problem
import Solution

RANKLIST_URL = Setting.url


######
#   RankList读取类
######
class ReadRankList:
    # 初始化
    def __init__(self):
        self.content = u''
        self.start_tr = 5  # 从第几个tr开始读取
        self.problem_number = 0  # 问题数量
        self.problem_list = []  # 问题列表
        self.users_list = []  # 用户列表
        self.rank_file = None  # rank文件实例

    # 运行，得到User类的列表
    def run(self):
        self.content = self.read_page(RANKLIST_URL)
        self.problem_list = self.get_problem_list()
        self.users_list = self.get_users()
        self.problem_solution_state()
        print u'获取用户信息完毕。'
        self.sort_users()
        print u'排序结束。'
        print u'开始输出。'

        self.write_rank_list()
        print u'写入排名文件完成。'

    # 连接到页面，并返回页面内容
    @staticmethod  # 静态方法
    def read_page(page_url):
        t_str = "Read page: " + str(page_url)
        print t_str
        request = urllib2.Request(page_url)
        response = urllib2.urlopen(request, timeout = Setting.time_out)
        content = response.read().decode("utf-8", "ignore")
        return content

    # 获取比赛的题目列表
    def get_problem_list(self):
        # 匹配
        pattern = re.compile(u'''<td><a style='color:#000000;' href='(.*?)'>(.*?)</a></td>''', re.S)
        items = re.findall(pattern, self.content)
        self.problem_number = len(items)
        # 生成空问题列表
        problem_list = [Problem.Problem() for i in range(len(items))]
        # 填入数值
        for i in range(len(problem_list)):
            problem_list[i].link = Setting.MNNU_url + items[i][0]
            problem_list[i].name = items[i][1]
        for i in range(min(len(problem_list), len(Setting.mark_list))):
            problem_list[i].mark = Setting.mark_list[i]
        return problem_list

    # 获取Users的列表
    def get_users(self):
        users = []
        # 匹配
        pattern = re.compile(u'''<tr>(.*?)</tr>''', re.S)
        items = re.findall(pattern, self.content)
        for item in items[self.start_tr:]:
            users.append(self.get_each_user(item))
        return users

    # 获取每个User的信息
    def get_each_user(self, content):
        # 匹配
        pattern = re.compile(u'''<a href='(.*?)'>(.*?)</a>.*?'''
                             + u'''<td><a href="(.*?)">(.*?)</a></td>''', re.S)
        items = re.findall(pattern, content)
        items = items[0]

        # 开始填装入User类
        user = User.User()
        user.url = Setting.MNNU_url + items[0]
        user.name = items[1].replace('\t', '').replace('\r\n', '').replace(' ', '')
        user.status_url = Setting.MNNU_url + items[2]
        user.ac_number = items[3]
        # 答题情况
        user.solution = [Solution.Solution() for i in range(self.problem_number)]
        # 获取答题情况
        pattern = re.compile(u'''<td(.*?)</td>''', re.S)
        solution_list = re.findall(pattern, content)
        solution_list = solution_list[4:]
        index = 0
        for solution in solution_list:
            user.solution[index], mark = self.get_each_solution(solution, index)
            index += 1
            user.mark += mark
        return user

    # 每个问题的解决情况
    def get_each_solution(self, solution, index):
        solve_problem = Solution.Solution()
        # 判断是否第一个解决这个问题
        pattern = re.compile(u'''background-color:(.*?);color:white;"''', re.S)
        items = re.findall(pattern, solution)
        if items:
            for item in items:
                if item == '#00ff99':
                    solve_problem.is_first = True
        # 如果AC算出因为时间而减少的分数
        pattern = re.compile(u'''<div class='rank_actime'>(.*?):(.*?):(.*?)</div>''', re.S)
        items = re.findall(pattern, solution)
        if len(items):
            items = items[0]
            solve_problem.is_solve = True
            cost_time = int(items[0]) * 60 * 60 + int(items[1]) * 60 + int(items[2])  # 花费时间(s)
            solve_problem.solve_time = cost_time
            cost_time /= 60  # 花费时间转化为(min)
            mark = self.problem_list[index].mark - cost_time * Setting.decrease_mark_each_minute
            if mark < (1.0 - Setting.max_decrease_with_time) * self.problem_list[index].mark:
                mark = int((1.0 - Setting.max_decrease_with_time) * self.problem_list[index].mark)
            solve_problem.mark = mark

        # 获取错误的次数
        pattern = re.compile(u'''class="rank_errcount">\(-(.*?)\)</div>''')
        items = re.findall(pattern, solution)
        if len(items):
            items = items[0]
            solve_problem.error_time = int(items)
            if solve_problem.is_solve:
                mark = solve_problem.mark - solve_problem.error_time * Setting.decrease_mark_each_error
                if mark < self.problem_list[index].mark * Setting.base_mark:
                    mark = int(Setting.base_mark * self.problem_list[index].mark)
                solve_problem.mark = mark
        # 返回解决实例

        return solve_problem, solve_problem.mark

    # 处理Problem总的回答情况
    def problem_solution_state(self):
        for user in self.users_list:
            index = 0
            for solution in user.solution:
                if solution.is_solve:
                    self.problem_list[index].ac_number += 1
                    self.problem_list[index].submit_number += 1
                self.problem_list[index].submit_number = self.problem_list[index].submit_number + solution.error_time
                index += 1

    # 排序
    def sort_users(self):
        self.users_list.sort()
        rank = 1
        for i in range(len(self.users_list)):
            if i != 0 and self.users_list[i - 1].mark == self.users_list[i].mark:
                self.users_list[i].rank = self.users_list[i - 1].rank
            else:
                self.users_list[i].rank = rank
            rank += 1

    # 写入排名文件
    def write_rank_list(self):
        self.begin_write()
        self.write_table_header()
        for user in self.users_list:
            self.write_user_solution(user)
        self.write_poblems_state()
        self.finish_write()
        self.create_finish_file()

    # 开始写入
    def begin_write(self):
        self.rank_file = codecs.open(Setting.temp_rank_list_file_name, "w", "utf-8")  # 开始和要写入的文件挂钩
        self.rank_file.write(u'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
            <link href="table_styles.css" rel="stylesheet" type="text/css"/>
            <link href="Ranks.css" rel="stylesheet" type="text/css"/>
            <title>排名</title>
        </head>
        <body>
        <h1 style="text-align:center;">排名</h1>

        <table id="mytable" cellspacing="0" style="margin:auto ;width: auto">
''')
        str_time = time.strftime('%Y-%m-%d %X', time.localtime()).encode('utf-8')
        str_time = u'<caption>Update at ' + str_time + u' </caption>'
        self.rank_file.write(str_time)

    # 写入表头
    def write_table_header(self):
        self.rank_file.write(u"<tr>")
        self.rank_file.write(u'<th class="rank">#</th>')
        self.rank_file.write(u'<th class="name">Name</th>')
        self.rank_file.write(u"<th>Score</th>")
        for problem in self.problem_list:
            content_str = u'<th><div class="table_title"><a href="' + problem.link + u'" class="problem">' + problem.name + u'</a></div><div>' + str(
                problem.mark) + u'</div></th>'
            self.rank_file.write(content_str)
        self.rank_file.write(u'</tr>')

    # 写入用户解决情况
    def write_user_solution(self, user):
        self.rank_file.write(u"<tr>")
        self.rank_file.write(u'<td class="rank">' + str(user.rank) + u'</td>')
        self.rank_file.write(u'<td><a href="' + user.url + u'" class="user_name">' + user.name + u'</a></td>')
        self.rank_file.write(u'<td><a href="' + user.status_url + u'">' + str(user.mark) + u'</a></td>')
        for solution in user.solution:
            self.rank_file.write(u'<td>')
            if solution.is_solve:
                error_time = u''
                if solution.error_time > 0:
                    error_time = u'<span class="error">(' + str(-1 * solution.error_time) + u')</span>'
                if solution.is_first:
                    self.rank_file.write(u'<div class="first_ac">' + str(solution.mark) + error_time + u'</div>')
                else:
                    self.rank_file.write(u'<div class="score">' + str(solution.mark) + error_time + u'</div>')
                slove_tiem_str = u'%.2d:%.2d:%.2d' % (
                    solution.solve_time / 60 / 60, (solution.solve_time / 60) % 60, solution.solve_time % 60)
                self.rank_file.write(u'<div class="time">' + slove_tiem_str + u'</div>')
            else:
                if solution.error_time > 0:
                    self.rank_file.write(u'<div class="error">-' + str(solution.error_time) + u'</div>')
            self.rank_file.write(u'</td>')
        self.rank_file.write(u'</tr>')

    # 写入所有问题解决情况
    def write_poblems_state(self):
        self.rank_file.write(u"<tr>")
        self.rank_file.write(u'<td></td>')
        self.rank_file.write(u'<td>')
        self.rank_file.write(u'<div><span class="ac">Accepted</span>/<span class="tried">Tried</span></div>')
        self.rank_file.write(u'<div class="ratio">Ratio</div>')
        self.rank_file.write(u'</td><td></td>')
        for problem in self.problem_list:
            self.rank_file.write(u'<td><div><span class="ac">' + str(problem.ac_number) + u'</span>/')
            self.rank_file.write(u'<span class="tried">' + str(problem.submit_number) + u'</span></div>')
            if problem.submit_number is not 0:
                ratio = 100 * problem.ac_number / problem.submit_number
            else:
                ratio = 0
            self.rank_file.write(
                u'<div class="ratio">' + str(ratio) + u'%</div></td>')

    # 结束写入
    def finish_write(self):
        self.rank_file.write(u'</table>')
        self.rank_file.write(u'</body>')
        self.rank_file.write(u'</html>')

    # 生成最终文件
    def create_finish_file(self):
        self.rank_file.close()
        shutil.move(Setting.temp_rank_list_file_name, Setting.rank_list_file_name)
