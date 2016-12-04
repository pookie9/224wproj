import numpy as np

teams = {'Royal Challengers Bangalore': 1,
			'Mumbai Indians': 2,
			'Kolkata Knight Riders': 3,
			'Chennai Super Kings': 4,
			'Delhi Daredevils': 5,
			'Kings XI Punjab': 6,
			'Rajasthan Royals': 7,
			'Sunrisers Hyderabad': 8,
			'Pune Warriors': 9,
			'Gujarat Lions': 10,
			'Rising Pune Supergiants': 0,
			'Deccan Chargers': 11,
			'Kochi Tuskers Kerala': 12
			}


def data():
	global teams

	A = np.zeros(shape=(11,11,4), dtype=int)
	curr = 0
	lines = [line.strip() for line in open('ipl.csv')]
	for line in lines:
		# print line
		if line is '':
			continue
		if 'IPL' in line:
			Id = line.find('IPL')
			print line[:Id-1]
			curr = teams[line[:Id-1]]
		else:
			if 'Opponent' not in line:
				elements = line.split(',')
				opp = teams[elements[0][2:]]
				if opp in (11,12):
					continue
				# print opp
				data = [int(a) for a in (elements[1], elements[2], elements[3], elements[6])]
				A[curr][opp] = data


	return A


if __name__ == '__main__':
	print data()






