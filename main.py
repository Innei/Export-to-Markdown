import pymysql
import time
import os
from re import sub


class ExportToMarkdown():
    def __init__(self, host: str, user: str, database: str, passwd=''):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = 3306
        self.database = database
        self.connectSQL()
        self.select_data()
        self.to_file()

    def connectSQL(self):
        try:
            sql = pymysql.connect(host=self.host, user=self.user, password=self.passwd, database=self.database,
                                  charset='utf8')
        except pymysql.Error as e:
            print(e)
            quit(1)
        else:
            print('连接成功')
            self.cur = sql.cursor()
            self.db = sql

    def select_data(self):
        db = self.db
        cur = self.cur
        data = []
        # 获取标题
        cur.execute('SELECT title FROM typecho_contents')
        unparse = cur.fetchall()
        title = [i for t in unparse for i in t]
        # print(title)
        data.append(title)

        # 获取slug
        cur.execute('SELECT slug FROM typecho_contents')
        unparse = cur.fetchall()
        slug = [i for t in unparse for i in t]
        data.append(slug)

        # 获取创建时间
        cur.execute('SELECT created FROM typecho_contents')
        unparse = cur.fetchall()
        created = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i)) for t in unparse for i in t]
        data.append(created)

        # 获取修改时间
        cur.execute('SELECT modified FROM typecho_contents')
        unparse = cur.fetchall()
        modified = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i)) for t in unparse for i in t]
        data.append(modified)

        # 获取文章内容
        cur.execute('SELECT text FROM typecho_contents')
        unparse = cur.fetchall()
        text = [sub('^<!--markdown-->', '', i) for t in unparse for i in t]
        data.append(text)

        # print(data)
        self.data = data

    def to_file(self):
        data = self.data
        try:
            os.mkdir('export')
        except FileExistsError:
            pass

        # data = [title,slug,created,modified,text]
        for index, file_name in enumerate(data[1]):
            with open('export/' + file_name + '.md', 'w+', encoding='utf-8') as f:
                content = '''---
title: {title}
date: {date}
tags: {tags}
categories: {categories}
---

{text}'''
                f.write(content.format(title=data[0][index], date=data[2][index], tags='', categories='',
                                       text=data[4][index]))


if __name__ == "__main__":
    pass
