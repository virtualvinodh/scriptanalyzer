import networkx as nx
from utilities import util
import copy

def all_euler_paths_new(G,source):
    g=copy.deepcopy(G)
    v=source
    
    ePath=[]
    eGraph = nx.MultiGraph()
    while g.size() > 0:
        #print "v:", v
        if v == source and eGraph.edges() == G.edges():
            break
        n = v 
        #print "n:", v
        # sort nbrs here to provide stable ordering of alternate cycles
        nbrs = sorted([v for u,v in g.edges(n)])
        #print "nbrs:", nbrs
        for v in nbrs:
            #print "Removing Edge:", (n,v)
            g.remove_edge(n,v)
            bridge = not nx.is_connected(g.to_undirected())
            if bridge:
                #print "Is Bridge I:"
                #print "Adding Edge:", (n,v)
                g.add_edge(n,v)  # add this edge back and try another
            else:
                #print "Is not Bridge"
                break  # this edge is good, break the for loop 
        if bridge:
            #print "Is Bridge II"
            #print "Removing Edge:", (n,v)
            g.remove_edge(n,v)          
            #print "Removing Node", n
            g.remove_node(n)    
        
        #print "Appending to Path:", n
        ePath.append(n)
        eGraph.add_edge(n,v)
    
    ePath.append(source)
    
    allPaths =[]
    allPaths.append(ePath)
    
    swap =0
    
    #print "Original Path:", ePath
    for num1, n1 in enumerate(ePath):
        for num2, n2 in enumerate(ePath):
            if n1 == n2 and num1 != num2 and num2!=len(ePath)-1 and num1 < num2:
                revPath =  ePath[num1+1:num2]
                if len(revPath) > 1:
                    swap = swap +1

    for pt in list(ShiftPaths(ePath)):
        allPaths.append(pt)
        for pth in list(ShiftPaths(pt)):
            allPaths.append(pth)
            for pthh in list(ShiftPaths(pth)):
                allPaths.append(pthh)
                for pthhh in list(ShiftPaths(pthh)):
                    allPaths.append(pthhh)   
    
                         
    return util.UniqueLists(allPaths)

def ShiftPaths(p):
    shifted = False
    for num1, n1 in enumerate(p):
        for num2, n2 in enumerate(p):
            if n1 == n2 and num1 != num2 and num2!=len(p)-1 and num1 < num2:
                #print n1,n2, num1,num2
                revPath =  p[num1+1:num2]
                if len(revPath) > 1:
                    revPath.reverse()
                    newPath = p[:num1+1] + revPath + p[num2:]
                    shifted = True
                    yield newPath
    if  not shifted:
        yield p