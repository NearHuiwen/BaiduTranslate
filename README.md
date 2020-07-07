## **百度翻译破解JS逆向爬虫**
Requests+PyExecJS

百度翻译网站调用的JS文件：index_2958d34.js

这个JS文件下载时间：2020年7月6日下载的，之后下载文件或许有出入

**目标**

```python
破解百度翻译接口，抓取翻译结果数据
```

**实现步骤**

- **1、Fidder抓包,找到json的地址,观察查询参数**

  ```python
  英转中  如：输入apple
  1、POST地址: https://fanyi.baidu.com/v2transapi?from=en&to=zh
  2、Form表单数据（多次抓取在变的字段） 
    from：	en
    to：		zh
    query：	apple
    transtype：	translang
    simple_means_flag：	3
    sign：	704513.926512
    token：	1977a2a7d3f405801ee8d92a2a98cebc
    domain：	common
  ```

- **2、抓取相关JS文件**

  ```python
  谷歌浏览器F12
  右上角 - 搜索 - sign: - 找到具体JS文件(index_2958d34.js) - 格式化输出
  ```


**3、在JS中寻找sign的生成代码**

```python
1、在格式化输出的JS代码中搜索: sign: 找到如下JS代码：sign: y(n),
2、通过设置断点，找到y(n)函数的位置，即生成sign的具体函数
   # 1. n 为要翻译的单词
   # 2. 鼠标移动到 y(n) 位置处，点击可进入具体y(n)函数代码块
```

**4、生成sign的m(a)函数具体代码如下(在一个大的define中)**

```javascript
function a(r) {
    if (Array.isArray(r)) {
        for (var o = 0, t = Array(r.length); o < r.length; o++)
            t[o] = r[o];
        return t
    }
    return Array.from(r)
}

function n(r, o) {
    for (var t = 0; t < o.length - 2; t += 3) {
        var a = o.charAt(t + 2);
        a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a),
            a = "+" === o.charAt(t + 1) ? r >>> a : r << a,
            r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
    }
    return r
}

function e(r) {
    var o = r.match(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g);
    if (null === o) {
        var t = r.length;
        t > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(t / 2) - 5, 10) + r.substr(-10, 10))
    } else {
        for (var e = r.split(/[\uD800-\uDBFF][\uDC00-\uDFFF]/), C = 0, h = e.length, f = []; h > C; C++)
            "" !== e[C] && f.push.apply(f, a(e[C].split(""))),
            C !== h - 1 && f.push(o[C]);
        var g = f.length;
        g > 30 && (r = f.slice(0, 10).join("") + f.slice(Math.floor(g / 2) - 5, Math.floor(g / 2) + 5).join("") + f.slice(-10).join(""))
    }
//        var u = void 0
//          , l = "" + String.fromCharCode(103) + String.fromCharCode(116) + String.fromCharCode(107);
//        u = null !== i ? i : (i = window[l] || "") || "";


//# u = null !== i ? i : (i = window[l] || "") || "";下面定义了var i=null;
// # null !== i 为假，执行(i = window[l] || "")，结果为320305.131321201
// # 这里多次运行发现window[1]是一个固定值：320305.131321201,(直接替换，调用js就可以得到结果了)，
// #  简化成u= false ? : null : 320305.131321201 || "",最后u=320305.131321201是一个固定值

    var u = '320305.131321201';
    for (var d = u.split("."), m = Number(d[0]) || 0, s = Number(d[1]) || 0, S = [], c = 0, v = 0; v < r.length; v++) {
        var A = r.charCodeAt(v);
        128 > A ? S[c++] = A : (2048 > A ? S[c++] = A >> 6 | 192 : (55296 === (64512 & A) && v + 1 < r.length && 56320 === (64512 & r.charCodeAt(v + 1)) ? (A = 65536 + ((1023 & A) << 10) + (1023 & r.charCodeAt(++v)),
            S[c++] = A >> 18 | 240,
            S[c++] = A >> 12 & 63 | 128) : S[c++] = A >> 12 | 224,
            S[c++] = A >> 6 & 63 | 128),
            S[c++] = 63 & A | 128)
    }
    for (var p = m, F = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(97) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(54)), D = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(51) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(98)) + ("" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(102)), b = 0; b < S.length; b++)
        p += S[b],
            p = n(p, F);
    return p = n(p, D),
        p ^= s,
    0 > p && (p = (2147483647 & p) + 2147483648),
        p %= 1e6,
    p.toString() + "." + (p ^ m)
}

var i = null;
//此行报错，直接注释掉即可
// t.exports = e
```

- **5、直接将代码写入本地js文件,利用PyExecJS模块执行js代码进行调试**

  ```python
    # 获取sign
    def get_sign(self, word):
        with open('get_sign.js', 'r') as f:
            js_data = f.read()
        execjs_obj = execjs.compile(js_data)
        sign = execjs_obj.eval(f'e("{word}")')
        return sign
  ```


- **6、获取token**

  ```python
    # 获取token
    def get_token(self):
        # 如果使用requests时报错requests.exceptions.SSLError: HTTPSConnectionPool
        # 找了很多的资料，有很多人说关闭证书验证（verify=False））可以解决这个问题或者说是在进行GET时,指定SSL证书.
        html = requests.get(self.get_url, headers=self.headers).text
        # 正则解析
        pattern = re.compile("token: '(.*?)'", re.S)
        token = pattern.findall(html)[0]
        return token
  ```
