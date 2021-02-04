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

def getStockAttrAsIndicator(attr):
	return lambda stock: getattr(stock, attr)

def getNumberAsIndicator(num):
	return lambda stock: [num for k in range(100)]

class GenerateStrategy(bt.Strategy):
	params = (
		('genes', []),
	)

	def __init__(self):
		self.genes = self.p.genes
		self.currGene = 0

		# selling
		self.sellInd1 = self.generateNumber(self.getGene())
		self.sellInd2 = self.generateNumber(self.getGene())
		self.sellInd3 = self.generateNumber(self.getGene())
		self.sellInd4 = self.generateNumber(self.getGene())
		self.sellOp1 = self.getOp(self.getGene())
		self.sellOp2 = self.getOp(self.getGene())
		self.sellCond = self.getGene()

		# buying
		self.buyInd1 = self.generateNumber(self.getGene())
		self.buyInd2 = self.generateNumber(self.getGene())
		self.buyInd3 = self.generateNumber(self.getGene())
		self.buyInd4 = self.generateNumber(self.getGene())
		self.buyOp1 = self.getOp(self.getGene())
		self.buyOp2 = self.getOp(self.getGene())
		self.buyCond = self.getGene()

		# money management
		self.mm = self.generateNumber(self.getGene())
		self.stakeAmt = self.getGene()*10
		self.riskAmt = self.getGene()
		self.positionSizeOp = self.getOp(self.getGene())

		# prioritization
		self.sortInd1 = (self.getIndexOf(sort_indicators,self.getGene(),0.0,1.0))
		self.sortInd2 = self.generateNumber(self.getGene())
		self.sortOp = self.getOp(self.getGene())
		self.reverseSort = self.getGene() < 0.5

		for d in self.datas:
			d.sellInd1 = self.sellInd1(d)
			d.sellInd2 = self.sellInd2(d)
			d.sellInd3 = self.sellInd3(d)
			d.sellInd4 = self.sellInd4(d)
			d.buyInd1 = self.buyInd1(d)
			d.buyInd2 = self.buyInd2(d)
			d.buyInd3 = self.buyInd3(d)
			d.buyInd4 = self.buyInd4(d)
			d.mm = self.mm(d)
			d.sortInd1 = self.sortInd1(d)
			d.sortInd2 = self.sortInd2(d)

		self.printableInfo = "{}".format(self.genes)

	def next(self):
		orderedstocks = sorted(self.datas, key=lambda stock: self.sortOp(stock.sortInd1, stock.sortInd2[0]), reverse=self.reverseSort)

		# close positions
		for d in self.datas:
			if self.getposition(d).size != 0:
				cond1 = self.getCond(self.sellOp1(d.sellInd1[0], d.sellInd2[0]), self.sellOp2(d.sellInd3[0], d.sellInd4[0]), self.sellCond)
				if cond1:
					self.close(d, size=self.getposition(d).size)

		# open positions
		for d in orderedstocks:
			if self.getposition(d).size != 0:
				continue

			# useful numbers
			risk = self.riskAmt*self.broker.get_value()
			stoploss_diff = d.mm[0]*self.stakeAmt
			buysize = int(self.positionSizeOp(risk, stoploss_diff))

			# we can't spend more than all our money
			if self.broker.get_cash() < buysize*d:
				continue

			# long signals
			cond1 = self.getCond(self.buyOp1(d.buyInd1[0], d.buyInd2[0]), self.buyOp2(d.buyInd3[0], d.buyInd4[0]), self.buyCond)
			if cond1:
				self.buy(d, size=buysize)

	# returns next gene to be processed or makes new one and returns it
	def getGene(self):
		if len(self.genes) > self.currGene:
			self.currGene += 1
			return self.genes[self.currGene-1]
		self.genes.append(random())
		self.currGene += 1
		return self.genes[-1]

	def normalize(self, num, low, high):
		return (num-low)/(high-low)

	def getIndexOf(self, arr, num, low, high):
		return arr[int(self.normalize(num,low,high) * len(arr))]

	def generateNumber(self, gene):
		if gene >= 0.75: # ohlcv
			return self.getIndexOf([
					getStockAttrAsIndicator('open'),
					getStockAttrAsIndicator('close'),
					getStockAttrAsIndicator('high'),
					getStockAttrAsIndicator('low'),
					getStockAttrAsIndicator('volume')
				], gene,0.75,1.0)
		if gene >= 0.5: # 0-100
			return getNumberAsIndicator(int(self.normalize(gene,0.5,0.75)*101))
		if gene >= 0.25: # price indicators
			return (self.getIndexOf(price_indicators,gene,0.25,0.5))
		# comparable indicators
		return (self.getIndexOf(comparable_indicators,gene,0.0,0.25))

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
		if gene < 0.25:
			return lambda x,y: x*y
		if gene < 0.5:
			return lambda x,y: x / (y if y != 0 else 1)
		if gene < 0.75:
			return lambda x,y: x+y
		return lambda x,y: x-y