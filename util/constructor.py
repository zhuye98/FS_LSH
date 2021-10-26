# -*-coding:utf-8-*-
import collections
import numpy as np
import scipy.sparse as sp
from util import tools
from scipy import io
import sys

#TODO
# To construct nodes, edges set and adjacent matrix


def nodes(length):
    return [i for i in range(length)]

def edges_matrix(path,name,len_node):
    """no edge weight
    file = open(path)
    edges = []
    for line in file.readlines():
        text = line.strip().split()
        x = int(text[0])
        y = int(text[1])
        edges.append([x,y])"""
    #edges

    mat = io.loadmat(path)
    sparseMatrix = sp.coo_matrix(mat.get(name))
    aa = sys.getsizeof(sparseMatrix)
    edges_dict = collections.defaultdict(list)
    edges_list = (np.column_stack((sparseMatrix.col,sparseMatrix.row))).tolist()
    for edge in edges_list:
        edge_t = tuple(edge)
        edges_dict[edge_t].append(1)

    #matrix
    edges = np.array(edges_list)
    nsl_adj = sp.coo_matrix((np.ones(edges.shape[0]), (edges[:, 0], edges[:, 1])),
                        shape=(len_node, len_node),
                        dtype=np.uint8)
    nsl_adj = nsl_adj + nsl_adj.T.multiply(nsl_adj.T > nsl_adj) - nsl_adj.multiply(nsl_adj.T > nsl_adj)

    nsl_adj = nsl_adj.todense()
    sl_adj = nsl_adj + np.eye(len_node, dtype=int)

    #nodes vectors
    nsl_nodes = nsl_adj.tolist()
    sl_nodes = sl_adj.tolist()

    edges_set = set()
    for k in range(len(edges)):
        node_1 = edges[k][0]
        node_2 = edges[k][1]
        edges_set.add((node_1, node_2))

    return edges_set, edges, nsl_nodes, sl_nodes

def allBuckets(sig_mat, b, r):
    n, d = sig_mat.shape

    assert(n==b*r)
    hashbuckets = collections.defaultdict(set)
    bands = np.array_split(sig_mat, b, axis=0)
    for i,band in enumerate(bands):
        for j in range(d):
            # The last value must be made a string, to prevent accidental
            # key collisions of r+1 integers when we really only want
            # keys of r integers plus a band index
            band_id = tuple(list(band[:,j])+[str(i)])
            hashbuckets[band_id].add(j)
    return hashbuckets


def candidatePairs(nsl_hashbucket, sl_hashbucket, zero_vec, band_num):
    #TODO
    # remove zero vector and leave buckets with only length larger than 1
    buckets_nozero_nsl = tools.removeZeroVec(nsl_hashbucket, zero_vec, band_num=band_num)
    buckets_nozero_sl = tools.removeZeroVec(sl_hashbucket, zero_vec, band_num=band_num)
    candidatePairs_nsl = tools.getPairs(buckets_nozero_nsl)
    candidataPairs_sl = tools.getPairs(buckets_nozero_sl)
    return candidatePairs_nsl.union(candidataPairs_sl)

def truePairs(candidate_pairs, nodes, threshold):
    truePairs = set()
    for pair in iter(candidate_pairs):
        if tools.isTrueJaccardSim(pair, nodes, threshold):
            truePairs.add(pair)
    return truePairs

def updateNodeSet(nodes, cliques):
    removed_nodes = tools.findAllNodes(cliques)
    append_nodes = [i for i in range(len(nodes),len(nodes)+len(cliques))]
    new_nodes = []
    new_cliques = collections.defaultdict(set)
    for j in range(len(nodes)):
        if nodes[j] not in removed_nodes:
            new_nodes.append(nodes[j])
    new_nodes.extend(append_nodes)

    for k in range(len(cliques)):
        id = int(k + len(nodes))
        value = cliques[k]
        for n in range(len(value)):
            new_cliques[id].add(value[n])

    return new_nodes, new_cliques

def updateNodeSet_(nodes, cliques, idx_id, new_idx):
    new_idx_=0
    removed_nodes = tools.findAllNodes(cliques)
    append_node = [i for i in range(new_idx, new_idx+len(cliques))]
    new_nodes = []
    new_cliques = collections.defaultdict(set)
    for j in range(len(idx_id)):
        if idx_id[j] not in removed_nodes:
            new_nodes.append(idx_id[j])
    new_nodes.extend(append_node)

    for k in range(len(cliques)):
        id = int(k + new_idx)
        value = cliques[k]
        for n in range(len(value)):
            new_cliques[id].add(value[n])
        new_idx_ = id

    return new_nodes, new_cliques, new_idx_+1

