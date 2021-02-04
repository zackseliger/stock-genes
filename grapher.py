import backtrader as bt
import backtrader
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
from strategies import *

cerebro = bt.Cerebro()
cerebro.broker = bt.brokers.BackBroker(slip_perc=0.005)
cerebro.broker.setcommission(commission=0.001)
cerebro.addstrategy(GenerateStrategy, genes=[0.7041730927868781, 0.8299276103260672, 0.020527094596077156, 0.22375052152620833, 0.7779601792724551, 0.9982795941313997, 0.5849749628638878, 0.01849657638580948, 0.35981670267593235, 0.01260483979143101, 0.43282860084085184, 0.48310986923801946, 0.5995017185208052, 0.3650672048974737, 0.06548061979640873, 0.8734692971961974])

cerebro.adddata(btfeeds.GenericCSVData(
	dataname='stocks/growth2019/FSLY.csv',
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