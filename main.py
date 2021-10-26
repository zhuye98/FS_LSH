# -*-coding:utf-8-*-
from util import constructor,tools, compress_note
from model import MinHash_LSH
from baseline import GenLouvain
import matplotlib.pyplot as plt
from tqdm import tqdm
import networkx as nx
import pandas as pd
import time
import os

#TODO
# step 1: find cliques via MinHash_LSH

start = time.time()
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
# Load network information, nodes set, edges set, and adjacent matrix
# number of nodes
len_node = 10106
dataset = 'amazon_1'
name = 'adj'
path = './data/' + dataset + '.mat'
node_path = './' + dataset + '_node.csv'
b = 20
r = 5
threshold = 0.8

# save cliques and nodes and edges set from different iteration
iter_cliques = []
iter_nodes = []
iter_edges = []

nodes = constructor.nodes(len_node)
print("constructor.edges_matrix:")
edges, edges_list, nsl_nodes, sl_nodes = constructor.edges_matrix(path,name,len_node)

# Find all zero vectors
zero_vec = tools.findZeroVec(nsl_nodes)

# Signature matrix
print("Signature matrix:")
nsl_sig_mat, sl_sig_mat = MinHash_LSH.sigMatrix(nsl_nodes,sl_nodes)
nsl_hashbucket = constructor.allBuckets(nsl_sig_mat, b ,r)
sl_hashbucket = constructor.allBuckets(sl_sig_mat, b, r)

# remove column number of zero vector
print("constructor.candidatePairs:")
candidatePairs = constructor.candidatePairs(nsl_hashbucket,sl_hashbucket, zero_vec, band_num=b)
print("constructor.truePairs:")
truePairs = constructor.truePairs(candidatePairs, sl_nodes, threshold)
# find all super nodes from true pairs
G=nx.Graph()
G.add_edges_from(truePairs)
cliques = list(nx.clique.find_cliques(G))


# update nodes set
new_nodes, new_cliques = constructor.updateNodeSet(nodes, cliques)
# update edges set
new_edges = constructor.updateEdgeSet(edges, new_nodes, cliques, len_node)

iter_cliques.append(new_cliques)
iter_nodes.append(new_nodes)
iter_edges.append(new_edges)

#TODO
# step 2: find cliques via brute force weighted Jaccard similarity
# with the list of threshold {0.7, 0.6, 0.5}

# update node length (len_node + len(new_cliques))
new_idx = len_node + len(new_cliques)

for threshold in tqdm([0.7, 0.6 ,0.5]):
    # Switch edges(id - id) to edges(idx -idx), then use the edges to construct adjacent matrix
    nodes_ = constructor.nodes(len(iter_nodes[-1]))
    edges_set_, edges_list_, nsl_nodes_, sl_nodes_ = constructor.edges_weighted_matrix(
        iter_nodes[-1], iter_edges[-1], iter_cliques[-1])
    zero_vec_ = tools.findZeroVec(nsl_nodes_)
    print(str(threshold) + ':bruteForcePairs')
    truePairs_ = constructor.bruteForcePairs(nsl_nodes_, sl_nodes_, zero_vec_, threshold)

    G1=nx.Graph()
    G1.add_edges_from(truePairs_)
    cliques_ = list(nx.clique.find_cliques(G1))

    # clique(idx) -> clique(id)
    cliques_id = tools.cliqueIdx2id(cliques_, iter_nodes[-1])
    print(str(threshold) + ':updatingNodeSet')
    # update nodes set and edges set
    new_nodes_, new_cliques_, new_idx_ = constructor.updateNodeSet_(nodes_, cliques_id, iter_nodes[-1], new_idx)
    print(str(threshold) + ':updatingEdgeSet')
    new_edges_ = constructor.updateEdgeSet_(iter_edges[-1], new_nodes_, cliques_id, new_idx)

    iter_cliques.append(new_cliques_)
    iter_nodes.append(new_nodes_)
    iter_edges.append(new_edges_)
    new_idx = new_idx_

# record the super nodes of the last layer?
compress_note.output_record(iter_cliques, len_node, dataset)
# output the current node list
nodes_list = pd.DataFrame(iter_nodes[-1])
nodes_list.to_csv(node_path, header=None, encoding='utf-8', index=False)


#end = time.time()
#print(end-start)

# Baselines
# output a symmetrical matrix to .mat file and make good use of GenLouvain
GenLouvain.genlouvain(iter_nodes[-1], iter_edges[-1], dataset_name=dataset)







