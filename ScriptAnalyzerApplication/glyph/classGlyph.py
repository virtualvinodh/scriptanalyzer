import networkx as nx, itertools, eulerian, copy
import math, numpy
from utilities import util

class Glyph:
    # Constructor
    def __init__(self, char, edges, heuristic):
        self.char = char
        self.G = nx.MultiGraph()
        self.G.add_edges_from(edges)
        
        self.ScriptDir, self.retrace = heuristic  
                 
    # Generate Trajectory 
    def GetTrajectory(self):
        # Generate Paths to all Nodes
        StartEndNodes = self.G.nodes()
        
        # Only Odd Nodes can start and end a glyph.. add Option to override this
        OddNodes = [nd for nd in StartEndNodes if self.G.degree(nd) % 2 == 1]
        
        StartEndNodes = OddNodes  # self.HeuristicStartEnd(StartEndNodes)
        
        # Start-End same only if the Glyoh is closed - only Even nodes are present
        
        StartEnd = [x for x in itertools.combinations(StartEndNodes, 2)]  # Combination between the nodes
        
        # If there are no Odd Nodes, Possiably the trajectory is in-between even Nodes
        if len(OddNodes) == 0:
            StartEnd += [(x, x) for x in self.G.nodes()]
        
        # Heuristic selection of Nodes        
#        if HeuristicSE:
#            StartEnd = self.HeuristicStartEnd(StartEnd)
#            print StartEnd
    
        # Trajectory from Node 1 to Node 2
        for Start, End in StartEnd:
            # print 'Path from', Start, 'to', End
            Paths = self.GetTrajectoryPath(Start, End)
            # Generate the reverse paths too (Reversed Euler paths are also Eulerian)
            RevPaths = [list(reversed(P)) for P in Paths[:]]
            yield (Start, End), Paths + RevPaths
            
    # Heursitic selection of Starting and Ending Nodes        
    def HeuristicStartEnd(self, StartEnd):
        nds = self.G.nodes(data=True)
        
        x = [nd[1]['x'] for nd in nds]
        y = [nd[1]['y'] for nd in nds]
        
        # Nodes at Each Corner 
        
        LeftN = [nd[0] for nd in nds if nd[1]['x'] == min(x)]
        RightN = [nd[0] for nd in nds if nd[1]['x'] == max(x)]
        TopN = [nd[0] for nd in nds if nd[1]['y'] == max(y)]
        BottomN = [nd[0] for nd in nds if nd[1]['y'] == min(y)]
        
        TopLeftN = list(set(TopN).intersection(set(LeftN)))
        TopRightN = list(set(TopN).intersection(set(RightN)))
        BottomLeftN = list(set(BottomN).intersection(set(LeftN)))
        BottomRightN = list(set(BottomN).intersection(set(RightN)))
        
#        print nds
#        print LeftN, RightN, TopN, BottomN
#        print TopLeftN, TopRightN, BottomLeftN, BottomRightN
        
        HeurSE = []        
