#coding=utf-8
import requests as req
import re
import time
from selenium import webdriver
import tkinter
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import Text as tkText
from random import random

__DOC__ = '''

https://blog.csdn.net/www89574622/article/details/87974931

http://chromedriver.storage.googleapis.com/index.html?path=75.0.3770.140/

use https://chrome.google.com/webstore/detail/chropath/ljngjbnaijcbncmcnjfhigebomdlkcjo
to get xpath
'''




comma_pattern = '''(?:“)(.+?)(?:”)'''
title_search = re.compile(comma_pattern,re.DOTALL|re.MULTILINE|re.UNICODE)

bibtex_button_link_pattern = '''<a\s+href."(.+?)".*?>BibTeX</a>'''
bibtex_button_search = re.compile(bibtex_button_link_pattern,re.DOTALL|re.MULTILINE|re.UNICODE)

citation_pattern = '''<pre.*?>(.+)</pre>'''
citation_search = re.compile(citation_pattern,re.DOTALL|re.MULTILINE)

google_cn='''https://scholar.google.co.uk/scholar?hl=zh-CN&as_sdt=0%2C5&q={}&btnG='''
google_cn='''https://scholar.google.com/scholar?hl=zh-CN&as_sdt=0%2C5&q={}&btnG=&oq='''
bing_cn='''https://cn.bing.com/academic/search?q={}'''

opt = webdriver.ChromeOptions()
driver = None #webdriver.Chrome(options=opt)

# tkroot
root = None


def sleep(sec):
    r = random()/10.0
    time.sleep(sec+r)


def get_titles_comma_sep(text):
    titles = title_search.findall(text)
    return titles

def get_titles_linebreak_sep(text):
    titles=[]
    tmp = []
    i=0
    textlen = len(text)
    while i<textlen:
        s = ''
        while i<textlen:
            if text[i] != '\n':
                s+=text[i]
                i+=1
                continue
            else:
                s+=text[i]
                i+=1
                tmp.append(s)
                s=None
                break
        if s is not None:
            tmp.append(s)

    s=''
    for segment in tmp:
        if segment!='\n':
            s= f'{s} {segment}'
        else:
            if s not in ['','\n']:
                titles.append(s)
                s=''
            else:
                s=''
    if len(s)>0:
        titles.append(s)

    return titles

def raw_titles_to_plus_sep(titles):
    res = []
    for t in titles:
        t=t.strip(',.“”-_')
        t=t.replace('-','')
        t=t.replace('_','')
        res.append('+'.join(t.strip().split()))
    return res

def query_google_with_retry(plus_sep_title,retry_times=10):
    global driver
    url = google_cn.format(plus_sep_title)
    driver.get(url)
    sleep(0.1)
    text = driver.page_source
    if len(re.findall("被引用次数",driver.page_source))==0:
        return None # no resutls found

    cite_button = driver.find_element_by_xpath("//a[@class='gs_or_cit gs_nph']//*[@class='gs_or_svg']")
    cite_button.click()

    sleep(0.3)
    try_times = retry_times
    SUCCEED=False
    while try_times>0:
        try:
            bib_link = driver.find_element_by_xpath("//a[contains(text(),'BibTeX')]")
            bib_link.click()
            SUCCEED=True
            break
        except:
            print('failed to get the bibtex link, retrying',try_times)
            sleep(0.2)
            try_times -= 1

    if not SUCCEED:
        print('try but failed to locate the bibtex download link within',retry_times,'times')
        return None

    sleep(0.2)
    res = citation_search.findall(driver.page_source)
    if len(res)!=0:
        return res[0]
    else:
        return None

