import random
from math import floor
from copy import deepcopy

from src.ExpressionTree import *
from src.general_tools import gen_random_constants, test_equivalent_by_brute_force
from src.LLVMTools import single_expression_to_tree





def check_term_simplifies_via_llvm(node):
    node_str = str(node)
    node_size_by_ops = len(node.get_binary_ops_as_list())

    optimized_tree = single_expression_to_tree(str(node))
    optimized_size_by_ops = len(optimized_tree.get_binary_ops_as_list())

    if node_size_by_ops > optimized_size_by_ops:
        return True

    return False

def add_nodes_to_add_subtree(start_leaf_node, queue):
    # make a generic right-leaning tree from a queue of nodes
    # why right leaning? it's easier than making a balanced tree
    # used to rearrange wide terms

    # if we get a unary op node, this code will fail...
    # should examine this case more carefully, but for now,
    # just search for and find the parent of the unary node
    # repeat until we get a binary op
    # Commented out again because when used for adding to a wide term,
    # sometimes this would cause the addition to occur outside the wide term.
    # We should probably be finding the lowest-most add operation and
    # adding there instead.
    #while (isinstance(start_leaf_node, UnaryOpNode)): #or isinstance(start_leaf_node.parent, UnaryOpNode)):
    #    start_leaf_node = start_leaf_node.parent

    # this code assumes the node to be replaced is the right child.
    # make sure this is the case. This is because this function is used
    # when working with wide addition terms where we want two make
    # two nodes adjacent to each other, and to be sure of where those
    # nodes are.
    if not start_leaf_node.parent is None:
        while (isinstance(start_leaf_node.parent, UnaryOpNode)):
            start_leaf_node = start_leaf_node.parent
        if start_leaf_node.parent.left == start_leaf_node:
            if start_leaf_node.parent.op == Operation.SHR or \
                start_leaf_node.parent.op == Operation.SHL:
                raise Exception("can't add to shift operation")
            tmp = start_leaf_node.parent.right
            start_leaf_node.parent.right = start_leaf_node
            start_leaf_node.parent.left = tmp
    else:
        #... however this function is also used by the const injection
        # and var injection methods which don't care where we are in the tree
        # if this is the case then we might be given the root of the tree,
        # which has no parent, and so the below code will error. In this case,
        # just shift ourselves down to the right child.
        start_leaf_node = start_leaf_node.right

    #root_node = start_leaf_node.parent
    #print("In add_nodes function, start_leaf_node.parent is: " + str(start_leaf_node.parent))

    while len(queue) > 0:
        current_leaf_parent = start_leaf_node.parent
        #print("In loop, leaf_node.parent is: " + str(start_leaf_node.parent))
        #print("original root node is: " + str(root_node))
        newbinop = BinaryOpNode(Operation.ADD, queue.pop(), start_leaf_node, start_leaf_node.parent)
        newbinop.left.parent = newbinop
        newbinop.right.parent = newbinop
        current_leaf_parent.right = newbinop
    return

# last ditch effort to fix issues from the programmatic way
# TD: replace the string equivalency test with proper node equivalence functions
# this will be a problem later
def make_nodes_adjacent_using_llvm(n1:Node, n2:Node, root_wide_term):
    # get string list of all nodes in wide term, minus n1 and n2
    # Note we might have duplicates like y + y. If n1 or n2 is y, then
    # we need to make sure we leave one fewer instance of y in the list.
    # get duplicates, subtract one, append to all_term_strs


    duplicates = [str(s) for s in root_wide_term.same_level_children if str(s) == str(n1) or str(s) == str(n2)]
    # remove gets rid of one instance, not all
    if len(duplicates) > 0:
        # get the string equivalent and compare? need to write node equality function
        n1_str = str(n1)
        n2_str = str(n2)
        if n1_str in duplicates:
            duplicates.remove(n1_str)
        if n2_str in duplicates:
            duplicates.remove(n2_str)


    all_term_strs = [str(s) for s in root_wide_term.same_level_children if not s == n1 and not s == n2]
    all_term_strs += duplicates

    try:
        new_left_child = BinaryOpNode(Operation.ADD, n1, n2, root_wide_term)
        new_right_child = single_expression_to_tree(str.join(" + ", all_term_strs))
    except Exception as e:
        print("Exception in making nodes adjacent with LLVM: " + str(e))
        print("n1: " + str(n1))
        print("n2: " + str(n2))
        print("all term strs: " + str(all_term_strs))
        return None


    root_wide_term.left = new_left_child
    root_wide_term.right = new_right_child.root

    new_right_child.set_parents()
    #print("new wide term tree setup is: " + str(root_wide_term))
    root_wide_term.assemble_wide_terms(None, True)
    return new_left_child