#        for SE in StartEnd:
#            if SE[0] in TopLeftN+BottomLeftN or SE[1] in TopRightN+BottomRightN:
#                HeurSE.append(SE)

        HeurSE = list(set(LeftN + RightN + TopN + BottomN))
        HeurSE = [x for x in itertools.combinations(HeurSE, 2)]

        return HeurSE
                
                
    # Return a Particular Path from a to b            
    def GetTrajectoryPath(self, Start, End):
        UniquePaths = []
        Paths = (list(self.GetEulerianPaths(Start, End)))  # List of all Eulerian Paths. A list of Lists
        # print Paths
        for Path in Paths:
            for P in Path:
                UniquePaths.append(P)  # Append Each <Path List> in the List of Lists to the master <list>    
        return util.UniqueLists(UniquePaths)  # Return the Unique Paths
    
    # Perform Basic PairMatching  - Input: [1,2,3,4]
    def PerformMatch(self, OddNodes):
        # Create Node Pairs from the Input NodeList
        NodeMatches = [x for x in itertools.combinations(OddNodes, 2)]  # [(1,2),(2,3),(3,4),(1.2)] etc
        # Create MatchPairs from the NodePairs
        PairMatches = [x for x in itertools.combinations(NodeMatches, len(OddNodes) / 2)]  # [((1,2),(2,3)),((3,4),(1,2)) etc]    
        MinMatch = []
        
        # List PairMatches only which have unique nodes
        # ((1,2),(3,4)) -> Unique ; ((2,3),(3,4)) not Unique 
        for pair in PairMatches:
            ListNode = []
            for u, v in pair:
                ListNode.append(u)
                ListNode.append(v)   
            if len(ListNode) == len(set(ListNode)):  # len(2,3,3,4) == len(unique(2,3,3,4) --> (2,3,4)) 
                MinMatch.append(pair)
        
        return MinMatch
    
    # Perform Minimum Perfect Matching
    def MinimizeMatch(self, Matches):
        WeightMatch = []
        # Add Weightage for each pair based on the distance : [((1,2),(3,4))] ; Weight = distance(1,2) + distance(3,4)
        for Match in Matches:
            PairWeight = 0
            for u, v in Match:
                PairWeight = PairWeight + nx.shortest_path_length(self.G, u, v)
            WeightMatch.append(PairWeight)     
        
        MinMatches = [Match for WM, Match in zip(WeightMatch, Matches) if WM == min(WeightMatch)]
        
        return MinMatches
    
    # Generate all Eulerian Paths between source and Target
    def GetEulerianPaths(self, Source, Target):
        EulG = copy.deepcopy(self.G)
        OddNodes = [nd for nd in self.G.nodes() if self.G.degree(nd) % 2 == 1]
        EvenNodes = [nd for nd in self.G.nodes() if self.G.degree(nd) % 2 == 0]
    
        PairNodes = OddNodes[:]  # Initially all Odd Nodes are assumed to be paired
        
        # if OddNodes remove, if EvenNode add to Pairnodes
        if Source != Target:
            if Source in OddNodes and Target in OddNodes:
                PairNodes.remove(Source)
                PairNodes.remove(Target)
            elif Source in EvenNodes and Target in OddNodes:    
                PairNodes.append(Source)
                PairNodes.remove(Target)
            elif Source in OddNodes and Target in EvenNodes:    
                PairNodes.remove(Source)
                PairNodes.append(Target)
            elif Source in EvenNodes and Target in EvenNodes:    
                PairNodes.append(Source)
                PairNodes.append(Target)
       
        PerfectMatch = self.PerformMatch(PairNodes)  # Perform Pair Matching
        MinPerfectMatch = self.MinimizeMatch(PerfectMatch)  # Perform Minimum Pair Matching
        
        # print "Minimum Perfect Matching:"
        # print MinPerfectMatch
            
        # Get a Euler Path for each Minimum Perfect Match
        for match in MinPerfectMatch:
            # print "For each match in MinPerfectMatch"
            # print match
            EulG = copy.deepcopy(self.G)
            # For each Pair
            for u, v in match:
                path = nx.shortest_path(self.G, u, v)  # get all paths
                for i in range(len(path) - 1):
                    EulG.add_edge(path[i], path[i + 1])
            EulG.add_edges_from([(Source, 'temp'), ('temp', Target)])  # Temp Node to get Eulerian Path  
            # print len(eulerian.all_euler_paths_new(EulG, 'temp'))
            EulerPaths = util.UniqueLists(eulerian.all_euler_paths_new(EulG, 'temp')) 
            # print EulerPaths
            EP = []
            # Remove the Temp node
            for P in EulerPaths:
                P.remove('temp')
                P.remove('temp')
                if P[0] != Source:
                    P.reverse()
                EP.append(P)
            yield EP 
            
        
    # Add Length as an attribute
    def GetShortestTrajectory(self, MinLength=True, MinCurve=True, Heuristic=True):
        # Generate all possible Trajectories
        
        print "Getting Shortest Paths"
        
        GPaths = list(self.GetTrajectory())
        self.AllPaths = []
        
        print "Here"
        
        for SrcTgt, path in GPaths:
            self.AllPaths.extend(path)

        print "Paths with All Traversals: ", len(self.AllPaths)
        
        if not self.retrace:            
            MinDist = sorted(set(map(len, self.AllPaths)))[:1]
        else:
            MinDist = sorted(set(map(len, self.AllPaths)))[:]  
            
        ShortPath = [path for path in self.AllPaths if len(path) in MinDist]
        
        ShortPathAll = ShortPath[:]
        
        print zip(map(self.CalcPathCurvatureCost, ShortPathAll), ShortPathAll)
        
        lenNorm = map(lambda x:-(x - 1), self.normalize(map(int, map(self.calcPathLength, ShortPathAll))))
        curvNorm = map(lambda x:-(x - 1), self.normalize(map(int, map(self.CalcPathCurvatureCost, ShortPathAll))))
        priorNorm = self.normalize(map(self.getPathPriority, ShortPathAll))
        dirNorm = map(lambda x:-(x - 1), self.normalize(map(self.CalcDirCost, ShortPathAll)))
        
        pathRnk = [(0.4 * lenN) + (0.4 * curvN) + (0.2 * priorN) for lenN, curvN, priorN, dirN in zip(lenNorm, curvNorm, priorNorm, dirNorm)]
        
        pathRanking = zip(pathRnk, ShortPathAll)
        
        pathRanking = sorted(pathRanking, reverse=True)
        