def query_bing_with_retry(plus_sep_title,retry_times=10):
    global driver
    url = bing_cn.format(plus_sep_title)
    driver.get(url)
    sleep(0.1)
    text = driver.page_source
    if len(re.findall("引用",driver.page_source))==0:
        return None # no resutls found

    cite_button = driver.find_element_by_class_name("caption_cite")
    cite_button.click()

    sleep(0.3)
    try_times = retry_times
    SUCCEED=False
    page_source = driver.page_source
    while try_times>0:
        try:
            #bib_link = bibtex_button_search.findall(driver.page_source)[0]
            bib_link = driver.find_element_by_xpath("//a[contains(text(),'BibTeX')]")
            bib_link_url = bib_link.get_attribute('href')
            bibpage = req.get(bib_link_url)
            if bibpage.status_code == 200:
                page_source = bibpage.text.replace('<br/>','\n')
            else:
                raise Exception('cannot get the page source')
            SUCCEED=True
            break
        except:
            print('failed to get the bibtex link, retrying',try_times)
            sleep(0.2)
            try_times -= 1

    if not SUCCEED:
        print('try but failed to locate the bibtex download link within',retry_times,'times')
        return None

    sleep(0.2)
    res = citation_search.findall(page_source) #<br/>
    if len(res)!=0:
        return res[0]
    else:
        return None

# at least we can use this patter to search for bibtex download link
p = '<a class="gs_citi" href="" xpath="1">BibTeX</a>'










#GUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUI
#
#
#
#
#      GUI            GUI            GUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUI 
#
#
#
#
#GUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUIGUI

def batch_comma_bibsearch(text,query_function=query_google_with_retry):
    '''input is like:
    P. Zhong and R. Wang, “Multiple-spectral-band CRFs for denoising junk
    bands of hyperspectral imagery,” IEEE Trans. Geosci. Remote Sens.,
    vol. 51, no. 4, pp. 2260–2275, Apr. 2013.
    [2] Y. Qian and M. Ye, “Hyperspectral imagery restoration using nonlocal
    spectral-spatial structured sparse representation with noise estimation,”
    IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens., vol. 6, no. 2,
    pp. 499–515, Apr. 2013.
    [3] J. Li, H. Zhang, Y. Huang, and L. Zhang, “Hyperspectral image classification
    by nonlocal joint collaborative representation with a locally
    adaptive dictionary,” IEEE Trans. Geosci. Remote Sens., vol. 52, no. 6,
    pp. 3707–3719, Jun. 2014.
    [4] A. Plaza, P. Martinez, J. Plaza, and R. Perez, “Dimensionality reduction
    and classification of hyperspectral image data using sequences of
    extended morphological transformations,” IEEE Trans. Geosci. Remote
    Sens., vol. 43, no. 2, pp. 466–479, Mar. 2005.
    [5] H. Zhang, J. Li, Y. Huang, and L. Zhang, “A nonlocal weighted joint
    sparse representation classification method for hyperspectral imagery,”
    IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens., vol. 7, no. 6,
    pp. 2056–2065, Jun. 2014.
    [6] J. Li, J. M. Bioucas-Dias, and A. Plaza, “Semisupervised hyperspectral
    image segmentation using multinomial logistic regression with active
    learning,” IEEE Trans. Geosci. Remote Sens., vol. 48, no. 11, pp. 4085– 
    4098, Nov. 2010.
    '''
    if "“" in text:
        raw_titles = get_titles_comma_sep(text)
    else:
        raw_titles = get_titles_linebreak_sep(text)
    print(raw_titles)
    plus_titles = raw_titles_to_plus_sep(raw_titles)
    res = []
    for plus_title in plus_titles:
        res.append(query_function(plus_title,retry_times=10))
        time.sleep(0.4)
    return res

def batch_comma_bibsearch_google(text):
    return batch_comma_bibsearch(text,query_google_with_retry)
def batch_comma_bibsearch_bing(text):
    return batch_comma_bibsearch(text,query_bing_with_retry)

def batchsearch_comma_gui(engine=batch_comma_bibsearch_google):
    global driver
    global root

    text = simpledialog.askstring('bibtitle','输入用引号包裹的论文标题',initialvalue='')
    if text is None or (len(text)==0):
        return
    driver = webdriver.Chrome(options=opt)
    res = engine(text)
    driver.close()
    pastboard_info = []
    for i in range(len(res)):
        if res[i] is None:
            res[i] = f'[{i}] results not found for this item'
        else:
            pastboard_info.append(res[i])
            res[i] = f'[{i}]\n' + res[i][:20] + '...'
    outinfo = "以下内容已经复制到剪贴板（复制到剪贴板的信息不包含序号和无法查到的bib条目，可直接使用）\n"+'\n'.join(res)
    pastboard_info = '\n'.join(pastboard_info)
    #pop = tkText(root)
    #pop.insert('insert',out)
    #pop.pack()
    #text = simpledialog.askstring('bibtitle','搜索结果',initialvalue = out,height=50)
    root.clipboard_clear()
    root.clipboard_append(pastboard_info)
    messagebox.showinfo('以下内容已经复制到剪贴板',outinfo)

