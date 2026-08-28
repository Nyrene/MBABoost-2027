from enum import StrEnum
from enum import Enum
from copy import deepcopy




space = " "
class Operation(StrEnum):
    XOR = '^'
    SHL = '<<'
    SHR = '>>'
    ARITH_NEG = '-'
    SUB = '-'
    ADD = '+'
    MUL = '*'
    DIV = '/'
    OR = '|'
    B_NEGATE = '~'
    AND = '&'
    UNKNOWN = '#'

class Attributes(Enum):
    UNKNOWN = 0

arith_ops = [Operation.ARITH_NEG, Operation.ADD, Operation.SUB, Operation.DIV, Operation.MUL]
bitwise_ops = [Operation.OR, Operation.AND, Operation.XOR, Operation.SHL, Operation.SHR, Operation.B_NEGATE]

def is_alternated(node1, node2):
    if (isinstance(node1, ConstNode) or isinstance(node1, VarNode)):
        return False

    if (isinstance(node2, ConstNode) or isinstance(node2, VarNode)):
        return False

    if node1.op in arith_ops and node2.op in bitwise_ops:
        return True

    if node2.op in arith_ops and node1.op in bitwise_ops:
        return True

    return False


class Node:
    # arithmetic, bitwise traits
   def __init__(self):
       self.parent = None
       self.old = None # currently unused
       self.obf_level = 0


   def try_bitwise_distribute(self):
        return False

   def try_arith_distribute(self):
        return False

   def try_distribute(self):
       return False

   def set_parents(self, parent=None):
       return

   def get_alternation(self):
       return 0

   def convert_subs_to_adds(self):
       return

   def is_terminal(self):
       return False

   def fold_consts(self) -> bool:
        return False

   def is_bitwise(self) ->bool:
        return False

   def get_num_binops(self) -> int:
        return 0

   def get_size(self) -> int:
        return 1

   def get_alternation(self):
        return 0

   def get_miasm_str(self):
       return

   def is_leaf(self):
       return None

   def inc_obf_level(self):
       self.obf_level += 1

   def assemble_wide_terms(self, parent_op, is_main_parent=False):
        return []

   def __str__(self):
       print("Str method on base Node class called")

   def indented_str(self):
       return ""

   def get_binary_ops_as_list(self):
       return []

   def contains(self, node):
        return False

   def get_num_ops(self):
       return 0

   def gen_dotvis(self):
       print("gen_dotviz on base node class called")
       return ""


   def __eq__(self, other):
       # not sure what to do here for the base class
       return False

   def replace_all_var_insts_with_subtree(self, varname, replacement):
       return

   def get_nodes_as_list(self):
       pass


class ConstNode(Node):
    def __init__(self, new_val: int, parent=None):
        super().__init__()
        self.value = int(new_val)
        self.parent=parent

    def fold_consts(self) -> bool:
        return False

    def is_bitwise(self) ->bool:
        return True

    def set_parents(self, parent=None):
        self.parent = parent
        return

    def __str__(self):
        return str(self.value)

    def is_terminal(self):
        return True

    def contains(self, node):
        return (node == self or node == self.value)

    def get_miasm_str(self):
        # ExprInt(0x1, size)
        return "ExprInt(" + str(self.value) + ", size)"

    def indented_str(self, indent, current_indent):
        return "\n" + "\t"*current_indent + "\t" + str(self.value), indent, 0

    def get_num_ops(self):
        return 0

    def get_num_binops(self) -> int:
        return 0

    def get_size(self) -> int:
        return 1

    def get_alternation(self):
        return 0

    def gen_dotvis(self):
        return str(self.value)

    def __eq__(self, other):
        try:
            return self.value == other.value
        except (Exception,):
            return False

    def get_nodes_as_list(self):
        return [self]

    def is_leaf(self):
        return True

    def replace_all_var_insts_with_subtree(self, varname, replacement):
        # constant, nothing to be done
        return

    def assemble_wide_terms(self, parent_op, is_main_parent=False):
        return [self]

