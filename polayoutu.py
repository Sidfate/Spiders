# !/usr/bin/env python
# encoding: utf-8
import sys
import requests
import redis
import time
import json
from lxml import etree 

reload(sys)
sys.setdefaultencoding('utf8')

get_edition_num_url = "http://www.polaxiong.com/collections/get_edition_num"
get_entries_url = "http://www.polaxiong.com/collections/get_entries_by_collection_id/"
r = redis.Redis(host='localhost', port=6379, db=0)

def get_edition_num():
	req = requests.get(get_edition_num_url)
	res = req.json()

	return res['data']['edition']

def get_entries(edition_num):
	url = get_entries_url+str(edition_num)
	req = requests.get(url)
	res = req.json()

	pics = res['data']
	entries = []

	for entry in pics:
		entries.append(entry['thumb'])
	return entries
	
def save_redis(data):
	key = time.strftime('%Y%m%d')
	r.set(key, json.dumps(data), 24*3600)

def main():
	edition_num = get_edition_num()
	pic_data = get_entries(edition_num)
	save_redis(pic_data)

if __name__ == '__main__':
    main()