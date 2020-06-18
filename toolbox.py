from itertools import count

def shift(l, max_n, up):
	l = list(set(l))
	l_ = sorted(l, reverse = not up)
	ite = count(0) if up else count(max_n - 1, -1)
	mapped = [(i if i == j else (i - 1 if up else i + 1)) for i, j in zip(l_, ite)]
	return {i: j for i, j in zip(l, (mapped if up else reversed(mapped)))}

if __name__ == '__main__':
	l = [0,1,3,4,5,9,10]
	print(shift(l, 11, True))
	print(shift(l, 11, False))