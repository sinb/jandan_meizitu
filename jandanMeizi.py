# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 10:26:29 2015

@author: hehe
"""
import sys
import urllib2
import re
from bs4 import BeautifulSoup
import os
import mechanize
import time
import random
class jandanCrawler():
    
    def __init__(self):
        self.browser = mechanize.Browser()
        self.browser.set_handle_robots(False)

        header = {'Accept': 'text/html,application/xhtml+xml,applicatiaaon/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
        header['User-Agent'] = 'Mozilla/{0}.{1} (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/{2}.0.1271.64 Safari/537.{3}'.format(random.randint(1,9), random.randint(1,9), random.randint(10,30), random.randint(1,20))
        self.browser.addheaders = header.items()

    def getHtml(self, url):
        response = self.browser.open(url)
        return response.get_data()

class jandan_meizi():
    def __init__(self, root_dir):
        self.root_dir = root_dir
        
    def findMeizi(self, formatted_result, oo=500):  
        #Next build lxml tree from formatted_result
        soup = BeautifulSoup(formatted_result)
        meizi_list = soup.findAll('li', id=re.compile('comment-[0-9]*'))
        for meizi in meizi_list:
            return_result = self.filterOO(meizi, oo)
            if return_result[3] == 1:
                self.downloadMeizi(return_result)     
                
                
        
    def filterOO(self, item, oo):
        vote = item.find('div', {"class": "vote"})
        support = int(vote.findAll('span',id=re.compile('cos_support-[0-9]*'))[0].text)
        unsupport = int(vote.findAll('span',id=re.compile('cos_unsupport-[0-9]*'))[0].text)
        img_link = item.find('a', {"class":"view_img_link"})
        if img_link is not None:
            img_url = img_link.get('href')        
            if support >= oo:
                return support, unsupport, img_url, 1
            else:
                return support, unsupport, img_url, 0
        else:
            ## error code 
            return 'no','no','no',2
                
    def downloadMeizi(self, url_ooxx):
        oo, xx, url, _ = url_ooxx
        file_name = url.split('/')[-1]
        file_name = str(oo) + '_' + str(xx) + '_' + file_name
        u = urllib2.urlopen(url)

        with open(os.path.join(self.root_dir, file_name), 'wb') as f:
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            print "Downloading: %s Bytes: %s" % (file_name, file_size)
            
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
            
                file_size_dl += len(buffer)
                f.write(buffer)
                status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                status = status + chr(8)*(len(status)+1)
                print status,
            print

def handle_argv():
    if len(sys.argv) == 4:
        start, end, oo = sys.argv[1:]
    elif len(sys.argv) == 3:
        start, end = sys.argv[1:]
        oo = 500
    else:
        print "输入格式错误"
        print "参考格式:"
        print "python jandanMeizi.py 1500 1400 #起始页面1500,终止页面1400,默认oo阈值是500"
        print "或者自定义阈值如下:"
        print "python jandanMeizi.py 1500 1400 200"
        raise
    return start, end, oo
              
if __name__ == '__main__':
    base_url = 'http://jandan.net/ooxx/page-'

    try:
        start, end, oo_threshold = handle_argv()
        start = int(start)
        end = int(end)
        oo_threshold = int(oo_threshold)
        print "开始页面:{0}, 终止页面{1}, oo阈值:{2}".format(start, end, oo_threshold)
    except TypeError:
        print sys.exit(0)
    
    if not os.path.isdir("meizitu"):
        os.mkdir("meizitu")    
    if not os.path.isdir("htmls"):
        os.mkdir("htmls") 
        
    jandan_crawler = jandanCrawler()        
    my_meizi = jandan_meizi('meizitu')

    for page in range(start, end-1, -1):
            
        url =  base_url + str(page)
        print url
        try:
            html = jandan_crawler.getHtml(url)
            ## if you want to keep the html for furthur crawling
            with open(os.path.join('htmls', str(page)+'.html'), 'wb') as f:
                f.write(html)
            my_meizi.findMeizi(html, oo=oo_threshold)
            time.sleep(3)                
        except mechanize.HTTPError as e:
            print "错误"
            error_code = e.getcode()
            if int(error_code) == 404:
                print error_code
                print "网址错了,试试网页还能打开不?"
            else:
                print error_code
                print "换个user agent试试"
                try_count = 1
                while try_count <= 10:
                    jandan_crawler = jandanCrawler()
                    try:
                        html = jandan_crawler.getHtml(url)
                        ## if you want to keep the html for furthur crawling
                        with open(os.path.join('htmls', str(page)+'.html'), 'wb') as f:
                            f.write(html)
                        my_meizi.findMeizi(html, oo=oo_threshold)
                        time.sleep(3)  
                        break
                    except mechanize.HTTPError as e:
                        try_count += 1                         

                    