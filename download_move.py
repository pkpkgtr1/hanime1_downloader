from selenium import webdriver
from selenium.webdriver.chrome.service import Service  
from selenium.webdriver.chrome.options import Options
import sqlite3
from lxml import html
import requests
from tqdm import tqdm
import time
import re

def download_file(lf_id,NY,url, filename=None):
    """
    下载文件并显示进度条
    :param url: 文件的URL地址
    :param filename: 保存的文件名，若None则使用URL中的文件名
    """
    try:
        # 发送HTTP GET请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 如果响应状态码不是2xx，会抛出异常
        
        # 获取文件总大小
        file_size = int(response.headers.get('Content-Length', 0))
        
        # 如果没有指定文件名，从URL中提取
        if filename is None:
            filename = url.split('/')[-1]
        
        # 创建tqdm进度条
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=filename)
        
        # 写入文件
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive chunks
                    file.write(chunk)
                    progress_bar.update(len(chunk))
        
        progress_bar.close()
        print(f"下载完成，文件已保存为：{filename}")
        db_insert_xzzt(lf_id,str(NY))
        
    except requests.exceptions.RequestException as e:
        print(f"下载失败：{e}")
    except Exception as e:
        print(f"发生错误：{e}")
    except KeyboardInterrupt:
        print("\n下载已取消")

def safe_filename_for_windows(name):
    char_map = {
        '!': '！',  # 全角感叹号 (FF01)
        '?': '？',  # 全角问号 (FF1F)
        '<': '＜',  # 全角小于号 (FF1C)
        '>': '＞',  # 全角大于号 (FF1E)
        ':': '：',  # 全角冒号 (FF1A)
        '"': '＂',  # 全角双引号 (FF02)
        '|': '｜',  # 全角竖线 (FF5C)
        '\\': '＼', # 全角反斜线 (FF3C)
        '/': '／',  # 全角斜线 (FF0F)
        '*': '＊',  # 全角星号 (FF0A)
        # ' ': '_',
    }

    for half, full in char_map.items():
        name = name.replace(half, full)

    safe_name = ''
    for char in name:
        if 0 <= ord(char) <= 31:
            safe_name += '_'
        else:
            safe_name += char

    return safe_name

def download_move_info(page):

    tree = html.fromstring(page)
    LF_NAME_XP = tree.xpath('//*[@id="content-div"]/div[1]/div[4]/div/div/h3/text()')
    LF_ZL= tree.xpath("//table[@class='download-table']/tbody/tr[contains(@style, 'text-align: center;')]/td[2]/text()")
    #LF_DOWNLOAD_URL= tree.xpath('//*[@id="content-div"]/div[1]/div[4]/div/div/table/tbody/tr[2]/td[5]/a')
    LF_DOWNLOAD_URL= tree.xpath('//a[contains(@class, "exoclick-popunder") and contains(@class, "juicyads-popunder")]')
    rq_info=[]

    data_urls = []
    for a_tag in LF_DOWNLOAD_URL:
        data_url = a_tag.get('data-url')
        if data_url:
            data_urls.append(data_url)



    return LF_NAME_XP,data_urls

def download_html(LF_id,NY):
    service = Service('./chromedriver.exe')  
    options = Options()
    #options.add_argument('--headless')
    options.add_argument('log-level=3')
    options.add_argument('--window-size=400,300')

    # 初始化Chrome浏览器
    browser =  webdriver.Chrome(service=service, options=options)


    try:
            browser.get("https://hanime1.me/download?v="+str(LF_id))
            browser.implicitly_wait(45)
            page = browser.page_source
            browser.quit()
            #打印源码，防止乱码加上编码格式；
            #print(page)

            if 'Server Error' in page:
                print(f"无里番页面,请检测输入是否正确")
            else:
                f=open(f'./tmp/{str(LF_id)}.html',mode="w",encoding="utf-8")
                f.write(page)
                f.close()
            download_info=download_move_info(page)
            #(download_info)
            if '新番預告' in download_info[0][0]: 
                print("#" * 40)  
                print(f"{download_info[0][0]}   此片为新番預告跳过下载")  
                print("#" * 40)  
            else:
                print("#" * 40) 
                print(f"{download_info[0][0]}")   
                pattern = r"-([^.]*)\." 
                num=1     
                for i in download_info[1]:                      
                    match = re.search(pattern, i)
                    if match:
                        quality = match.group(1)
                        #print(f"\033[33m{num}.选择下载视频质量： {quality}\033[0m")
                        num+=1
                    else:
                        print(f"4.跳过下载")  

                     
                #user_input = input("请输入数字: ").strip() or 1
                user_input = 1
                if user_input == 4:
                    pass
                else:
                    num_1=int(user_input)-1
                    print('正在下载：',download_info[1][num_1])
                    download_name=f"{safe_filename_for_windows(download_info[0][0])}"
                    download_file(LF_id,NY,download_info[1][num_1],f'./{NY}/{download_name}.mp4')  #下载文件


    except Exception as e:
            print(f"打开网页时发生错误,请检测网页https://hanime1.me/download?v={LF_id}是否能打开") 
            browser.quit()

def db_insert_xzzt(LF_ID,table_name):
    try:
        # 连接数据库
        conn = sqlite3.connect("hanime1.db")
        # 创建游标对象
        cursor = conn.cursor()
        # 执行插入操作
        cursor.execute(f"UPDATE '{table_name}' SET sfxz='1' WHERE id='{LF_ID}'")
        # 提交更改
        conn.commit()
    except sqlite3.Error as e:
        print(f"错误：{e}")
    finally:
        # 确保关闭连接
        if 'conn' in locals():
            conn.close()

def db_get_lfid(table_name):

    try:
        # 连接数据库
        conn = sqlite3.connect("hanime1.db")
        # 创建游标对象
        cursor = conn.cursor()
        # 执行查询，获取所有记录
        cursor.execute(f"SELECT id,name_cn FROM '{table_name}' a WHERE sfxz IS NOT '1' ")
        # 提取所有记录
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"错误：{e}")
        return []
    finally:
        # 确保关闭连接
        if 'conn' in locals():
            conn.close()

#with open('./tmp/105166.html', 'r',encoding='utf-8') as file:
    #content = file.read()

#aaa=download_move_info(content)  #download_html (105266)
#print (aaa[1])  #download_html (105266)
#download_html (105286,'202505')


