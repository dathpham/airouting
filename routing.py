# -*- coding: utf-8 -*-
"""
Created on Mon May 31 21:09:45 2021

@author: phdat
"""
## This is for research


import pandas as pd
import numpy as np
import random
import win32com.client as com
import xlsxwriter
import matplotlib.pyplot as plt
from time import time
import datetime

xls = pd.ExcelFile('C:\\Users\\phdat\\Desktop\\Research\\AIresearchmeeting\\SharatNetwork\\Vissim\\ToyDynamicData.xlsx')
sheet1 = pd.read_excel(xls, 'LinkInfo')
sheet2 = pd.read_excel(xls, 'TravelCost')
linktop=sheet1[['LinkID','StartNode','EndNode']]

ninfo = pd.ExcelFile('C:\\Users\\phdat\\Desktop\\Research\\AIresearchmeeting\\SharatNetwork\\Vissim\\Nodes.xlsx')
S1= pd.read_excel(ninfo, 'Sheet1')
nodeXY=S1[['X','Y']]

traveltimewithob=pd.read_csv('C:\\Users\\phdat\\Desktop\\Research\\AIresearchmeeting\\SharatNetwork\\Vissim\\LinkTravelTimes_WithObstruction.csv',header=None)

traveltime=traveltimewithob.fillna(150)

def oldreturnargmin(qtable, cur_node, nextnodelist):
    nextnodes = nextnodelist[cur_node-1][0]
    q=[]
    for i in nextnodes:
        q.append(qtable[cur_node-1][i-1])
    b= nextnodes[np.argmin(q)]
    b=b.item()
    if not isinstance(b,int):
        return random.choice(b)
    else: return b

def oldreturnoptimalroute(s,d,nextnodelist,qtable):
    route=[]
    route.append(s);
    cu_node=s
    while(cu_node!=d):
        take_node = oldreturnargmin(qtable, cu_node, nextnodelist);
        route.append(take_node);
        print(cu_node, sep=' ', end='->', flush=True)
        cu_node=take_node;

    return route

def getnextnode(linktop,cur_node):
    nextnodes=[]
    for i in np.arange(len(linktop['LinkID'])):
        if linktop['StartNode'][i]== cur_node :
            nextnodes.append(linktop['EndNode'][i])
    return nextnodes

def gettime(linktop, sheet2 ,cur_node,take_node,time):
    for i in np.arange(len(linktop['LinkID'])):
        if linktop['StartNode'][i]== cur_node and linktop['EndNode'][i]== take_node:
            return sheet2[time][i]

            
No_Node=25

emtyd={i:[] for i in range(No_Node)}
j=1
for i in range(No_Node):
    
    emtyd[i].append(getnextnode(linktop,j))
    j=j+1

nextnodelist=pd.Series(data=emtyd, index=np.arange(No_Node))




learn_rate=0.5;
qtable=np.zeros((No_Node,No_Node))
            
time = 0 # time interval

ttable=np.zeros((No_Node,No_Node))


for i in range(No_Node):
    nnodes=nextnodelist[i][0]
    for k in nnodes:
       ttable[i][k-1]=gettime(linktop, sheet2 ,i+1,k,time)

#make a static distance table

dtable = np.zeros((No_Node,No_Node))
for i in range(No_Node):
    nnodes=nextnodelist[i][0]
    for k in nnodes:
       dtable[i][k-1]=2500


def getttable(t):
    t_table=np.zeros((No_Node,No_Node))
    for i in range(No_Node):
        nnodes=nextnodelist[i][0]
        
        for k in nnodes:
            t_table[i][k-1]=gettime(linktop, traveltime ,i+1,k,t)
    return t_table

def qrouting(s,d,lrate,q_table,time,resetQ=True):
    if resetQ==True : qtable=np.zeros((No_Node,No_Node))
    else : qtable =np.copy(q_table)
    r=[]
    for _ in range(200):

        cur_node=s
        take_node=1;

        
        while(cur_node!=d):
            take_node = oldreturnargmin(qtable, cur_node, nextnodelist)
            take_nextnode= oldreturnargmin(qtable, take_node, nextnodelist)
        
        
            qtable[cur_node-1][take_node-1]=qtable[cur_node-1][take_node-1]+lrate*(qtable[take_node-1][take_nextnode-1] + gettime(linktop, traveltime ,cur_node,take_node,time) - qtable[cur_node-1][take_node-1])
            
            if cur_node==s: 
                r=[s]
                
            
            r.append(take_node)
            cur_node=take_node;
            #print(cur_node, sep=' ', end='->', flush=True)
            a=r
            if cur_node==d: r=[]
            
    return a,qtable

