set1 = [(1,2),(2,3.1),(4,5),(5,6),(1,2)]
set2 = [(2.2,12.1),(12,3),(2,4),(6.2,5),(3,5.2)]
set3 = [(2,4.1),(12,3),(2,4),(6,5),(3,5),(1,3),(4,2)]

dist = lambda x,y: ((x[0]-y[0])**2 + (x[1]-y[1])**2)**0.5

setN = []

for i,s in enumerate(set1):
    st = []
    for j,t in enumerate(set2):
        st.append(dist(s,t))
    
    setN.append(st)
    
k = [1,3,2,4,5,6,1,2,3,5]

for i,m in enumerate(k):
    count = 0
    for j,n in enumerate(k):
        if m==n:
            count += 1
            if count > 1:
                k.remove(n)
                print k
        
print        
print sorted(k)
print sorted(list(set(k)))