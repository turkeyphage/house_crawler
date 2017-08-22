#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
from flask import Flask, render_template, request

import re
import pymysql
import json


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

host_ip = '<HOST_IP>'
username = '<USERNAME>'
password = '<PASSWORD>'
db_name = '<DB_NAME>'

@app.route('/', methods= ['POST', 'GET'])
def index():

    if request.method == 'POST':
        searchString = request.form['queryStr']   

    else:
        searchString = request.args.get('queryStr')
 
    if searchString == None: 
        return render_template("index.html", search_value="")
    else:

        searchString = searchString.strip()

        if searchString == "":
            return render_template("index.html", search_value="")
        else:
            db = pymysql.connect(host=host_ip, user=username,
                                 password=password, db=db_name, charset='utf8')
            cursor = db.cursor()

            finalResults = []
            cityRegex = re.compile(r'\w\w[縣市]')
            match_city = cityRegex.search(searchString)

            searchCity = ""
            others = ""

            if match_city == None:
                #可能是直接打了街道地址
                others = searchString
                queryString = """SELECT  * FROM house_items WHERE obj_address like '%s' ORDER BY id; """ % ("%" + others + "%")
                cursor.execute(queryString)
                theResult = cursor.fetchall()

                if len(theResult) != 0:
                        for ele in theResult:
                            item = {
                                "id": str(ele[13]),
                                "price": str(ele[1]) + "萬"
                            }

                            finalResults.append(item)
            else:

                searchCity = match_city.group()
                others = searchString.replace(searchCity, "")
                queryString = """ SELECT obj_city FROM house_items WHERE obj_city LIKE '%s' ORDER BY id; """ % (
                    "%" + searchCity + "%") 
                cursor.execute(queryString)
                theResult = cursor.fetchall()

                if len(theResult) == 0:
                    #沒有在縣市名單內
                    others = searchString
                    queryString = """SELECT  * FROM house_items WHERE obj_address like '%s' ORDER BY id; """ % (
                        "%" + others + "%")
                    cursor.execute(queryString)
                    theResult = cursor.fetchall()

                    if len(theResult) != 0:
                        for ele in theResult:

                            item = {
                                "id": str(ele[13]),
                                "price": str(ele[1]) + "萬"
                            }

                            finalResults.append(item)

                else:
                    queryString = """SELECT * FROM house_items WHERE obj_city in (select obj_city from house_items where obj_city = '%s') and obj_address like '%s' ORDER BY id; """ % (
                        searchCity, "%" + others + "%")
                    cursor.execute(queryString)
                    theResult = cursor.fetchall()

                    if len(theResult) != 0:
                        for ele in theResult:
                            
                            item = {
                                "id": str(ele[13]),
                                "price": str(ele[1]) + "萬"
                            }
                            finalResults.append(item)

            cursor.close()
            db.close()

            if len(finalResults) != 0:
                return render_template("index.html", search_value=searchString, finalResults=finalResults)
            else:
                return render_template("index.html", search_value=searchString)


@app.route('/detail.html', methods=['POST', 'GET'])
def detail():
    if request.method == 'POST':
        searchID = request.form['id']

    else:
        searchID = request.args.get('id')
    db = pymysql.connect(host=host_ip, user=username,
                         password=password, db=db_name, charset='utf8')
    cursor = db.cursor()
    queryString = """SELECT  * FROM house_items WHERE id = %d """ % (int(searchID))

    cursor.execute(queryString)

    returnItem = cursor.fetchall()[0]
    itemDetail = {
        'url': returnItem[0],
        'price': str(returnItem[1])+"萬",
        'address': returnItem[2],
        'city': returnItem[3],
        'building': str(returnItem[4])+"坪",
        'field': str(returnItem[5])+"坪",
        'pattern': returnItem[6],
        'type':returnItem[7],
        'park': returnItem[8],
        'elevator': returnItem[9],
        'floor': returnItem[10],
        'year': str(returnItem[11]),
        'desc': returnItem[12],
        'id': returnItem[13]
        }

    cursor.close()
    db.close()
    
    return render_template("detail.html", detailValue=itemDetail)



if __name__ == '__main__':
	app.run(host=host_ip, port=5000)
