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
    #session.headers['Host'] = "https://buy.yungching.com.tw/region"


def main():
    #所有縣市
    allCities = ['台北市', '新北市', '基隆市', '宜蘭縣', '新竹市', '新竹縣', '桃園市', '苗栗縣', '台中市', '彰化縣',
                '南投縣', '嘉義市', '嘉義縣', '雲林縣', '台南市', '高雄市', '澎湖縣', '金門縣', '屏東縣', '台東縣', '花蓮縣']

    main_url = "https://buy.yungching.com.tw/region"


    for city in allCities:
        cityString = city + "-_c"
        s = requests.Session()
        set_session_header(s)
        page_url = "/".join([main_url, cityString])
        response = s.get(page_url)
        

        if response.status_code == 200:
            # print(response.content.decode('utf-8'))
            soup = BeautifulSoup(response.content, 'html5lib')

            if len(soup.select('.ga_click_trace')) > 0:
                try:
                    #找到總共頁數
                    totalPages = int(soup.select('.m-pagination-bd .ga_click_trace')[-1]['href'].split('=')[-1])
                    # print(totalPages)
                    for pageNum in range(1, totalPages + 1):
                        sleep(2)
                        pageIndex = "?pg=" + str(pageNum)
                        currentPage = "/".join([main_url, cityString, pageIndex])
                        set_session_header(s)
                        response = s.get(currentPage)
                        # print(currentPage)
                        if response.status_code == 200:
                            # print(response.content.decode('utf-8'))
                            soup = BeautifulSoup(response.content, "html5lib")

                            # print(soup.getText())
                            if len(soup.select('.m-list-item .item-info .item-title.ga_click_trace')) > 0:
                                allitem_urls = soup.select(
                                    '.m-list-item .item-info .item-title.ga_click_trace')
                                
                                for ele in allitem_urls:
                                    
                                    ele_url = ele['href']
                                    
                                    url_base = "https://buy.yungching.com.tw"
                                    item_url = url_base + ele_url
                                    
                                    set_session_header(s)
                                    sleep(2)
                                    response = s.get(item_url)

                                    if response.status_code == 200 and "ROBOTS" not in response.content.decode('utf-8'):
                                        soup = BeautifulSoup(response.content, 'html5lib')
                                        
                                        try:
                                            if "Request unsuccessful" not in soup.getText() and "該物件已下架或不存在" not in soup.getText() and "網站維護中" not in soup.getText():

                                                obj_url = item_url
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

                                                if len(soup.select('.detail-list-lv2')) > 0:
                                                    try:
                                                        obj_sizeDescription = soup.select(
                                                            '.detail-list-lv2')[0].getText().strip().replace(" ", "").replace("\n", " ")
                                                    except Exception as e:
                                                        print(str(e))

                                                if len(soup.select('.price-num')) > 0:
                                                    try:
                                                        obj_price = float(soup.select('.price-num')
                                                                        [0].getText().replace(",", ""))
                                                    except Exception as e:
                                                        print(str(e))

                                                if len(soup.select('.house-info-addr')) > 0:
                                                    try:
                                                        obj_address = soup.select('.house-info-addr')[0].getText()
                                                    except Exception as e:
                                                        print(str(e))

                                                    try:
                                                        obj_city = obj_address[:3]
                                                    except Exception as e:
                                                        print(str(e))

                                                if len(soup.select('.m-house-detail-list.bg-bed')) > 0:
                                                    try:
                                                        obj_pattern = soup.select('.m-house-detail-list.bg-bed')[0].select(
                                                            '.detail-list-lv1')[0].getText().strip().replace(" ", "").replace("\n", " ")
                                                    except Exception as e:
                                                        print(str(e))

                                                if len(soup.select('.m-house-detail-list.bg-car .detail-list-lv1 li')) > 0:
                                                    try:
                                                        parkDetail = soup.select(
                                                            '.m-house-detail-list.bg-car .detail-list-lv1 li')
                                                        parkDetail = [ele.text.strip().replace(
                                                            " ", "").replace("\n", "") for ele in parkDetail]
                                                        for ele in parkDetail:
                                                            if "車位" in ele:
                                                                obj_park = True
                                                    except Exception as e:
                                                        print(str(e))

                                                if len(soup.select('.m-house-detail-ins .detail-list-lv1 li')) > 0:
                                                    try:
                                                        houseDetailIns = soup.select(
                                                            '.m-house-detail-ins .detail-list-lv1 li')
                                                        houseDetailIns = [ele.text.strip().replace(
                                                            " ", "").replace("\n", "") for ele in houseDetailIns]

                                                        for ele in houseDetailIns:
                                                            if "電梯" in ele:
                                                                obj_elevator = True
                                                    except Exception as e:
                                                        print(str(e))

                                                if len(soup.select('.m-house-detail-list.bg-square .detail-list-lv1 li')) > 0:
                                                    areaDetail = soup.select(
                                                        '.m-house-detail-list.bg-square .detail-list-lv1 li')
                                                    areaDetail = [ele.text.strip().replace(
                                                        " ", "").replace("\n", "") for ele in areaDetail]

                                                    for ele in areaDetail:
                                                        if "土地坪數" in ele:
                                                            try:
                                                                obj_fieldSize = float(
                                                                    ele.split("：")[-1].replace("坪", ""))
                                                            except ValueError:
                                                                print("object " + fn + " 土地坪數無法轉換成數字")


                                                if len(soup.select('.house-info-sub .text span')) > 0:
                                                    houseInfo = soup.select('.house-info-sub .text span')
                                                    houseInfo = [ele.text.strip().replace(
                                                        " ", "").replace("\n", "") for ele in houseInfo]
                                                    for ele in houseInfo:
                                                        if "建物" in ele:
                                                            try:
                                                                obj_buildingSize = float(
                                                                    ele.replace("建物", "").replace("坪", ""))
                                                            except ValueError:
                                                                print("object " + fn + " 建物坪數無法轉換成數字")

                                                        if "年" in ele:
                                                            try:
                                                                obj_year = float(ele.replace("年", ""))
                                                            except ValueError:
                                                                print("object " + fn + " 年數無法轉換成數字")

                                                        if "~" in ele:
                                                            try:
                                                                obj_floor = ele.split("~")[0]
                                                            except Exception as e:
                                                                print(str(e))

                                                    try:
                                                        obj_type = " ".join(houseInfo[-2:])
                                                    except Exception as e:
                                                        print(str(e))

                                                print([obj_url, obj_price, obj_address, obj_city, obj_buildingSize, obj_fieldSize,
                                                    obj_pattern, obj_type, obj_park, obj_elevator, obj_floor, obj_year, obj_sizeDescription])

                                                try:
                                                    # update database
                                                    db = pymysql.connect(host='<HOST_IP>', user='<USERNAME>', password='<PASSWORD>', db='<DB_NAME>', charset='utf8')  
                                                    cursor = db.cursor()
                                                    sqlStr = """INSERT INTO house_items ( obj_url, obj_price, obj_address, obj_city, obj_buildingSize, obj_fieldSize, obj_pattern, obj_type, obj_park, obj_elevator, obj_floor, obj_year, obj_sizeDescription) VALUES('%s', %f, '%s', '%s', %f, %f, '%s', '%s', %d, %d, '%s', %f, '%s') ON DUPLICATE KEY UPDATE obj_url = VALUES(obj_url), obj_price=VALUES(obj_price), obj_address=VALUES(obj_address), obj_city=VALUES(obj_city), obj_buildingSize=VALUES(obj_buildingSize), obj_fieldSize=VALUES(obj_fieldSize), obj_pattern=VALUES(obj_pattern), obj_type=VALUES(obj_type), obj_park=VALUES(obj_park), obj_elevator=VALUES(obj_elevator), obj_floor=VALUES(obj_floor), obj_year=VALUES(obj_year), obj_sizeDescription=VALUES(obj_sizeDescription);""" % (
                                                        obj_url, obj_price, obj_address, obj_city, obj_buildingSize, obj_fieldSize, obj_pattern, obj_type, obj_park, obj_elevator, obj_floor, obj_year, obj_sizeDescription)     
                                                    cursor.execute(sqlStr)
                                                    db.commit()
                                                    cursor.close()
                                                    print("Database updated : %s " % obj_url)
                                                    db.close()

                                                except Exception as e:
                                                    print(str(e))

                                        except Exception as e:
                                            print(str(e))
                                        
                except Exception as e:
                    print(str(e))


        sleep(3)

if __name__ == "__main__":
    main()
