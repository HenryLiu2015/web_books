import datetime
import os
from time import sleep

import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

num_chapter = 3400
dfCatalogue = pd.DataFrame({'no': np.arange(num_chapter), 'name': 'NaN', 'href': 'http://'})
novel_name = "都市极品神医"
startNum = 1901
endNum = startNum
cCount = 10
digit = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
curPath = os.getcwd()  # 获取当前文件夹
base_url = "https://www.ibiquge.net"
article_no = "/75_75066/"  # /99_99547/都市极品神医
url = base_url + article_no
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
}


def get_catalogue():
    print(datetime.datetime.utcnow())
    fTemp = open(curPath + "\\" + 'catalogue_dsjpsy.html', 'r', encoding='utf-8')
    respTemp = fTemp.read()
    soup = BeautifulSoup(respTemp, 'lxml')
    temp = soup.select('div#list>dl')
    myCatalogue = temp[0].find_all('a')
    for mc in myCatalogue:
        # 删除最新章节中的内容,处理内部异常字符
        cText = mc.text
        cText = cText.replace('`', '')
        cText = cText.replace('?', '')
        cHref = mc.attrs['href']
        if ("第" in cText) and "章" in cText:
            if cText.find("第") != -1:
                fPos = cText.find("第")
            ePos = cText.find("章")
            iStr = cText[(fPos + 1):ePos]
            if iStr.isdecimal():
                i = int(iStr)
            else:
                i = trans(iStr)
            dfCatalogue.loc[i, 'name'] = cText
            dfCatalogue.loc[i, 'href'] = cHref
    # print(dfCatalogue)
    dfCatalogue.to_csv(curPath + "\\" + "catalogue.csv")
    print(datetime.datetime.utcnow())


def _trans(s):
    num = 0
    if s:
        idx_q, idx_b, idx_s = s.find('千'), s.find('百'), s.find('十')
        if idx_q != -1:
            num += digit[s[idx_q - 1:idx_q]] * 1000
        if idx_b != -1:
            num += digit[s[idx_b - 1:idx_b]] * 100
        if idx_s != -1:
            # 十前忽略一的处理
            num += digit.get(s[idx_s - 1:idx_s], 1) * 10
        if s[-1] in digit:
            num += digit[s[-1]]
    return num


def trans(chn):
    chn = chn.replace('零', '')
    idx_y, idx_w = chn.rfind('亿'), chn.rfind('万')
    if idx_w < idx_y:
        idx_w = -1
    num_y, num_w = 100000000, 10000
    if idx_y != -1 and idx_w != -1:
        return trans(chn[:idx_y]) * num_y + _trans(chn[idx_y + 1:idx_w]) * num_w + _trans(chn[idx_w + 1:])
    elif idx_y != -1:
        return trans(chn[:idx_y]) * num_y + _trans(chn[idx_y + 1:])
    elif idx_w != -1:
        return _trans(chn[:idx_w]) * num_w + _trans(chn[idx_w + 1:])
    return _trans(chn)


def get_books():
    global startNum, endNum
    fileName = 'temp.txt'
    f = open(curPath + "\\" + fileName, 'a+', encoding='utf-8')
    f.seek(0)
    f.truncate()
    j = 0
    for j in range(cCount):
        endNum = endNum + 1
        if dfCatalogue.loc[startNum + j, 'href'] != 'http://':
            print(datetime.datetime.utcnow())
            url_list = base_url + dfCatalogue.loc[startNum + j, 'href']
            resp = requests.get(url_list, headers=headers)
            if resp.status_code != 200:
                sleep(5)
                resp = requests.get(url_list, headers=headers)
            soup = BeautifulSoup(resp.content, 'lxml')
            # 本章标题
            title = dfCatalogue.loc[startNum + j, 'name']
            print(title)
            # 本章内容，并处理无用的<br/>
            cur_content = soup.find("div", id="content").contents
            # 删除不必要的标签
            cur_content_str = ""
            # 重写
            print(datetime.datetime.utcnow())
            for i in range(len(cur_content)):
                if cur_content[i].name or cur_content[i] == '\n':
                    pass
                else:
                    cur_temp = cur_content[i].replace('\xa0', '')
                    cur_content_str = cur_content_str + cur_temp.strip() + '\n'
            f.write("\n" + title + "\n")
            f.write(cur_content_str)
    f.close()
    # 修改文件名字
    os.rename(curPath + "\\" + fileName,
              curPath + "\\" + novel_name + str(startNum) + "-" + str(endNum) + ".txt")


if __name__ == '__main__':
    get_catalogue()
    get_books()