##Dijkstra
#source: https://www.geeksforgeeks.org/printing-paths-dijkstras-shortest-path-algorithm/


def minDistance(dist,queue):
        # Initialize min value and min_index as -1
    minimum = float("Inf")
    min_index = -1
          
        # from the dist array,pick one which
        # has min value and is till in queue
    for i in range(len(dist)):
        if dist[i] < minimum and i in queue:
            minimum = dist[i]
            min_index = i
    return min_index

di=[]
def printPath(parent, d):
          
        #Base Case : If j is source
    if parent[d] == -1 : 
        print(d+1, sep=' ', end='->', flush=True)
        return 
        return di.append(d+1)
    printPath(parent , parent[d])
    print(d+1, sep=' ', end='->', flush=True)
    return di.append(d+1)
    
def dijkstra(ttable, src):
  
    row = No_Node
    col = No_Node
  
        # The output array. dist[i] will hold
        # the shortest distance from src to i
        # Initialize all distances as INFINITE 
    dist = [float("Inf")] * row
  
        #Parent array to store 
        # shortest path tree
    parent = [-1] * row
  
        # Distance of source vertex 
        # from itself is always 0
    dist[src] = 0
      
        # Add all vertices in queue
    # queue = []
    # for i in range(row):
    #     queue.append(i)
    
    queue =list(np.arange(row))       
        
        #Find shortest path for all vertices
    while queue:
  
            # Pick the minimum dist vertex 
            # from the set of vertices
            # still in queue
            u = minDistance(dist,queue) 
  
            # remove min element     
            queue.remove(u)
  
            # Update dist value and parent 
            # index of the adjacent vertices of
            # the picked vertex. Consider only 
            # those vertices which are still in
            # queue
            for i in range(col):
                '''Update dist[i] only if it is in queue, there is
                an edge from u to i, and total weight of path from
                src to i through u is smaller than current value of
                dist[i]'''
                if ttable[u][i]!=0:
                    if dist[u] + ttable[u][i] < dist[i]:
                        dist[i] = dist[u] + ttable[u][i]
                        parent[i] = u
                       
  
        # print the constructed distance array

    return parent

s,d=1,20
# printPath(dijkstra(ttable, s-1), d-1)

def dkrouting(s,d,ttable):
    
    printPath(dijkstra(ttable, s-1), d-1)
    return



############ A* algorithm 
## code modified from https://www.pythonpool.com/a-star-algorithm-python/

 # This is heuristic function using Euclidean Distance from a to b
def h(a,b):
    return np.linalg.norm(nodeXY.iloc[a-1].to_numpy()-nodeXY.iloc[b-1].to_numpy())



def a_star_algorithm(s, d,t_table):
        # In this open_lst is a lisy of nodes which have been visited, but who's 
        # neighbours haven't all been always inspected, It starts off with the start 
  #node
        # And closed_lst is a list of nodes which have been visited
        # and who's neighbors have been always inspected
    open_lst = set([s])
    closed_lst = set([])
 
        # poo has present distances from start to all other nodes
        # the default value is +infinity
    poo = {}
    poo[s] = 0
 
        # par contains an adjac mapping of all nodes
    par = {}
    par[s] = s
 
    while len(open_lst) > 0:
        n = None
 
        # it will find a node with the lowest value of f() -
        for v in open_lst:
            if n == None or poo[v] + h(v,d) < poo[n] + h(n,d):
                n = v;
 
        if n == None:
            print('Path does not exist!')
            return None
 
            # if the current node is the stop
            # then we start again from start
        if n == d:
            reconst_path = []
 
            while par[n] != n:
                reconst_path.append(n)
                n = par[n]
 
            reconst_path.append(s)
 
            reconst_path.reverse()
 
            print('Path found: {}'.format(reconst_path))
            return reconst_path
 
            # for all the neighbors of the current node do
        for m in getnextnode(linktop,n):
              # if the current node is not presentin both open_lst and closed_lst
                # add it to open_lst and note n as it's par
            if m not in open_lst and m not in closed_lst:
                open_lst.add(m)
                par[m] = n
                poo[m] = poo[n] + t_table[m-1][n-1]
 
                # otherwise, check if it's quicker to first visit n, then m
                # and if it is, update par data and poo data
                # and if the node was in the closed_lst, move it to open_lst
            else:
                if poo[m] > poo[n] + t_table[m-1][n-1]:
                    poo[m] = poo[n] + t_table[m-1][n-1]
                    par[m] = n
 
                    if m in closed_lst:
                        closed_lst.remove(m)
                        open_lst.add(m)
 
            # remove n from the open_lst, and add it to closed_lst
            # because all of his neighbors were inspected
        open_lst.remove(n)
        closed_lst.add(n)
 
    print('Path does not exist!')
    return None

#x.insert(0,s)
x=[s]


def returncost(route,t):
    cost=[]
    t_table=getttable(t)
    for i in np.arange(len(route)):
        if i==len(route)-1: break
    
        cost.append(t_table[route[i]-1][route[i+1]-1])
    return sum(cost)

def return_static_cost(route):
    cost=[]
    
    for i in np.arange(len(route)):
        if i==len(route)-1: break
    
        cost.append(dtable[route[i]-1][route[i+1]-1])
    return sum(cost)

# t0 = time()
# qrouting(s,d)
# t1 = time()
# dkrouting(s,d,ttable)
# t2 = time()

# print ('function qrouting takes %f' %(t1-t0))
# print ('function dkrouting takes %f' %(t2-t1))


# for i in range(1,150):
#      match=[]
#     compt=[]
#     route=[]
#     t0 = time()
#     r,q=qrouting(s,d,i*0.01,qtable,True)
#     t1 = time()
#     route.append(r)
#     x=[s]
#     dkrouting(s,d,ttable)
#     print ('learn rate = ',i*0.01,'qrouting takes %f' %(t1-t0), "match Dijkstra:",x==r)
#     compt.append(t1-t0)




# def rt(f):
#     if f=='q':
#         for i in range(len(No_Node)):
#             #print('qrouting: misisecond')
#             t0 = datetime.datetime.now()
#             oqrouting(1,i+1)
#             t1 = datetime.datetime.now()
#             delta1=(t1-t0)
#             #print(delta1.total_seconds() * 1000, sep=',', end='', flush=True)
#             print(delta1.total_seconds() * 1000)
#     if f=='d':
#         for i in range(len(No_Node)):
#             #print('dkrouting: misisecond')
#             t2 = datetime.datetime.now()
#             dkrouting(1,i+1,ttable)
#             t3 = datetime.datetime.now()
#             delta=(t3-t2)
#             #print(delta.total_seconds() * 1000, sep=',', end='', flush=True)
#             print(delta.total_seconds() * 1000)

# def rtr(f):
#     if f=='q':
#         for i in range(len(No_Node)):
#             #print('qrouting: misisecond')
#             t0 = datetime.datetime.now()
#             orqrouting(1,i+1)
#             t1 = datetime.datetime.now()
#             delta1=(t1-t0)
#             #print(delta1.total_seconds() * 1000, sep=',', end='', flush=True)
#             print(i+1,':',delta1.total_seconds() * 1000)
#     if f=='d':
#         for i in range(len(No_Node)):
#             #print('dkrouting: misisecond')
#             t2 = datetime.datetime.now()
#             dkrouting(1,i+1,ttable)
#             t3 = datetime.datetime.now()
#             delta=(t3-t2)
#             #print(delta.total_seconds() * 1000, sep=',', end='', flush=True)
#             print(i+1,':',delta.total_seconds() * 1000)



#X[np.isnan(X)] = 0.

# workbook = xlsxwriter.Workbook('ttable.xlsx')
# worksheet = workbook.add_worksheet()
# row = 0
# for col, data in enumerate(ttable):
#     worksheet.write_column(row, col, data)

# workbook.close()

