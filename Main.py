import os,json,requests,shutil,zipfile
from numpy import empty
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import time
import pandas as pd
import csv
import datetime

def downloadRelevantFiles(overwrite = False):
    #Gotta do the header otherwise they block you lul
    headers = {
        'user-agent': 'Clayton Jannusch Education claytonjannusch@gmail.com',
    }

    if not os.path.exists("ticker.txt") or overwrite:
        url = 'https://www.sec.gov/include/ticker.txt'
        r = requests.get(url, allow_redirects=True,headers=headers)
        open('ticker.txt', 'wb').write(r.content)

    if not os.path.exists("companyfacts.zip") or not os.path.exists("companyfacts") or overwrite:
        url = 'http://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip'
        r = requests.get(url, allow_redirects=True, stream = True,headers=headers)
        open('companyfacts.zip', 'wb').write(r.content)
        #Unzips file
        with zipfile.ZipFile("companyfacts.zip", 'r') as zip_ref:
            zip_ref.extractall("companyfacts")

def convertTickersToCIKDict():
    file = open("ticker.txt", 'r')
    lines = file.readlines()
    tickerToCIKDict,cikToTickerDict = {},{}
    for line in lines:
        tickerToCIKDict[line[0:line.index("\t")]] = line[line.index("\t") + 1:-1]

    cikToTickerDict = {v: k for k, v in tickerToCIKDict.items()}

    return tickerToCIKDict,cikToTickerDict

def convertTickerToCIK(ticker,tickerToCIKDict):
    return tickerToCIKDict[ticker]

def convertCIKToTicker(CIK,cikToTickerDict):
    return cikToTickerDict[CIK]

def getFactsOfCompany(CIK, toGraph = False, debug = False):
    
    if type(CIK) == int:
        CIK = str(CIK)
    file = "CIK"
    for i in range(10 - len(CIK)):
        file = file + "0"

    file = file + CIK + ".json"
    fileName = os.path.join("companyfacts",file)
    file = open(fileName)
    result = json.load(file)
    if debug:
        print(result["entityName"])
    file = open("Fields To Grab.txt", 'r')
    listOfFields = file.readlines()
    for field in listOfFields:
        
        try:
            data = result['facts']['us-gaap'][field.strip()]['units']['USD']
            if debug:
                print("got data in", field)
        except Exception as excep:
            if debug:
                print("error",excep.with_traceback)
            continue
        
        dates,values = [],[]
        for point in data:
            dates.append(point['end'])
            values.append(point['val'])

        #print(len(dates),len(values))
        
        if toGraph:

            x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval = 365))
            plt.plot(x,values)
            plt.xlabel('date' + ' (' + str(len(values)) + ' # of data points)', fontsize=16)
            plt.ylabel(field, fontsize=8)
            plt.gcf().autofmt_xdate()
            plt.show()
    
    return result

def readNames():

    listOfFiles = os.listdir("companyfacts")

    count = 0
    listOfNames = []

    for file in listOfFiles:
        fileName = os.path.join("companyfacts",file)
        file = open(fileName)
        result = json.load(file)
        try:
            name = result["entityName"]
        except Exception:
            print("error getting name")
            continue
        if name == "":
            continue
        listOfNames.append(name)
        count = count + 1
        
    print(set(listOfNames))

def getFieldOfCompanyOfGivenYear(CIK,fieldInQuestion,Year,debug = False):
    result = getFactsOfCompany(CIK, toGraph = False, debug = False)
    try:
        data = result['facts']['us-gaap'][fieldInQuestion]['units']['USD']
    except Exception:
        if debug:
            print("could not find field")
        return
    toReturn = None
    for point in data:
        #print(point)
        if point['form'] == "10-K" and point['end'][0:4] == str(Year) and point['fy'] == Year:
            toReturn = (point['val'],point['end'])
            #print(point)
    if toReturn == None:
        print("Could not find Field:", fieldInQuestion, "for year",Year)

    return toReturn

def getPastFieldWithinInterval(CIK,fieldInQuestion,beginningYear,endingYear):
    data = []
    for i in range(endingYear-beginningYear):
        data.append(getFieldOfCompanyOfGivenYear(CIK,fieldInQuestion,beginningYear + i))

    return data

def getFieldsForGivenCompany(CIK):
       
    if type(CIK) == int:
        CIK = str(CIK)
    file = "CIK"
    for i in range(10 - len(CIK)):
        file = file + "0"

    file = file + CIK + ".json"
    fileName = os.path.join("companyfacts",file)
    file = open(fileName)
    result = json.load(file)
    data = result['facts']['us-gaap']
    return data.keys()

def getAllFieldsForLastFiveYearsToCSV(CIK):
    year = datetime.datetime.now().year
    file = open("Fields To Grab.txt", 'r')
    listOfFields = getFieldsForGivenCompany(CIK)
    #listOfFields = file.readlines()
    #listOfFields = ["AccountsPayableCurrent","AccruedLiabilitiesCurrent","Assets","AvailableForSalesSecurities"]
    finalCSVData = []
    count = 0
    for field in listOfFields:
        print(field)
        '''
        if count == 25:
        break'''
        dataList = []
        result = getPastFieldWithinInterval(CIK,field,year - 5,year)
        #print(result)
        for item in result:
            #print(item)
            if item == None:
                dataList.append(None)
                continue
            dataList.append(item[0])
        #print(dataList)
        finalCSVData.append(pd.Series(dataList,index=[str(year - 5),str(year - 4),str(year - 3),str(year - 2),str(year - 1)], name = field))
        count = count + 1
    #print(finalCSVData)

    df = pd.DataFrame(finalCSVData)
    #print(df)

    df.to_csv("test123.csv", encoding='utf-8')




def Main():
    start_time = time.time()
    downloadRelevantFiles()
    tickerToCIKDict,cikToTickerDict = convertTickersToCIKDict()
    print("init time took ", time.time() - start_time, "to run")

    #print(convertTickerToCIK("aapl",tickerToCIKDict))
    #getFactsOfCompany(convertTickerToCIK("f",tickerToCIKDict))
    #getFactsOfCompany(4611)
    #readNames()

    #dataPoint = getFieldOfCompanyOfGivenYear(convertTickerToCIK("amd",tickerToCIKDict),"CashAndCashEquivalentsAtCarryingValue",2020)
    #print(dataPoint)

    start_time = time.time()

    #dataPoints = getPastFieldWithinInterval(convertTickerToCIK("amd",tickerToCIKDict),"Assets",2010,2021)
    #print(dataPoints)

    getAllFieldsForLastFiveYearsToCSV(convertTickerToCIK("amd",tickerToCIKDict))
    print()
    print("init time took ", time.time() - start_time, "to find the field for given year")

Main()