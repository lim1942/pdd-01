import re
import json
import time
import requests
import pandas as pd

def get_pdd(search_name: str) -> None:
    def get_anti():
        return requests.post("http://127.0.0.1:3000/pdd", data={
            "cookie": headers['cookie'],
            "referrer": url,
        }).text

    url = f'https://mobile.yangkeduo.com/search_result.html?search_key={search_name}'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Host": "yangkeduo.com",
        "Upgrade-Insecure-Requests": "1",
        'cache - control': 'no - cache',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36',
        # 抓包填写cookie
        'cookie': 'api_uid=CiH5oV62JmFWMQBSGIJCAg==; ua=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F78.0.3904.70%20Safari%2F537.36; _nano_fp=XpdJl0UbnpEJXqXbXo_CA7wCUbsc0CR3yFZ4ktmI; webp=1; msec=1800000; chat_config={"host_whitelist":[".yangkeduo.com",".pinduoduo.com",".10010.com/queen/tencent/pinduoduo-fill.html",".ha.10086.cn/pay/card-sale!toforward.action","wap.ha.10086.cn","m.10010.com"]}; chat_list_rec_list=chat_list_rec_list_pe0nsy; JSESSIONID=257C1B44FABD83F767D970EA75217FB6; PDDAccessToken=S2RQHAOWJJ4YUTW4WRNXDYEJMIXWLKEJYTV7NC26FN37FJKUIMOA1131870; pdd_user_id=4530760472; pdd_user_uin=WMVF2T73GZKY36CAGKDYVD6XCA_GEXDA',
        # 抓包填写AccessToken
        'AccessToken': 'S2RQHAOWJJ4YUTW4WRNXDYEJMIXWLKEJYTV7NC26FN37FJKUIMOA1131870',
    }

    response = requests.get(url, headers=headers)
    data = re.findall(r"window.rawData=([\s\S]*?)</script>", response.text)
    if not data:
        raise Exception("extract json error")
    data = data[0].strip().strip(";")
    json_data = json.loads(data)["store"]["data"]["ssrListData"]
    msg_data = dict(json.loads(json_data["loadSearchResultTracking"]["req_params"]),
                    **{"flip": json_data["flip"]})
    print('list_id:\n', msg_data["list_id"])
    list = []
    json_list = json_data["list"]
    for i in json_list:
        item = {}
        item['goodName'] = i["goodsName"]
        item["price"] = i["price"]
        item["salesTip"] = i["salesTip"]
        list.append(item)
        print(item)

    headers[
        'Referer'] = 'https://mobile.yangkeduo.com/search_result.html?search_key=%E9%BB%84%E5%B1%B1%E6%AF%9B%E5%B3%B0'
    api_url = 'https://mobile.yangkeduo.com/proxy/api/search'
    flip = msg_data["flip"]
    for x in range(2, 4):
        anti_content = get_anti()
        params = {
            # cookie-> pdd_user_id
            "pdduid": "",
            'item_ver': 'lzqq',
            "source": "search",
            'track_data': 'refer_page_id, 10169_1588921856889_pbyppi39t3',
            "search_met": "",
            "list_id": msg_data["list_id"],
            "sort": "default",
            "filter": "",
            "q": search_name,
            "page": x,
            "size": 50,
            "flip": flip,
            "anti_content": anti_content
        }
        res = requests.get(api_url, headers=headers, params=params)
        print(res.text)
        json_list = res.json()["items"]
        flip = res.json()["flip"]
        for i in json_list:
            item = {}
            item['goodName'] = i["item_data"]["goods_model"]["goods_name"]
            item["price"] = i["item_data"]["goods_model"]["price_info"]
            item["salesTip"] = i["item_data"]["goods_model"]["sales_tip"]
            list.append(item)
            print(item)
        time.sleep(3)
    df = pd.DataFrame(columns=['goodName','price','salesTip'],data=list)
    df.to_csv(f'{search_name}.csv', encoding='utf-8')


if __name__ == '__main__':
    lists = [
        '黄山毛峰',
        '金赛香菇',
        '若羌灰枣',
        '敖汉小米',
        '红富士苹果',
        '库尔勒香梨',
        '绿心猕猴桃',
        '海南芒果',
        '四川丑橘',
    ]
    for search_name in lists:
        get_pdd(search_name)