# workbook = xlsxwriter.Workbook('qtablelinkEva.xlsx')
# worksheet = workbook.add_worksheet()
# row = 0
# for col, data in enumerate(qtable):
#     worksheet.write_column(row, col, data)

# workbook.close()

# import matplotlib.pyplot as plt
# # line 1 points
# x1 = [5,15,25,35]
# y1 = [d1.mean(),d2.mean(),d3.mean(),d4.mean()]
# # plotting the line 1 points 
# plt.plot(x1, y1, label = "Dijkstra")
# # line 2 points
# x2 = [5,15,25,35]
# y2 = [q1.mean(),q2.mean(),q3.mean(),q4.mean()]
# # plotting the line 2 points 
# plt.plot(x2, y2, label = "Qrouting")
# plt.xlabel('Number of Node')
# # Set the y axis label of the current axis.
# plt.ylabel('Computation time')
# # Set a title of the current axes.
# plt.title('Time Complexity in Millisecond ')
# # show a legend on the plot
# plt.legend()
# # Display a figure.
# plt.show()

###Learning rate vs computation time for s,d=35,19
# X_m=[]
# Y_m=[]
# X_no=[]
# Y_no=[]

# for i in range(1,150):

#     t0 = time()
#     r,q=qrouting(s,d,i*0.01,qtable,0,True)
#     t1 = time()
    
#     x=[s]
#     dkrouting(s,d,ttable)
#     print ('Lrate:',i*0.01,'QR takes %f' %(t1-t0), "Optimal?",x==r)
#     if (x==r): 
#         X_m.append(i);
#         Y_m.append(t1-t0)
#     else: 
#         X_no.append(i)
#         Y_no.append(t1-t0)



###optimal learning rate

X_q=[]
Y_q=[]


for i in range(1,150):

    
    r,q=qrouting(s,d,i*0.01,qtable,0,True)
    
  
    X_q.append(i);
    Y_q.append(returncost(r,0))



plt.figure(figsize=(11,11))
plt.title('Route Cost vs Learning Rate ')
x = np.linspace(0,5,100)
plt.scatter(X_q, Y_q,marker='o')
plt.xlabel('Learning rate')
plt.ylabel('Route Cost')
plt.show()

#best learning rate = 0.29

# X_qm=[]   #X of qrouting that match
# Y_qm=[]   #Y of qrouting that match
# X_qn=[]  # X of qrouting that not match
# Y_qn=[]   #Y of qrouting that not match
# X_nd=[]  # X of Dijkstra
# Y_nd=[]  # Y of Dijkstra

# qtable=np.zeros((No_Node,No_Node))
# q=qtable
# for i in range(0,600,10):
#     t0 = time()
#     r,q=qrouting(s,d,1,qtable,i,True)
#     t1 = time()
#     ttable=getttable(i)
#     x=[s]
#     t2 = time()
#     dkrouting(s,d,ttable)
#     t3 = time()
#     if (x==r): 
#         X_qm.append(i);
#         Y_qm.append(t1-t0)
#     else: 
#         X_qn.append(i)
#         Y_qn.append(t1-t0)

import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.gofplots import qqplot_2samples

#test OD
testOD =((1,25),(21,5),(10,16),(6,24),(22,4),(4,16),(18,5),(12,20),(17,5),(22,9))
Ys_a=[]
Ys_d=[]
Xs=[]
for (s,d) in testOD:
    a = a_star_algorithm(s, d,dtable)
    di=[s]
    
    dkrouting(s,d,dtable)
    Ys_a.append(return_static_cost(di))
    Ys_d.append(return_static_cost(a))
    Xs.append(i)
    print(return_static_cost(a)-return_static_cost(di))



pp_x = sm.ProbPlot(np.array(Ys_d))
pp_y = sm.ProbPlot(np.array(Ys_a))
qqplot_2samples(pp_x, pp_y,xlabel='Dijkstra',ylabel='A*',line='45')
plt.show()


# for each of 10 OD pairs, run and plot 3 plot each