class VarNode(Node):
    # for storing parameters
    def __init__(self, new_varname: str, parent=None, use_literal_name=False):
        super().__init__()
        self.varname = new_varname

        self.parent=parent

        if ExpressionTree.swap_param_for_vars and not use_literal_name:
            self.varname = new_varname.strip("%")
            self.varname = "param" + self.varname
            match self.varname:
                case "param0":
                    self.varname = "x"
                case "param1":
                    self.varname = "y"
                case "param2":
                    self.varname = "z"
                case "param3":
                    self.varname = "a"
                case "param4":
                    self.varname = "b"
                case "param5":
                    self.varname = "c"
                case "param6":
                    self.varname = "d"
                case "param7":
                    self.varname = "e"
                case "param8":
                    self.varname = "f"
                case "param9":
                    self.varname = "g"
                case "param10":
                    self.varname = "h"
                case "param11":
                    self.varname = "t"


    def is_bitwise(self) ->bool:
        return True

    def __str__(self):
        return str(self.varname)

    def contains(self, node):
        return (self == node or node == self.varname)

    def fold_consts(self) -> bool:
        return False

    def is_terminal(self):
        return True

    def convert_subs_to_adds(self):
        return

    def set_parents(self, parent=None):
        self.parent = parent
        return

    def assemble_wide_terms(self, parent_op, is_main_parent=False):
        return [self]

    def get_miasm_str(self):
        return str(self.varname)

    def indented_str(self, indent, current_indent):
        return "\n" + "\t"*current_indent + "\t" + str(self.varname), indent, 0

    def get_num_ops(self):
        return 0

    def gen_dotvis(self):
        return self.varname

    def __eq__(self, other):
        try:
            return self.varname == other.varname
        except (Exception,):
            return False

    def is_leaf(self):
        return True

    def get_nodes_as_list(self):
        return [self]

    def replace_all_var_insts_with_subtree(self, varname, replacement):
        if varname == self.varname:
            print("Error: cannot replace node from inside varname")
        return

