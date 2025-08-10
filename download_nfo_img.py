import sqlite3
import os
import requests
import datetime
import re
 
def download_single_image(url, file_name=None, save_path="./202505"):
    """
    下载单张图片并保存到指定路径，允许自定义文件名。
    
    Args:
        url (str): 图片的URL地址。
        file_name (str, optional): 自定义的文件名。默认为None，表示使用URL中的文件名。
        save_path (str): 图片保存的路径，默认为当前目录下的images文件夹。
    
    Returns:
        bool: 下载成功返回True，失败返回False。
    """
    try:
        # 检查并创建保存路径
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        # 发送HTTP GET请求获取图片数据
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查HTTP请求是否成功
        
        # 如果未提供自定义文件名，提取URL中的文件名
        if not file_name:
            file_name = url.split("/")[-1]
        
        # 确保文件路径的完整性
        save_file = os.path.join(save_path, file_name)
        
        # 以二进制写入模式保存图片
        with open(save_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        
        print(f"成功下载图片并保存为：{save_file}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"下载图片失败：{e}")
        return False
    except Exception as e:
        print(f"保存图片失败：{e}")
        return False


def extract_before_brackets(text):
  """
  提取字符串中第一个 [] 之前的内容。

  Args:
    text: 要处理的字符串。

  Returns:
    第一个 [] 之前的内容，如果字符串中没有 []，则返回整个字符串。
  """
  match = re.search(r'^(.*?)\[', text)
  if match:
    return match.group(1)
  else:
    return text
  
def extract_from_start_to_指定内容(text, 指定内容):
  """
  提取从字符串开头到指定内容之间的内容（不包括指定内容）。

  Args:
    text: 要处理的字符串。
    指定内容: 作为结束标记的字符串。

  Returns:
    从开头到指定内容之间的内容，如果未找到指定内容，则返回整个字符串。
  """
  pattern = r"^(.*?)" + re.escape(指定内容)
  match = re.search(pattern, text)
  if match:
    return match.group(1)
  else:
    return text


def get_table_data(table_name):
    """
    获取指定数据库表中的所有数据。
    
    Args:
        db_name (str): 数据库文件名。
        table_name (str): 表名。
    
    Returns:
        list: 包含表中所有记录的列表，每个记录是一个元组。
    """
    try:
        # 连接数据库
        conn = sqlite3.connect("hanime1.db")
        # 创建游标对象
        cursor = conn.cursor()
        # 执行查询，获取所有记录
        cursor.execute(f"SELECT * FROM '{table_name}'")
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

def get_table_names():
    try:
        conn = sqlite3.connect("hanime1.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name desc LIMIT 6")
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    except sqlite3.Error as e:
        print(f"错误：{e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def extract_before_first_space(text):
  """
  提取字符串中第一个空格之前的内容。

  Args:
    text: 要处理的字符串。

  Returns:
    第一个空格之前的内容，如果字符串中没有空格，则返回整个字符串。
  """
  match = re.search(r'^(\S*) ', text)
  if match:
    return match.group(1)
  else:
    return text

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

def sc_nfo_jpg(NY):
    gltj=[' 後編',' 前編',' ＃',' 第']
    table_name = str(NY)
    current_time = datetime.datetime.now()
    dt_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    data = get_table_data(table_name)

    if data:
        for row in data:
            #里番id
            LF_ID = row[0]
            #里番日文名
            LF_NAME_JP=row[1]
            #里番中文名
            LF_NAME_CN=row[2]
            #制作公司
            LF_ZZGS= row[3]
            #里番发行日期
            LF_FSRQ = row[4]
            #里番内容
            LF_NR = row[5]
            #里番图片
            LF_IMG = row[6]
            #里番标签
            LF_TAG = row[7]
            tags=LF_TAG.split(',')
            #print(tags)
            
            
            hanime_tags = '\n    '.join(f'<tag>{x}</tag>' for x in tags)
            #print(hanime_tags)
            img_filename = f"{safe_filename_for_windows(LF_NAME_CN)}"
            download_single_image(LF_IMG, img_filename + "-poster.png", save_path=f"./{str(NY)}")

            HJ_NAME_JP=extract_before_brackets(LF_NAME_JP)
            if 'OVA ' in HJ_NAME_JP:
                print(HJ_NAME_JP)
                for j in gltj :
                        GL_LF_NAME_JP = extract_from_start_to_指定内容(HJ_NAME_JP, j)
                        if GL_LF_NAME_JP != HJ_NAME_JP:
                            break
            
            else:
                for j in gltj :
                        GL_LF_NAME_JP = extract_from_start_to_指定内容(HJ_NAME_JP, j)
                        if GL_LF_NAME_JP != HJ_NAME_JP:
                            break
                GL_LF_NAME_JP = extract_before_first_space(GL_LF_NAME_JP)


            show_nfo = f'''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <movie>
    <plot><![CDATA[{LF_NR.replace('\n','<br>\n')}]]></plot>
    <customrating>里番</customrating>
    <mpaa>里番</mpaa>
    <lockdata>false</lockdata>
    <dateadded>{dt_str}</dateadded>
    <title>{LF_NAME_JP}</title> 
    <title_jp>{LF_NAME_JP}</title_jp> 
    <title_cn>{LF_NAME_CN}</title_cn> 
    <rating></rating> 
    <criticrating></criticrating> 
    <uncensored>True</uncensored> 
    <year>{str(LF_FSRQ[:4])}</year>
    <premiered>{LF_FSRQ.replace('年','-').replace('月','-').replace('日','').replace(' ','')}</premiered>
    <releasedate>{LF_FSRQ.replace('年','-').replace('月','-').replace('日','').replace(' ','')}</releasedate>
    {hanime_tags}
    <studio>{LF_ZZGS}</studio>
    <set>
    <name>{GL_LF_NAME_JP}</name>
    </set>
    <art>
    <poster>{LF_NAME_JP}-poster.png</poster>
    </art>
    <maker>制作商</maker>
    <label>{LF_ID}</label>
    <num>{LF_ID}</num>
    <release>{LF_FSRQ.replace('年','-').replace('月','-').replace('日','').replace(' ','')}</release>
    <website>https://hanime1.me/watch?v={LF_ID}</website>
    </movie>
    '''
            #print(show_nfo)
            nfo_filename = f"{safe_filename_for_windows(LF_NAME_CN)}"

            with open(f'./{str(NY)}/'+nfo_filename+'.nfo' , 'w',encoding="utf-8") as file:
                                file.write(show_nfo)


        
    else:
        print(f"表{table_name}为空，或者无法获取数据。")




