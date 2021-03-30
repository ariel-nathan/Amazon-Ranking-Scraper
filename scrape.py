import csv
import json
import re
from config import apiToken
from datetime import date
from urllib.request import urlopen

today = date.today()
csvName = "Ranking Tracker " + str(today) + ".csv"
asinlist = []
productList = []
colNames = ['asin', 'title', 'price', 'category rank 1', 'category rank 1 label', 'category rank 2', 'category rank 2 label', 'category rank 3', 'category rank 3 label', 'date']
x = 0
i = 1
errorCount = 0

url = 'https://api.proxycrawl.com/scraper?token=' + apiToken + '&url=https://amazon.com/dp/'

with open(csvName, 'w', newline='') as csvfile: 
    writer = csv.DictWriter(csvfile, fieldnames = colNames)
    writer.writeheader()

with open('asins.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        asinlist.append(row[0])
        x += 1

def getAsinData(asin):
    global i
    
    handler = urlopen(url + asin)
    productData = json.loads(handler.read())

    productInfo = productData['body']['productInformation']

    for z in productInfo:
        if (z['name'] == "Best Sellers Rank"):
            productRank = z['value']

    catLabel1 = productRank[productRank.index("in"):productRank.index("(") - 1]
    z = productRank.index(')') + productRank[productRank.index(')'):].index('in')
    catLabel2 = productRank[z:]

    productRank = productRank.replace('100','')
    temp = re.findall(r'\d+', productRank.replace(',',''))
    res = list(map(int, temp))

    if len(res) == 2:
        res.append(None)
        catLabel3 = None
    else: 
        n = productRank.index(')') + productRank[productRank.index(')'):].index('in') + 1
        catLabel3 = productRank[n + productRank[n:].index('in'):]

    product = {
    'asin': productData['body']['productInformation'][3]['value'],
    'title': productData['body']['name'],
    'price': productData['body']['price'],
    'category rank 1': res[0],
    'category rank 1 label': catLabel1,
    'category rank 2': res[1],
    'category rank 2 label':  catLabel2,
    'category rank 3': res[2],
    'category rank 3 label': catLabel3,
    'date': today
    }

    productList.append(product)

    with open(csvName, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = colNames)
        writer.writerow(product)

    return(product)

#for asin in asinlist:
    #try:
    #    print("Processing ASIN: " + asin)
    #    getAsinData(asin)
    #except Exception as e:
    #    errorCount += 1
    #    print("Error on Parent ASIN: " + asin)
    #    pass
    #finally:
    #    print("Processing Done on ASIN: " + asin + " | " + str(i) + " out of " + str(x))
    #    if (i == x):
    #        print("All items processed")
    #    i += 1