def updateEdgeSet(edges, nodes, clique, len_node):
    # TODO three types of edges
    #  the first type is the edge interconnecting two original nodes
    #  the second type is the edge interconnecting an original node and a super node
    #  the third type is the edge interconnecting two super nodes

    # create a dictionary for edges with weight: (node1, node2): weight
    new_edges = collections.defaultdict(set)

    for edge in iter(edges):
        # Type one
        if edge[0] in nodes and edge[1] in nodes:
            id = tools.sorted((edge[0],edge[1]))
            new_edges[id].add(1)
        # Type two
        elif edge[0] in nodes and edge[1] not in nodes:
            relat_cliques = tools.findRelatClique(edge[1], clique, len_node)
            for i in range(len(relat_cliques)):
                id = tools.sorted((edge[0],relat_cliques[i]))
                if id in new_edges.keys():
                    weight = new_edges[id].pop() + 1
                    new_edges[id].add(weight)
                else:
                    new_edges[id].add(1)

        elif edge[1] in nodes and edge[0] not in nodes:
            relat_cliques = tools.findRelatClique(edge[0], clique, len_node)
            for i in range(len(relat_cliques)):
                id = tools.sorted((edge[1],relat_cliques[i]))
                if id in new_edges.keys():
                    weight = new_edges[id].pop() + 1
                    new_edges[id].add(weight)
                else:
                    new_edges[id].add(1)
    # Type three
    for j in range(0,len(clique)):
        for k in range(j+1, len(clique)):
            cliq_id1 = j + len_node
            cliq_id2 = k + len_node
            clique_a = set(clique[j])
            clique_b = set(clique[k])
        # cliques dont really need to have a intersection part
            listOfEdges = tools.combination(clique_a, clique_b)

            id = (cliq_id1, cliq_id2)
            weight = 0
            # calculate weights
            for edge in iter(listOfEdges):
                if edge in edges:
                    weight += 1
            if weight != 0:
                new_edges[id].add(weight)
    return new_edges

def updateEdgeSet_(edges, nodes, clique, len_node):
    # create a dictionary for edges with weight: (node1, node2): weight
    new_edges = collections.defaultdict(set)
    edges_copy = edges.copy()
    for edge in edges_copy:
        # Type one
        if edge[0] in nodes and edge[1] in nodes:
            id = tools.sorted((edge[0],edge[1]))
            weight = list(edges_copy[edge])[0]
            new_edges[id].add(weight)
        # Type two
        elif edge[0] in nodes and edge[1] not in nodes:
            relat_cliques = tools.findRelatClique(edge[1], clique, len_node)
            for i in range(len(relat_cliques)):
                id = tools.sorted((edge[0], relat_cliques[i]))
                value = list(edges_copy[(edge[0], edge[1])])[0]
                if id in new_edges.keys():
                    weight = new_edges[id].pop() + value
                    new_edges[id].add(weight)
                else:
                    new_edges[id].add(value)

        elif edge[1] in nodes and edge[0] not in nodes:
            relat_cliques = tools.findRelatClique(edge[0], clique, len_node)
            for i in range(len(relat_cliques)):
                id = tools.sorted((edge[1], relat_cliques[i]))
                value = list(edges_copy[(edge[0], edge[1])])[0]
                if id in new_edges.keys():
                    weight = new_edges[id].pop() + value
                    new_edges[id].add(weight)
                else:
                    new_edges[id].add(value)

    # Type three
    for j in range(0,len(clique)):
        for k in range(j+1, len(clique)):
            cliq_id1 = j + len_node
            cliq_id2 = k + len_node
            clique_a = set(clique[j])
            clique_b = set(clique[k])
            # cliques dont really need to have a intersection part
            listOfEdges = tools.combination(clique_a, clique_b)
            id = (cliq_id1, cliq_id2)
            weight = 0
            # calculate weights
            for edge in iter(listOfEdges):
                if list(edges_copy[edge]):
                    weight += list(edges_copy[edge])[0]
            if weight != 0:
                new_edges[id].add(weight)

    return new_edges

def edges_weighted_matrix(nodes, edges, clique):
    # TODO
    #  Switch edges(id,id,weight) to edges(idx,idx,weight)
    #  Construct two types of adjacent weighted matrix
    #  return edges(type of list, type of dictionary), adjacent matrix

    len_node = len(nodes)
    # Switch
    edges_list, weight_list, edges_set = tools.edges2list(nodes, edges)
    # Construct symmetric matrix
    nsl_adj = sp.coo_matrix((weight_list, (edges_list[:, 0], edges_list[:, 1])),
                            shape=(len_node, len_node),
                            dtype=np.uint8)
    nsl_adj = nsl_adj + nsl_adj.T.multiply(nsl_adj.T > nsl_adj) - nsl_adj.multiply(nsl_adj.T > nsl_adj)
    nsl_adj = nsl_adj.todense()
    sl_adj = nsl_adj + np.eye(len_node, dtype=int)
    sl_adj_weighted = tools.appendWeight(sl_adj, clique)
    #nodes vectors
    nsl_nodes = nsl_adj.tolist()
    sl_nodes = sl_adj_weighted.tolist()

    return edges_set, edges_list, nsl_nodes, sl_nodes

def bruteForcePairs(nsl_nodes, sl_nodes, zero_vec, threshold):
    # TODO
    #  Calculate the weighted Jaccard similarity of each pair nodes via brute force
    #  Two types of symmetric adjacent matrix, individually
    #  Union all similar pair nodes, no duplications

    length = len(nsl_nodes)
    truePairs = set()

    for i in range(length):
        if i not in zero_vec:
            for j in range(i+1, length):
                if j not in zero_vec:
                    # To nsl nodes
                    if tools.isTureWeightedSim(nsl_nodes[i], nsl_nodes[j], threshold):
                        truePairs.add((i,j))
                    if tools.isTureWeightedSim(sl_nodes[i], sl_nodes[j], threshold):
                        truePairs.add((i,j))
    return truePairs