#        
#        minDir = sorted(Dir,reverse=True)[:1]
#        minDirInd = [x for x,y in enumerate(Dir) if y in minDir]
#        minDirPath = [ShortPath[x] for x in minDirInd]
#        
#        print ShortPath
        # ShortPath = minDirPath
            
        # Rank Paths 

        ShortPath = [path for rank, path in pathRanking[:5]]
        print pathRanking
        print ShortPath
        
        print "Total Short Paths - SE Priority:", len(ShortPath)
        print "Shortest Paths Complete"
    
        return ShortPath
    
    def normalize(self, listL):
        mn, mx = min(listL), max(listL)
        rangeR = mx - mn
        if rangeR != 0:
            return [float(m - mn) / rangeR for m in listL]
        else:
            print len(listL)
            return [0 for m in range(0, len(listL))]    
        
    # Stroke Path - [(A,B),(B,C),(C,D)]
    # Path = [A,B,C]
    
    def getStrokePath(self, path):
        return [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    
    def calcPathLength(self, path):
        return sum(map(self.calcLength, self.getStrokePath(path)))
    
    def calcLength(self, Stroke):
        # print Stroke
        for ed in self.G.edges(data=True):
            if tuple(sorted([ed[0], ed[1]])) == tuple(sorted(Stroke)):
                # print ed[2]['bs'].path.length()
                return ed[2]['bs'].path.length()    
    
    def getAngleList(self, path):
        angleList = []
    
        p = self.getStrokePath(path)
        
        for i in range(len(p) - 1):
            angleList.append(self.CostCurv(p[i], p[i + 1]))

        return angleList
    
    def CalcPathCurvatureCost(self, path):
        p = self.getStrokePath(path)
        # print p
        curvCost = sum([self.CostCurv(p[i], p[i + 1]) for i in range(len(p) - 1)])
        
        return curvCost
    
    def getStroke(self, Stroke):
        for ed in self.G.edges(data=True):
            eds = tuple(sorted([ed[0], ed[1]]))
            if tuple(sorted(eds)) == tuple(sorted(Stroke)):
                return ed
            
    
    ### Try using Tangents Again
    
    # Getting the Tangential points of the a given stroke
    def getTangent(self, Stroke, Node):
        # Common Node
        NodeXY = tuple([(nd[1]['x'], nd[1]['y']) for nd in self.G.nodes(data=True) if nd[0] == Node][0])
        
        # Fix Node of the Stroke
        #FirstXY = (Stroke[2]['bs'].interimPoints[0].scenePos().x(), Stroke[2]['bs'].interimPoints[0].scenePos().y())
        FirstXY = (Stroke[2]['bs'].controlPoints[0][0], Stroke[2]['bs'].controlPoints[0][1])
        
#        
        #print map(int,FirstXY), map(int,NodeXY)
        
        # If the first node of the Strokes is the common Node
        if util.dist(map(int,NodeXY),map(int,FirstXY)) < 2:
            print "First Point"
            P1X, P1Y = NodeXY
            
            # The Tangent is Frst Node <--> Control Point next to it
            #P2X, P2Y = Stroke[2]['bs'].interimPoints[1].scenePos().x(), Stroke[2]['bs'].interimPoints[1].scenePos().y()
            P2X, P2Y = Stroke[2]['bs'].controlPoints[1][0], Stroke[2]['bs'].controlPoints[1][1]

        else:
            #print "Last Point"
            P2X, P2Y = NodeXY
            
            # Else: the Tangent is Last Node <--> Control Point before it
            #P1X, P1Y = Stroke[2]['bs'].interimPoints[-2].scenePos().x(), Stroke[2]['bs'].interimPoints[-2].scenePos().y()
            P1X, P1Y = Stroke[2]['bs'].controlPoints[-2][0], Stroke[2]['bs'].controlPoints[-2][1]
                
        #print "Getting Tangent of ", Stroke, Node, (P1X, P1Y), (P2X, P2Y)
                         
        return (P1X, P1Y), (P2X, P2Y)
    
    def approxAngle(self, ang):
        Ang = [0, 22.5, 45, 67.5, 90]
        
        ang = int(math.degrees(ang))

        for a in Ang:
            if ang <= (a + (10)) and ang >= (a - 10):
                ang = a    
                
        return ang     
        
    # Angle between strokes    
    def CostCurv(self, StrokeA, StrokeB):
        if StrokeA == StrokeB:
            return 0
        else:
            sA, sB = self.getStroke(StrokeA), self.getStroke(StrokeB)
            
            comNd = list(set([sA[0], sA[1]]) & set([sB[0], sB[1]]))[0]
            #print "Common Node", comNd
            
            # Getting Tangent of the Strokes and their slopes for calculating the angle between them
            tangA, tangB = self.getTangent(sA, comNd), self.getTangent(sB, comNd)
            mA, mB = util.slope(tangA[0],tangA[1]), util.slope(tangB[0],tangB[1])
                        
            ang = util.angleFromSlope(mA, mB)
            
            #print StrokeA, StrokeB, "Angle",math.degrees(math.fabs(ang))self.approxAngle(math.fabs(ang))
            
            return self.approxAngle(math.fabs(ang))
                                
            if ang < 0:
                ang = self.approxAngle(-ang)
            else:
                ang = (180) - self.approxAngle(ang)
        
#            ang = int(math.degrees(ang))
#            
#            Ang = [0,22.5,45,67.5,90]
#            
#            for a in Ang:
#                if ang <= (a + (10)) and ang >= (a - 10):
#                    ang = a 
            

            # print  StrokeA,StrokeB,ang
            # print "======================================="

            return ang                          
            ### Add Logic to calculate angle between segments ### 


    def getPathPriority(self, path):
        start = path[0]
        end = path[-1]
        
        print start, end, path,

        L2RInd, T2BInd = self.ScriptDir

        L2R = self.G.node[end]['x'] - self.G.node[start]['x']
        T2B = self.G.node[end]['y'] - self.G.node[start]['y']
        
        stDeg, endDeg = self.G.degree(start), self.G.degree(end)
        
        pr = 0
        
        # Add Boundary Conditions
        if stDeg == 1:
            pr += 3 
        if endDeg == 1 :
            pr += 3
        if stDeg > 1 and stDeg % 2 == 1:
            pr += 2
        if endDeg > 1 and endDeg % 2 == 1:
            pr += 2
            
        nds = self.G.nodes(data=True)
        
        x = [nd[1]['x'] for nd in nds]
        y = [nd[1]['y'] for nd in nds]
        
        LeftN = [nd[0] for nd in nds if nd[1]['x'] == min(x)]
        RightN = [nd[0] for nd in nds if nd[1]['x'] == max(x)]
        TopN = [nd[0] for nd in nds if nd[1]['y'] == max(y)]
        BottomN = [nd[0] for nd in nds if nd[1]['y'] == min(y)]
        
        TopLeftN = list(set(TopN).intersection(set(LeftN)))
        TopRightN = list(set(TopN).intersection(set(RightN)))
        BottomLeftN = list(set(BottomN).intersection(set(LeftN)))
        BottomRightN = list(set(BottomN).intersection(set(RightN)))
        
#        if start in [LeftN, RightN,TopN,BottomN]:
#            pr += 1
#        if end in [LeftN, RightN,TopN,BottomN]:
#            pr += 1
              
        if not L2RInd:
            L2R = -L2R
        if not T2BInd:
            T2B = -T2B
            
        # print T2B,L2R

        if L2R > 0:
            pr += 2 
        if T2B > 0:
            pr += 1

        return pr 
    
    
    def CalcDirCost(self, path):
        p = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        #print p
        pDir = map(self.getDirection, p)
       
        pDirCost = self.getDirCost(pDir)
        
        #print pDirCost
        
        plen = map(self.calcLength, p)
        
        return pDirCost
    
    def getDirCost(self, path):
        p = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        print p
        
        costP = []
        
        for A, B in p:
            
            if len(A.split(" ")) == 2 and len(B.split(" ")) == 2:
                if A == B:
                    costP.append(2)
                elif A.split(" ")[0] == B.split(" ")[0]:
                    costP.append(1)
                elif A.split(" ")[1] == B.split(" ")[1]:
                    costP.append(2)    
                    
            if len(A.split(" ")) == 1 and len(B.split(" ")) == 1:
                if A == B:
                    costP.append(2)
                    
            if len(A.split(" ")) == 1 and len(B.split(" ")) == 2:
                if A == B.split(" ")[0]:
                    costP.append(1)
                elif A == B.split(" ")[0]:
                    costP.append(1)
            
            if len(A.split(" ")) == 2 and len(B.split(" ")) == 1:
                if B == A.split(" ")[0]:
                    costP.append(1)
                elif B == A.split(" ")[0]:
                    costP.append(1)
            
        return sum(costP)

    def getDirection(self, Stroke):
        A, B = Stroke
        L2R = self.G.node[B]['x'] - self.G.node[A]['x']
        T2B = self.G.node[B]['y'] - self.G.node[A]['y']
                
        if L2R == 0 and T2B < 0:
            return "North"
        if L2R == 0 and T2B > 0:
            return "South"
            
        if L2R > 0 and T2B == 0:
            return "East"
        if L2R < 0 and T2B == 0:
            return "West"   
            
        if L2R > 0 and T2B < 0:
            return "North East"
        if L2R > 0 and T2B > 0:
            return "South East"
        if L2R < 0 and T2B < 0:
            return "North West"
        if L2R < 0 and T2B > 0:
            return "South West" 
                    
        # print L2R, T2B



# ## For TSP related problem : Check backup 22nd March
    
    def GetTrajectoryMulti(self):
        print "Getting Multi-stroke Paths"
        
        OddNodes = [nd for nd in self.G.nodes() if self.G.degree(nd) % 2 == 1]
        PerfectMatch = self.PerformMatch(OddNodes)
        
        MultiPath = []
        
        for pair in PerfectMatch:             
            p = []
            angl = 0
            # print "Resetting Angle"
            for u, v in pair:
                paths = list(nx.all_simple_paths(self.G, u, v))
                # print pair, paths,
                pathsAng = map(self.CalcPathCurvatureCost, paths)
                pathsAngRnk = sorted(set(pathsAng))[:1]
                angl += pathsAngRnk[0]
                # print pathsAng
                path = [pt for ang, pt in zip(pathsAng, paths) if ang in pathsAngRnk]
                # print pair, paths,pathsAng, angl, path
                p.append(path)
                
            pathsT = list(itertools.product(*p))
            for pathsM in pathsT:
                if pathsM:
                    pathM = reduce(lambda x, y:x + y, [self.getStrokePath(path) for path in pathsM]) 
                    if len(pathM) == len(self.G.edges()):
                        MultiPath.append((angl, pair, pathM))
                       
        if MultiPath:
            for angle, pair, paths in MultiPath: 
                if angle == sorted(MultiPath)[0][0]:
                    yield paths

#        for angle, pair, paths in MultiPath[:]:
#            print angle,pair,paths
#            pathsT = list(itertools.product(*paths))
#            print pathsT
#            #print paths
#            for pathsM in pathsT:
#                print list(pathsM)
#                pathM = reduce(lambda x,y:x+y,[self.getStrokePath(path) for path in pathsM])              
#                if len(pathM) == len(self.G.edges()):
#                    print pathM
#                    MultiPaths.append(pathM)
                    
    def GetTrajectoryMulti2(self):
        print "Getting Multi-stroke Paths - 2:"
        
        oddnodes = len([nd for nd in self.G.nodes() if self.G.degree(nd) % 2 != 0])
            
        AllPathsN = [self.getStrokePath(path) for path in self.AllPaths]

        MPR = []

        for path in AllPathsN:
            reTrace = [i for i in range(len(path) - 1) if set(path[i]) == set(path[i + 1])]
            MPR.append(tuple(reTrace))
            
        MultiPaths = []
        
        for reTrace, path in zip(MPR, AllPathsN):
            MP = []
            j = 0
            for i in reTrace:
                MP.append(path[j:i + 1])
                j = i + 2
            MP.append(path[j:])            
            
            MP = [M for M in MP if M]
            
            MultiPaths.append(tuple(MP))
        
        # StrokeCount = sorted([len(list(MP)) for MP in MultiPaths if len(list(MP)) > 1])[:1]
        # print MultiPaths
        MultiPaths = [MP for MP in MultiPaths if len(list(MP)) <= (oddnodes / 2)]
        
        MPRnk = []
        
        for path in MultiPaths:
            ang = []       
            for stroke in path:
                p = [SS[0] for SS in stroke]
                p.append(stroke[-1][1])
                ang.append(self.CalcPathCurvatureCost(p))
            
            MPRnk.append((sum(ang), path))
            
        MPRnkCurv = list(set([ang for ang, path in sorted(MPRnk)[:1]]))
        
        MPRnk = [path for ang, path in MPRnk if ang in MPRnkCurv]
        MPRnk = util.UniqueLists([list(itertools.chain(*MP)) for MP in MPRnk if len(MP) > 1])
            
        print "Multi Paths complete"    
         
        return MPRnk
    
    def orderStrokes(self, strokes):
        strokes = list(strokes)
#        for stroke in strokes: