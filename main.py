import pymysql
import time
import os
from re import sub


class ExportToMarkdown():
    def __init__(self, host: str, user: str, database: str, passwd=''):
        self.host = host
        self.user = user
        self._passwd = passwd
        self.port = 3306
        self.database = database
        self._connectSQL()
        self._select_data()
        self._to_file()

    def _connectSQL(self):
        try:
            sql = pymysql.connect(host=self.host, user=self.user, password=self._passwd, database=self.database,
                                  charset='utf8')
        except pymysql.Error as e:
            print(e)
            quit(1)
        else:
            print('连接成功')
            self.cur = sql.cursor()
            self.db = sql

    def _select_data(self):
        db = self.db
        cur = self.cur
        data = []
        # 获取标题
        cur.execute('SELECT title FROM typecho_contents where type = \'post\'')
        unparse = cur.fetchall()
        title = [i for t in unparse for i in t]
        # print(title)
        data.append(title)

        # 获取slug
        cur.execute('SELECT slug FROM typecho_contents where type = \'post\'')
        unparse = cur.fetchall()
        slug = [i for t in unparse for i in t]
        data.append(slug)

        # 获取创建时间
        cur.execute('SELECT created FROM typecho_contents where type = \'post\'')
        unparse = cur.fetchall()
        created = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i)) for t in unparse for i in t]
        data.append(created)

        # 获取修改时间
        cur.execute('SELECT modified FROM typecho_contents where type = \'post\'')
        unparse = cur.fetchall()
        modified = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i)) for t in unparse for i in t]
        data.append(modified)

        # 获取文章内容
        cur.execute('SELECT text FROM typecho_contents where type = \'post\'')
        unparse = cur.fetchall()
        text = [sub('^<!--markdown-->', '', i) for t in unparse for i in t]
        data.append(text)

        # 获取分类
        # 注意 typecho把slug当做永久链接的一部分, 而hexo只需要分类名 所以提取slug 而不是title
        cur.execute('SELECT * FROM typecho_metas where type = \'category\'')
        unparse = cur.fetchall()
        categories = {}
        for i in unparse:
            categories[i[0]] = i[2],  # mid : slug
        # data.append(categories)

        # 获取标签

        cur.execute('SELECT * FROM typecho_metas where type = \'tag\'')
        unparse = cur.fetchall()
        tags = {}
        for i in unparse:
            tags[i[0]] = i[2],  # mid : slug

        # data.append(tags)

        # 获取对应关系

        cur.execute('select * from typecho_relationships order by cid asc')
        unparse = cur.fetchall()
        relationships = []
        before = 0
        for i in unparse:
            relationship = {}
            if before == i[0]:
                relationships[-1][i[0]].append(i[1])

            else:
                relationship[i[0]] = [i[1]]
                before = i[0]
                relationships.append(relationship)

        # data.append(relationships)
        # print(data)

        # tags哈希表
        parse_tags = []
        for relationship in relationships:
            for index in relationship.keys():
                parse_tag = []
                for item in relationship[index]:
                    if tags.get(item):
                        parse_tag.append(tags.get(item))
                    else:
                        parse_tag.append('')
            if parse_tag:
                parse_tags.append(parse_tag)
            else:
                parse_tags.append([''])

            data.append(parse_tags)
            # cates
            parse_cates = []
            for relationship in relationships:
                for index in relationship.keys():
                    parse_cate = []
                    for item in relationship[index]:
                        if categories.get(item):
                            parse_cate.append(categories.get(item))
                if parse_cate:
                    parse_cates.append(parse_cate)

            data.append(parse_cates)

            self.data = data

    def _to_file(self):
        data = self.data
        try:
            os.mkdir('export')
        except FileExistsError:
            pass

        # data = [title,slug,created,modified,text,tags:list->tuple,cates:list->tuple]
        for index, file_name in enumerate(data[1]):
            with open('export/' + file_name + '.md', 'w+', encoding='utf-8') as f:
                content = '''---
title: {title}
date: {date}
tags: {tags}
categories: {categories}
---

{text}'''  # tags
                # data[5][index]
                tags = '\n'
                if data[5][index] != ['']:
                    for tag in data[5][index]:
                        for t in tag:
                            tags += '- ' + t + '\n'
                elif data[5][index] == ['']:
                    tags = ''

                cates = '\n'
                if data[6][index] != ['']:
                    for cate in data[6][index]:
                        for t in cate:
                            cates += '- ' + t + '\n'
                elif data[6][index] == ['']:
                    cates = ''

                f.write(content.format(title=data[0][index], date=data[2][index], tags=tags,
                                       categories=cates,
                                       text=data[4][index]))


if __name__ == "__main__":
    ExportToMarkdown(host='', user='', database='', passwd='')
