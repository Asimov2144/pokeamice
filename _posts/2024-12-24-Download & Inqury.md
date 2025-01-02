# 批量下载卡图&查询服务器存档时间
**宝活小妙招**\
![alt text](https://pokeamice.com/wp-content/uploads/2022/10/anime15.gif){: .align-center}

## 下载卡图

得先推测出链接的格式，比如 <a href="https://special.pokemon.cn/" title = "151">https://special.pokemon.cn/</a> 上有一些151卡图的链接
点开卡图后可以发现对应的静态链接
 <a href="https://static.campaignchowsangsang.com/pokemon/151/big/151_001.png" title = "151_001">https://static.campaignchowsangsang.com/pokemon/151/big/151_001.png</a> \
<img src="https://static.campaignchowsangsang.com/pokemon/151/big/151_001.png" alt="151_001_alt" title="妙蛙种子">{: .align-center}

如果不需要利用浏览器查询文件时间的话，可以写一个python脚本
    
    import os

    img_url = "https://static.campaignchowsangsang.com/pokemon/151/big/151_"
    os.mkdir(".//151//")
    path_file = ".\\151\\"

    def urllib_dl():
        from  urllib.request import urlretrieve
        urlretrieve(img_url_full,path_img)

    for i in range(1,151):
        index = str(i).zfill(3)
        img_url_full = img_url + index+ ".png"
        path_img = path_file+index+".png"
        urllib_dl()

## 用浏览器批量下载
如果需要查询的话 就去Chrome的插件页面查找 **Bulk Image Downloader From Url List**\
or 直接点击
<a href="https://chromewebstore.google.com/detail/bulk-image-downloader-fro/kekkjfalendfifgchoceceoahjnejmgf?hl=zh-CN&utm_source=ext_sidebar" title = "chrome_dl_image">https://chromewebstore.google.com/detail/bulk-image-downloader-fro/kekkjfalendfifgchoceceoahjnejmgf?hl=zh-CN&utm_source=ext_sidebar</a> 

用excel拖动生成对应的链接（土办法）
https://static.campaignchowsangsang.com/pokemon/151/big/151_[001-151].png （and more）

随后开始批量下载

## 查询下载信息

下载完成后 在chrome浏览器中输入

    chrome://version/

随后找到自己的个人资料路径:\
示例：个人资料路径	

    C:\Users\2144j\AppData\Local\Google\Chrome\User Data\Default
找到History文件（这是一个数据表文件，不带后缀）

下载sqlite in https://sqlitebrowser.org/

用sqlite打开History数据表
其中有downloads的表头，在by_ext_name的标签处输入bulk，过滤出由插件bulk image download下载的内容

就能看到对应的信息~\
![alt text](https://pokeamice.com/wp-content/gallery/docs_img/151_database.png){: .align-center}
其中服务器时间一般会是GMT，即格林尼治时间,记得做一些时区准换

而对应的start time和end time是unix时间戳，用于服务器之间的通信\
例如 1735031971 其表示GMT: 2024年 12月 24日 Tuesday AM 9点 19分

而在Chrome里不知道为啥变成了另一串数字，无法用正常的epoch time转real time的方法
所以需要定标一下\
比如

    13379499180012960 

对应了 

    2024年 12月 24日 Tuesday 15点 33分

那么

    13379362293102500 

就对应了 

    2024年 12月 23日 Monday AM 1点 31分

其中1分钟，60秒对应了时间戳中的60000000.

链接鸣谢：

1.https://zhuanlan.zhihu.com/p/388007229\
2.https://www.epochconverter.com/\
3.https://special.pokemon.cn/151/


