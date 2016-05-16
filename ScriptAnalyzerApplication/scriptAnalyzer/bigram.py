import nltk
from nltk.probability import LaplaceProbDist  
from nltk.model import NgramModel
import codecs


tamil1f = codecs.open("C:\Users\Administrator\Desktop\Script_Data\Tamil_1.csv")
tamil2f = codecs.open("C:\Users\Administrator\Desktop\Script_Data\Tamil_2.csv")

tamil1_alpha = [] 
tamil1_alpha_all = []

tamil2_alpha = [] 
tamil2_alpha_all = []


for line in tamil1f.readlines()[1:]:
    tamil1_alpha.append(["St"]+line.split(",")[-1].replace("\n","").replace("[","").replace("]","").replace("\r","").split("|")+["En"])
    tamil1_alpha_all += ["St"]+line.split(",")[-1].replace("\n","").replace("[","").replace("]","").replace("\r","").split("|")+["En"]

for line in tamil2f.readlines()[1:]:
    tamil2_alpha.append(["St"]+line.split(",")[-1].replace("\n","").replace("[","").replace("]","").replace("\r","").split("|")+["En"])
    tamil2_alpha_all += ["St"]+line.split(",")[-1].replace("\n","").replace("[","").replace("]","").replace("\r","").split("|")+["En"]

        
s_bg1 = nltk.bigrams(tamil1_alpha_all)
s_bg2 = nltk.bigrams(tamil2_alpha_all)

fdist1 = nltk.FreqDist(s_bg1)
fdist2 = nltk.FreqDist(s_bg2)

estimator1 = lambda fdist, bins: LaplaceProbDist(fdist, len(tamil1_alpha_all)+1)
estimator2 = lambda fdist, bins: LaplaceProbDist(fdist, len(tamil2_alpha_all)+1)

model1 = NgramModel(3,tamil1_alpha_all,estimator=estimator1)  
model2 = NgramModel(3,tamil2_alpha_all,estimator=estimator2)

print model1.entropy(tamil1_alpha[0])
print model1.perplexity(tamil1_alpha[0])


    