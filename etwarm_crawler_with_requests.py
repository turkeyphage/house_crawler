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

    main_url = "http://www.etwarm.com.tw/object_list"


    for city in allCities:
        
        cityString = "area=" + city
        url_region = "?".join([main_url, cityString])
        
        s = requests.Session()
        set_session_header(s)
        # print(url_region)
        response = s.get(url_region)
        # print(response.status_code)
        # print(response.content.decode('utf-8'))

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html5lib')

            if len(soup.select('.page a')) > 0:
                paginations = soup.select('.page a')
                
                try:
                    #計算總共有幾頁
                    totalPages = 1
                    for ele in paginations:
                        maybePage = int(ele['href'].split('=')[-1])
                        if maybePage > totalPages:
                            totalPages = maybePage
                
                    for i in range(1, totalPages+1):
                        pageString = "page=" + str(i)
                        url_region_page = "&".join([url_region, pageString])
                        sleep(2)
                        set_session_header(s)
                        response = s.get(url_region_page)
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html5lib')
                            
                            if len(soup.select('.obj_info a')) > 0:
                                #獲取物件url
                                a_list = soup.select('.obj_info a')
                                itemURL_list = []
                                for each_a in a_list:
                                    houseItemURL = each_a['href']
                                    itemURL_list.append(houseItemURL)


                                if len(itemURL_list) > 0:
                                    for each_url in itemURL_list:
                                        sleep(2)
                                        set_session_header(s)
                                        response = s.get(each_url)

                                        if response.status_code == 200 and "ROBOTS" not in response.content.decode('utf-8'):
                                            soup = BeautifulSoup(response.content, 'html5lib')

                                            try:
                                                if "Request unsuccessful" not in soup.getText() and "該物件已下架或不存在" not in soup.getText() and "網站維護中" not in soup.getText():

                                                    obj_url = each_url
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

                                                    #price
                                                    if len(soup.select('.data_basic .obj_data_contain.fl .price')) > 0:
                                                        obj = soup.select('.data_basic .obj_data_contain.fl .price')
                                                        obj = [ele.text.strip().replace(" ", "").replace("\n", "")
                                                            for ele in obj]
                                                        try:
                                                            obj_price = float(obj[0].replace(",", ""))

                                                        except Exception as e:
                                                            print(str(e))

                                                    #address
                                                    if len(soup.select('#obj_data_detail .table .tr .td')) > 0:
                                                        obj = soup.select('#obj_data_detail .table .tr .td')
                                                        obj = [ele.text.strip().replace(" ", "").replace("\n", "") for ele in obj]
                                                    

                                                        if "‧格局" in obj:
                                                            index = obj.index("‧格局")
                                                            if obj[index + 1] != "-":
                                                                #pattern
                                                                obj_pattern = obj[index + 1]

                                                        if "‧地址" in obj:
                                                            index = obj.index("‧地址")
                                                            if obj[index + 1] != "-":
                                                                #address
                                                                obj_address = obj[index + 1]
                                                                #city
                                                                obj_city = obj_address[:3]

                                                        if "‧類型" in obj:
                                                            index = obj.index("‧類型")
                                                            if obj[index + 1] != "-":
                                                                #type
                                                                obj_type = obj[index + 1]

                                                        if "‧屋齡" in obj:
                                                            index = obj.index("‧屋齡")
                                                            if obj[index + 1] != "-":
                                                                try:
                                                                    #year
                                                                    obj_year = float(obj[index + 1].replace("年", ""))

                                                                except Exception as e:
                                                                    print(str(e))

                                                        if "‧電梯" in obj:
                                                            index = obj.index("‧電梯")
                                                            if obj[index + 1] != "-" and obj[index + 1] != "無":
                                                                #elevator
                                                                obj_elevator = True

                                                        if "‧車位" in obj:
                                                            index = obj.index("‧車位")
                                                            if obj[index + 1] != "-" and obj[index + 1] != "無":
                                                                #park
                                                                obj_park = True

                                                        if "‧樓層" in obj:
                                                            index = obj.index("‧樓層")
                                                            if obj[index + 1] != "-":
                                                                try:
                                                                    #floor
                                                                    obj_floor = obj[index + 1].strip().replace(" ",
                                                                                                            "").replace("(總樓層)", "").split('/')[0]
                                                                except Exception as e:
                                                                    print(str(e))

                                                    #size
                                                    if len(soup.select('.space')) > 0:
                                                        sizeObj = soup.select('.space')
                                                        try:
                                                            size = [ele.text.strip().replace(" ", "").replace("\n", "")
                                                                    for ele in sizeObj][0].replace("約", "")
                                                            pingIndex = size.index("坪")
                                                            # redundantStr = size[pingIndex:]

                                                            #building_size
                                                            obj_buildingSize = float(
                                                                size.replace(size[pingIndex:], ""))

                                                        except Exception as e:
                                                            print(str(e))

                                                    if len(soup.select('.data_building_list_type div')) > 0:
                                                        obj = soup.select('.data_building_list_type div')
                                                        obj = [ele.text.strip().replace(" ", "").replace("\n", "")
                                                            for ele in obj]

                                                        if "‧土地坪數" in obj:
                                                            index = obj.index("‧土地坪數")
                                                            if obj[index + 1] != "-":
                                                                try:
                                                                    #field_size
                                                                    obj_fieldSize = float(
                                                                        obj[index + 1].replace("約", "").replace("坪", ""))
                                                                except Exception as e:
                                                                    print(str(e))

                                                    if len(soup.select('.data_building_items li')) > 0:
                                                        obj = soup.select('.data_building_items li')
                                                        obj = [ele.text.strip().replace(" ", "").replace(
                                                            "\n", "").replace("\t", " ") for ele in obj]
                                                        #size_description
                                                        obj_sizeDescription = ", ".join(obj[:])

                                                    print([obj_url, obj_price, obj_address, obj_city, obj_buildingSize, obj_fieldSize,
                                                        obj_pattern, obj_type, obj_park, obj_elevator, obj_floor, obj_year, obj_sizeDescription])

                                                    try:
                                                        # update database
                                                        db = pymysql.connect(
                                                            host='<HOST_IP>', user='<USERNAME>', password='<PASSWORD>', db='<DB_NAME>', charset='utf8')
                                                        cursor = db.cursor()
                                                        sqlStr = """INSERT INTO house_items ( obj_url, obj_price, obj_address, obj_city, obj_buildingSize, obj_fieldSize, obj_pattern, obj_type, obj_park, obj_elevator, obj_floor, obj_year, obj_sizeDescription) VALUES('%s', %f, '%s', '%s', %f, %f, '%s', '%s', %d, %d, '%s', %f, '%s') ON DUPLICATE KEY UPDATE obj_url = VALUES(obj_url), obj_price=VALUES(obj_price), obj_address=VALUES(obj_address), obj_city=VALUES(obj_city), obj_buildingSize=VALUES(obj_buildingSize), obj_fieldSize=VALUES(obj_fieldSize), obj_pattern=VALUES(obj_pattern), obj_type=VALUES(obj_type), obj_park=VALUES(obj_park), obj_elevator=VALUES(obj_elevator), obj_floor=VALUES(obj_floor), obj_year=VALUES(obj_year), obj_sizeDescription=VALUES(obj_sizeDescription);""" % (
                                                            obj_url, obj_price, obj_address, obj_city, obj_buildingSize, obj_fieldSize, obj_pattern, obj_type, obj_park, obj_elevator, obj_floor, obj_year, obj_sizeDescription)
                                                        cursor.execute(sqlStr)
                                                        db.commit()
                                                        cursor.close()
                                                        db.close()
                                                        print("Database updated : %s " % obj_url)

                                                    except Exception as e:
                                                        print(str(e))



                                            except Exception as e:
                                                print(str(e))
                    # print(houseItemURL)

                except Exception as e:
                    print(str(e))

        sleep(5)

if __name__ == "__main__":
    main()
