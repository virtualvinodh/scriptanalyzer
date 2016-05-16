## http://jeremykun.com/2012/07/25/dynamic-time-warping/
## http://www.mblondel.org/journal/2009/08/31/dynamic-time-warping-theory/
 
def dynamicTimeWarp(seqA, seqB, d = lambda x,y: ((x[0]-y[0])**2 + (x[1]-y[1])**2)**0.5 ):
    # create the cost matrix
    numRows, numCols = len(seqA), len(seqB)
    cost = [[0 for _ in range(numCols)] for _ in range(numRows)]
 
    # initialize the first row and column
    cost[0][0] = d(seqA[0], seqB[0])
    
    for i in xrange(1, numRows):
        cost[i][0] = cost[i-1][0] + d(seqA[i], seqB[0])

    for j in xrange(1, numCols):
        cost[0][j] = cost[0][j-1] + d(seqA[0], seqB[j])
            
    # fill in the rest of the matrix
    for i in xrange(1, numRows):
        for j in xrange(1, numCols):
            choices = cost[i-1][j], cost[i][j-1], cost[i-1][j-1]
            cost[i][j] = min(choices) + d(seqA[i], seqB[j])

    return cost[-1][-1]

#test1 = [(1,1),(2,3),(4,5),(10,12),(10,12)]*100
#test2 = [(3,1),(2,3),(4,5)]
#
#print  mlpy.dtw_std(test1,test2)
#import cProfile
#print dynamicTimeWarp(test1,test1)
#cProfile.run('dynamicTimeWarp(test1,test1)')




