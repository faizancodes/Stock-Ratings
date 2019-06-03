import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from itertools import cycle

stockGrades = []
symbols = []
stockCounter = 0
c = 0

def getProxies(inURL):
    page = requests.get(inURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    terms = soup.find_all('tr')
    IPs = []

    for x in range(len(terms)):  
        
        term = str(terms[x])        
        
        if '<tr><td>' in str(terms[x]):
            pos1 = term.find('d>') + 2
            pos2 = term.find('</td>')

            pos3 = term.find('</td><td>') + 9
            pos4 = term.find('</td><td>US<')
            
            IP = term[pos1:pos2]
            port = term[pos3:pos4]
            
            if '.' in IP and len(port) < 6:
                IPs.append(IP + ":" + port)
                #print(IP + ":" + port)

    return IPs 

proxyURL = "https://www.us-proxy.org/"
pxs = getProxies(proxyURL)
proxyPool = cycle(pxs)

def convertNum(stng):
    s = ''

    if len(stng) > 20:
        return 0

    for x in range(len(stng)):
        if x != len(stng) - 1 and stng[x] == '-' and stng[x + 1] != '-':
            s += stng[x]
        
        elif stng[x] == '.':
            s += stng[x]

        elif x != len(stng) - 1 and stng[x] != ',' and stng[x] != "'" and stng[x] != '"' and (not stng[x].isalpha()) and stng[x] != ':' and stng[x].isdigit() and stng[x + 1] != '"':
            s += stng[x]

    if len(s) > 0 and len(s) < 10:
        try:
            return float(s)
        except:
            return 0

    return 0


def convertGrade(stng):
    if len(stng) > 3:
        return 'null'
    else:
        return stng


def getGrade(arr):
    
    score = 0

    for x in range(len(arr)):
        if arr[x][1] == 'A+':
            score += 4.3
        if arr[x][1] == 'A':
            score += 4
        if arr[x][1] == 'A-':
            score += 3.7
        if arr[x][1] == 'B+':
            score += 3.3
        if arr[x][1] == 'B':
            score += 3
        if arr[x][1] == 'B-':
            score += 2.7
        if arr[x][1] == 'C+':
            score += 2.3
        if arr[x][1] == 'C':
            score += 2 
        if arr[x][1] == 'C-':
            score += 1.7
        if arr[x][1] == 'D+':
            score += 1.3
        if arr[x][1] == 'D':
            score += 1
        if arr[x][1] == 'D-':
            score += 0.7

    return score / len(arr)


def bubbleSort(subList): 
    
    l = len(subList) 

    for i in range(0, l): 
        
        for j in range(0, l-i-1): 
            
            if (subList[j][1] < subList[j + 1][1]): 
                tempo = subList[j] 
                subList[j]= subList[j + 1] 
                subList[j + 1] = tempo 

    return subList 


def getSymbols(inURL):
    
    global symbols
    global stockCounter
    global c

    page = requests.get(inURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    symbs = soup.find_all('a', {'class' : 'screener-link-primary'})

    for x in range(len(symbs)):
        if '&amp;b=1' in str(symbs[x]):
            symbols.append(str(symbs[x])[str(symbs[x]).find('&amp;b=1') + 10 : str(symbs[x]).find('/a') - 1])
            stockCounter = stockCounter + 1

        if stockCounter % 20 == 0:
            c = c + 20
            getSymbols('https://finviz.com/screener.ashx?v=111&o=-marketcap' + '&r=' + str(c))
        
        if stockCounter >= 500:
            break



def getInfo(sym):

    global stockGrades

    valuationStats = []
    profitabilityStats = []
    growthStats = []
    perfStats = []

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

    re = requests.get('https://www.reuters.com/finance/stocks/financial-highlights/' + sym, proxies = {"http": next(proxyPool)})
    reSoup = str(BeautifulSoup(re.text, 'html.parser'))

    yh = requests.get('https://finance.yahoo.com/quote/' + sym + '/key-statistics', proxies = {"http": next(proxyPool)})
    yhSoup = str(BeautifulSoup(yh.text, 'html.parser'))

    sa = requests.get('https://seekingalpha.com/symbol/' + sym + '/profitability', headers = headers, proxies = {"http": next(proxyPool)})
    saSoup = str(BeautifulSoup(sa.text, 'html.parser'))

    sa2 = requests.get('https://seekingalpha.com/symbol/' + sym + '/overview', headers = headers, proxies = {"http": next(proxyPool)})
    sa2Soup = str(BeautifulSoup(sa2.text, 'html.parser'))

    #print(yhSoup)
    #print(reSoup)
    #print(saSoup)
    #print(sa2Soup)

    rawYearChange = yhSoup[yhSoup.find('52WeekChange":') + 20 : yhSoup.find(',"morningStarRiskRating')]
    yearChange = convertNum(rawYearChange[rawYearChange.find('fmt') + 6 : rawYearChange.find('%')]) 

    rawSPYearChange = yhSoup[yhSoup.find('SandP52WeekChange":{') + 20 : yhSoup.find('},"priceToBook":{')]
    sp500YearChange = convertNum(rawSPYearChange[rawSPYearChange.find('fmt":"') + 6 : rawSPYearChange.find('%')])

    rawMC = yhSoup[yhSoup.find('marketCap":{') + 10 : yhSoup.find('volumeAllCurrencies')]
    marketCap = rawMC[rawMC.find('"fmt":"') + 7 : rawMC.find(',"longFmt":') - 1]

    rawCompDes = sa2Soup[sa2Soup.find('pageConfig":{') : sa2Soup.find(',"is_etf":') - 1]
    companyDescription = rawCompDes[rawCompDes.find('description":') + 14 : ]

    print('\n' + sym)

    '''
    print('\nMarket Cap:', marketCap)
    print('\n' + companyDescription)
    '''

    #print('\n52 Week Change:', str(yearChange) + '%')
    #print('SPY 52 Week Change:', str(sp500YearChange) + '%') 
    
    ####Valuation

    rawPeTTM = saSoup[saSoup.find('P/E GAAP (TTM)') + 20 : saSoup.find('P/E GAAP (TTM)') + 115]
    peTTMVal = rawPeTTM[rawPeTTM.find('value') + 7 : rawPeTTM.find(',"nm_flag')]
    peTTMGrade = rawPeTTM[rawPeTTM.find('grade') + 8 : rawPeTTM.find('","field')]
    valuationStats.append(['P/E GAAP (TTM)', peTTMGrade, peTTMVal])

    rawPE = saSoup[saSoup.find('P/E GAAP (FWD)') + 20 : saSoup.find('P/E GAAP (FWD)') + 115]
    peVal = rawPE[rawPE.find('value') + 7 : rawPE.find(',"nm_flag')]
    peGrade = rawPE[rawPE.find('grade') + 8 : rawPE.find('","field')]
    valuationStats.append(['P/E GAAP (FWD)', peGrade, peVal])

    rawPEG = saSoup[saSoup.find('PEG GAAP (TTM)') + 20 : saSoup.find('PEG GAAP (TTM)') + 115]
    pegVal = rawPEG[rawPEG.find('value') + 7 : rawPEG.find(',"nm_flag')]
    pegGrade = rawPEG[rawPEG.find('grade') + 8 : rawPEG.find('","field')]
    valuationStats.append(['PEG GAAP (TTM)', pegGrade, pegVal])

    rawPegFWD = saSoup[saSoup.find('PEG Non-GAAP (FWD)') + 20 : saSoup.find('PEG Non-GAAP (FWD)') + 115]
    pegFWDVal = rawPegFWD[rawPegFWD.find('value') + 7 : rawPegFWD.find(',"nm_flag')]
    pegFWDGrade = rawPegFWD[rawPegFWD.find('grade') + 8 : rawPegFWD.find('","field')]
    valuationStats.append(['PEG Non-GAAP (FWD)', pegFWDGrade, pegFWDVal])
    
    rawPriceSales = saSoup[saSoup.find('Price/Sales (FWD)') + 20 : saSoup.find('Price/Sales (FWD)') + 115]
    priceSalesVal = rawPriceSales[rawPriceSales.find('value') + 7 : rawPriceSales.find(',"nm_flag')]
    priceSalesGrade = rawPriceSales[rawPriceSales.find('grade') + 8 : rawPriceSales.find('","field_order')]
    valuationStats.append(['Price/Sales (FWD)', priceSalesGrade, priceSalesVal])

    rawPriceCashFlow = saSoup[saSoup.find('Price/Cash Flow (FWD)') + 20 : saSoup.find('Price/Cash Flow (FWD)') + 115]
    pricecashFlowVal = rawPriceCashFlow[rawPriceCashFlow.find('value') + 7 : rawPriceCashFlow.find(',"nm_flag')]
    pricecashFlowGrade = rawPriceCashFlow[rawPriceCashFlow.find('grade') + 8 : rawPriceCashFlow.find('","field_order')]
    valuationStats.append(['Price/Cash Flow (FWD)', pricecashFlowGrade, pricecashFlowVal])

    rawpriceBook = saSoup[saSoup.find('Price to Book (FWD)') + 20 : saSoup.find('Price to Book (FWD)') + 115]
    priceBookVal = rawpriceBook[rawpriceBook.find('value') + 7 : rawpriceBook.find(',"nm_flag')]
    priceBookGrade = rawpriceBook[rawpriceBook.find('grade') + 8 : rawpriceBook.find('","field_order')]
    valuationStats.append(['Price to Book (FWD)', priceBookGrade, priceBookVal])

    '''
    print('\nValuation:')
    print('Average:', getGrade(valuationStats))
    print('P/E Grade (TTM):', convertGrade(peTTMGrade), '(' + peTTMVal + ')')
    print('P/E Grade (FWD):', convertGrade(peGrade), '(' + peVal + ')')
    print('PEG Grade (TTM):', convertGrade(pegGrade), '(' + pegVal + ')')
    print('PEG Grade (FWD):', pegFWDGrade, '(' + pegFWDVal + ')')
    print('Price / Sales Grade:', priceSalesGrade, '(' + priceSalesVal + ')')
    print('Price/Cash Flow (FWD)', pricecashFlowGrade, '(' + pricecashFlowVal + ')')
    print('Price to Book (FWD):', priceBookGrade, '(' + priceBookVal + ')')
    '''


    ####Profitability 

    grossMargin = saSoup[saSoup.find('Gross Profit Margin (TTM)') + 20 : saSoup.find('Gross Profit Margin (TTM)') + 115]
    grossMarginVal = grossMargin[grossMargin.find('value') + 7 : grossMargin.find(',"nm_flag')]
    grossMarginGrade = grossMargin[grossMargin.find('grade') + 8 : grossMargin.find('","field_order')]
    profitabilityStats.append(['Gross Profit Margin (TTM)', grossMarginGrade, grossMarginVal + '%'])

    netIncomeMargin = saSoup[saSoup.find('Net Income Margin (TTM)') + 20 : saSoup.find('Net Income Margin (TTM)') + 115]
    netIncomeMarginVal = netIncomeMargin[netIncomeMargin.find('value') + 7 : netIncomeMargin.find(',"nm_flag')]
    netIncomeMarginGrade = netIncomeMargin[netIncomeMargin.find('grade') + 8 : netIncomeMargin.find('","field_order')]
    profitabilityStats.append(['Net Income Margin (TTM)', netIncomeMarginGrade, netIncomeMarginVal + '%'])

    cashFromOp = saSoup[saSoup.find('Cash From Operations (TTM)') + 20 : saSoup.find('Cash From Operations (TTM)') + 115]
    cashFromOpVal = cashFromOp[cashFromOp.find('value') + 7 : cashFromOp.find(',"nm_flag')]
    cashFromOpGrade = cashFromOp[cashFromOp.find('grade') + 8 : cashFromOp.find('","field_order')]
    profitabilityStats.append(['Cash From Operations (TTM)', cashFromOpGrade, cashFromOpVal])

    fcfMargin = saSoup[saSoup.find('Levered FCF Margin (TTM)') + 20 : saSoup.find('Levered FCF Margin (TTM)') + 115]
    fcfMarginVal = fcfMargin[fcfMargin.find('value') + 7 : fcfMargin.find(',"nm_flag')]
    fcfMarginGrade = fcfMargin[fcfMargin.find('grade') + 8 : fcfMargin.find('","field_order')]
    profitabilityStats.append(['Levered FCF Margin (TTM)', fcfMarginGrade, fcfMarginVal + '%'])

    rawROE = saSoup[saSoup.find('Return on Common Equity (TTM)') + 20 : saSoup.find('Return on Common Equity (TTM)') + 115]
    roeVal = rawROE[rawROE.find('value') + 7 : rawROE.find(',"nm_flag')]
    roeGrade = rawROE[rawROE.find('grade') + 8 : rawROE.find('","field_order')]
    profitabilityStats.append(['Return on Equity (TTM)', roeGrade, roeVal + '%'])

    '''
    print('\nProfitability:')
    print('Average:', getGrade(profitabilityStats))
    print('Gross Profit Margin Grade (TTM):', grossMarginGrade, '(' + grossMarginVal + '%)')
    print('Net Income Margin Grade (TTM):', netIncomeMarginGrade, '(' + netIncomeMarginVal + '%)')
    print('Cash From Operations Grade (TTM):', cashFromOpGrade, '(' + cashFromOpVal + ')')
    print('Levered FCF Margin Grade (TTM):', fcfMarginGrade, '(' + fcfMarginVal + '%)')
    print('Return on Equity:', roeGrade, '(' + roeVal + '%)')
    '''

    ####Growth

    rG = saSoup[saSoup.find('Revenue Growth (YoY)') + 20 : saSoup.find('Revenue Growth (YoY)') + 115]
    revGrowthVal = rG[rG.find('value') + 7 : rG.find(',"nm_flag')]
    revGrowthGrade = rG[rG.find('grade') + 8 : rG.find('","field_order')]
    growthStats.append(['Revenue Growth (YoY)', revGrowthGrade, revGrowthVal + '%'])

    rG2 = saSoup[saSoup.find('Revenue Growth (FWD)') + 20 : saSoup.find('Revenue Growth (FWD)') + 115]
    revGrowthFWDVal = rG2[rG2.find('value') + 7 : rG2.find(',"nm_flag')]
    revGrowthFWDGrade = rG2[rG2.find('grade') + 8 : rG2.find('","field_order')]
    growthStats.append(['Revenue Growth (FWD)', revGrowthFWDGrade, revGrowthFWDVal + '%'])
    
    epsG = saSoup[saSoup.find('EPS Diluted Growth (YoY)') + 20 : saSoup.find('EPS Diluted Growth (YoY)') + 115]
    epsGrowthVal = epsG[epsG.find('value') + 7 : epsG.find(',"nm_flag')]
    epsGrowthGrade = epsG[epsG.find('grade') + 8 : epsG.find('","field_order')]
    growthStats.append(['EPS Growth (YoY)', epsGrowthGrade, epsGrowthVal + '%'])

    epsG2 = saSoup[saSoup.find('EPS Diluted Growth (FWD)') + 20 : saSoup.find('EPS Diluted Growth (FWD)') + 115]
    epsFWDGrowthVal = epsG2[epsG2.find('value') + 7 : epsG2.find(',"nm_flag')]
    epsFWDGrowthGrade = epsG2[epsG2.find('grade') + 8 : epsG2.find('","field_order')]
    growthStats.append(['EPS Growth (FWD)', epsFWDGrowthGrade, epsFWDGrowthVal + '%'])

    roeG = saSoup[saSoup.find('ROE Growth (YoY)') + 20 : saSoup.find('ROE Growth (YoY)') + 115]
    roeGrowthVal = roeG[roeG.find('value') + 7 : roeG.find(',"nm_flag')]
    roeGrowthGrade = roeG[roeG.find('grade') + 8 : roeG.find('","field_order')]
    growthStats.append(['ROE Growth (YoY)', roeGrowthGrade, roeGrowthVal + '%'])
    
    roeG2 = saSoup[saSoup.find('ROE Growth (FWD)') : saSoup.find('ROE Growth (FWD)') + 115]
    roeFWDGrowthVal = roeG2[roeG2.find('value') + 7 : roeG2.find(',"nm_flag')]
    roeGrowthFWDGrade = roeG2[roeG2.find('grade') + 8 : roeG2.find('","field_order')]
    growthStats.append(['ROE Growth (FWD)', roeGrowthFWDGrade, roeFWDGrowthVal + '%'])

    epsLTGrowth = saSoup[saSoup.find('EPS FWD Long Term Growth (3-5Y CAGR)') + 20 : saSoup.find('EPS FWD Long Term Growth (3-5Y CAGR)') + 115]
    epsLTGrowthVal = epsLTGrowth[epsLTGrowth.find('value') + 7 : epsLTGrowth.find(',"nm_flag')]
    epsLTGrowthGrade = epsLTGrowth[epsLTGrowth.find('grade') + 8 : epsLTGrowth.find('","field_order')]
    growthStats.append(['EPS FWD Long Term Growth (3-5Y CAGR)', epsLTGrowthGrade, epsLTGrowthVal + '%'])

    capexGrowth = saSoup[saSoup.find('CAPEX Growth (YoY)') + 20 : saSoup.find('CAPEX Growth (YoY)') + 105]
    capexGrowthVal = capexGrowth[capexGrowth.find('value') + 7 : capexGrowth.find(',"nm_flag')]
    capexGrowthGrade = capexGrowth[capexGrowth.find('grade') + 8 : capexGrowth.find('","field_order')]
    growthStats.append(['CAPEX Growth (YoY)', capexGrowthGrade, capexGrowthVal + '%'])

    workCGrowth = saSoup[saSoup.find('Working Capital Growth (YoY)') + 20 : saSoup.find('CAPEX Growth (YoY)') + 105]
    workCGrowthVal = workCGrowth[workCGrowth.find('value') + 7 : workCGrowth.find(',"nm_flag')]
    workCGrowthGrade = workCGrowth[workCGrowth.find('grade') + 8 : workCGrowth.find('","field_order')]
    growthStats.append(['Working Capital Growth (YoY)', workCGrowthGrade, workCGrowthVal + '%'])

    '''
    print('\nGrowth:')
    print('Average:', getGrade(growthStats))
    print('Revenue Growth Grade (YOY):', revGrowthGrade, '(' + revGrowthVal + '%)')
    print('Revenue Growth Grade (FWD):', revGrowthFWDGrade, '(' + revGrowthFWDVal + '%)')
    print('EPS Growth Grade (YOY):', convertGrade(epsGrowthGrade), '(' + epsGrowthVal + '%)')
    print('EPS Growth Grade (FWD):', convertGrade(epsFWDGrowthGrade), '(' + epsFWDGrowthVal + '%)')
    print('EPS FWD Long Term Growth Grade:', epsLTGrowthGrade, '(' + epsLTGrowthVal + '%)')
    print('ROE Growth Grade (YOY):', convertGrade(roeGrowthGrade), '(' + roeGrowthVal + '%)')
    print('ROE Growth Grade (FWD):', convertGrade(roeGrowthFWDGrade), '(' + roeFWDGrowthVal + '%)')
    print('CAPEX Growth Grade:', capexGrowthGrade, '(' + capexGrowthVal + '%)')
    print('Working Capital Growth Grade (YOY):', workCGrowthGrade, '(' + workCGrowthVal + '%)')
    '''
   
    ####Performance

    threeMonthPerf = saSoup[saSoup.find('3M Price Performance') + 20 : saSoup.find('3M Price Performance') + 115]
    threeMonthPerfVal = threeMonthPerf[threeMonthPerf.find('value') + 7 : threeMonthPerf.find(',"nm_flag')]
    threeMonthPerfGrade = threeMonthPerf[threeMonthPerf.find('grade') + 8 : threeMonthPerf.find('","field_order')]
    perfStats.append(['3M Price Performance', threeMonthPerfGrade, threeMonthPerfVal + '%'])

    sixMonthPerf = saSoup[saSoup.find('6M Price Performance') + 20 : saSoup.find('6M Price Performance') + 115]
    sixMonthPerfVal = sixMonthPerf[sixMonthPerf.find('value') + 7 : sixMonthPerf.find(',"nm_flag')]
    sixMonthPerfGrade = sixMonthPerf[sixMonthPerf.find('grade') + 8 : sixMonthPerf.find('","field_order')]
    perfStats.append(['6M Price Performance', sixMonthPerfGrade, sixMonthPerfVal + '%'])

    nineMonthPerf = saSoup[saSoup.find('9M Price Performance') + 20 : saSoup.find('9M Price Performance') + 115]
    nineMonthPerfVal = nineMonthPerf[nineMonthPerf.find('value') + 7 : nineMonthPerf.find(',"nm_flag')]
    nineMonthPerfGrade = nineMonthPerf[nineMonthPerf.find('grade') + 8 : nineMonthPerf.find('","field_order')]
    perfStats.append(['9M Price Performance', nineMonthPerfGrade, nineMonthPerfVal + '%'])

    oneYearPerf = saSoup[saSoup.find('1Y Price Performance') + 20 : saSoup.find('1Y Price Performance') + 115]
    oneYearPerfVal = oneYearPerf[oneYearPerf.find('value') + 7 : oneYearPerf.find(',"nm_flag')]
    oneYearPerfGrade = oneYearPerf[oneYearPerf.find('grade') + 8 : oneYearPerf.find('","field_order')]
    perfStats.append(['1Y Price Performance', oneYearPerfGrade, oneYearPerfVal + '%'])

    '''
    print('\nPerformance:')
    print('Average:', getGrade(perfStats))
    print('3M Price Performance:', threeMonthPerfGrade, '(' + threeMonthPerfVal + '%)')
    print('6M Price Performance:', sixMonthPerfGrade, '(' + sixMonthPerfVal + '%)')
    print('9M Price Performance:', nineMonthPerfGrade, '(' + nineMonthPerfVal + '%)')
    print('1Y Price Performance:', oneYearPerfGrade, '(' + oneYearPerfVal + '%)')
    '''
    
    stockGrades.append([sym, ((getGrade(valuationStats) * 1.25 + (getGrade(profitabilityStats) * 1.10) + (getGrade(growthStats) * 1.10) + (getGrade(perfStats) * 1.10)) / 4) * 25, marketCap, companyDescription, valuationStats, profitabilityStats, growthStats, perfStats])

    print('Overall Rating:', ((getGrade(valuationStats) * 1.25 + (getGrade(profitabilityStats) * 1.10) + (getGrade(growthStats) * 1.10) + (getGrade(perfStats) * 1.10)) / 4) * 25)


getSymbols('https://finviz.com/screener.ashx?v=111&o=-marketcap')

for x in range(len(symbols)):
    getInfo(symbols[x])

print()

stockGrades = bubbleSort(stockGrades)

for x in range(0, 5):
    
    for y in range(len(stockGrades[x])):
            
        if y >= 4:
            for z in range(len(stockGrades[x][y])):
                print(stockGrades[x][y][z])
        else:
            print(stockGrades[x][y])

        print()
