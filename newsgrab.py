import requests
from lxml import etree
import re
__all__ = ["crawl","XH","CD","GT","chinadaily","multipages"]
__version__ = "1.1.1"
def crawl(url):
    content = {}
    url = re.sub("^\s*|\s*$", "", url)
    myheader={"content-type":"text/html;charset=utf-8"\
                 ,"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"}
    try:
        response = requests.get(url=url,headers=myheader)
    except:
        return False, str(requests.get(url=url,headers=myheader).status_code)+":网络出现错误"
    page = etree.HTML(response.text)
    try:
        web = re.search("^((https|http|ftp|rtsp|mms)?:\/\/).*(\.com|\.cn|\.net|\.org|\.edu)",url).group()
    except:
        return False, "网站格式不对，请重新确认"
    if "chinadaily"in web:
        return CD(page,content)
    elif "globaltimes"in web:
        return GT(page,content)
    elif "xinhuanet"in web:
        return XH(page,content)
    elif "reuters"in web:
        return Reuters(page,content)
    else:
        return False, "很抱歉，此网站暂时不支持爬取"

def CD(page,content):
    divpages = page.xpath("// div[@id ='div_currpage']/a[position()<last()-1]/@href")
    pagetype = page.xpath("// div[@class='main_art']")
    if divpages:
        if pagetype:
            signal,content = chinadaily(page,content)
            for divpage in divpages:
                content["content"] += content["content"]+multipages("https:"+divpage)
            return signal, content
        else:
            signal, content = chinadaily(page, content, home=False)
            for divpage in divpages:
                content["content"] += content["content"] + multipages("https:" + divpage, home=False)
            return signal, content
    else:
        if pagetype:
            return chinadaily(page,content)
        else:
            return chinadaily(page, content,home=False)

def chinadaily(page,content,home=True):
    if home:
        try:
            content["title"] = page.xpath("/html/body/div[@class='main_art']/div[@class='lft_art']/h1/text()")[0]
            content["title"] = re.sub("\s*\n\s*", "", content["title"])
            info = page.xpath("/html/body/div[@class='main_art']/div[@class='lft_art']/div[@class='info']/span[1]/text()")[0].split("|")
            content["author"] = re.sub("\n\s*", "", info[0])
            content["press"] = re.sub("\n\s*", "", info[1])
            content["time"] = re.sub("\n\s*", "", info[-1])
            content["content"] = "\n".join(page.xpath("/html/body/div[@class='main_art']/div[@class='lft_art']/div[@id='Content']/p/text()"))
            return True, content
        except Exception as error:
            return False, error
    else:
        try:
            content["title"] = page.xpath("/html/body/div[@class='content']/div[@class='content-left left']/h1/text()")[0]
            content["title"] = re.sub("\s*\n\s*", "", content["title"])
            info = page.xpath("/html/body/div[@class='content']/div[@class='content-left left']/p/text()")[0].split("|")
            content["author"] = re.sub("\n\s*", "", info[0])
            content["press"] = re.sub("\n\s*", "", info[1])
            content["time"] = re.sub("\n\s*", "", info[-1])
            content["content"] = "\n".join(page.xpath("/html/body/div[@class='content']/div[@class='content-left left']/div[@id='Content']/p/text()"))
            return True, content
        except Exception as error:
            return False, error

def multipages(href,home=True):
    url = re.sub("^\s*|\s*$", "", href)
    myheader = {"content-type": "text/html;charset=utf-8" , "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"}
    response = requests.get(url=url, headers=myheader)
    page = etree.HTML(response.text)
    if home:
        return "\n".join(page.xpath("/html/body/div[@class='main_art']/div[@class='lft_art']/div[@id='Content']/p/text()"))
    else:
        return "\n".join(page.xpath("/html/body/div[@class='content']/div[@class='content-left left']/div[@id='Content']/p/text()"))

def GT(page,content):
    try:
        content["title"]=page.xpath("/html/body/div[@id='contents']/div[@id='left']/div[@class='row-fluid article-title']/h3/text()")[0]
        content["title"]=re.sub("^\s*|\s*$","",content["title"])
        info=page.xpath("//*[@id='left']/div[@class='row-fluid article-source']/div[1]/text()")
        if re.search("By (\w*\s){1,}",info[0])==None:
            content["author"]="Reporter"
        else:
            content["author"]=re.search("By (\w*\s){1,}",info[0]).group()
        content["press"]=re.search("Source(.*?)(?=Published)",info[0]).group()
        content["time"]=re.search("Published.*",info[0]).group()
        content["content"]=page.xpath("string(//*[@id='left']/div[3]/div)")
        content["content"]=re.sub("^\s*|\s*$","",content["content"])
        return True, content
    except Exception as error:
        return False, error

def XH(page,content):
    '''divpages = page.xpath("// div[@id ='div_currpage']/a[position()<last()-1]/@href")
    if divpages:
        try:
            content["title"] = page.xpath("/html/body/div[@class='main clearfix']/h1/text()")[0]
            content["title"] = re.sub("^\s*|\s*$", "", content["title"])
            info = page.xpath("/html/body/div[@class='main clearfix']/div[@class='wzzy']/i/text()")
            content["author"] = info[2]
            content["press"] = info[0]
            content["time"] = info[1]
            content["content"] = "\n".join(page.xpath("/html/body/div[@class='main clearfix']/div[@class='content']/p/text()"))
            content["content"] = re.sub("^\s*|\s*$", "", content["content"])
            for page in divpages:
                content["content"] = content["content"] + multipages_XH(page)
            return True, content
        except Exception as error:
            return False, error
    else:'''
    try:#目前新华网应该不需要分页功能
        content["title"]=page.xpath("/html/body/div[@class='main clearfix']/h1/text()")[0]
        content["title"]=re.sub("^\s*|\s*$","",content["title"])
        info=page.xpath("/html/body/div[@class='main clearfix']/div[@class='wzzy']/i/text()")
        content["author"]=info[2]
        content["press"]=info[0]
        content["time"]=info[1]
        content["content"]="\n".join(page.xpath("/html/body/div[@class='main clearfix']/div[@class='content']/p/text()"))
        content["content"]=re.sub("^\s*|\s*$","",content["content"])
        return True, content
    except Exception as error:
        return False, error

def Reuters(page, content):
    try:
        content["title"] = page.xpath("//h1/text()")[0]
        content["title"] = re.sub("^\s*|\s*$", "", content["title"])
        #content["time"] = "/".join(page.xpath("//div[contains(@class,'ArticleHeader-info-container')]/div/time/text()"))
        content["content"] = "\n".join(page.xpath("//div[@class='ArticleBodyWrapper']/p/text()"))
        content["content"] = re.sub("^\s*|\s*$", "", content["content"])
        return True, content
    except Exception as error:
        return False, error
'''def multipages_XH(href):
    url = re.sub("^\s*|\s*$", "", href)
    myheader = {"content-type": "text/html;charset=utf-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"}
    response = requests.get(url=url, headers=myheader)
    page = etree.HTML(response.text)
    return "\n".join(page.xpath("/html/body/div[@class='main clearfix']/div[@class='content']/p/text()"))'''
