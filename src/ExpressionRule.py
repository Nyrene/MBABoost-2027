import random
from copy import deepcopy
from enum import StrEnum
from enum import Enum
from random import randint

#from ExpressionTree import Operation, ExpressionTree, Node, BinaryOpNode, UnaryOpNode
import src.ExpressionTree
from src.ExpressionTree import *
#from general_tools import single_expression_to_tree
from src.LLVMTools import single_expression_to_tree
from src.ExpressionTree import ConstNode

class rule_type(Enum):
    IDENT = 1
    DYN_CONST = 2
    UNKNOWN = 3


# for now, rules are assumed to be binary operators
class ExpressionRule:
    def __init__(self, start="", replacement="", op=Operation.UNKNOWN, vars=None, letter=None):
        self.start = start
        self.replacement = replacement
        self.op = op
        self.vars = vars
        self.times_used = 0
        self.tree = None
        self.replacement_top_level_op = None
        self.hd_letter = letter
        return

    def getExpressionTree(self):
        return single_expression_to_tree(self.replacement)

def apply_rule_to_node(node, expr_rule:ExpressionRule, mod_consts=True):
    # if float consts == True, then when possible, apply the rule so that
    # any constant operands are modified and moved to the outside.
    # for instance, AND and OR bitwise identities apply negation and nots to one operand,
    # and have a resulting form with one operand left standalone on one side of the top-level op.
    # if one operand of the given node is a constant and the rule is for OR/AND, flip the
    # order of the operands so that the constant value ends up standalone.

    if (isinstance(node, ExpressionTree)):
        node = node.root

    if (mod_consts):
        #print("debug: flipping nodes in apply_rule_to_node for op: " + node.op)
        if node.op == Operation.AND:
            #TD: refactor: add a flip_nodes method to the expression tree binary op class
            # constant should be on the left side
            if (isinstance(node.right, ConstNode)):
                tmp = node.left
                node.left = node.right
                node.right = tmp
        if node.op == Operation.OR:
            # constant node should be on the right side
            if (isinstance(node.left, ConstNode)):
                tmp = node.left
                node.left = node.right
                node.right = tmp


    rtree = expr_rule.getExpressionTree()


    if expr_rule.op != node.op:
        print("Trying to apply rule to current node, ops don't match:")
        #print("Rule node is: " + expr_rule.op)
        #print("this node is: " + node.op)
        #print(str(node) + "-> " + str(rtree))
        print("Returning.")
        return

    #print("Debug: in replace rule: node is: " + str(node))
    #print("Debug: in replace rule: node.left is: " + str(node.left))
    #print("Debug: in replace rule: node.right is: " + str(node.right))
    #print("Debug: in replace rule: rule is: " + str(rtree))
    #print("rtree vars are: " + str(expr_rule.vars[0]) + ", " +  str(expr_rule.vars[1]))
    rtree.replace_all_var_insts_with_subtree(expr_rule.vars[0], node.left)
    #print("Debug: rtree after first replacement replacement is: " + str(rtree))
    rtree.replace_all_var_insts_with_subtree(expr_rule.vars[1], node.right)
    #print("Debug: rtree after second replacement is replacement is: " + str(rtree))

    node.old = deepcopy(node)
    node.op = rtree.root.op
    node.left = rtree.root.left
    node.right = rtree.root.right

    all_nodes = node.get_nodes_as_list()
    for n in all_nodes:
        n.inc_obf_level()
    return


