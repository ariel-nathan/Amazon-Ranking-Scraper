import csv
import json
import re
from config import *
from datetime import date, datetime
from urllib.request import urlopen

i = 1
asinList = []
errorCount = 0
remainingRequests = 0

url = 'https://api.proxycrawl.com/scraper?token=' + apiToken + '&url=https://amazon.com/dp/'

def getAsinData(asin):
    global remainingRequests
    
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

def process(asinList):
    global i
    x = len(asinList)
    global errorCount
    for asin in asinList:
        try:
            print("Processing ASIN: " + asin[0])
            getAsinData(asin[0])
        except Exception as e:
            errorCount += 1
            print("Error on Parent ASIN: " + asin[0])
            print("Error: " + str(e))
            pass
        finally:
            print("Processing Done on ASIN: " + asin[0] + " | " + str(i) + " out of " + str(x) + "\n")
            if (i == x):
                print("All items processed")
                if (errorCount > 0):
                    print(str(errorCount) + " Errors Caught")
            i += 1

with open('asins.csv', 'r') as f:
    reader = csv.reader(f)

    for asin in reader:
        asinList.append(asin)

#To process all asins on list
process(asinList)
#To process a single asin in case of error
#process([["B08NWGF4XB"]])