class UnaryOpNode(Node):
    def __init__(self, op, node, parent=None):
        # op can be a string or an enum instance.
        super().__init__()
        self.parent=parent

        if (not isinstance(node, Node)):
            print("Error: Item given to UnaryOpNode is not Node object")
            exit(0)

        if op != "~" and op != "-" and op != Operation.arith_neg and op != Operation.b_negate:
            print("Error: invalid unary operation: " + str(op))
            exit(0)

        self.op = op
        """try:
            self.op = Operation[op]
            #print(Operation(op))
        except Exception as e:
            print(e)
            self.op = op
        #finally:
        #    print("Couldn't init UnaryOp with given operation: " + str(op))
"""
        self.node = node

    def __str__(self):
        return self.op + str(self.node)

    def contains(self, node):
        if (node == self):
            return True
        else:
            return self.node.contains(node)

    def get_terminal_node(self):
        # for cases like "-3" and "~-~f":
        # assumes that is_terminal has already been called elsewhere
        # to ensure this is actually a terminal node and not something like
        # "~-(f + a). If not, throw exception
        if not self.is_terminal():
            raise ValueError("Error getting most terminal unary node: not terminal: " + str(self))

        current_node = self.node
        while isinstance(current_node, UnaryOpNode):
            current_node = current_node.node

        return current_node

    def is_terminal(self):
        # if node, or node's node is a leaf node, then return true
        # try to catch cases like -~3, etc
        return self.node.is_terminal()

    def set_parents(self, parent=None):
        self.parent = parent
        self.node.set_parents(self)
        return

    def is_bitwise(self):
        if self.op == Operation.SUB:
            # special case. with a simple SUB check, this makes things like (-x | 3) return false, as the negation
            # prevents distribution.
            # However, sometimes we might have terms that we can actually distribute across each other after obfuscating,
            # like (-x | 3) & (-x | y), and so we want to include these terms in our bitwise collection.
            # This check will return these terms, but will not return eg -(z | 57), which we explicitly do not want.
            if self.is_terminal():
                return True
            return False
        else:
            return self.node.is_bitwise()

    def convert_subs_to_adds(self):
        self.node.convert_subs_to_adds()
        return

    def assemble_wide_terms(self, parent_op, is_main_parent=False):
        # assemble possible wide terms from this node as well
        self.node.assemble_wide_terms(parent_op, True)
        return [self]

    def fold_consts(self) -> bool:
        return self.node.fold_consts()

    def get_miasm_str(self):
        return self.op + self.node.get_miasm_str()

    def is_leaf(self):
        return False

    def indented_str(self, indent, current_indent):
        return "\n" + "\t"*current_indent + "\t" + str(self.op + str(self.node))

    def get_num_ops(self):
        return 1 + self.node.get_num_ops()

    def get_num_binops(self) -> int:
        return self.node.get_num_binops()

    def get_size(self) -> int:
        return 1 + self.node.get_size()

    def get_alternation(self):
        # count unlike edges
        if not (isinstance(self.node, ConstNode) or isinstance(self.node, VarNode)):
            if is_alternated(self, self.node):
                return 1 + self.node.get_alternation()
            else:
                return self.node.get_alternation()
        return 0

    def replace_all_var_insts_with_subtree(self, varname, replacement):
        try:
            if self.node.varname == varname:
                self.node = deepcopy(replacement)
                self.node.set_parents(self)
            else:
                self.node.replace_all_var_insts_with_subtree(varname, replacement)
        except (Exception,):
            self.node.replace_all_var_insts_with_subtree(varname, replacement)
            return

        return

    def get_nodes_as_list(self):
        #if self.is_terminal():
        #    return [self]
        return self.node.get_nodes_as_list()

    def get_binary_ops_as_list(self):
        return self.node.get_binary_ops_as_list()

    def gen_dotvis(self):
        #x2[label = "|"];
        #labels = []
        #defs = []

        #opLabel =

       # return "id" + str(id(self))
        pass

    def __eq__(self, other):
        try:
            return (self.node == other.node) and (self.op == other.op)
        except (Exception,):
            return False