for (s,d) in testOD:
    X_q=[]   #X of qrouting
    Y_q=[]   #Y of qrouting 
    X_d=[]  # X of dijktra
    Y_d=[]   #Y of dijktra
    X_a=[]  # X of A*
    Y_a=[]  # Y of A*

    qtable=np.zeros((No_Node,No_Node))

    for i in range(0,719,1):
    
        r,q=qrouting(s,d,0.29,qtable,i,True)
    
        ttable=getttable(i)
        a = a_star_algorithm(s, d,ttable)
        di=[s]
    
        dkrouting(s,d,ttable)
        X_q.append(i)
        Y_q.append(returncost(r,i))
        X_d.append(i)
        Y_d.append(returncost(di,i))
        X_a.append(i)
        Y_a.append(returncost(a,i))

    qqplot_2samples(np.array(Y_q), np.array(Y_d),xlabel='Qrouting',ylabel='Dijkstra',line='45')
    plt.show()
    qqplot_2samples(np.array(Y_a), np.array(Y_d),xlabel='A*',ylabel='Dijkstra',line='45')
    plt.show()



####
route_list_d=[]

route_list_q=[]

route_list_a=[]

qtable=np.zeros((No_Node,No_Node))
s,d=1,25
for i in range(0,719,1):

        r,q=qrouting(s,d,0.29,qtable,i,True)

        ttable=getttable(i)
        a = a_star_algorithm(s, d,ttable)
        di=[s]

        dkrouting(s,d,ttable)
        route_list_a.append(a)
        route_list_d.append(di)
        route_list_q.append(r)


route_list_q_uniq=np.unique(route_list_q,axis=0)


#draw Graph

import networkx as nx
import matplotlib.pyplot as plt


edges=[]
for i in range(79):
    
    edges.append((linktop['StartNode'][i], linktop['EndNode'][i], {'weight': 2500}))

G = nx.Graph()

G.add_edges_from(edges)
pos = nx.spring_layout(G)

%matplotlib inline
nx.draw_networkx(G,pos)
# draw path in red
path = nx.shortest_path(G,source=1,target=25)
path_edges = list(zip(path,path[1:]))
nx.draw_networkx_nodes(G,pos,nodelist=path,node_color='r')
nx.draw_networkx_edges(G,pos,edgelist=path_edges,edge_color='r',width=2)
plt.axis('equal')
plt.show()

#plot route 1st change
nx.draw_networkx(G,pos)
# draw path in red
path = route_list_q_uniq[1]
path_edges = list(zip(path,path[1:]))
nx.draw_networkx_nodes(G,pos,nodelist=path,node_color='r')
nx.draw_networkx_edges(G,pos,edgelist=path_edges,edge_color='r',width=2)
plt.axis('equal')
plt.show()

#draw path
x.draw_networkx(G,pos)
# draw path in red
pathq = Y10_q[0]
patha = Y10_a[0]
pathd = Y10_d[0]
path_edgesq = list(zip(pathq,pathq[1:]))
path_edgesa = list(zip(patha,patha[1:]))
path_edgesd = list(zip(pathd,pathd[1:]))
nx.draw_networkx_nodes(G,pos,nodelist=[1,25],node_color='b',node_size=700)
nx.draw_networkx_nodes(G,pos,nodelist=pathq,node_color='r')
nx.draw_networkx_edges(G,pos,edgelist=path_edgesq,edge_color='r',width=2)
nx.draw_networkx_nodes(G,pos,nodelist=pathd,node_color='g')
nx.draw_networkx_edges(G,pos,edgelist=path_edgesd,edge_color='g',width=2)
nx.draw_networkx_nodes(G,pos,nodelist=patha,node_color='y')
nx.draw_networkx_edges(G,pos,edgelist=path_edgesa,edge_color='y',width=2)

plt.axis('equal')
plt.show()




# nx.draw_networkx_nodes(G,pos,node_size=70)
# nx.draw_networkx_nodes(G,pos=pos)
# nx.draw_networkx_labels(G,pos=pos)
nx.draw_networkx(G)

##plot seperate window
#%matplotlib qt

## plot inline
#%matplotlib inline


s,d=1,20

X_q=[]   #X of qrouting
Y_q=[]   #Y of qrouting 
X_d=[]  # X of dijktra
Y_d=[]   #Y of dijktra
X_a=[]  # X of A*
Y_a=[]  # Y of A*

qtable=np.zeros((No_Node,No_Node))

