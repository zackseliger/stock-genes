import backtrader as bt
import backtrader.feeds as btfeeds
from strategies import *
from os import listdir
from random import random, shuffle

strategies = [GenerateStrategy, BuyAllThenSell]

# pre-pick stocks
dir = 'stocks/2016'
stocks = []
files = listdir(dir)
shuffle(files)
for filename in files:
    if random() < 0.03:
        stocks.append(filename)

print("sharpe ratio, avg_annual_returns / maxdrawdown")
i = 0
for strat in strategies:
    cerebro = bt.Cerebro()
    cerebro.broker = bt.brokers.BackBroker(slip_perc=0.005)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(strat, genes=[0.5457295278636372, 0.8801599941537148, 0.9088442015166772, 0.10208213542285316, 0.4137291774413333, 0.46704072047990386, 0.2046664281744598, 0.5399403231589993, 0.0018024432574534899, 0.32560781133248473, 0.35961484431495616, 0.7055387845837777, 0.008689012261361984, 0.8998654788667223, 0.6565077972773707, 0.8730635766441551, 0.02065244215424633, 0.5048941501784833, 0.8736717403247426, 0.01870815182783192, 0.13920373719605494, 0.839140510619019])

    cerebro.addanalyzer(bt.analyzers.AnnualReturn)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, annualize=True, riskfreerate=0.01)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)

    # add data
    for filename in stocks:
        cerebro.adddata(btfeeds.GenericCSVData(
            dataname=dir+'/'+filename,
            dtformat=('%Y-%m-%d'),

            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=6
        ))

    # run stretegy and get stats
    results = cerebro.run()[0]
    sharpe_ratio = results.analyzers[2].get_analysis()['sharperatio']
    if sharpe_ratio is None: sharpe_ratio = 0
    returns = results.analyzers[0].rets
    avg_returns = sum(returns)/len(returns)
    maxdrawdown = results.analyzers[1].get_analysis()['max'].drawdown/100
    if maxdrawdown == 0: maxdrawdown = 0.0001
    print(
        str(round(sharpe_ratio,2)) + ", " +
        str(round(avg_returns,2)) + " / " +
        str(round(maxdrawdown,2)) + " = " +
        str(round(avg_returns/maxdrawdown,2))
    )

    ta = results.analyzers[3].get_analysis()
    if "won" in ta:
        h1 = ['Total Trades', 'Total Won', 'Total Lost', 'Strike Rate', 'RRR', 'Average P/L', 'Overall P/L']
        r1 = [ta.total.total, ta.won.total, ta.lost.total, round((ta.won.total/ta.total.closed)*100,2), round(abs(ta.won.pnl.average/ta.lost.pnl.average), 2), round(ta.pnl.net.average, 2), round(ta.pnl.net.total,2)]
        print(("{:<15}"*(len(h1)+1)).format('',*h1))
        print(("{:<15}"*(len(h1)+1)).format('',*r1))
    else:
        print(("{:<15}"*2).format('',"Trade Analysis Unavailable"))

    # write equity curve to csv
    # numDays = len(results.observers[0].value)
    # arr = results.observers[0].value.get(0,numDays)
    # f = open("thing"+str(i)+".csv", 'w')
    # for price in arr:
    #     f.write("{}\n".format(price))
    # f.close()
    # i += 1