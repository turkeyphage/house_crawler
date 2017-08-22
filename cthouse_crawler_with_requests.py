#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3

from bs4 import BeautifulSoup
import requests
import random
from time import sleep
import pymysql


def set_session_header(session):
    UAS = ("Mozilla / 5.0 (Macintosh Intel Mac OS X 10_12_5) AppleWebKit / 603.2.4 (KHTML, like Gecko) Version / 10.1.1 Safari / 603.2.4",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0"
           )
    session.headers['User-Agent'] = UAS[random.randrange(len(UAS))]
    session.headers['Accept'] = "text / html, application / xhtml + xml, application / xml; q = 0.9, image / webp, image / apng, * / *; q = 0.8"
    session.headers['Connection'] = "keep-alive"
    session.headers['Accept-Encoding'] = "gzip, deflate"


def main():
    #所有縣市
    allCities = ['台北市', '新北市', '基隆市', '宜蘭縣', '新竹市', '新竹縣', '桃園市', '苗栗縣', '台中市', '彰化縣',
                '南投縣', '嘉義市', '嘉義縣', '雲林縣', '台南市', '高雄市', '澎湖縣', '金門縣', '屏東縣', '台東縣', '花蓮縣']


    main_url = "http://buy.cthouse.com.tw/area"


    for city in allCities:
        city = city + "-city"
        cityURL = "/".join([main_url, city])

        # print(cityURL)

        # get total page
        s = requests.Session()
        set_session_header(s)
        response = s.get(cityURL)


        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html5lib')
            if len(soup.select('.searchResult .pageBar a')) > 0:

                try:
                    tablePagination = soup.select('.searchResult .pageBar a')
                    finalPages = int([ele['href'] for ele in tablePagination][-2].replace('page', "").replace('.html', ""))
                    # print(finalPages)

                    sleep(2)

                    for i in range(1, finalPages+1):
                        pageIndex = "page"+str(i)+".html"
                        pageURL = "/".join([cityURL, pageIndex])
                        # print(pageURL)
                        set_session_header(s)
                        response = s.get(pageURL)

                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html5lib')
                            if len(soup.select('.objlist__item .col4-2 .item__intro a')) > 0:
                                items_url_part = [ele['href'] for ele in soup.select('.objlist__item .col4-2 .item__intro a')]
                                
                                if len(items_url_part) > 0:
                                    for ele in items_url_part:
                                        item_url = "http://buy.cthouse.com.tw" + ele
                                        
                                        set_session_header(s)
                                        response = s.get(item_url)

                                        if response.status_code == 200 and "ROBOTS" not in response.content.decode('utf-8'):
                                            soup = BeautifulSoup(response.content, 'html5lib')

                                            try:
                                                if "Request unsuccessful" not in soup.getText() and "該物件已下架或不存在" not in soup.getText() and "網站維護中" not in soup.getText():
                                                    obj_url = item_url
                                                    obj_price = 0.0  # 總價
                                                    obj_address = ""  # 地址
                                                    obj_city = ""  # 所在城市
                                                    # 建物登記大小(坪)
                                                    obj_buildingSize = 0.0
                                                    # 土地登記大小(坪)
                                                    obj_fieldSize = 0.0
                                                    obj_pattern = ""  # 格局
                                                    obj_type = ""  # 類型
                                                    obj_park = False  # 車位
                                                    obj_elevator = False  # 電梯
                                                    obj_floor = "0"  # 樓層
                                                    obj_year = 0.0  # 屋齡
                                                    obj_sizeDescription = ""  # 建地詳述

                                                    if len(soup.select('.detail__type .type__item .item__td ul li')) > 0:
                                                        objDetail = [ele.text.strip().replace(" ", "").replace("\n", "") for ele in soup.select('.detail__type .type__item .item__td ul li')]
                                                        
                                                        for ele in objDetail:
                                                            if '總價：' in ele:
                                                                
                                                                try:
                                                                    #price
                                                                    ele = ele.replace('總價：', "").replace(",", "").replace("億", "")
                                                                    ele = ele[:ele.find("萬")]
                                                                    obj_price = float(ele)
                                                                except Exception as e:
                                                                    print(str(e))


                                                            if '建物登記：' in ele:
                                                                try:
                                                                    #building size
                                                                    ele = ele.replace('建物登記：', "")
                                                                    ele = ele[:ele.find("坪")]    
                                                                    obj_buildingSize = float(ele)
                                                                except Exception as e:
                                                                    print(str(e))

                                                            if '土地坪數：' in ele:
                                                                try:
                                                                    #field size
                                                                    ele = ele.replace(
                                                                        '土地坪數：', "")
                                                                    ele = ele[:ele.find("坪")]                                                            
                                                                    obj_fieldSize = float(ele)
                                                                except Exception as e:
                                                                    print(str(e))

                                                            if '格局：' in ele:
                                                                try:
                                                                    #pattern
                                                                    obj_pattern = ele.replace('格局：', "")                                                                
                                                                except Exception as e:
                                                                    print(str(e))

                                                            if '地址：' in ele:
                                                                try:
                                                                    #address and city
                                                                    obj_address = ele.replace('地址：', "").replace("臺", "台")
                                                                    obj_city = obj_address[:3]
                                                                except Exception as e:
                                                                    print(str(e))

                                                            if '所在樓層：' in ele:
                                                                try:
                                                                    #floor
                                                                    obj_floor = ele.replace('所在樓層：', "")
                                                                    
                                                                except Exception as e:
                                                                    print(str(e))
                                                            
                                                            if '屋齡：' in ele:
                                                                try:
                                                                    #year
                                                                    ele = ele.replace('屋齡：', "").split("年")
                                                                
                                                                    if len(ele) == 1:
                                                                        #可能是預售屋，或是沒有 "個月"
                                                                        try:
                                                                            obj_year = float(ele[0])
                                                                        except Exception as e:
                                                                            print(str(e))
                                                                    elif len(ele) == 2:
                                                                        try:
                                                                            year = float(ele[0])
                                                                            month = round(float(ele[1].replace("個月", "")) / 12, 1)
                                                                            obj_year = year + month
                                                                        except Exception as e:
                                                                            print(str(e))
                                

                                                                except Exception as e:
                                                                    print(str(e))

                                                            if "車位描述：" in ele:
                                                                ele = ele.replace("'車位描述：", "")
                                                                if "無" not in ele:
                                                                    #park
                                                                    obj_park = True
                                                            
                                                            # obj_elevator 無法預測，因此預設都是 False
                                                            # obj_type 無法預測，因此預設都是 ""

                                                    #size description
                                                    if len(soup.select('.house__introRow .introRow__item')) > 0:
                                                        description = [ele.text.strip().replace(" ", "").replace("\n", "") for ele in soup.select('.house__introRow .introRow__item')]
                                                        if len(description) > 1:
                                                            obj_sizeDescription = description[1]            


                                                    print([obj_url, obj_price, obj_address, obj_city, obj_buildingSize, obj_fieldSize, obj_pattern, obj_type, obj_park, obj_elevator, obj_floor, obj_year, obj_sizeDescription])

                                                    try:
                                                        # update database
                                                        db = pymysql.connect(host='<HOST_IP>', user='<USERNAME>', password='<PASSWORD>', db='<DB_NAME>', charset='utf8')
                                                        cursor = db.cursor()
                                                        sqlStr = """INSERT INTO house_items ( obj_url, obj_price, obj_address, obj_city, obj_buildingSize, obj_fieldSize, obj_pattern, obj_type, obj_park, obj_elevator, obj_floor, obj_year, obj_sizeDescription) VALUES('%s', %f, '%s', '%s', %f, %f, '%s', '%s', %d, %d, '%s', %f, '%s') ON DUPLICATE KEY UPDATE obj_url = VALUES(obj_url), obj_price=VALUES(obj_price), obj_address=VALUES(obj_address), obj_city=VALUES(obj_city), obj_buildingSize=VALUES(obj_buildingSize), obj_fieldSize=VALUES(obj_fieldSize), obj_pattern=VALUES(obj_pattern), obj_type=VALUES(obj_type), obj_park=VALUES(obj_park), obj_elevator=VALUES(obj_elevator), obj_floor=VALUES(obj_floor), obj_year=VALUES(obj_year), obj_sizeDescription=VALUES(obj_sizeDescription);""" % (obj_url, obj_price, obj_address, obj_city, obj_buildingSize, obj_fieldSize, obj_pattern, obj_type, obj_park, obj_elevator, obj_floor, obj_year, obj_sizeDescription)
                                                        cursor.execute(sqlStr)
                                                        db.commit()
                                                        cursor.close()
                                                        db.close()
                                                        print("Database updated : %s " % obj_url)

                                                    except Exception as e:
                                                        print(str(e))





                                            except Exception as e:
                                                print(str(e))

                                        sleep(2)
                                
                        sleep(2)



                except Exception as e:
                    print(str(e))

        sleep(2)


if __name__ == "__main__":
    main()
