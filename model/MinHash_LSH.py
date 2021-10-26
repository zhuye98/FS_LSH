# -*-coding:utf-8-*-
import os
import numpy as np
import itertools
import collections

def sigMatrix(nsl_nodes, sl_nodes):
    hm_1 = HashManager(nsl_nodes)
    sig_mat_1 = hm_1(nsl_nodes,100)
    hm_2 = HashManager(sl_nodes)
    sig_mat_2 = hm_2(sl_nodes,100)

    return sig_mat_1,sig_mat_2


class HashManager():
    def __init__(self, a_matrix):
        self.a_matrix = a_matrix
        self.N = len(a_matrix)
        self.params = None

    def _initParams(self, n_sig):
        self.params = np.random.randint(self.N, size=[n_sig,2])
        print("")

    def _permuteRow(self, row):
        p= (self.params@np.array([1,row]))%self.N
        return p

    def __call__(self, nodes, n_sig, init=True):
        # Initialize if we change signature matrix length
        # or if we request to re-initialize
        if self.params is None or len(self.params) != n_sig or init:
            self._initParams(n_sig)

        #initialize signature matrix
        sig = np.full((n_sig, len(nodes)), np.inf)

        # each doc in docs is assumed to be an iterable object
        for j, node in enumerate(nodes):
            for k in range(self.N):
                if nodes[j][k] == 1:
                    orig_row = k
                    curr_col = self._permuteRow(orig_row)
                    sig[:,j] = np.minimum(sig[:,j],curr_col)

        return sig.astype(int)
