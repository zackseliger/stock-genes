import backtrader as bt
import backtrader
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
from strategies import *

cerebro = bt.Cerebro()
cerebro.broker = bt.brokers.BackBroker(slip_perc=0.005)
cerebro.broker.setcommission(commission=0.0005)
cerebro.addstrategy(GenerateStrategy, genes=[0.05228696310423586, 0.541827538356338, 0.6828415671892255, 0.09716989513451102, 0.6623085722836487, 0.6985341187279919, 0.2008480470739944, 0.12394928861514165, 0.6462453607118114, 0.9395497239201074, 0.011643557656475845, 0.7643126674702218, 0.9685914559128024, 0.5954753614095193, 0.9078483310869062, 0.6340259111038894, 0.05531651191655085])

cerebro.adddata(btfeeds.GenericCSVData(
	dataname='stocks/2000/T.csv',
	dtformat=('%Y-%m-%d'),

	datetime=0,
	open=1,
	high=2,
	low=3,
	close=4,
	volume=6
))

cerebro.run()
cerebro.plot()