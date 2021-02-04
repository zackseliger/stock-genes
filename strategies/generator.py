import backtrader as bt
import backtrader.indicators as btind
from Indicators import *
from random import random

price_indicators = [
	btind.MovingAverageSimple,
	btind.ExponentialMovingAverage,
	btind.MovAv.Smoothed,
	MinMax,
	VolumeWeightedAveragePrice,
	btind.AverageTrueRange
]

comparable_indicators = [
	btind.AroonUp,
	btind.AroonDown,
	btind.PlusDirectionalIndicator,
	btind.MinusDirectionalIndicator,
	AbsStrengthBulls,
	AbsStrengthBears,
	btind.RelativeStrengthIndex
]

sort_indicators = [
	btind.RelativeStrengthIndex,
	SentimentZoneOscillator,
	VolatilitySwitch,
	MoneyFlowIndex,
	SchaffTrend,
	btind.AverageDirectionalMovementIndex,
	Effort,
	Juice,
	VolumeOsc
]

class GenerateStrategy(bt.Strategy):
	params = (
		('genes', []),
	)

	def __init__(self):
		self.genes = self.p.genes

		# generate genes if they weren't provided
		while len(self.genes) < 16:
			self.genes.append(random())

		for d in self.datas:
			d.atr = btind.AverageTrueRange(d, period=14)
			d.sellNum1 = self.generateNumber(d, self.genes[0])
			d.sellNum2 = self.generateNumber(d, self.genes[1])
			d.sellNum3 = self.generateNumber(d, self.genes[2])
			d.sellNum4 = self.generateNumber(d, self.genes[3])
			d.sellOp1 = self.getOp(self.genes[4])
			d.sellOp2 = self.getOp(self.genes[5])
			# d.sellCombo = self.getCombo(self.genes[5])
			d.buyNum1 = self.generateNumber(d, self.genes[6])
			d.buyNum2 = self.generateNumber(d, self.genes[7])
			d.buyNum3 = self.generateNumber(d, self.genes[8])
			d.buyNum4 = self.generateNumber(d, self.genes[9])
			# d.buyCombo = self.getCombo(self.genes[10])
			d.buyOp1 = self.getOp(self.genes[10])
			d.buyOp2 = self.getOp(self.genes[11])
			d.sortFactor = (self.getIndexOf(sort_indicators,self.genes[12],0.0,1.0))(d)

		self.printableInfo = "{}".format(self.genes)

	def next(self):
		orderedstocks = sorted(self.datas, key=lambda stock: stock.sortFactor, reverse=self.genes[13]<0.5)

		# close positions
		for d in self.datas:
			if self.getposition(d).size != 0:
				cond1 = self.getCond(d.sellOp1(d.sellNum1, d.sellNum2), d.sellOp2(d.sellNum3, d.sellNum4), self.genes[14])
				if cond1:
					self.close(d, size=self.getposition(d).size)

		# open positions
		for d in orderedstocks:
			if self.getposition(d).size != 0:
				continue

			# useful numbers
			risk = 0.02*self.broker.get_value()
			stoploss_diff = d.atr[0]*3
			buysize = int(risk / stoploss_diff)

			# we can't spend more than all our money
			if self.broker.get_cash() < buysize*d:
				continue

			# long signals
			cond1 = self.getCond(d.buyOp1(d.buyNum1, d.buyNum2), d.buyOp2(d.buyNum3, d.buyNum4), self.genes[15])
			if cond1:
				self.buy(d, size=buysize)

	def normalize(self, num, low, high):
		return (num-low)/(high-low)

	def getIndexOf(self, arr, num, low, high):
		return arr[int(self.normalize(num,low,high) * len(arr))]

	def generateNumber(self, stock, gene):
		if gene >= 0.75: # ohlcv
			return self.getIndexOf([stock.open,stock.close,stock.high,stock.low,stock.volume], gene,0.75,1.0)
		if gene >= 0.5: # 0-100
			return int(self.normalize(gene,0.5,0.75)*101)
		if gene >= 0.25: # price indicators
			return (self.getIndexOf(price_indicators,gene,0.25,0.5))(stock)
		# comparable indicators
		return (self.getIndexOf(comparable_indicators,gene,0.0,0.25))(stock)

	def getCond(self, num1, num2, gene):
		if gene < 0.2:
			return num1 < num2
		if gene < 0.4:
			return num1 <= num2
		if gene < 0.6:
			return num1 == num2
		if gene < 0.8:
			return num1 >= num2
		return num1 > num2

	def getCombo(self, gene):
		if gene < 0.5:
			return lambda x,y: x and y
		return lambda x,y: x or y

	def getOp(self, gene):
		if gene < 0.33:
			return lambda x,y: x*y
		if gene < 0.66:
			return lambda x,y: x+y
		return lambda x,y: x-y