for i in range(0,719,1):
    
    r,q=qrouting(s,d,0.29,qtable,i,True)
    
    ttable=getttable(i)
    a = a_star_algorithm(s, d,ttable)
    di=[s]
    
    dkrouting(s,d,ttable)
    X_q.append(i)
    Y_q.append(returncost(r,i))
    X_d.append(i)
    Y_d.append(returncost(di,i))
    X_a.append(i)
    Y_a.append(returncost(a,i))

plt.figure(figsize=(11,11))
plt.title('. : Dijkstra, + : Qrouting, x : A* ')
x = np.linspace(0,5,100)
plt.scatter(X_q, Y_q,marker='+')
plt.scatter(X_d, Y_d,marker='.')
plt.scatter(X_a, Y_a,marker='x')
plt.xlabel('Timestep')
plt.ylabel('Route Cost')
plt.show()

##RMS
rs_DQ=(np.array(Y_q)-np.array(Y_d))**2
rs_DA=(np.array(Y_a)-np.array(Y_d))**2

plt.figure(figsize=(11,11))
plt.title(' Squared Error per timestep between Dijkstra and Qrouting ')
x = np.linspace(0,5,100)
plt.scatter(X_q, rs_DQ,marker='x')
plt.xlabel('Timestep')
plt.ylabel('Squared Error')
plt.show()

plt.figure(figsize=(11,11))
plt.title(' Squared Error per timestep between Dijkstra and A*')
x = np.linspace(0,5,100)
plt.scatter(X_q, rs_DA,marker='x')
plt.xlabel('Timestep')
plt.ylabel('Squared Error')
plt.show()

fig = plt.figure(1, figsize=(9, 6))
ax = fig.add_subplot(111)    
bp1 = ax.boxplot(rs_DQ)
bp2 = ax.boxplot(rs_DA)

import seaborn as sns
from seaborn_qqplot import pplot
import statsmodels.api as sm
import pylab as py

data=pd.DataFrame()

data['Dijkstra_Qrouting squared error']=rs_DQ

data['Dijkstra_A* squared error']=rs_DA

sns.boxplot( data=data,order=["Dijkstra_Qrouting squared error", "Dijkstra_A* squared error"])


pplot(data, x="sepal_length", y="petal_length", hue="species", kind='qq', height=4, aspect=2, display_kws={"identity":False, "fit":True})

sm.qqplot(data, line ='45')
py.show()


plt.figure()
plt.scatter(np.sort(Y_a), np.sort(Y_d))
plt.xlabel('A*')
plt.ylabel('Dijkstra')
plt.show()
plt.close()

plt.figure()
plt.scatter(np.sort(Y_q), np.sort(Y_d))
plt.xlabel('Q-routing')
plt.ylabel('Dijkstra')
plt.show()
plt.close()

#compare A* cost vs Dijk cost
compare = [a >= d for a,d in zip(np.array(Y_a),np.array(Y_d))]

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.transforms as mtransforms
fig, ax = plt.subplots()
ax.scatter(np.sort(Y_a), np.sort(Y_d))
line = mlines.Line2D([0, 1], [0, 1], color='red')
transform = ax.transAxes
line.set_transform(transform)
ax.add_line(line)
plt.show()




# import statsmodels.api as sm
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.graphics.gofplots import qqplot_2samples

# pp_a = sm.ProbPlot(np.array(Y_a))
# pp_d = sm.ProbPlot(np.array(Y_d))
# pp_q = sm.ProbPlot(np.array(Y_q))
# qqplot_2samples(pp_q, pp_d,xlabel='Qrouting',ylabel='Dijkstra',line='45')
# plt.show()
# qqplot_2samples(pp_a, pp_d,xlabel='A*',ylabel='Dijkstra',line='45')
# plt.show()


# qqplot_2samples(pp_x, pp_y)
# plt.show()

# qqplot_2samples(np.array(Y_q), np.array(Y_d),xlabel='Qrouting',ylabel='Dijkstra',line='45')
# plt.show()
# qqplot_2samples(np.array(Y_a), np.array(Y_d),xlabel='A*',ylabel='Dijkstra',line='45')
# plt.show()
# qqplot_2samples(rs_DQ, rs_DA,xlabel='A*',ylabel='Dijkstra',line='45')
# plt.show()
