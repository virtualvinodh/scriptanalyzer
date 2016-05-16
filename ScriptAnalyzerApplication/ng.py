#from nltk.corpus import reuters  
#from nltk.corpus import genesis  
#from nltk.probability import LaplaceProbDist  
#from nltk.model import NgramModel
#import nltk
#
#tokens = ["N","S","N","S","N","E"]
#
#estimator = lambda fdist, bins: LaplaceProbDist(fdist, 300)
#
#model = NgramModel(5,tokens,estimator=estimator)  
#
#print model.perplexity(tokens)
##print model.entropy(tokens)
#
#tokens = ["N","N","N","N","N","N"]
#
#model = NgramModel(2,tokens,estimator=estimator)  
#
#print model.perplexity(tokens)
##print model.entropy(tokens)


#sample = ['a','b','c','d','e']
##sample = ['a','a','b','a','a']
#
#import nltk
import math

prob = [(sample.count(e)/float(len(sample))) for e in list(set(sample))]

entropy = -sum([p*math.log(p) for p in prob])

print entropy

from utilities import util

k =['a','b','c','d','e','g','f']
r = [0]+[1,4,6]+[len(k)]

k1 = []
for j in range(len(r)-1):
    k1.append(k[r[j]:r[j+1]])

print k1
    
    
    