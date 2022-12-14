import os
import time
import base64
import requests
import argparse
import re
import json
import execjs
import glob
import sys
from natsort import natsorted
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from Crypto.Cipher import AES
from glob import iglob

# 请先设置该选项，请注意一定要填写正确，开头有https，结尾没有/
edu_URL = 'https://e-xxxxx.com'

# 判断是否填写
if(edu_URL == 'https://e-xxxxx.com'):
    print('警告：请先配置edu_URL')
    sys.exit()
sign = 'f9d0ab30b349d69040646082f30c9380'  # sign默认为这个 如果在浏览器抓包和这个不一样 请手动改一下
parser = argparse.ArgumentParser(description='这是一个某edu下载器 Power By Linvery')
parser.add_argument('-c', dest='courseid', required=True,
                    help='请输入课程ID')
args = parser.parse_args()
courseid = args.courseid


courseURL = edu_URL+'/course/'+str(courseid)
# header=''
session = requests.session()
# session.headers=header


@dataclass
class DownLoad_M3U8(object):
    m3u8_url: str
    file_name: str
    key: str

    def __post_init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36', }
        self.threadpool = ThreadPoolExecutor(max_workers=10)
        if not self.file_name:
            self.file_name = 'new.mp4'

    def get_ts_url(self):
        res = requests.get(self.m3u8_url).text
        m3u8_list = re.findall('#EXTINF:.+?\n(https.+?)\n', res)
        return m3u8_list

    def download_single_ts(self, urlinfo):
        url, ts_name = urlinfo
        key = self.key.encode('UTF-8')
        cryptor = AES.new(key, AES.MODE_ECB)
        res = requests.get(url, headers=self.headers)
        with open(ts_name, 'wb') as fp:
            plain_text = cryptor.decrypt(res.content)
            fp.write(plain_text)

    def download_all_ts(self):
        ts_urls = self.get_ts_url()
        for i in range(len(ts_urls)):
            print(ts_urls[i])
            self.threadpool.submit(self.download_single_ts, [
                                   ts_urls[i], f'{i}.ts'])
        self.threadpool.shutdown()

    def run(self):
        self.download_all_ts()
        ts_path = '*.ts'
        with open(self.file_name, 'wb') as fn:
            for ts in natsorted(iglob(ts_path)):
                with open(ts, 'rb') as ft:
                    scline = ft.read()
                    fn.write(scline)
        for ts in iglob(ts_path):
            os.remove(ts)


def get_lessonInfo():
    res = session.get(courseURL).text
    print(courseURL)
    lessonName = re.findall('<p class="classname" title="(.+?)">', res)[0]
    lessonsDatas_str = re.findall('lessonsDatas = (.+?),\n', res)[0]
    lessonsDatas_list = re.findall('{.+?}', lessonsDatas_str)
    lessonsDatas = []
    for i in range(len(lessonsDatas_list)):
        lessonsDatas.append(json.loads(lessonsDatas_list[i]))
    return lessonsDatas, lessonName


def requests_get_key(lessonsID):
    m3u8_key_url = edu_URL+'/video/api?do=api&m=getkey&lesson_id='+lessonsID+'&sign='+sign
    res = session.get(m3u8_key_url)
    if(len(res.text) < 10):
        return False, False
    else:
        m3u8_url = edu_URL+'/video/m3u8?do=api&m=m3u8&id='+lessonsID+'&dp=high'
        JSCode = open(os.path.abspath(os.path.dirname(__file__)) +
                      '\decode.js', 'r', encoding='utf8').read()
        CTX = execjs.compile(JSCode)
        return m3u8_url, CTX.call('decode', res.text, lessonsID)


def ali_get_aliVodAuth(lessonsID):
    url = edu_URL+'/video/'+lessonsID
    res = session.get(url).text
    res_json = json.loads(re.findall('lesInfo = (.+?);', res)[0])
    aliVodAuth = json.loads(base64.b64decode(
        res_json['aliVodAuth']).decode("UTF-8"))
    vodVideoId = res_json['vodVideoId']
    createData = {
        'AccessKeyId': aliVodAuth['AccessKeyId'],
        'AuthInfo': aliVodAuth['AuthInfo'],
        'SecurityToken': aliVodAuth['SecurityToken'],
        'AccessKeySecret': aliVodAuth['AccessKeySecret']
    }
    webPlayAuth = base64.b64encode(json.dumps(
        createData).encode("UTF-8")).decode("UTF-8")
    return webPlayAuth, vodVideoId


def download(method, WebPlayAuth, vodVideoId, file_name, mp4_name):
    if(method == 'aliyun'):
        start = time.time()
        command = os.path.abspath(os.path.dirname(__file__))+'\core.exe '+method + \
            ' -p "'+WebPlayAuth+'" -v '+vodVideoId+' -o="'+file_name+'" --chanSize 10'
        print(command)
        os.system(command)
        end = time.time()
        print('耗时:', end - start)

    # 下载完改名字

    oldName = glob.glob(file_name+'\*.m3u8.mp4')[0]
    newName = file_name+'\\'+mp4_name
    while True:
        if(os.path.exists(oldName)):
            if(len(glob.glob(newName)) == 0):
                os.rename(oldName, newName)
            else:
                os.remove(oldName)
            break
        else:
            time.sleep(1)


if __name__ == '__main__':
    lessonsDatas, lessonName = get_lessonInfo()
    lessonsDatasLen = len(lessonsDatas)
    # print(lessonsDatasLen)
    for data in lessonsDatas:
        # 如果mp4name带有奇怪参数，自动转义
        mp4_name = data['lesson_sort']+' '+data['title']+'.mp4'
        mp4_name = mp4_name.replace("/", "-")

        lessonsID = data['lesson_id']
        m3u8_url, key = requests_get_key(str(lessonsID))
        file_name = os.path.abspath(
            os.path.dirname(__file__))+'\\'+lessonName
        full_path = file_name+'\\'+mp4_name
        if(os.path.exists(file_name) is False):
            os.mkdir(file_name)
        if(key != False):
            print(m3u8_url, key)
            if(os.path.exists(full_path)):
                continue
            else:
                M3U8 = DownLoad_M3U8(m3u8_url, full_path, key)
                M3U8.run()
        else:
            if(os.path.exists(full_path)):
                continue
            else:
                webPlayAuth, vodVideoId = ali_get_aliVodAuth(str(lessonsID))
                download('aliyun', webPlayAuth,
                         vodVideoId, file_name, mp4_name)
