#!/usr/bin/env python    
#encoding: utf-8  

import sys    
reload(sys)
sys.setdefaultencoding('utf8')

import requests
from lxml import etree
from Esql.Builder import Builder as MySQL
import numpy as np
import matplotlib.pyplot as plt
from config import configs

# 爬取页面信息
def get_page(i):
    url = 'https://movie.douban.com/top250?start='+str(25*(i-1))
    html = requests.get(url).content.decode('utf-8')
    selector = etree.HTML(html)

    movies = []
    #category 
    info = selector.xpath('//div[@class="info"]/div[@class="bd"]/p[1]/text()')
    #movice's name
    name = selector.xpath('//div[@class="info"]/div[@class="hd"]/a/span[@class="title"][1]/text()')
    #movice's href
    href = selector.xpath('//div[@class="info"]/div[@class="hd"]/a/@href')

    for i,j in enumerate(info[1::2]):
        movie = {}
        raw = str(j).strip()
        movie['cate'] = raw.split('/')[-1][2:].split(' ')
        movie['name'] = name[i]
        movie['href'] = href[i]
        movies.append(movie)
    return movies

# 储存数据
def save_data(db, data):
    for movie in data:
        db.table('movie').insert({'name': movie['name'], 'href': movie['href']})
        movie_id = db.getInsertId()
        for cate in movie['cate']:
            cate_id = db.table('movie_category').where('name', cate).pluck('id')
            if not cate_id:
                db.table('movie_category').insert({'name': cate})
                cate_id = db.getInsertId()
                
            db.table('movie_category_relation').insert({'movie_id': movie_id, 'cate_id': cate_id})

# 数据分析与展示
def pylot_show(db):
    cates = db.table('movie_category').get()
    count = []   # 每个分类的数量
    category = []  # 分类

    for cate in cates:
        count.append(db.table('movie_category_relation').where('cate_id', cate['id']).count())
        category.append(cate['name'])

    y_pos = np.arange(len(category))  # 定义y轴坐标数
    plt.barh(y_pos, count, align='center', alpha=0.4)  # alpha图表的填充不透明度(0~1)之间
    plt.yticks(y_pos, category)  # 在y轴上做分类名的标记

    for count, y_pos in zip(count, y_pos):
        # 分类个数在图中显示的位置，就是那些数字在柱状图尾部显示的数字
        plt.text(count, y_pos, count,  horizontalalignment='center', verticalalignment='center', weight='bold')  
    plt.ylim(+28.0, -1.0) # 可视化范围，相当于规定y轴范围
    plt.title(u'豆瓣电影TOP250')   # 图表的标题
    plt.ylabel(u'电影分类')     # 图表y轴的标记
    plt.subplots_adjust(bottom = 0.15) 
    plt.xlabel(u'分类出现次数')  # 图表x轴的标记
    plt.savefig('douban.png')   # 保存图片

if __name__ == '__main__':
    db = MySQL(configs['db'])

    # 数据存储
    # for i in range(10):
    #     movies = get_page(i+1)
    #     save_data(db, movies)
    pylot_show(db)


