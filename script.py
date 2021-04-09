import os
import re
import csv
import json
import pandas as pd
from urllib.request import urlopen
from config import apiToken, collection
from datetime import date, datetime

asinList = []
url = 'https://api.proxycrawl.com/scraper?token=' + apiToken + '&url=https://amazon.com/dp/'

asins_csv = pd.read_csv('./asins.csv', names=["ASIN"])

for asin in asins_csv['ASIN']:
    asinList.append(asin)

def processAsins(asinList):
    i = 1
    x = len(asinList)
    errorList = []

    for asin in asinList:
        try:
            print("Processing ASIN " + asin)
            getAsinData(asin)
        except Exception as e:
            print("Error on Parent ASIN: " + asin)
            print("Error Message: " + str(e))
            errorList.append([asin, str(e)])
            pass
        finally:
            print("Processing Done on ASIN: " + asin + " | " + str(i) + " out of " + str(x) + "\n")

            if (i == x):
                handleErrors(errorList)

            i += 1

def getAsinData(asin):
    handler = urlopen(url + asin)
    productData = json.loads(handler.read())

    remainingRequests = productData['remaining_requests']
    print("Remaining API Calls: " + str(remainingRequests))

    productInfo = productData['body']['productInformation']

    for info in productInfo:
        if (info['name'] == "Best Sellers Rank"):
            productRank = info['value']

    catLabel1 = productRank[productRank.index("in"):productRank.index("(") - 1]
    tempz = productRank.index(')') + productRank[productRank.index(')'):].index('in')

    productRank = productRank.replace('100','')
    tempx = re.findall(r'\d+', productRank.replace(',',''))
    res = list(map(int, tempx))

    if len(res) == 2:
        catLabel2 = productRank[tempz:]
        res.append(None)
        catLabel3 = None
    elif len(res) > 2: 
        tempy = productRank[tempz:].index('#') - 1
        catLabel2 = productRank[tempz:tempy+tempz]
        tempn = productRank.index(')') + productRank[productRank.index(')'):].index('in') + 1
        catLabel3 = productRank[tempn + productRank[tempn:].index('in'):]
    else:
        res.append(None)
        res.append(None)
        catLabel2 = None
        catLabel3 = None

    product = {
    'parent-asin': asin,
    'asin': productData['body']['productInformation'][3]['value'],
    'title': productData['body']['name'],
    'category': productData['body']['breadCrumbs'][-1]['name'],
    'price': productData['body']['price'],
    'main-image': productData['body']['mainImage'],
    'category rank 1': res[0],
    'category rank 1 label': catLabel1,
    'category rank 2': res[1],
    'category rank 2 label':  catLabel2,
    'category rank 3': res[2],
    'category rank 3 label': catLabel3,
    'date': datetime.now()
    }

    print("Adding Record to Database")
    collection.insert_one(product)

def handleErrors(errorList):
    errorCount = len(errorList)

    if (errorCount > 0):
        print(str(errorCount) + " Errors Caught")
        with open('errors.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for error in errorList:
                writer.writerow(error)
        print("Errors logged to errors.csv\n")
        choice = input("Would you like to retry the ASINs with Errors? (y/n): ")
        if (choice == "y" or choice == "Y"):
            processAsins(errorList)
        elif (choice == "n" or choice == "N"):
            print("Ok, program completed")
        else:
            print("Error: Invalid Input")
    else:
        try:
            print("All items processed succesfully")
            os.remove('errors.csv')
        except:
            pass

processAsins(asinList)