import re
import requests
import os
from selenium import webdriver
from tqdm import tqdm

'''
更新日志
1.1 自动跳过空章节
1.2 卡在一页时会自动刷新
1.3 增加进度条功能
'''



class getComic():
    def __init__(self):
        self.Name='化物语'
        self.indexurl='http://manhua.kukudm.com/comiclist/2372/'
        self.start_chap=54
        


Name='化物语'
indexurl='http://manhua.kukudm.com/comiclist/2372/'
options=webdriver.FirefoxOptions()           
options.headless=True
start_chap=61


def SavePic(filename,url):
    '''
    保存单张图片的函数
    '''
    try:
        content=requests.get(url).content
        with open(filename,'wb') as f:
            f.write(content)
    except:
        SavePic(filename,url)
    
def get_TOF(index_url):
    '''
    从主页面获取各章节url
    '''
    
    url_list=[]
    
    #模拟浏览器打开网站
    browser=webdriver.Firefox(options=options)
    browser.get(index_url)
    browser.implicitly_wait(3)
    
    #获取章节列表的元素
    comics_list_id=browser.find_element_by_id("comiclistn")
    chapter_list=comics_list_id.find_elements_by_xpath("./*")
    
    #生成章节列表
    for part in chapter_list:
        link=part.find_elements_by_tag_name('a')[1]
        url_list.append(link.get_attribute('href'))
    
    browser.quit()
    
    Comics=dict(name=Name,urls=url_list)
    
    print("目录信息爬取成功")
    
    return Comics
    

def get_pic(browser,cururl,dirname,i,n):
    '''
    为防止卡在一个页面设置的递归函数
    '''
    try:
        browser.get(cururl)
        #获取图片url
        pic_url=browser.find_element_by_tag_name('img').get_attribute('src')
        filename=dirname+'/'+str(i)+'.jpg'
        #保存图片到本地
        SavePic(filename,pic_url)
        #获取下一页url
        NextPage = browser.find_elements_by_tag_name('a')[-1].get_attribute('href')
        return NextPage
    except:
        return get_pic(browser,cururl,i)

def get_pics(Comics):
    '''
    根据主页面获取的信息逐章爬取图片
    '''
    comic_list=Comics['urls']
    basedir=Comics['name']
    
    #desired_capabilities = DesiredCapabilities.FIREFOX
    
    browser=webdriver.Firefox(options=options)
    #desired_capabilities["pageLoadStrategy"] = "normal"
    curchap=0
    
    for url in comic_list:
        curchap+=1
        if curchap<start_chap:
            continue
        
        #打开某一章节页面
        browser.get(url)
        browser.implicitly_wait(10)
        
        try:
            #获取标题
            title=browser.title
            #获取页数
            temptext=browser.find_element_by_xpath("//*[contains(text(),'共')]").text
        except:
            print('章节缺失')
            continue
        
        #在本地创建文件夹保存
        dirname=basedir+'/'+str(title)
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        
        pageNum=int(re.findall(r'\d+',temptext)[1])

        cururl=url
        
        pbar=tqdm(range(pageNum))
        for i in pbar:
            cururl=get_pic(browser,cururl,dirname,i+1,0)
            pbar.set_description('{}  '.format(title)+'共'+str(pageNum)+'页')
        
    browser.quit()
    print('所有章节下载完毕')
    
    
Comics=get_TOF(indexurl)
get_pics(Comics)