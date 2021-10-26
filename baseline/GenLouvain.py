# -*-coding:utf-8-*-
import numpy as np
import scipy.sparse as sp
import scipy.io


#todo:
# use the newest node set and edge set to form a different index matrix
# then output this matrix to a .mat file
# then use this matlab code Genlouvain to do community detection
# reload the results of Genlouvain and calculate the onmi

def formNewEdge(id_idx, edge):
    new_edge = []
    for key in edge.keys():
        new_edge.append([id_idx[key[0]],id_idx[key[1]]])
    return new_edge

def formMatrix(length, edge, dataset_name):
    edges = np.array(edge)
    adj = sp.coo_matrix((np.ones(edges.shape[0]), (edges[:, 0], edges[:, 1])),
                            shape=(length, length),
                            dtype=np.double)
    adj = adj + adj.T.multiply(adj.T > adj) - adj.multiply(adj.T > adj)
    adj = adj.todense()
    # name as "dataset+fslsh.mat"
    scipy.io.savemat('./result/' + dataset_name+'_result.mat', mdict={'adj': adj})

def genlouvain(node_id, edge, dataset_name):
    length = len(node_id)
    idx = [i for i in range(0,length)]
    id_idx = dict(zip(node_id,idx))

    new_edge = formNewEdge(id_idx, edge)
    formMatrix(length, new_edge, dataset_name)