class Ruleset():
    def __init__(self):
        self.rules = []
        self.rules_by_letter = {}
        self.rules_by_op = {Operation.ADD: [],
                            Operation.SUB: [],
                            Operation.MUL: [],
                            Operation.XOR: [],
                            Operation.AND: [],
                            Operation.OR: [],
                            Operation.DIV: [],
                            Operation.B_NEGATE: [],
                            Operation.ARITH_NEG: []
                            }
        self.init_mba_identities()

        return

    def clear_rule_info(self):
        for r in self.rules:
            r.times_used = 0

    def apply_random_rule(self, node):
        cur_node = node
        while (isinstance(cur_node, UnaryOpNode)):
            cur_node = cur_node.node

        node = cur_node

        #if not isinstance(node, ExpressionTree.BinaryOpNode):
        #    print("Error: apply_random_rule: given node is not a binary operation")
        #    print("Given node is: " + str(node))
        #    print("Type is: " + type(node).__name__)
        #    print("returning")
        #    return

        op_type = node.op
        try:
            all_rules_op = self.rules_by_op[op_type]
        except:
            print("No rules available for op: " + op_type + ", skipping.")

            return

        #apply_rule_to_node(node, random_selection)
        try:
            random_selection = all_rules_op[random.randrange(len(all_rules_op))]
            apply_rule_to_node(node, random_selection)
        except Exception as e:
            print("Couldn't apply rule to node: " + str(node))
            print(str(e))

    def get_rule_for_letter(self, letter):
        return self.rules_by_letter[letter]

    def get_random_rule_for_op(self, operation):
        rules_for_op = self.rules_by_op[operation]
        return rules_for_op[random.randrange(len(rules_for_op))]

    def __str__(self):
        retStr = ""

        for op in self.rules_by_op.keys():
            for r in self.rules_by_op[op]:
                retStr += ("\nRule(" + op + "): " + r.replacement + "Times used: " + str(r.times_used))

        return retStr

    def init_mba_identities(self):
        # sub
        self.rules.append(ExpressionRule("a - b", "(a ^ b) - 2 * (~a & b)", Operation.SUB, ["a", "b"], "k"))
        self.rules.append(ExpressionRule("a - b", "(a & ~b) - (~a & b)", Operation.SUB, ["a", "b"], "l"))
        #self.rules.append(ExpressionRule("a - b", "a + ~b + 1", Operation.SUB, ["a", "b"]))
        #self.rules.append(ExpressionRule("a - b", "2*(a & ~b) - (a ^ b)", Operation.SUB, ["a", "b"], "m"))
        self.rules.append(ExpressionRule("a - b", "(a & ~b) + (a & ~b) + -(a ^ b)", Operation.SUB, ["a", "b"], "m"))

        # add
        #self.rules.append(ExpressionRule("a + b", "a - ~b - 1", Operation.ADD, ["a", "b"]))
        # expanding 2* into term + term
        #originals
        #self.rules.append(ExpressionRule("a + b", "(a ^ b) + 2 *((a & b))", Operation.ADD, ["a", "b"], "g"))
        # self.rules.append(ExpressionRule("a + b", "2 * (a | b) + -(a ^ b)", Operation.ADD, ["a", "b"], "i"))
        # expanded:
        self.rules.append(ExpressionRule("a + b", "(a | b) + (a | b) + -(a ^ b)", Operation.ADD, ["a", "b"], "i"))

        self.rules.append(ExpressionRule("a + b", "(a ^ b) + (a & b) + (a & b)", Operation.ADD, ["a", "b"], "g"))
        self.rules.append(ExpressionRule("a + b", "(a | b) + (a & b)", Operation.ADD, ["a", "b"], "h"))

        #self.rules.append(ExpressionRule( "a + b", "(x + y) ^ 107 ^ 73 ^ 34", Operation.ADD, ["a", "b"]))
        # xor
        self.rules.append(ExpressionRule("a ^ b", "(a | b) + -(a & b)", Operation.XOR, ["a", "b"]))
        #self.rules.append(ExpressionRule("a ^ b", "(a ^ 75 ^ b ^ 75)", Operation.XOR, ["a", "b"]))

        # or
        self.rules.append(ExpressionRule("a | b", "(a & ~b) + b", Operation.OR, ["a", "b"], "u"))


        # and
        self.rules.append(ExpressionRule("a & b", "(~a | b) + a + 1", Operation.AND, ["a", "b"], "v"))
        #self.rules.append(ExpressionRule("a & b", "(a & b) ^ (a) ^ (a)", Operation.AND, ["a", "b"]))
        #self.rules.append(ExpressionRule("a & b", "(a & b) ^ 20 ^ 20", Operation.AND, ["a", "b"]))
        #self.rules.append(ExpressionRule("a & b", "(a & b) ^ 73 ^ 73", Operation.AND, ["a", "b"]))

        # dynamic rulesets: to be applied to any given pattern
        # how do we define the starting rule considering it's operation agnostic?
        # (is it operation agnostic?)

        # set up rules by op
        for r in self.rules:
            self.rules_by_op[r.op].append(r)

        for r in self.rules:
            self.rules_by_letter[r.hd_letter] = r

