import backtrader as bt
import backtrader.feeds as btfeeds
from strategies import *
from os import listdir
from random import random, shuffle

strategies = []
for i in range(5000):
	strategies.append(GenerateStrategy)

# describe the runs we're gonna make to evaluate each stock
stockRuns = [
	['2000', 0.5],
	['2000', 0.5],
	['2000', 0.5],
	['2008', 0.5],
	['2008', 0.5],
	['2008', 0.5],
	['2016', 0.1],
	['2016', 0.1],
	['2016', 0.1],
	['2016', 0.1],
	['2016', 0.1],
	['2016', 0.1],
	['2016', 0.1],
	['2016', 0.1],
	['2016', 0.1],
	['2016', 0.1],
	['2011etf', 1],
	['2011etf', 1],
	['2011etf', 1],
	['2020', 0.5],
	['2020', 0.5],
	['crypto', 0.7],
	['growth2018', 0.6],
	['growth2018', 0.6],
	['growth2018', 0.6],
	['growth2018', 0.6],
	['growth2019', 0.5],
	['growth2019', 0.5],
	['NQ100_1', 0.5],
	['NQ100_2', 0.5]
]

# run strategy for each stock
print("strike rate * risk to reward ratio")
for strategy in strategies:
	print("evaluating {}...".format(strategy.__name__))
	wrs = []
	rrrs = []
	trades = []
	pnls = []
	expected_returns = []

	# for if our name is verrry special
	genes = []
	if strategy.__name__ == GenerateStrategy.__name__:
		for i in range(16):
			genes.append(random())
		print(genes)

	for run_desc in stockRuns:
		# pick stocks
		dir = 'stocks/'+run_desc[0]
		stocks = []
		files = listdir(dir)
		shuffle(files)
		for filename in files:
				if random() < run_desc[1]:
						stocks.append(filename)

		# setup cerebro and add data
		cerebro = bt.Cerebro()
		cerebro.broker = bt.brokers.BackBroker(slip_perc=0.005)
		cerebro.broker.setcommission(commission=0.001)
		cerebro.addstrategy(strategy, genes=genes)
		cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
		# data
		for filename in stocks:
			cerebro.adddata(btfeeds.GenericCSVData(
					dataname=dir+'/'+filename, dtformat=('%Y-%m-%d'),
					datetime=0, open=1, high=2, low=3, close=4, volume=6
			))

		# run and get stats
		results = cerebro.run()[0]
		ta = results.analyzers.ta.get_analysis()
		if "won" in ta:
			wr = (ta.won.total/ta.total.closed)
			rrr = abs(ta.won.pnl.average / (ta.lost.pnl.average if ta.lost.pnl.average != 0 else 1))
			num_trades = ta.total.total
			pnl = round(ta.pnl.net.total,2)
			wrs.append(wr)
			rrrs.append(rrr)
			trades.append(num_trades)
			pnls.append(pnl)
			expected_returns.append(wr*rrr*num_trades+pnl)
		else:
			print("Error: Unable to analyze trades")
			break

	# print averages
	if len(expected_returns) == len(stockRuns):
		avg_wr = round(sum(wrs) / len(wrs), 2)
		avg_rrr = round(sum(rrrs) / len(rrrs), 2)
		avg_num_trades = round(sum(trades) / len(trades), 2)
		avg_pnl = round(sum(pnls) / len(pnls))
		avg_e = round(sum(expected_returns) / len(expected_returns), 2)
		print("{} * {} * {} + {} =  {}".format(avg_wr, avg_rrr, avg_num_trades, avg_pnl, avg_e))
		f = open('log.txt', 'a')
		f.write("{}".format(genes))
		f.write("\n")
		f.write("{} * {} * {} + {} = {}\n\n".format(avg_wr, avg_rrr, avg_num_trades, avg_pnl, avg_e))
		f.close()