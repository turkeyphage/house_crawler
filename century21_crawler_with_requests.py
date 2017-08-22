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

    main_url = "http://www.century21.com.tw/index/House/Buy"


    # get total page
    s = requests.Session()
    set_session_header(s)
    response = s.get(main_url)


    if response.status_code == 200:
        # print(response.content.decode('utf-8'))
        soup = BeautifulSoup(response.content, 'html5lib')
        if len(soup.select('.tablePagination.textC.borderT ul li')) > 0:

            try:
                tablePagination = soup.select(
                    '.tablePagination.textC.borderT ul li')
                finalPage = int([ele.text.strip().replace(" ", "").replace(
                    "\n", "") for ele in tablePagination][-2])
                # print(finalPage)

                sleep(2)

                for i in range(1, finalPage + 1):
                    pageIndex = "page=" + str(i)
                    pageURL = "?".join([main_url, pageIndex])
                    # print(pageURL)

                    set_session_header(s)
                    response = s.get(pageURL)
                    if response.status_code == 200:
                        # print(response.content.decode('utf-8'))
                        soup = BeautifulSoup(response.content, 'html5lib')
                        if len(soup.select('.main.clearfix .infoBox h2 a')) > 0:
                            items_href = [ele['href'] for ele in soup.select(
                                '.main.clearfix .infoBox h2 a')]

                            sleep(2)

                            for item in items_href:
                                item_url = 'http://www.century21.com.tw' + item

                                # 爬取各個房屋
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
                                            # obj_totalfloor = 1 #樓層
                                            obj_year = 0.0  # 屋齡
                                            obj_sizeDescription = ""  # 建地詳述


                                            if len(soup.select('.forms.unstyled.clearfix li .w-half')) > 0:
                                                obj = soup.select('.forms.unstyled.clearfix li .w-half')
                                                obj = [ele.text.strip().replace(" ", "").replace("\n", "") for ele in obj]

                                                for ele in obj:
                                                    #price
                                                    if '總價' in ele:
                                                        try:
                                                            obj_price = float(ele.replace("總價", "").replace(
                                                                "萬", "").replace(",", ""))
                                                        except Exception as e:
                                                            print(str(e))

                                                    if '種類' in ele:
                                                        try:
                                                            obj_type = ele.replace("種類", "").replace("/用途", "")
                                                        except Exception as e:
                                                            print(str(e))
                                                    
                                                    if '地址' in ele:
                                                        try:
                                                            obj_address = ele.replace("地址", "")
                                                            obj_city = obj_address[:3]
                                                        except Exception as e:
                                                            print(str(e))

                                                    if '樓層' in ele:
                                                        try:
                                                            obj_floor = ele.replace("樓層", "").replace(
                                                                "樓", "")
                                                        except Exception as e:
                                                            print(str(e))
                                                    
                                                    if '格局' in ele:
                                                        try:
                                                            obj_pattern = ele.replace("格局", "")
                                                        except Exception as e:
                                                            print(str(e))

                                                    if '屋齡' in ele:
                                                        try:
                                                            obj_year = float(ele.replace("屋齡", "").replace("年", ""))
                                                        except Exception as e:
                                                            print(str(e))

                                                    if '車位' in ele:
                                                        if '有' in ele :
                                                            obj_park = True
                                                    
                                                    if '電梯' in ele:
                                                        if '有' in ele:
                                                            obj_elevator = True

                                                

                                            if len(soup.select('.forms.unstyled.area li .w-half')) > 0:
                                                    obj = soup.select('.forms.unstyled.area li .w-half')
                                                    obj = [ele.text.strip().replace(" ", "").replace("\n", "") for ele in obj]
                                                    
                                                    for ele in obj:

                                                        if '主建築面積' in ele:
                                                            try:
                                                                obj_buildingSize = float(ele.replace("主建築面積","").replace("坪",""))
                                                            except Exception as e:
                                                                print(str(e))

                                                        if '土地持有面積' in ele:
                                                            try:
                                                                obj_fieldSize = float(ele.replace("土地持有面積", "").replace("坪", ""))
                                                            except Exception as e:
                                                                print(str(e))

                                                        obj_sizeDescription = " ".join([obj_sizeDescription, ele])

                                                    obj_sizeDescription = obj_sizeDescription.strip()


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



if __name__ == "__main__":
    main()