class BinaryOpNode(Node):
    def __init__(self, op, left: Node, right: Node, parent=None):
        super().__init__()
        self.op = "error"
        self.same_level_children = [] # all children which are associative and commutative
                                    # with this node
        self.parent=parent

        if not isinstance(left, Node):
            print("Error: left hand given to BinaryOpNode is not Node type")
            print(str(left))
            exit(0)

        if not isinstance(right, Node):
            print("Error: right hand given to BinaryOpNode is not Node type")
            print(str(right))
            exit(0)

        try:
            self.op = Operation(op)
        except:
            print("Couldn't init BinaryOp with given operation: " + str(op))

        self.left = left
        self.right = right

    def is_terminal(self):
        return False


    def is_bitwise(self):
        if self.op == Operation.AND or self.op == Operation.OR or self.op == Operation.XOR:
            return self.left.is_bitwise() and self.right.is_bitwise()

        return False

    def contains(self, node):
        if (node == self):
            return True

        return (self.left.contains(node) or self.right.contains(node))

    def convert_subs_to_adds(self):
        if self.op == Operation.SUB:
            self.right = UnaryOpNode(Operation.ARITH_NEG, self.right, self)
            self.right.node.parent = self.right
            self.op = Operation.ADD

        self.left.convert_subs_to_adds()
        self.right.convert_subs_to_adds()

        return

    def set_parents(self, parent=None):
        self.parent = parent
        self.left.set_parents(self)
        self.right.set_parents(self)
        return

    def eval_consts(self):
        if (isinstance(self.left, ConstNode)) and (isinstance(self.right, ConstNode)):
            return eval(str(self.left) + " " + str(self.op) + " " + str(self.right))
        return None


    def assemble_wide_terms(self, parent_op=None, is_main_parent=False):
        if self.op != Operation.ADD:
            # if it's not an addition operation, return self. Before doing so, continue the search for
            # other possibly nested wide terms.
            self.left.assemble_wide_terms(None, True)
            self.right.assemble_wide_terms(None, True)
            return [self]
        else:
            if is_main_parent:
                # this node is the main owner of wide terms on this level
                self.same_level_children = self.left.assemble_wide_terms(None, False) + \
                                           self.right.assemble_wide_terms(None, False)
            else:
                # return all following addition terms as their own instances
                return self.left.assemble_wide_terms(None, False) + \
                                           self.right.assemble_wide_terms(None, False)
        return



    def fold_consts(self) -> bool:
        if isinstance(self.right, BinaryOpNode):
            if isinstance(self.right.right, ConstNode) and isinstance(self.right.left, ConstNode):
                n = ConstNode(self.right.eval_consts())
                self.right = n
                return True
            else:
                return self.right.fold_consts()

        if isinstance(self.left, BinaryOpNode):
            if isinstance(self.left.right, ConstNode) and isinstance(self.left.left, ConstNode):
                n = ConstNode(self.left.eval_consts())
                self.left = n
                return True
            else:
                return self.left.fold_consts()


        return False


    def try_bitwise_distribute(self):
        if self.op == Operation.AND and isinstance(self.right, BinaryOpNode):
            if self.right.op == Operation.OR:
                self.op = Operation.OR
                tmpLeft = self.left
                self.left = BinaryOpNode(Operation.AND, tmpLeft, self.right.left)
                self.right = BinaryOpNode( Operation.AND, tmpLeft, self.right.right)
                return True

        if self.op == Operation.OR and isinstance(self.right, BinaryOpNode):
            if self.right.op == Operation.AND:
                self.op = Operation.AND
                tmpLeft = self.left
                self.left = BinaryOpNode(Operation.OR, tmpLeft, self.right.left)
                self.right = BinaryOpNode( Operation.OR, tmpLeft, self.right.right)
                return True
        return False

    def is_leaf(self):
        return False

    def try_arith_distribute(self):
        if self.op == Operation.MUL and isinstance(self.right, BinaryOpNode):
            if self.right.op == Operation.ADD or self.right.op == Operation.SUB:
                self.op = self.right.op
                tmpLeft = self.left
                self.left = BinaryOpNode(Operation.MUL, tmpLeft, self.right.left)
                self.right = BinaryOpNode( Operation.MUL, tmpLeft, self.right.right)
                return True

        return False

    def try_distribute(self):
        res1 = self.try_arith_distribute()
        res2 = self.try_bitwise_distribute()

        return res1 or res2



    def get_nodes_as_list(self):
        return [self] + self.left.get_nodes_as_list() + self.right.get_nodes_as_list()

    def get_binary_ops_as_list(self):
        return [self] + self.left.get_binary_ops_as_list() + self.right.get_binary_ops_as_list()

    def __str__(self):
        return "( " + str(self.left) + space + self.op + space + str(self.right) + " )"

    def indented_str(self, indent, current_indent):
        return "\n" + "\t"*current_indent + "\t" + str("( " + str(self.left.indented_str(indent, current_indent+1)) + space + self.op + space + str(self.rightindented_str(indent, current_indent+1)) + " )")

    def get_miasm_str(self):
        return "( " + self.left.get_miasm_str() + space + self.op + space + self.right.get_miasm_str() + " )"

    def get_num_ops(self):
        return 1 + self.left.get_num_ops() + self.right.get_num_ops()

    def get_num_binops(self) -> int:
        return 1 + self.left.get_num_binops() + self.right.get_num_binops()

    def get_size(self) -> int:
        return self.left.get_size() + self.right.get_size() + 1

    def get_alternation(self):
        alternation = 0
        if is_alternated(self, self.left):
            alternation += 1
        if is_alternated(self, self.right):
            alternation += 1

        return alternation + self.left.get_alternation() + self.right.get_alternation()

    def gen_dotvis(self):
        pass

    def __eq__(self, other):
        try:
            return (self.op == other.op) and (self.left == other.left) and (self.right == other.right)
        except (Exception,):
            return False


    def replace_all_var_insts_with_subtree(self, varname, replacement):
        try:
            if self.left.varname == varname:
                self.left = deepcopy(replacement)
                self.left.set_parents(self)
        except:
            self.left.replace_all_var_insts_with_subtree(varname, replacement)

        try:
            if self.right.varname == varname:
                self.right = deepcopy(replacement)
                self.right.set_parents(self)
        except:
            self.right.replace_all_var_insts_with_subtree(varname, replacement)
        return