# rearranges the root wide term in place
def make_nodes_adjacent_in_wide_addition_term(n1, n2, root_wide_term):
    print("in adjacent function: given wide term length is: " + str(len(root_wide_term.same_level_children)))
    root_wide_term.assemble_wide_terms(is_main_parent=True)
    print("after assembling wide terms: " + str(len(root_wide_term.same_level_children)))
    print("all wide terms in adjacency function, after assembling: ")
    for x in root_wide_term.same_level_children:
        print("\t" + str(x))

    # 1) make new binop with n1 and n2, set parent to root_wide_term, make left child
    # of root_wide_term

    # do nothing, already set
    if n1.parent == n2.parent:
        return

    if n1 == n2:
        print("given nodes are already adjacent! returning")


    new_binop = BinaryOpNode(Operation.ADD, n1, n2, root_wide_term)
    n1.parent = new_binop
    n2.parent = new_binop
    root_wide_term.left = new_binop

    list_remaining = [x for x in root_wide_term.same_level_children if not x is n1 and not x is n2]

    root_wide_term.right = list_remaining.pop()
    root_wide_term.right.parent = root_wide_term

    # 2) for all remaining terms, ignoring n1 and n2, create new subtree
    # and set to right child of root_wide_term; also set parent to root_wide_term
    add_nodes_to_add_subtree(root_wide_term.right, list_remaining)
    root_wide_term.assemble_wide_terms(None, True)
    return new_binop

def initial_obf_wide_term(wide_term, tree_ref):
    pass

def get_rand_index(list_length):
    return random.randrange(0, list_length)

def get_and_pop_random_from_list(given_list):
    return given_list.pop(random.randrange(len(given_list)))


def obf_two_given_nodes_in_wide_term(n1, n2, wide_term, ruleset):
    make_nodes_adjacent_using_llvm(n1, n2, wide_term)
    ruleset.apply_random_rule(n1.parent)
    return n1.parent

def obf_and_simplify_nodes_in_wide_term(n1, n2, wide_term, ruleset):
    #make_nodes_adjacent_using_llvm(n1, n2, wide_term)
    make_nodes_adjacent_in_wide_addition_term(n1, n2, wide_term)
    ruleset.apply_random_rule(n1.parent)

    optimize_node(n1.parent)

    return n1.parent


