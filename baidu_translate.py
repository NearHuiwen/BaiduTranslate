import requests
import re
import execjs

"""
百度翻译爬虫
"""
class BaiduTranslateSpider(object):
    def __init__(self):
        self.get_url = 'https://fanyi.baidu.com/'
        # 如下是用的是谷歌浏览器的参数
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "Cookie": "BIDUPSID=F7EA077794AFF67549CC5DFDF36B23AC; PSTM=1578129730; BAIDUID=F7EA077794AFF675C0E6B3E784127506:FG=1; BDUSS=EwRWlEcTF3d2R5bGpwWW42bFUweUFZdE5kV0VrMzUtQjNrU09LNGhFdlktMGhlSVFBQUFBJCQAAAAAAAAAAAEAAADJMKM1z8C1wb3w0-PA0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANhuIV7YbiFeYV; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1594021149; __yjsv5_shitong=1.0_7_58360b44d3696338f12a7510b5a8253ad77a_300_1594028514037_219.128.144.201_b4e6f84f; yjs_js_security_passport=0c1f45b0f2058cf16349938844e2c5e956259f4c_1594028531_js",
        }

    # 获取token
    def get_token(self):
        # 如果使用requests时报错requests.exceptions.SSLError: HTTPSConnectionPool
        # 找了很多的资料，有很多人说关闭证书验证（verify=False））可以解决这个问题或者说是在进行GET时,指定SSL证书.
        html = requests.get(self.get_url, headers=self.headers).text
        # 正则解析
        pattern = re.compile("token: '(.*?)'", re.S)
        token = pattern.findall(html)[0]
        return token

    # 获取sign
    def get_sign(self, word):
        with open('get_sign.js', 'r') as f:
            js_data = f.read()
        execjs_obj = execjs.compile(js_data)
        sign = execjs_obj.eval(f'e("{word}")')
        return sign

    # 获取翻译结果
    # 参数名	参数解释
    # from	原文语种
    # to	译文语种
    # query	原文内容
    # transtype	翻译类型(transtype，这个参数一般不用更改，网上说有realtime 和 translang 两种)
    # simple_means_flag	未知
    # sign	签名
    # token	客户端请求标识
    def get_result(self, word, fro, to):
        token = self.get_token()
        sign = self.get_sign(word)
        form_data = {
            "from": fro,
            "to": to,
            "query": word,
            "transtype": "translang",
            "simple_means_flag": "3",
            "sign": sign,
            "token": token,
            "domain":'common'
        }
        html_json = requests.post(
            url=f'https://fanyi.baidu.com/v2transapi?from={fro}&to={to}',
            data=form_data,
            headers=self.headers
        ).json()

        result = html_json['trans_result']['data'][0]['dst']
        return result


if __name__ == '__main__':
    spider = BaiduTranslateSpider()
    print("请输入需要的要求(1或者2)：")
    print("1.英译中      2.中译英")
    menu = "请选择："
    choice = input(menu)
    if choice == '1':
        fro = 'en'
        to = 'zh'
    else:
        fro = 'zh'
        to = 'en'
    word = input('请输入要翻译的单词：')
    result = spider.get_result(word, fro, to)
    print("翻译结果：" + '\n' +result)
