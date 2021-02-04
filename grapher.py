import backtrader as bt
import backtrader
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
from strategies import *

cerebro = bt.Cerebro()
cerebro.broker = bt.brokers.BackBroker(slip_perc=0.005)
cerebro.broker.setcommission(commission=0.001)
cerebro.addstrategy(GenerateStrategy, genes=[0.5457295278636372, 0.8801599941537148, 0.9088442015166772, 0.10208213542285316, 0.4137291774413333, 0.34376237332888215, 0.2046664281744598, 0.5399403231589993, 0.0018024432574534899, 0.32560781133248473, 0.33536855779212715, 0.7055387845837777, 0.19006660216025528, 0.8998654788667223, 0.6565077972773707, 0.8730635766441551, 0.02065244215424633, 0.5048941501784833, 0.8736717403247426, 0.01870815182783192, 0.13920373719605494, 0.9749403193305477])

cerebro.adddata(btfeeds.GenericCSVData(
	dataname='stocks/2016/MSFT.csv',
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