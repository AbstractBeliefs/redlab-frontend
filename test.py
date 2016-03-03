seq=[20,17,16,10,8,5,4,3,0]

def merge_sequence(seq,interval):
	# Function finds subsets of values sequence sequence,
	# which are distant no more than specified interval
	#parametres:
	#	seq Sequence of numbers
	#	interval Value of interval to be checked
	#return:
	#	list of merged intervals
	result=[]
	if len(seq):
		prev=seq[0]
		hi=0
		lo=0
		for p in seq:
			if p+interval<prev:
				prev=p
				print'res:', hi,lo,seq[hi],seq[lo-1]
				result.append([seq[hi],seq[lo-1]])
				hi=lo
			else:
				prev=p
			lo+=1
		print'res:', hi,lo,seq[hi],seq[lo-1]	
		result.append([seq[hi],seq[lo-1]])
	return result
print merge_sequence(seq,2)

print 'interval 5'
print merge_sequence(seq,5)
print merge_sequence([0],1)
print merge_sequence([],1)