def batchsearch_comma_google_gui():
    return batchsearch_comma_gui(engine=batch_comma_bibsearch_google)
def batchsearch_comma_bing_gui():
    return batchsearch_comma_gui(engine=batch_comma_bibsearch_bing)


def help():
    global root
    messagebox.showinfo('帮助信息','''必应不需要翻墙，谷歌需要先翻墙才行。
点击谷歌或必应后，将要查找的论文名称Ctrl+V粘贴到输入框里，点击确定。
接受的论文格式如下两种所示
引号包裹论文名的：
[5] H. Zhang, J. Li, Y. Huang, and L. Zhang, “A nonlocal weighted joint
sparse representation classification method for hyperspectral imagery,”
IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens., vol. 7, no. 6,
pp. 2056–2065, Jun. 2014.
[6] J. Li, J. M. Bioucas-Dias, and A. Plaza, “Semisupervised hyperspectral
image segmentation using multinomial logistic regression with active
learning,” IEEE Trans. Geosci. Remote Sens., vol. 48, no. 11, pp. 4085– 
4098, Nov. 2010.

或

仅论文名，用换行符分隔的：
Noise reduction of hyperspectral imagery（换行）
using hybrid spatial-spectral derivative-domain wavelet shrinkage（换行）
（一个换行）
Hyperspectral image processing by jointly（换行）
filtering wavelet component tensor（换行）
（一个换行）
（两个换行）
（三个换行）
Hyperspectral image denoising using first order spectral roughness（换行）
penalty in wavelet domain（换行）

连续的行将被认为是同一个论文标题。空换行用来分隔不同的论文标题。

结果将复制到您的剪贴板。
        ''')


def main_gui():
    global root
    global driver
    root = tkinter.Tk()
    root.minsize(300,50)
    button1 = tkinter.Button(root, text='Google学术', command=batchsearch_comma_google_gui)
    button1.pack(side='left',expand=True)
    button2 = tkinter.Button(root, text='Bing学术', command=batchsearch_comma_bing_gui)
    button2.pack(side='left',expand=True)
    button3 = tkinter.Button(root,text='帮助',command=help)
    button3.pack(side='left',expand=True)
    root.mainloop()
    if driver is not None:
        try:
            driver.close()
        except:
            pass



test='''
[5] H. Zhang, J. Li, Y. Huang, and L. Zhang, “A nonlocal weighted joint
sparse representation classification method for hyperspectral imagery,”
IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens., vol. 7, no. 6,
pp. 2056–2065, Jun. 2014.
[6] J. Li, J. M. Bioucas-Dias, and A. Plaza, “Semisupervised hyperspectral
image segmentation using multinomial logistic regression with active
learning,” IEEE Trans. Geosci. Remote Sens., vol. 48, no. 11, pp. 4085– 
4098, Nov. 2010.
'''


def main():
    res = batch_comma_bibsearch_google(test)
    print(res)
    driver.close()


if __name__ == '__main__':
    main_gui()







































def query(plus_sep_title):
    '''deprecated'''
    access = google_cn.format(plus_sep_title)
    res = req.get(access)
    res.close()
    if (res.status_code==200):
        return res.text
    else:
        return None



def query_chrome(plus_sep_title):
    '''deprecated'''
    url = google_cn.format(plus_sep_title)
    driver.get(url)
    sleep(0.5)
    text = driver.page_source
    if len(re.findall("被引用次数",driver.page_source))==0:
        return None # no resutls found
    cite_button = driver.find_element_by_xpath("//a[@class='gs_or_cit gs_nph']//*[@class='gs_or_svg']")
    cite_button.click()
    sleep(0.8)
    bib_link = driver.find_element_by_xpath("//a[contains(text(),'BibTeX')]")
    bib_link.click()
    sleep(0.2)
    res = citation_search.findall(driver.page_source)
    if len(res)!=0:
        return res[0]
    else:
        return None







































