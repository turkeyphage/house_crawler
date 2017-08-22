#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
from bs4 import BeautifulSoup
import requests
import random
from time import sleep



def set_session_header(session):
    UAS = ("Mozilla / 5.0 (Macintosh Intel Mac OS X 10_12_5) AppleWebKit / 603.2.4 (KHTML, like Gecko) Version / 10.1.1 Safari / 603.2.4",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0"
           )
    session.headers['User-Agent'] = UAS[random.randrange(len(UAS))]
    session.headers['Accept'] = "text / html, application / xhtml + xml, application / xml; q = 0.9, image / webp, image / apng, * / *; q = 0.8"
    session.headers['Connection'] = "keep-alive"
    session.headers['Accept-Encoding'] = "gzip, deflate"
    session.headers['Host'] = "buy.sinyi.com.tw"
    # session.headers['Referer'] = "http://buy.sinyi.com.tw/?_ga=2.135616115.311666799.1502097538-413232226.1501309130"

# random_agent = UAS[random.randrange(len(UAS))]


def main():
    #縣市不分區
    main_url = "http://buy.sinyi.com.tw/list/index.html"

    s = requests.Session()

    set_session_header(s)
    response = s.get(main_url)

    # print(type(response.status_code))
    # print(response.status_code)
    # print(response.content.decode('utf-8'))

    soup = BeautifulSoup(response.content, 'html.parser')

    pagesTEXT = soup.findAll("li", class_="page")
    pages = []
    for ele in pagesTEXT:
        try:
            pageNum = int(ele.text)
            pages.append(pageNum)
        except Exception as e:
            print(str(e))

        # for a in td.findAll("a", href=True, target="_blank"):
        #     print(a.text)

    print(pages)

    sleep(3)


    if len(pages) > 0:
        totalPages = pages[-1]
        totalPages_list = []

        for i in range(1, totalPages + 1):
            pageIndex = str(i) + ".html"
            pageURL = main_url.replace("index.html", pageIndex)
            totalPages_list.append(pageURL)

        #開始一頁頁找物件：
        for each_page in totalPages_list:
            
            set_session_header(s)

            response = s.get(each_page)
            soup = BeautifulSoup(response.content, 'html.parser')
            items_url = []
            for item in soup.find_all(attrs={'id': 'search_result_list'}):
                for link in item.find_all('a'):
                    item_link = link.get('href')
                    if item_link != "#":
                        totalLink = "http://buy.sinyi.com.tw" + item_link
                        items_url.append(totalLink)

            sleep(3)


            #一頁一頁進去爬細部內容
            if len(items_url) > 0:
                for eleURL in items_url:
                    print(eleURL)

                    set_session_header(s)

                    response = s.get(eleURL)
                    
                    print(response.content.decode('utf-8'))

                    if response.status_code == 200 and "ROBOTS" not in response.content.decode('utf-8'):
                        soup = BeautifulSoup(response.content, 'html.parser')

                        
                        obj_url = eleURL
                        obj_price = 0.0  # 總價
                        obj_address = ""  # 地址
                        obj_city = ""  # 所在城市
                        obj_buildingSize = 0.0  # 建物登記大小(坪)
                        obj_fieldSize = 0.0  # 土地登記大小(坪)
                        obj_pattern = ""  # 格局
                        obj_type = ""  # 類型
                        obj_park = False  # 車位
                        obj_elevator = False  # 電梯
                        obj_floor = "0"  # 樓層
                        # obj_totalfloor = 1 #樓層
                        obj_year = 0.0  # 屋齡
                        obj_sizeDescription = ""  # 建地詳述

                        if len(soup.select('.pingDetails_ul')) > 0:
                            obj_sizeDescription = soup.select('.pingDetails_ul')[0].getText(
                            ).strip().replace(" ", "").replace("\n", " ")

                        if len(soup.select('.price')) > 0:
                            obj_price = float(soup.select('.price')[
                                            0].getText().replace(",", ""))

                        obj_mess = soup.find('div', {'id': 'basic-data'}).findAll('tr')

                        for i in range(1, len(obj_mess)):
                            # print(info.text.replace(" ", ""))
                            # print("------------------------")
                            cols = obj_mess[i].findAll('td')
                            cols = [ele.text.strip().replace(" ", "").replace("\n", "")
                                    for ele in cols]
                            # print(cols)
                            for item in cols:
                                if "地址" in item:
                                    obj_address = cols[cols.index(item) + 1]
                                    obj_city = obj_address[:3]

                                if "格局" in item:
                                    obj_pattern = cols[cols.index(item) + 1]

                                if "建物登記" in item:
                                    obj_buildingSize = float(
                                        cols[cols.index(item) + 1].replace("坪", ""))

                                if "土地登記" in item:
                                    obj_fieldSize = float(
                                        cols[cols.index(item) + 1].replace("坪", ""))

                                if "屋齡" in item:
                                    obj_year = float(
                                        cols[cols.index(item) + 1].replace("年", ""))

                                if "樓層" in item:
                                    obj_floor = cols[cols.index(item) + 1].replace("樓", "")

                                if "類型" in item:
                                    obj_type = cols[cols.index(item) + 1]

                        obj_info = soup.findAll("div", {"class": "short"})

                        for i in obj_info:
                            desc = i.text
                            answerPair = desc.split("：")
                            # print(answerPair)
                            if "車\xa0\xa0\xa0\xa0\xa0\xa0\xa0位" in answerPair[0]:
                                parkingAnswer = answerPair[-1]
                                if "無" in parkingAnswer:
                                    obj_park = False
                                else:
                                    obj_park = True

                            if "電\xa0\xa0\xa0\xa0\xa0\xa0\xa0梯" in answerPair[0]:
                                elevatorAnswer = answerPair[-1]
                                if "無" in parkingAnswer:
                                    obj_elevator = False
                                else:
                                    obj_elevator = True

                        print([obj_url, obj_price, obj_address, obj_city, obj_buildingSize, obj_fieldSize, obj_pattern, obj_type, obj_park, obj_elevator, obj_floor, obj_year, obj_sizeDescription])
                        
                        sleep(3)


if __name__ == "__main__":
    main()
    # with open(fn, "a") as file_handler:
    #     for item in items_url:
    #         file_handler.write("%s\n" % item)




# totalPages = soup.select(
#     '#buy_contenter, #buy_content, #search_pagination, li, .page')
# print(totalPages)
# int(browser.find_element_by_id("search_pagination").find_elements_by_tag_name("li")[-1].text)

