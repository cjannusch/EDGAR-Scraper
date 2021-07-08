import os,json,requests,shutil,zipfile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import time

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

def getFieldOfCompanyOfGivenYear(CIK,fieldInQuestion,Year):
    result = getFactsOfCompany(CIK, toGraph = False, debug = False)

    data = result['facts']['us-gaap'][fieldInQuestion]['units']['USD']

    for point in data:
        #print(point)
        if point['form'] == "10-K" and point['end'][0:4] == str(Year) and point['fy'] == Year:
            toReturn = (point['val'],point['end'])
            #print(point)

    return toReturn

def Main():
    start_time = time.time()
    downloadRelevantFiles()
    tickerToCIKDict,cikToTickerDict = convertTickersToCIKDict()
    print("init time took ", time.time() - start_time, "to run")

    #print(convertTickerToCIK("aapl",tickerToCIKDict))
    #getFactsOfCompany(convertTickerToCIK("f",tickerToCIKDict))
    #getFactsOfCompany(4611)
    #readNames()

    dataPoint = getFieldOfCompanyOfGivenYear(convertTickerToCIK("amd",tickerToCIKDict),"CashAndCashEquivalentsAtCarryingValue",2020)
    print(dataPoint)
    dataPoint = getFieldOfCompanyOfGivenYear(convertTickerToCIK("amd",tickerToCIKDict),"CashAndCashEquivalentsAtCarryingValue",2019)
    print(dataPoint)
    dataPoint = getFieldOfCompanyOfGivenYear(convertTickerToCIK("amd",tickerToCIKDict),"CashAndCashEquivalentsAtCarryingValue",2018)
    print(dataPoint)
    dataPoint = getFieldOfCompanyOfGivenYear(convertTickerToCIK("amd",tickerToCIKDict),"CashAndCashEquivalentsAtCarryingValue",2017)
    print(dataPoint)
    dataPoint = getFieldOfCompanyOfGivenYear(convertTickerToCIK("amd",tickerToCIKDict),"CashAndCashEquivalentsAtCarryingValue",2016)
    print(dataPoint)

    print("init time took ", time.time() - start_time, "to find the field for given year")

Main()