def repeat_obf_wide_term(wide_term_index, tree_ref, ruleset):

    # the index is because I designed this very poorly.
    # TD: refactor!!!
    wide_term = do_not_use_get_wide_addition_terms(tree_ref)[wide_term_index]
    print("Starting wide term is: " + str(wide_term))
    target = floor(0.25 * len(wide_term.same_level_children))

    # first, apply some binops against each other, if they have a size of 1(total
    # node size 3).

    sorted_dict = sort_wide_terms_to_dict(wide_term)
    bitwise = sorted_dict[BITWISE]
    single_bitwise = [b for b in bitwise if len(b.get_nodes_as_list()) == 3]

    print("Collected # single_bitwise ops: " + str(len(single_bitwise)))

    target_single_bitwise = floor(0.3 * len(single_bitwise))
    for t in range(target_single_bitwise):
        wide_term = do_not_use_get_wide_addition_terms(tree_ref)[wide_term_index]
        n1 = get_and_pop_random_from_list(single_bitwise)
        n2 = get_and_pop_random_from_list(single_bitwise)
        # simplify/mutate the children individually if possible
        result_parent = obf_two_given_nodes_in_wide_term(n1, n2, wide_term, ruleset)
        result_parent.left = optimize_node(result_parent.left)
        result_parent.right = optimize_node(result_parent.right)
        # note that optimize_node returns a copy, does not modify in place


    for t in range(target):
        wide_term = do_not_use_get_wide_addition_terms(tree_ref)[wide_term_index]
        n1 = get_and_pop_random_from_list(wide_term.same_level_children)
        n2 = get_and_pop_random_from_list(wide_term.same_level_children)
        # simplify/mutate the children individually if possible
        result_parent = obf_two_given_nodes_in_wide_term(n1, n2, wide_term, ruleset)
        result_parent.left = optimize_node(result_parent.left)
        result_parent.right = optimize_node(result_parent.right)
        # note that optimize_node returns a copy, does not modify in place

    print("\n\nRepeated obf on wide term complete, result is: " + str(wide_term))




def inject_consts(node:Node):
    numbers = gen_random_constants()
    nodes_to_add = [ConstNode(x) for x in numbers]
    add_nodes_to_add_subtree(node, nodes_to_add)

    return

def check_contains_different_variables(node1, node2):
    n1_all_nodes = node1.get_nodes_as_list()
    n2_all_nodes = node2.get_nodes_as_list()

    all_node1_varnames = [x.varname for x in n1_all_nodes if isinstance(x, VarNode)]
    all_node2_varnames = [x.varname for x in n2_all_nodes if isinstance(x, VarNode)]

    for x in all_node1_varnames:
        if x not in all_node2_varnames:
            return True

    return False


def inject_vars(varname:str, node_to_add_to):
    new_nodes = [VarNode(varname, use_literal_name=True),
                 UnaryOpNode(Operation.ARITH_NEG, VarNode(varname, use_literal_name=True))]

    add_nodes_to_add_subtree(node_to_add_to, new_nodes)

    return

def do_not_use_get_wide_addition_terms(node:ExpressionTree) -> []:
    # NOTE: THIS FUNCTION ONLY USED BY TESTS
    # NOT USED BY OBF TREE
    # TD: remove this code
    # 'wide' here means greater than two terms.
    # for instance, (x + (d * 2) will return an empty list.
    # (x + 2 + (d * 2) will return a list that contains the BinaryOp node which has the list
    # of assembled terms: x, 2, (d* 2).

    if isinstance(node, Node):
        node.assemble_wide_terms(None, True)
    else:
        node.assemble_wide_terms()

    wide_terms = []

    try:
        binop_list = node.get_binary_ops_as_list()
    except:
        print("Error: couldn't get wide terms for given node: ")
        print(node)
        return []

    for n in binop_list:
        if len(n.same_level_children) > 2 and n.op == Operation.ADD:
            wide_terms.append(n)

    return wide_terms

CONSTS = "consts"
VARS = "vars"
OTHER = "other"
BITWISE = "bitwise"

# note: the obfuscator class is NOT USING THIS FUNCTION ANYMORE
# instead, recalcTermInfo is
def sort_wide_terms_to_dict(node):
    given_terms = node.same_level_children

    sorted_terms_dict = {
        "bitwise" :[],
        "consts":[],
        "vars" :[],
        "other" :[]
    }

    for t in given_terms:
        if isinstance(t, ConstNode):
            sorted_terms_dict[CONSTS].append(t)
        elif isinstance(t, VarNode):
            sorted_terms_dict[VARS].append(t)
        elif isinstance(t, UnaryOpNode):
            if isinstance(t.node, ConstNode):
                # there are more cases than this to check but leaving
                # it for now
                sorted_terms_dict[CONSTS].append(t)
            else:
                sorted_terms_dict[OTHER].append(t)
        elif isinstance(t, BinaryOpNode):
            # brute force the all bitwise check...
            # TD optimize later
            all_bitwise = True
            all_binops_in_node = t.get_binary_ops_as_list()
            for s in all_binops_in_node:
                if isinstance(s, BinaryOpNode):
                    if s.op == Operation.ADD or s.op == Operation.SUB \
                        or s.op == Operation.MUL or s.op == Operation.DIV:
                        all_bitwise = False
            if all_bitwise:
                sorted_terms_dict[BITWISE].append(t)
            else:
                sorted_terms_dict[OTHER].append(t)

    return sorted_terms_dict