class ExpressionTree:
    # class vars declared here
    swap_param_for_vars = True

    def  __init__(self, new_root:Node):
        self.root = new_root
        all_ops = new_root.get_nodes_as_list()
        self.all_varnames = []
        self.all_varnames = [str(x) for x in all_ops if isinstance(x, VarNode)]
        self.all_varnames = list(set(self.all_varnames))
        new_root.set_parents()
        return

    def convert_subs_to_adds(self):
        self.root.convert_subs_to_adds()
        return



    def collect_all_varname_literals(self):
        nodes = self.get_binary_ops_as_list()
        self.all_varnames = [x.varname for x in nodes if isinstance(x, VarNode)]
        return

    def set_parents(self):
        self.root.set_parents(None)
        return

    def is_terminal(self):
        return self.root.is_terminal()

    def is_leaf(self):
        return self.root.is_leaf()

    def fold_consts(self) -> bool:
        return self.root.fold_consts()

    def contains(self, node):
        return self.root.contains(node)

    def __str__(self):
       root_str = str(self.root)
       # try compressing the spaces somewhat...
       root_str = root_str.replace(" ( ", "(")
       root_str = root_str.replace(" ) ", ")")
       return root_str
       #return str(self.root)

    def indented_str(self, indent, current_indent):
        return str(self.root), indent, 0

    def __eq__(self, other):
        if isinstance(other, ExpressionTree):
            return self.root == other.root
        elif isinstance(other, Node):
            return self.root == other
        else:
            return False

    def assemble_wide_terms(self):
        bin_ops = self.get_binary_ops_as_list()
        for b in bin_ops:
            b.same_level_children = []

        if not self.root == None:
            self.root.assemble_wide_terms(None, True)
        return

    # for rule replacements, for instance: x + y transforms to x & y | 2 (fake example)
    # first the rule candidate (the right handside of the transformation) needs to have
    # whatever is being substituted for x and y
    # then the tree to which the rule is being applied will have its operation replaced
    # with the new replacement (not in this function)
    def replace_all_var_insts_with_subtree(self, target_varname, replacement):
        #if self.root.eq
        if isinstance(self.root, VarNode) and self.root.varname == target_varname:
            self.root = deepcopy(replacement)
        else:
            self.root.replace_all_var_insts_with_subtree(target_varname, replacement)
        return

    #def applyRule(self, op, ):

    def try_distribute(self):
        res1 = self.root.try_bitwise_distribute()
        res2 = self.root.try_arith_distribute()

        return (res1 or res2)


    def get_num_ops(self):
       return (self.root.get_num_ops())

    def get_num_binops(self):
        return self.root.get_num_binops()

    # defined by all binary, unary op nodes, and terminals
    def get_size(self) -> int:
        return self.root.get_size()
    # returns number of binary, unary nodes whose parents are different op type
    def get_alternation(self) -> int:
        return self.root.get_alternation()

    def gen_dotvis(self):
       pass
    def deepCopy(self):
        return ExpressionTree(deepcopy(self.root))

    def get_nodes_as_list(self):
        return self.root.get_nodes_as_list()

    def get_binary_ops_as_list(self):
        return self.root.get_binary_ops_as_list()

    def get_miasm_str(self):
        return self.root.get_miasm_str()



