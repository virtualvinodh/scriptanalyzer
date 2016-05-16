from nltk.util import ngrams
from nltk.corpus import reuters  
from nltk.corpus import genesis  
from nltk.probability import LaplaceProbDist  
from nltk.model import NgramModel
import nltk

sentence = 'She covered a Bob Dylan song for Amnesty International.'

## http://www.inf.ed.ac.uk/teaching/courses/icl/nltk/probability.pdf
## http://www.nltk.org/book/ch02.html

n = 2
bigrams = ngrams(sentence.split(), n)

print bigrams

## Append starting points and ending points

#for grams in sixgrams:
#    print grams
    
estimator = lambda fdist, bins: LaplaceProbDist(fdist, len(sentence.split())+1)

model = NgramModel(2,sentence.split(),estimator=estimator)  

print model.generate(1, ("her","take"))
print 
print model.entropy(["she","covered"])