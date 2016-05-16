k = [1,5,7,9,10,11,13,18,19]

kN= []

i = 0

while i < len(k)-1:
    if abs(k[i]-k[i+1]) > 1:
        kN.append(k[i])
    else:
        kN.append((k[i]+k[i+1])/float(2))
        i = i + 1
        
    i=i+1
    
if k[-2] == kN[-1]:
    kN.append(k[-1])
    
print k
print kN