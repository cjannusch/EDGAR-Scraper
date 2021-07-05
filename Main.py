import os,json,requests,shutil,zipfile

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

def readNames():

    listOfFiles = os.listdir("companyfacts")

    count = 0

    for file in listOfFiles:
        if count == 1:
            break
        fileName = os.path.join("companyfacts",file)
        #fileName = os.path.join("companyfacts","CIK0001018724.json")
        file = open(fileName)
        result = json.load(file)
        print(type(result))
        print(result["entityName"])
        count = count + 1

def Main():
    downloadRelevantFiles()
    #tickerToCIKDict,cikToTickerDict = convertTickersToCIKDict()
    #print(convertTickerToCIK("aapl",tickerToCIKDict))
    #getFactsOfCompany(convertTickerToCIK("plug",tickerToCIKDict))

Main()