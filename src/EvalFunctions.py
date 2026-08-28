from src.ExpressionTree import *
from src.LLVMTools import single_expression_to_tree
from src.general_tools import test_equivalent_by_brute_force


# TD: use size here and in the % decrease function, not num_ops
def calc_percent_size_reduction_from_tree1to_tree2(tree1:ExpressionTree, tree2:ExpressionTree):
    if (isinstance(tree1, str)):
        tree1 = single_expression_to_tree(tree1)
    if (isinstance(tree2, str)):
        tree2 = single_expression_to_tree(tree2)

    tree1_num_ops = len(tree1.get_binary_ops_as_list())
    tree2_num_ops = len(tree2.get_binary_ops_as_list())

    if tree1_num_ops == 0:
        return 0.0
    size_reduction = ((tree1_num_ops - tree2_num_ops) / tree1_num_ops) * 100.0

    return size_reduction


def calc_percent_size_increase_node1_to_node2(tree1, tree2):
    # ((New – Old) / Old) x 100
    if (isinstance(tree1, str)):
        tree1 = single_expression_to_tree(tree1)
    if (isinstance(tree2, str)):
        tree2 = single_expression_to_tree(tree2)

    tree1_num_ops = len(tree1.get_binary_ops_as_list())
    tree2_num_ops = len(tree2.get_binary_ops_as_list())

    if tree1_num_ops == 0:
        return 0.0
    size_increase = ((tree2_num_ops - tree1_num_ops) / tree1_num_ops) * 100.0
    return size_increase


def get_percentage_equivalent_synth_terms(ground_truth_tree, obf_tree):
    num_gt_terms = ground_truth_tree.get_num_binops()
    num_equivalent_terms = len(get_equivalent_synth_terms(ground_truth_tree, obf_tree))

    if num_equivalent_terms == 0:
        return 0
    return (num_gt_terms * 1.0) / num_equivalent_terms

def get_percentage_cse(tree:ExpressionTree, min_num_binops=1):
    size = tree.get_size()
    term_dict = get_term_dict_for_node(tree, min_num_binops)

    total_ops = tree.get_binary_ops_as_list()
    ops_greater_than_size = [x for x in total_ops if x.get_num_binops() >= min_num_binops]
    num_ops_greater_than_size = len(ops_greater_than_size)

    # percent cse = total duplicate nodes / total nodes

    total_cse = 0
    for k, v in term_dict.items():
        if v > 1:
            total_cse += v

    if num_ops_greater_than_size == 0:
        return 0
    percent_cse = (total_cse / num_ops_greater_than_size) * 100.00
    return percent_cse


def get_equivalent_synth_terms(ground_truth_tree:ExpressionTree, obf_tree:ExpressionTree, minimum_size=2):
    # this function stores all ground truth subtrees greater than size 2 and then
    # returns a list of all nodes in the obfuscated tree which are equivalent (by brute force checking)
    # with any of the ground truth nodes, minus the root node (which should always be equivalent).

    gt_nodes = [x for x in ground_truth_tree.get_binary_ops_as_list() if x.get_size() >= minimum_size]
    obf_tree_nodes = [x for x in obf_tree.get_binary_ops_as_list() if x.get_size() >= minimum_size]

    if obf_tree.root in obf_tree_nodes:
        obf_tree_nodes.remove(obf_tree.root)

    if ground_truth_tree.root in gt_nodes:
        gt_nodes.remove(ground_truth_tree.root)

    obf_tree_equivalents = []

    for o in obf_tree_nodes:
        for g in gt_nodes:
            if test_equivalent_by_brute_force(str(o), str(g), print_out=False):
                obf_tree_equivalents.append(o)


    return obf_tree_equivalents

def get_percent_alternated(tree:ExpressionTree):
    num_alternated = tree.get_alternation()
    total_ops = tree.get_num_ops()

    if total_ops == 0:
        return 0

    percent_alternated = (num_alternated / (total_ops * 1.0)) * 100.0

    return percent_alternated

def get_term_dict_for_node(node:Node, min_num_binops=1):
    # size refers to the minimum node size for collecting unique nodes
    if (isinstance(node, ExpressionTree)):
        node = node.root

    node_dict = {}
    if min_num_binops == 1:
        all_nodes = node.get_binary_ops_as_list()
    else:
        all_nodes = [x for x in node.get_binary_ops_as_list() if x.get_num_binops() >= min_num_binops]

    for n in all_nodes:
        str_rep = str(n).strip(" ")
        if str(n) not in node_dict:
            node_dict[str_rep] = 1
        else:
            node_dict[str_rep] += 1

    return node_dict





def get_unique_terms_for_node(tree, min_num_binops=1):
    node_dict = get_term_dict_for_node(tree, min_num_binops)

    list_nodes = []

    for k, v in node_dict.items():
        if v == 1:
            list_nodes.append(v)

    return list_nodes

def get_duplicates_dict_for_node(node:Node):
    term_dict = get_term_dict_for_node(node)

    duplicates_dict = {}
    for key, val in term_dict.items():
        if val > 1:
            duplicates_dict[key] = val

    return duplicates_dict


def print_unique_terms(tree:ExpressionTree, min_num_binops=1):
    info = get_term_dict_for_node(tree, min_num_binops)

    print("all unique nodes for: " + str(tree))
    for k, v in info.items():
        print("\t" + k + ": " + str(v))

    return


def get_percentage_unique(tree:ExpressionTree, min_num_binops=1):
    percentage = 0.0
    info_dict = get_term_dict_for_node(tree, min_num_binops)
    total_ops = tree.get_binary_ops_as_list()

    ops_greater_than_size = [x for x in total_ops if x.get_num_binops() >= min_num_binops]

    num_ops_greater_than_size = len(ops_greater_than_size)
    unique_nodes = [x for x in info_dict.keys() if info_dict[x] == 1]


    if num_ops_greater_than_size == 0:
        return 0

    percentage = (len(unique_nodes) / num_ops_greater_than_size) * 100
    return percentage




#sample_expr =  "(x + y) - (x + y)"
#sample_tree = single_expression_to_tree(sample_expr)

#print("Sample expression num ops: " + str(sample_tree.get_num_ops()))
#print("Node dictionary: ")
#info = get_unique_terms_for_node(sample_tree)


#for k, v in info.items():
#    print("\t" + k + ": " + str(v))

#print("Calculated unique node %: " + str(calcPercentUnique(sample_tree)))

