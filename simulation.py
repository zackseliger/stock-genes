import backtrader as bt
import backtrader.feeds as btfeeds
from strategies import *
from os import listdir
from random import random, shuffle

num_population = 50
num_genes = 22
population = []
for i in range(num_population):
	population.append([[], 0])
	for j in range(num_genes):
		population[i][0].append(random())

def breed(parent1, parent2, mutation_rate=0.04):
	kiddo = []
	cuttoff = int(random()*(len(parent1)+1))
	for i in range(len(parent1)):
		if i < cuttoff:
			kiddo.append(parent1[i])
		else:
			kiddo.append(parent2[i])

		if random() < mutation_rate:
			kiddo[i] = random()

	return kiddo

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
	['growth2018', 0.6],
	['growth2019', 0.5],
	['growth2019', 0.5],
	['NQ100_1', 0.5],
	['NQ100_2', 0.5]
]

num_generations = 100
for gen_num in range(num_generations):
	# get fitness
	for person in population:
		expected_returns = []

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
			cerebro.addstrategy(GenerateStrategy, genes=person[0])
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
				expected_returns.append(pnl)
			else:
				print("Error: Unable to analyze trades")
				break

		# calculate fitness
		if len(expected_returns) == len(stockRuns):
			fitness = round(sum(expected_returns) / len(expected_returns), 2)
			person[1] = fitness
			print("fitness: {}".format(person[1]))

	# for all strategies w negative returns, make their fitness on a scale from [0,1] based on highest return
	largest = float('-inf')
	for person in population:
		if abs(person[1]) > largest:
			largest = abs(person[1])
	for person in population:
		if person[1] < 0:
			person[1] = abs(largest/person[1])

	# create weighted pool by fitness to choose new population
	pool = []
	total = 0
	for i in range(len(population)):
		total += max(population[i][1],0) * max(population[i][1],0)
	if total == 0: total = 1
	for i in range(len(population)):
		for j in range(round(max(population[i][1],0) * max(population[i][1],0) / total * 100)):
			pool.append(i)

	new_population = []
	# if we have no fit members, make new population
	if len(pool) == 0:
		for i in range(num_population):
			new_population.append([[], 0])
			for j in range(num_genes):
				new_population[i][0].append(random())
	else:
		for i in range(num_population):
			# pick random parents and make new kiddo
			parent1 = population[pool[int(random()*len(pool))]]
			parent2 = population[pool[int(random()*len(pool))]]

			new_population.append([breed(parent1[0], parent2[0]), 0])

	# log the fittest person and go to next generation
	fittest_person = population[0]
	for i in range(len(population)):
		if population[i][1] > fittest_person[1]:
			fittest_person = population[i]
	f = open('log.txt', 'a')
	f.write("{}\n{}\n\n".format(fittest_person[0], fittest_person[1]))
	f.close()
	print("most fit: {} ({}/{})".format(fittest_person[1], gen_num+1, num_generations))
	population = new_population
