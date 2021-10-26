# -*-coding:utf-8-*-
# 记录最后一层压缩的节点团，包括每个节点团所包含的所有节点集，并输出保存，dictionary

def output_record(cliques, len_node, dataset):
    compress_nodes = ordered_communities(cliques)
    pass_length = len(cliques[1]) + len_node
    len_cmt = len(compress_nodes) +len_node
    for i in range(pass_length,len_cmt):
        temp_list = list(compress_nodes[i])
        for j in temp_list:
            if j > (len_node - 1):
                cm = compress_nodes[j]
                compress_nodes[i].update(cm)
                compress_nodes[i].remove(j)
    f = open('./dict/' + dataset + '_data.txt','w')
    f.write(str(compress_nodes))
    f.close()


def ordered_communities(cliques):
    all_cmt = {}
    for cmt in cliques:
        if len(cmt) != 0:
            all_cmt.update(cmt)
    return all_cmt



