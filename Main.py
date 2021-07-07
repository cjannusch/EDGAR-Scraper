import os,json,requests,shutil,zipfile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

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

def getFactsOfCompany(ticker):
    
    if type(ticker) == int:
        ticker = str(ticker)
    file = "CIK"
    for i in range(10 - len(ticker)):
        file = file + "0"

    file = file + ticker + ".json"
    fileName = os.path.join("companyfacts",file)
    file = open(fileName)
    result = json.load(file)
    print(result["entityName"])
    file = open("Fields To Grab.txt", 'r')
    listOfFields = file.readlines()
    for field in listOfFields:
        
        try:
            data = result['facts']['us-gaap'][field.strip()]['units']['USD']
            print("got data in", field)
        except Exception as excep:
            print("error",excep.with_traceback)
            continue
        
        dates,values = [],[]
        for point in data:
            dates.append(point['end'])
            values.append(point['val'])

        print(len(dates),len(values))
        
        x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval = 365))
        plt.plot(x,values)
        plt.xlabel('date' + ' (' + str(len(values)) + ' # of data points)', fontsize=16)
        plt.ylabel(field, fontsize=8)
        plt.gcf().autofmt_xdate()
        plt.show()


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

def Main():
    downloadRelevantFiles()
    tickerToCIKDict,cikToTickerDict = convertTickersToCIKDict()
    #print(convertTickerToCIK("aapl",tickerToCIKDict))
    #getFactsOfCompany(convertTickerToCIK("f",tickerToCIKDict))
    #getFactsOfCompany(4611)
    readNames()
Main()