# TD: set up the ExpressionTree to include
# a ref to the tree instead of passing it around like this
def check_prep_wide_term(node, tree_ref):
    term_dict = sort_wide_terms_to_dict(node)

    if (len(term_dict[CONSTS]) == 0):
        inject_consts(node)


    if len(term_dict[BITWISE]) == 0 and len(term_dict[VARS]) == 0:
        # randomly select a variable or two to inject
        all_vars_in_tree = tree_ref.all_varnames
        rand_choice = all_vars_in_tree[random.randrange(len(all_vars_in_tree))]
        inject_vars(rand_choice.varname)

    pass


def check_mutates(node):
    # very rudimentary for now. pass through LLVM opts and
    # if the result is smaller, return True.
    startSize = len(node.get_nodes_as_list())
    optNode = single_expression_to_tree(str(node), optimized=True)

    if startSize > len(optNode.get_nodes_as_list()):
        return True

    return False


# Expects two subexpressions of any size which contain entirely bitwise binary operations.
# Simple check: do they share any variables? Or, do they both have constants?
def check_bitwise_nodes_contain_potential_mutators(node1, node2):
    if (isinstance(node1, BinaryOpNode) and not node1.is_bitwise()):
        print("In check_bitwise_nodes_contain_potential_mutators: node 1 is mixed, returning False")
        return False

    if (isinstance(node2, BinaryOpNode) and not node2.is_bitwise()):
        print("In check_bitwise_nodes_contain_potential_mutators: node 2 is mixed, returning False")
        return False

    n1_all_nodes = node1.get_nodes_as_list()
    n2_all_nodes = node2.get_nodes_as_list()
    all_node1_consts = [x for x in n1_all_nodes if isinstance(x, ConstNode)]
    all_node2_consts = [x for x in n2_all_nodes if  isinstance(x, ConstNode)]

    if len(all_node2_consts) > 0 and len(all_node1_consts) > 0: return True

    all_node1_varnames = [x.varname for x in n1_all_nodes if isinstance(x, VarNode)]
    all_node2_varnames = [x.varname for x in n2_all_nodes if isinstance(x, VarNode)]

    for x in all_node1_varnames:
        if x in all_node2_varnames:
            return True

    return False


# returns true if the two given terms do not contain any of the same variables,
# and if only one or neither term both contain constants.
def check_are_terms_disjoint(node1:Node, node2:Node):
    n1_all_nodes = node1.get_nodes_as_list()
    n2_all_nodes = node2.get_nodes_as_list()
    all_node1_consts = [x for x in n1_all_nodes if isinstance(x, ConstNode)]
    all_node2_consts = [x for x in n2_all_nodes if isinstance(x, ConstNode)]
    if len(all_node2_consts) > 0 and len(all_node1_consts) > 0: return False

    all_node1_varnames = [x.varname for x in n1_all_nodes if isinstance(x, VarNode)]
    all_node2_varnames = [x.varname for x in n2_all_nodes if isinstance(x, VarNode)]

    for x in all_node1_varnames:
        if x in all_node2_varnames:
            return False

    return True



def optimize_node(node):
    # some nodes can be simplified to '0' and will break the parsing code.
    # just return the original node in this case.
    try:
        optNode = single_expression_to_tree(str(node), optimized=True).root
    except:
        return node


    return optNode



