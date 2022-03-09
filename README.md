# aliyun-m3u8-EDUdownloader

aliyun-m3u8-EDUdownloader 是一个使用了 Python 语言编写调用Go模块解析m3u8和自动解密Key的某EDU版本视频网站的自动化下载工具，支持aliyun加密版本与普通版本加密方式。

本工具只供学习研究，如有侵权请联系删除

## 用法
0、连上自己学校的VPN或在学校内网访问

1、安装Python3的模块
pip install requests
pip install pycryptodome

2、 在run.py配置edu_URL
填写edu_URL，懂的都懂

3、使用Python3执行run.py
python3 run.py -c 22013

ps：https://e-xxxxx.com/course/22013

4、有任何疑问 欢迎在Github的Issue中提交

## 调用Go模块的参考链接

https://github.com/lbbniu/aliyun-m3u8-downloader

go模块被我打包成exe，目前仅支持win版本，如果需要Linux版本，需要安装Golang环境自行编译，并自行修改run.py的123行。

## License

[MIT License](./LICENSE)