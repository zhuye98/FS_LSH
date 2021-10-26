# -*-coding:utf-8-*-
import numpy as np
import collections
from onmi import onmi
from omega_index import Omega


#todo
# read two csv file as two community sets, use onim.py to calculate
# overlapping community nmi.
# 1. three paths of label files, one is the ground true label file, one is the
#    direct genlouvain label file, one is the fast similarity genlouvain
#    label file. The former two can be formed as set of community in the
#    same way, the latter one need to do something different.
# 2. one path of the after-fslsh compressed node, working with the above
#    latter label file to form a set of community

dataset = 'Email'
gt_label_path = './label/gt_' + dataset + '_label.csv'
glv_label_path = './label/glv_' + dataset + '_label.csv'
fslsh_glv_path = './label/fslsh_glv_' + dataset + '_label.csv'
cmt_path = 'dict/' + dataset + '_data.txt'

# read label from each file
gt_label = np.genfromtxt(gt_label_path, delimiter=',', skip_header=False)
glv_label = np.genfromtxt(glv_label_path, delimiter=',', skip_header=False)
fslsh_glv_label = np.genfromtxt(fslsh_glv_path, delimiter=',', skip_header=False)
gt_label_list = gt_label.tolist()
glv_label_list = glv_label.tolist()
fslsh_glv_label_list = fslsh_glv_label.tolist()

# how many communities for each label and the total number of nodes
max_gt = int(max(gt_label_list))
max_glv = int(max(glv_label_list))
max_fslsh_glv = int(max(fslsh_glv_label_list))
length = len(gt_label_list)

# allocate nodes to different communities according to the label
communities_gt = collections.defaultdict(list)
for i in range(length):
    id = str(int(gt_label_list[i]))
    communities_gt[id].append(i)

communities_glv = collections.defaultdict(list)
for i in range(length):
    id = str(int(glv_label_list[i]))
    communities_glv[id].append(i)

cmt_gt = []
for i in range(max_gt):
    cmt_gt.append(communities_gt[str(i+1)])

cmt_glv = []
for i in range(max_glv):
    cmt_glv.append(communities_glv[str(i+1)])

# combine with the cmt set
with open('./' +dataset + '_node.csv', 'r', encoding='UTF-8-sig') as f:
    nodes_list = []
    for line in f.readlines():
        line = line.strip()
        nodes_list.append(int(line))

f = open('dict/' + dataset + '_data.txt', 'r')
cmt = eval(f.read())

# construct fslsh_glv communities
communities_fsglv = collections.defaultdict(list)
for i in range(len(fslsh_glv_label_list)):
    id = str(int(fslsh_glv_label_list[i]))
    if nodes_list[i] < length:
        communities_fsglv[id].append(nodes_list[i])
    else:
        cmp_nodes = cmt[nodes_list[i]]
        temp_set = set(communities_fsglv[id])
        temp_set.update((cmp_nodes))
        communities_fsglv[id] = list(temp_set)

cmt_fsglv = []
for i in range(max_fslsh_glv):
    cmt_fsglv.append(communities_fsglv[str(i+1)])

print("dataset:",dataset)
omega_1 = Omega(communities_gt, communities_glv)
print("Genlouvain:",omega_1.omega_score)
omega_2 = Omega(communities_gt, communities_fsglv)
print("FSlsh-Genlouvain:",omega_2.omega_score)
print("compressibility:",len(fslsh_glv_label_list)/length)