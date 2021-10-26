# -*-coding:utf-8-*-
import itertools
import collections
import numpy as np

def findZeroVec(nodes):
    zero_vec = []
    for i in range(len(nodes)):
        if sum(nodes[i]) == 0:
            zero_vec.append(i)
    return zero_vec

# find all nodes from clique
def findAllNodes(clique):
    nodes = []
    for i in range(len(clique)):
        for j in range(len(clique[i])):
            if clique[i][j] not in nodes:
                nodes.append(clique[i][j])
    return nodes

# remove zero vectors and bucket number larger than 1
def removeZeroVec(nsl_hashbucket, zero_vec, band_num):
    bucket_list = [[] for row in range(band_num)]
    for bucket in nsl_hashbucket:
        value = nsl_hashbucket[bucket]
        band_id = int(bucket[-1])
        if len(value) > 1:
            list_a = list(value)
            list_b = list(value)
            for i in range(len(value)):
                if isZeroVec(list_a[i],zero_vec) == True:
                    list_b.remove(list_a[i])
            if len(list_b) > 1:
                bucket_list[band_id].append(list_b)
    return bucket_list

def isZeroVec(index, zero_vec):
    if index in zero_vec:
        return True
    else:
        return False

def isTrueJaccardSim(pair, nodes, threshold):
    pair_a = nodes[pair[0]]
    pair_b = nodes[pair[1]]
    all_count = 0
    inter_count = 0
    for i in range(len(pair_a)):
        if pair_a[i] | pair_b[i] != 0:
            all_count += 1
            if pair_a[i] & pair_b[i] == 1:
                inter_count += 1

    similarity = inter_count/all_count
    if similarity > threshold:
        return True
    else:
        return False

def isTureWeightedSim(pair_a, pair_b, threshold):
    length = len(pair_a)
    min_value = 0
    max_value = 0
    for i in range(length):
        if pair_a[i] | pair_b[i] != 0:
            min_value += min(pair_a[i], pair_b[i])
            max_value += max(pair_a[i], pair_b[i])
    similarity = min_value/max_value
    if similarity > threshold:
        return similarity
    else:
        return False


def getPairs(hashbuckets):
    candidate_pairs = set()
    for i in range(len(hashbuckets)):
        for j in range(len(hashbuckets[i])):
            bucket = set(hashbuckets[i][j])
            for pair in itertools.combinations(bucket, 2):
                candidate_pairs.add(pair)
    return candidate_pairs


def findRelatClique(node, clique, len_node):
    clique_index_list = []
    for i in range(len(clique)):
        if node in clique[i]:
            clique_index_list.append(i+len_node)
    return clique_index_list


def sorted(id):
    if id[0] < id[1]:
        return (id[0], id[1])
    else:
        return (id[1], id[0])


def edges2list(nodes, edges):
    edges_list = []
    weight_list = []
    edges_set = collections.defaultdict(set)
    for edge in edges:
        idx1 = nodes.index(edge[0])
        idx2 = nodes.index(edge[1])
        weight = list(edges[edge])[0]
        edges_list.append([idx1,idx2])
        weight_list.append(weight)

        id = (idx1, idx2)
        edges_set[id].add(weight)

    return np.array(edges_list), np.array(weight_list), edges_set

def idx2id(removed_nodes_idx, idx_id):
    id_list = []
    for i in range(len(removed_nodes_idx)):
        id_list.append(idx_id[removed_nodes_idx[i]])
    return id_list


def cliqueIdx2id(cliques, idx_id):
    new_clique = []
    for i in range(len(cliques)):
        c = []
        for j in range(len(cliques[i])):
            c.append(idx_id[cliques[i][j]])
        new_clique.append(c)
    return new_clique

def combination(clique_a, clique_b):
    edges = set()
    inter = clique_a & clique_b
    # To clique a
    side_b = clique_b - inter
    for i in iter(clique_a):
        for j in iter(side_b):
            edges.add(sorted((i,j)))
    # To clique b
    side_a = clique_a - inter
    for k in iter(clique_b):
        for l in iter(side_a):
            edges.add(sorted((k,l)))
    return edges

def appendWeight(adj, cliques):
    # generate weight list
    weight_list = []
    for index in cliques:
        weight_list.append(len(cliques[index]))
    # generate weight adj
    len_clique = len(cliques)
    start_index = adj.shape[0] - len_clique
    for i in range(len_clique):
        idx = start_index + i
        adj[idx,idx] = weight_list[i]
    return adj

