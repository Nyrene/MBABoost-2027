
from math import ceil
from random import shuffle

from src.ExpressionRule import *
from src.ExtraTreeFunctions import *
from src.EvalFunctions import get_duplicates_dict_for_node
from src.gen_mba_trait_info import print_traits_for_node


ruleset = Ruleset()

# Info for refactoring later:
# Not used/needed from ExtraTreeFunctions:
#   get_wide_addition_terms()

# currently left in ExtraTreeFunctions:
#   check_mutates() # probably could be renamed to check_simplifies()
#   check_bitwise_nodes_contain_potential_mutators()
#   check_are_terms_disjoint()
#   optimize_node

class WideTerm:
    def __init__(self, node: BinaryOpNode, tree_ref:ExpressionTree, obfuscator_ref):
        self.node_ref = node
        self.tree_ref = tree_ref
        self.obfuscator_ref = obfuscator_ref
        self.all_same_level_terms = []
        self.constant_children = []
        self.variable_children = []
        self.other_children = []
        self.bitwise_children = []
        self.terminal_children = []
        self.single_op_bitwise_constant = []

        self.contains_injected_constants = False
        self.contains_injected_vars = False

        # set up info
        self.recalc_term_info()

    def debug_print_children_by_type(self):
        print("Printing wide term children for term: " + str(self.node_ref))

        print("All terms: (total number: " + (str(len(self.all_same_level_terms))) + ")")
        for x in self.all_same_level_terms:
            print(" ,", str(x), end="")

        print("\nother children(" + str(len(self.other_children)) + "): ")
        for x in self.other_children:
            print("\t" + str(x))

        print("bitwise binary ops(" + str(len(self.bitwise_children)) + "): ")
        for x in self.bitwise_children:
            print("\t" + str(x))

        print("op with constant LH or RH(" + str(len(self.single_op_bitwise_constant)) + "): ")
        for x in self.single_op_bitwise_constant:
            print("\t" + str(x))

        print("constants(" + str(len(self.constant_children)) + "): ")
        for x in self.constant_children:
            print("\t" + str(x))

        print("variable children:(" + str(len(self.variable_children)) + "): ")
        for x in self.variable_children:
            print("\t" + str(x))

        print("terminals(overlaps with consts, vars(" + str(len(self.terminal_children)) + "): ")
        for x in self.terminal_children:
            print("\t" + str(x))

        print("Done printing wide children terms by type")

        return

    # returns true, or the variable names that the wide term does not have
    # so if eg there are vars x, y, z, in the entire tree, but this subtree
    # only contains x and y, then this function will return [z]
    def get_inverse_intersection_tree_variables(self):
        all_varnames = self.tree_ref.all_varnames

        # get these from same level children vars, not all nodes,
        # otherwise unuseable nodes like ((x & y) * 7) will exclude things

        #all_nodes = self.node_ref.get_nodes_as_list()
        all_nodes = self.variable_children
        local_varnames = [str(x) for x in all_nodes if (isinstance(x, VarNode))]
        missing_varnames = list(set(local_varnames) ^ set(all_varnames))

        return missing_varnames

    def recalc_term_info(self):
        self.node_ref.assemble_wide_terms(None, is_main_parent=True)
        #self.node_ref.convert_subs_to_adds()
        #print("node ref is: " + str(self.node_ref))
        self.all_same_level_terms = self.node_ref.same_level_children
        self.constant_children = []
        self.variable_children = []
        self.other_children = []
        self.bitwise_children = []
        self.terminal_children = []
        self.single_op_bitwise_constant = []
        # no longer using the extra tree tools function - sorting here instead
        for c in self.all_same_level_terms:
            if c.is_terminal():
                self.terminal_children.append(c)
                this_terminal = c
                if isinstance(c, UnaryOpNode):
                    this_terminal = c.get_terminal_node()
                # logic here: if c is a unary, check what the
                # associated node's type is. APPEND C STILL because
                # we want to add eg "~-3" and not just "3".
                # if it's not a unary node, this_terminal just equals the node.
                if (isinstance(this_terminal, VarNode)):
                    self.variable_children.append(c)
                if (isinstance(this_terminal, ConstNode)):
                     self.constant_children.append(c)

            # bitwise or other:
            if c.is_bitwise() and isinstance(c, BinaryOpNode):
                self.bitwise_children.append(c)
                try:
                    if (isinstance(c.left, ConstNode) or isinstance(c.right, ConstNode)):
                        self.single_op_bitwise_constant.append(c)
                except:
                    pass
            if isinstance(c, BinaryOpNode) and not c.is_bitwise():
                self.other_children.append(c)

            if isinstance(c, UnaryOpNode) and not c.is_terminal() and not c.is_bitwise():
                self.other_children.append(c)

    def __str__(self):
        return "Wide term object: " + str(self.node_ref)

    def print_stats(self):
        print("Printing stats for wide term: " + str(self.node_ref))
        # calculate info:
        # no. terms
        print("\tTotal number of terms: " + str(len(self.node_ref.same_level_children)))
        # % single bitwise terms
        print("all terms: ")
        for t in self.all_same_level_terms:
            print(str(t))

        print("\t Number of single bitwise terms: " + "XXXXX")
        # % children which only contain one variable
        print("\t Number of SLCs which contain one variable: " + "XXXXX")
        # % children which contain two variables
        print("\t Number of SLCs which contain two variables or more: " + "XXXXX")
        # % children larger than 1 binary operation, total
        print("\t Number of SLCs larger than one binary operation: " + "XXXXX")
        # % children larger than 2 binary operations, total
        print("\t Number of SLCs larger than 2 binary operations: " + "XXXXX")
        # number unique constants, number duplicate constants
        print("\t Number of unique constants / Number of duplicate constants: " + "XXXXX")
        return

    def get_num_children_with_gtx_variables(self, no_variables=1, total_expression_variables=None):
        # get the number of children with greater than a given number of variables. If total
        # vars given, print those too.
        pass

    def get_num_children_with_x_variables(self, no_variables=1, total_expression_variables=None):
        # get the number of children with exactly X variables. If total vars given, print
        # those too.
        pass




    # counts binary ops, does not count unary ops
    # eg don't mistakenly count ~-e as two ops, count it as one
    def get_avg_child_size(self):
        count = 0
        running_total = 0.0

        for x in self.all_same_level_terms:
            count += 1
            if x.is_terminal():
                running_total += 1
            else:
                all_ops_in_child = x.get_nodes_as_list()
                for n in all_ops_in_child:
                    if n.is_terminal():
                        running_total += 1

        return running_total / count


    def apply_seed_round(self):
        print("Start of seed round")
        self.tree_ref.set_parents()
        if not test_equivalent_by_brute_force(self.obfuscator_ref.get_obf_expr_str(),
                                              self.obfuscator_ref.original_ground_truth_str):
            print("False case")
            raise Exception("False equivalence check")
        #queue1 = []
        #queue2 = []
        #queue1 += (self.constant_children)
        #queue2 += (self.variable_children)

        #for b in self.bitwise_children[0:floor(len(self.bitwise_children) / 2)]:
        #    if b.get_num_ops() < 4:
                #print("\t\tIn seed round, appending bitwise op: " + str(b))
        #        queue1.append(b)

        #for b in self.bitwise_children[floor(len(self.bitwise_children) / 2):]:
        #    if b.get_num_ops() < 4:
                #print("\t\tIn seed round, appending bitwise op: " + str(b))
        #        queue2.append(b)

        #print("\nQueue 1 is: \n\t")
        #for q in queue1:
            #print(", " + str(q), end="")

        #print("\nQueue 2 is: \n\t")
        #for q in queue2:
            #print(", " + str(q), end = "")
        #print("\n")

        #### applying the obfuscation
        # stop breaking the rule of modifying an iterable while we're going through it...
        # especially because our LLVM function will optimize some of the wide term
        # which can impact the surrounding terms
        # although it's more work, recalculate and re-select the terms to obfuscate as we go

        continue_obf = False
        if (len(self.terminal_children) > 2):
            continue_obf = True
        else:
            if self.variable_children and not self.constant_children:
                print("injecting consts to : " + str(self.variable_children[0]) + ", parent is: " + str(self.variable_children[0].parent))
                inject_consts(self.variable_children[0])
                ruleset.apply_random_rule(self.variable_children[0].parent)
            self.recalc_term_info()
            print("After seed round inject consts")
            if not test_equivalent_by_brute_force(self.obfuscator_ref.get_obf_expr_str(),
                                                  self.obfuscator_ref.original_ground_truth_str, exit_on_false=False):
                print("False case")
                raise Exception("False equivalence check")
            continue_obf = True
        # sometimes that doesn't work so try again
        if self.bitwise_children and len(self.all_same_level_terms) < 5:
            inject_consts(self.bitwise_children[0])
            ruleset.apply_random_rule(self.bitwise_children[0].parent)
            self.recalc_term_info()

        print("After seed round inject consts")
        if not test_equivalent_by_brute_force(self.obfuscator_ref.get_obf_expr_str(),
                                              self.obfuscator_ref.original_ground_truth_str, exit_on_false=False):
            raise Exception("False equivalence check")



        #while len(self.terminal_children) > 2:f
        max_attempts = 5
        cur_attempts = 0

        while continue_obf and cur_attempts < max_attempts:
            self.tree_ref.set_parents()
            self.recalc_term_info()
            print("In seed round loop")
            # try to pair constants and terminals. Leave one constant out.
            # If none, then try to pair terminals and single bitwise ops.
            cur_attempts += 1
            n1 = None
            n2 = None

            if self.variable_children:
                shuffle(self.variable_children)
                n1 = self.variable_children.pop()
                if self.constant_children:
                    shuffle(self.constant_children)
                    n2 = self.constant_children.pop()
                else:
                    if self.bitwise_children:
                        shuffle(self.bitwise_children)
                        n2 = self.bitwise_children.pop()
            elif self.constant_children:
                n1 = self.constant_children.pop()
                if self.bitwise_children:
                    shuffle(self.bitwise_children)
                    n2 = self.bitwise_children.pop()

            if n1 and n2:
                print("String before seed round obf: " + str(self) )
                print("Selected nodes: " + str(n1) + ", " + str(n2))
                try:
                    new_parent_op = make_nodes_adjacent_using_llvm(n1, n2, self.node_ref)
                    if new_parent_op == None:
                        continue
                    print("After making adjacent: " + str(self.node_ref))
                    if not test_equivalent_by_brute_force(self.obfuscator_ref.get_obf_expr_str(),
                                                          self.obfuscator_ref.original_ground_truth_str, exit_on_false=False):
                        raise Exception("False equivalence check")
                    ruleset.apply_random_rule(new_parent_op)
                except:
                    pass
                    #print("Couldn't make nodes adjacent. Obf'ing neighbor if we have const and var selected.")
                    #if (isinstance(n1, VarNode) and isinstance(n2, ConstNode)):
                    #    print("Obfuscating and continuing.")
                    #    ruleset.apply_random_rule(n1.parent)


                #print("After making adjacent: " + str(self.node_ref))

                #print("Testing equivalence: ")
                #test_equivalent_by_brute_force(str(self.tree_ref), (self.obfuscator_ref.ground_truth_str), True)
                #print("After applying rule: " + str(self.node_ref))
                #print("Testing equivalence: ")
                #test_equivalent_by_brute_force(str(self.tree_ref), (self.obfuscator_ref.ground_truth_str), True)
                #print("Before recalc term info: " + str(self.node_ref))
                #self.recalc_term_info()
                #print("after recalc term info: wide term inside seed round: " + str(self.node_ref))
                #print("tree inside seed round: " + str(self.tree_ref))
                #print("wide term after seed round obf: " + str(self))
                #if not test_equivalent_by_brute_force(self.obfuscator_ref.get_obf_expr_str(), self.obfuscator_ref.original_ground_truth_str):
                #    print("False case")

            if not len(self.terminal_children) > 2:
                continue_obf = False
        #self.node_ref.try_distribute()
        self.recalc_term_info()
        attempts = ceil(len(self.bitwise_children) / 3)
        for i in range(0, attempts):
            ruleset.apply_random_rule(self.bitwise_children[i])

        self.tree_ref.try_distribute()
        return

    def apply_diversify_round(self, percentage=100):
        # percentage applies to how many of the terms to obf, because
        # we might not want to obfuscate all terms in this round


        #saved_expr = str(self.tree_ref)
        #print("Debug DIVERSIFY ROUND info: starting wide level term is: " + saved_expr)
        #self.debug_print_children_by_type()
        """
        self.all_same_level_terms = []
        self.constant_children = []
        self.variable_children = []
        self.other_children = []
        self.bitwise_children = []
        self.terminal_children = []
        self.single_op_bitwise_constant = []
        """

        # get list all single bitwise ops

        # get overall threshold to obf
        # this is # of single bitwise ops - 2
        terms_avail = self.single_op_bitwise_constant
        #num_obf_remaining = len(terms_remaining) - 2
        #cur_expr_str = str(self.tree_ref)
        cur_iteration = 0
        max_attempts = 5
        removed = []
        while cur_iteration < max_attempts:
            cur_iteration += 1
            self.recalc_term_info()
            #print("\n\n\n\t Current diversify round selection and candidates: ")
            #print("Current single bitwise ops: ")
            #print("\t\t\t", end="")
            #for b in self.bitwise_children:
            #    print(", " + str(b))
            #print("\nCurrent same level children: ")
            #print("\t\t\t", end="")
            #for s in self.all_same_level_terms:
            #    print(", " + str(s), end="")

            #print("\n")
            terms_remaining = self.single_op_bitwise_constant
            if not terms_remaining:
                continue
            terms_remaining = self.bitwise_children
            current = terms_remaining.pop()
            removed.append(current)

            candidates = [x for x in self.bitwise_children + self.variable_children if not x in removed and not x.contains(current.left) and not x.contains(current.right)]
            if not candidates:
                print("No candidates available; ending loop. Number of iterations: " + str(cur_iteration))
                return
            #print("\t\t Current node: " + str(current))
            #print("\t\t Candidates which do not contain the same LH or RH, or overall node: ")
            #print("\t\t", end="")
            #for c in candidates:
            #    print(str(c) + ", ", end="")
            #print("\n")


            # randomly select candidate and apply obfuscation
            selection = get_and_pop_random_from_list(candidates)
            #print("Expr before making adjacent: " + str(self.node_ref))
            print("diversification round: Selected nodes for adjacency: " + str(current) + ", " + str(selection))
            op = make_nodes_adjacent_using_llvm(current, selection, self.node_ref)
            #print("Expr after making adjacent: " + str(self.node_ref))
            #if (test_equivalent_by_brute_force(saved_expr, str(self.tree_ref), exit_on_false=False)):
            #    print("\tNew expression with adjacency is equivalent.")
            ruleset.apply_random_rule(op)
            #op.left = optimize_node(op.left)
            #op.right = optimize_node(op.right)
            self.node_ref.try_distribute()
            #self.recalc_term_info()
            #print("\nExpression at end of current application: " + str(self.node_ref))
            #print("Testing equivalent, iteration: " + str(cur_iteration))
            #test_equivalent_by_brute_force(self.obfuscator_ref.ground_truth_str, str(self.tree_ref), exit_on_false=False)
            print("End of diversify round")
        return


    def apply_mutation_round(self):
        # get list all single bitwise ops
        print("Mutation round on wide expr: " + str(self.node_ref))
        self.tree_ref.assemble_wide_terms()
        # get overall threshold to obf
        # this is # of single bitwise ops - 2
        terms_remaining = self.single_op_bitwise_constant + self.constant_children + self.variable_children + self.bitwise_children
        if not terms_remaining:
            terms_remaining = self.other_children
        num_obf_remaining = len(terms_remaining) - 2
        cur_expr_str = str(self.tree_ref)

        removed = []
        max_attempts = 4
        attempts = 0
        while num_obf_remaining > 0 and attempts <= max_attempts:
            attempts += 1
            # print("\n\n\n\t Current diversify round selection and candidates: ")
            # print("Current single bitwise ops: ")
            # print("\t\t\t", end="")
            # for b in self.bitwise_children:
            #    print(", " + str(b))
            # print("\nCurrent same level children: ")
            # print("\t\t\t", end="")
            # for s in self.all_same_level_terms:
            #    print(", " + str(s), end="")

            # print("\n")
            self.recalc_term_info()
            terms_remaining = self.single_op_bitwise_constant + self.constant_children + self.variable_children + self.bitwise_children
            shuffle(terms_remaining)
            if not terms_remaining:
                return
            current = terms_remaining.pop()
            removed.append(current)
            candidates = [x for x in self.bitwise_children + self.variable_children if
                          check_bitwise_nodes_contain_potential_mutators(current, x) and not x == current]
            if not isinstance(current, ConstNode):
                if not (isinstance(current, UnaryOpNode) and not (isinstance(current.get_terminal_node(), ConstNode))):
                    candidates += self.constant_children

            if not candidates:
                print("Mutation round: No candidates available; continuing but incrementing count: " + str(attempts))
                attempts += 1
                num_obf_remaining -= 1
                continue
            # print("\t\t Current node: " + str(current))
            # print("\t\t Candidates which do not contain the same LH or RH, or overall node: ")
            # print("\t\t", end="")
            # for c in candidates:
            #    print(str(c) + ", ", end="")
            # print("\n")
            num_obf_remaining -= 2
            attempts += 1

            # randomly select candidate and apply obfuscation
            selection = get_and_pop_random_from_list(candidates)
            print("Expr before making adjacent: " + str(self.node_ref))
            print("Selected nodes for adjacency: " + str(current) + ", " + str(selection))
            op = make_nodes_adjacent_using_llvm(current, selection, self.node_ref)
            print("Expr after making adjacent: " + str(self.node_ref))
            #if (test_equivalent_by_brute_force(self.obfuscator_ref.ground_truth_str, str(self.tree_ref), exit_on_false=False)):
            #    print("\tNew expression with adjacency is equivalent.")
            ruleset.apply_random_rule(op)
            # also optimize the LH and RH to distribute, factor, etc, change form
            if op is None:
                continue
            op.left = optimize_node(op.left)
            op.right = optimize_node(op.right)
            self.recalc_term_info()
            self.node_ref.try_distribute()
            #print("\nExpression at end of current application: " + str(self.node_ref))
            #print("Testing equivalent, iteration: " + str(cur_iteration))
            #test_equivalent_by_brute_force(self.obfuscator_ref.ground_truth_str, str(self.tree_ref), exit_on_false=False)

        return

class Obfuscator:
    def __init__(self, start_expression, optimize_gt=False):
        self.start_expr_str = start_expression
        self.original_ground_truth_str = start_expression
        if optimize_gt:
            self.original_ground_truth_str = str(single_expression_to_tree(start_expression, optimized=True))
        self.ground_truth_str = start_expression.replace("a", "g")
        self.ground_truth_str = self.ground_truth_str.replace("b", "h")


        tmp_str = start_expression
        tmp_str = tmp_str.replace("a", "g")
        tmp_str = tmp_str.replace("b", "h")
        self.obf_tree = single_expression_to_tree(tmp_str, optimized=True)


        self.gt_num_ops = single_expression_to_tree(self.ground_truth_str).get_num_ops()

        # note: we can't support 'a' and 'b' in input expressions
        # prep tree before calculating wide terms, etc
        self.obf_tree.convert_subs_to_adds()
        #print("Testing equivalence after converting subs to adds: ")
        #test_equivalent_by_brute_force(self.ground_truth_str, self.get_obf_expr_str(), exit_on_false=False)
        #print("Expression after converting subs to adds: " + str(self.obf_tree))

        self.all_wide_terms = []
        self.all_var_names_strs = []
        self.all_constants_ints = []
        self.term_dict = {} # dict: nodestr, number of occurrences


        # init wide term info
        self.build_wide_addition_term_list()



    def build_wide_addition_term_list(self) -> []:
        # 'wide' here means greater than two terms.
        # for instance, (x + (d * 2) will return an empty list.
        # (x + 2 + (d * 2) will return a list that contains the BinaryOp node which has the list
        # of assembled terms: x, 2, (d* 2).
        node = self.obf_tree.root
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


        self.all_wide_terms = []
        for x in wide_terms:
            self.all_wide_terms.append(WideTerm(x, self.obf_tree, self))
        return



    def print_all_tree_info(self):
        all_nodes = self.obf_tree.get_nodes_as_list()

        print("************************************************")
        print("************ Tree Debug Info: ******************")
        print("************************************************")
        print("Current tree: " + str(self.obf_tree))
        print("Ground truth: " + self.ground_truth_str)
        print("All variable names: ", end="")
        for x in self.obf_tree.all_varnames:
            print(x + ", ", end="")
        print("\nAll constants: ", end="")
        for x in all_nodes:
            if isinstance(x, ConstNode):
                print(str(x) + ", ", end="")

        if len(self.all_wide_terms) > 0:
            print("\n\n **** Wide term info:")
            for w in self.all_wide_terms:
                print("\n")
                w.print_stats()
        else:
            print("\nNo wide addition terms to print for this expression.")

        print("\n")
        print("************************************************")
        print("************ End Tree Debug Info: **************")
        print("************************************************")
        return

    def print_obf_info(self):
        # print: % duplication, # wide terms, wide term list,
        # other info...
        print("************************************************")
        print("************ Tree Obfuscation Info: **************")
        print("************************************************")
        print("Given expression: " + self.start_expr_str)
        print("Obfuscated expresion: " + self.get_obf_expr_str())
        print("Average wide child size(excluding unary ops): ")
        print(self.get_avg_wide_child_size())
        print("Average number of variables per wide child(counting -y and y as different): ")
        print("Overall avg duplicate terms larger than 3 operations: ")
        print("Overall avg duplicate terms larger than 3 operations, per wide term: ")
        print("% of total expressions which are part of a wide term:")

        print("************************************************")

        pass




    def inventory_and_inject_consts(self):
        #print("Running algorithm; first, just running general on existing wide terms")
        if self.obf_tree.get_num_ops() == 0:
            print("Tree given is single variable; cannot obfuscate")
        try:
            #print("Obf'ing root node")
            #ruleset.apply_random_rule(self.obf_tree.root)
            #self.obf_tree.convert_subs_to_adds()
            print("Obf'ing 1-2 bitwise-only nodes")
            options = [x for x in self.obf_tree.get_binary_ops_as_list() if
                   x.right.is_bitwise() and x.left.is_bitwise() and (x.op != Operation.MUL and x.op != Operation.DIV) \
                   and x.op != Operation.SHL and x.op != Operation.SHR]
            if options:
                ruleset.apply_random_rule(options[0])
            if len(options) > 1:
                ruleset.apply_random_rule(options[1])

        except:
            try:
                print("Obf'ing 1 other random ops instead")
                options = [x for x in self.obf_tree.get_binary_ops_as_list() if x.is_bitwise() and (x.op == Operation.AND or x.op == Operation.OR)]
                if options:
                    random.shuffle(options)
                    ruleset.apply_random_rule(options[0])
                else:
                    options = [x for x in self.obf_tree.get_binary_ops_as_list() if not
                               x.is_bitwise() and (x.op == Operation.ADD or x.op == Operation.SUB)]
                    random.shuffle(options)
                    ruleset.apply_random_rule(options[0])
            except:
                pass
            pass


        self.build_wide_addition_term_list()


        #if len(self.all_wide_terms) == 0 or len(self.all_wide_terms) == 1:
        print("0 or 1 wide terms to run on; injecting. Expression before injection: " + str(self.obf_tree))
        self.inject_wide_terms()
        self.build_wide_addition_term_list()

            #print("Expression after injecting: " + str(self.obf_tree))
            #print("Checking equivalence: ")
            #test_equivalent_by_brute_force(str(self.obf_tree), str(self.ground_truth_str), True)

        #self.build_wide_addition_term_list()
        all_varnames = self.obf_tree.all_varnames
        print("Num wide terms after adding: " + str(len(self.all_wide_terms)))
        # for some reason sometimes we can still end up with none even after the addition. Bug somewhere
        if len(self.all_wide_terms) == 0 or len(self.all_wide_terms) == 1:
            self.inject_wide_terms()
            self.build_wide_addition_term_list()
        """
        for w in self.all_wide_terms:
            print("\t wide term starting as: " + str(w.node_ref))
            rand_select = w.node_ref.same_level_children[0]
            inject_consts(rand_select)
            for v in all_varnames:
                inject_vars(v, rand_select)
                self.obf_tree.set_parents()
            w.recalc_term_info()
            print("\t wide term after injection: " + str(w.node_ref))
            test_equivalent_by_brute_force(self.ground_truth_str, self.get_obf_expr_str(), exit_on_false=False)
        """

        #print("Inventory pass: attempting to obf root node, which is op: " + str(self.obf_tree.root.op))
        #if (self.obf_tree.root.op == Operation.MUL or self.obf_tree.root.op == Operation.DIV):
        #    print("\n Cannot obf MUL or DIV. Leaving")
        #else:
        #    ruleset.apply_random_rule(self.obf_tree.root)
        #    test_equivalent_by_brute_force(self.ground_truth_str, self.get_obf_expr_str(), exit_on_false=False)

        #print("After inventory and inject pass, tree is: " + str(self.obf_tree))
        #print("Number of wide terms: " + str(len(self.all_wide_terms)))
        #self.build_wide_addition_term_list()
        #print("\t end of injection: ")
        #test_equivalent_by_brute_force(self.ground_truth_str, self.get_obf_expr_str(), exit_on_false=True)
        print("End of inventory pass, num wide terms is: " + str(len(self.all_wide_terms)))


    def obf_random_single_bitwise(self, wide_term):
        initial_list = wide_term.bitwise_children
        candidates = []
        for c in initial_list:
            if c.left.is_terminal() and c.right.is_terminal:
                candidates.append(c)

        if (len(candidates)) == 0:
            print("No good candidates for obf'ing single bitwise expression. Returning")
            return

        selection = candidates[random.randrange(0, len(candidates))]
        #print("Random bitwise rule to obfuscate: " + str(selection))
        ruleset.apply_random_rule(selection)
        self.build_wide_addition_term_list()
        #print("result: " + str(selection))
        return

    def v2_create_wide_terms(self, num_terms_to_create):
        print("Creating wide terms up to number: " + str(num_terms_to_create))
        tmp_limit = 4
        if (num_terms_to_create > tmp_limit):
            print("Adjusting to limit: " + str(tmp_limit))
            num_terms_to_create = tmp_limit
        terms_created = 0

        skip_list = []
        all_ops = self.obf_tree.get_binary_ops_as_list()
        bitwise_ops = [x for x in all_ops if x.is_bitwise() and x not in skip_list]
        arith_ops = [x for x in all_ops if not x.is_bitwise() and x not in skip_list]
        addition_ops = [x for x in all_ops if x.op == Operation.ADD and x not in skip_list]


        while (terms_created < num_terms_to_create):
            cur_op = None
            if len(addition_ops) > 0:
                cur_op = addition_ops.pop()
            elif len(bitwise_ops) > 0:
                cur_op = bitwise_ops.pop()
            elif len(arith_ops) > 0:
                cur_op = arith_ops.pop()
            else:
                # non-ideal candidates for obfuscation
                list_all_nodes = self.obf_tree.get_nodes_as_list()
                varnodes = [x for x in list_all_nodes if x.is_terminal() and not isinstance(x, ConstNode)]
                this_var = get_and_pop_random_from_list(varnodes)
                inject_consts(this_var)
                other_vars = [x for x in self.obf_tree.all_varnames if str(x) != str(this_var)]
                for v in other_vars:
                    inject_vars(v, this_var)
                terms_created += 1
                continue

            failed = False
            try:
                inject_consts(cur_op.parent)
                other_vars = [x for x in self.obf_tree.all_varnames() if str(x) != str(this_var)]
                for v in other_vars:
                    inject_vars(v, this_var)
                ruleset.apply_random_rule(cur_op)
            except:
                try:
                    inject_consts(cur_op)
                    ruleset.apply_random_rule(cur_op)
                except:
                    terms_created += 1
                    skip_list.append(cur_op)
                    continue



            terms_created += 1
            self.build_wide_addition_term_list()
            self.obf_tree.assemble_wide_terms()

        print("Added wide terms, expression is now: " + str(self.obf_tree))

        return

    def v2_run_obf(self, optimize_after=True, apply_size_limiter=True):
        # step 1: inventory initial state; continue obfuscating until heuristics have passed
        # initially, these are arbitrary; will play around with these

        limiter = 3
        minimum_percent_wide_terms = 75.0
        maximum_cse = 30.0
        maximum_percent_equivalent_synth_trees = 10.0
        maximum_percent_size_increase = 300.0

        tree_percent_wide_terms = self.get_percent_wide_term()
        all_nodes = [x for x in self.obf_tree.get_nodes_as_list() if x.is_bitwise() and x.get_size() > 1]

        try:
            for i in range(0, 1):
                try_op = all_nodes.pop()
                print("obfing op: " + str(try_op))
                ruleset.apply_random_rule(try_op)
        except:
            pass

        #if self.obf_tree.root.is_bitwise():
        #    ruleset.apply_random_rule(self.obf_tree.root)
        #    self.build_wide_addition_term_list()


        all_varnames = self.obf_tree.all_varnames
        print("\t Printing all available variables")
        for x in all_varnames:
            print("\t\tvarname: " + str(x))

        # if no wide terms, create them, prioritizing higher ops in the tree
        # (lower tree depth)
        #print("Test size: " + str((self.obf_tree.get_size() * .1)))
        print("Starting wide terms: " + str(len(self.all_wide_terms)))
        initial_wide_term_threshold = self.obf_tree.get_size() * .2
        if self.obf_tree.get_size() < 6:
            self.v2_create_wide_terms(2)
        if (len(self.all_wide_terms) < initial_wide_term_threshold and len(self.all_wide_terms) < 5):
            self.v2_create_wide_terms(floor(self.obf_tree.get_size() * .2))
            #pass
        # also, there are per-wide term traits
        print("\tAll available wide terms: (total: " + str(len(self.all_wide_terms)) + ")")
        for w in self.all_wide_terms[0:limiter]:
            print("\t\t " + str(w))
            vars_to_add = w.get_inverse_intersection_tree_variables()
            print("\t\tMissing vars: ")
            for v in vars_to_add:
                print("\t\t\t" + str(v))

            if len(vars_to_add) > 0:
                print("\t\ttest: adding all missing vars")
                for v in vars_to_add[0:3]:
                    inject_vars(v, w.node_ref.left)
                    print("\t\tWide term after adding var: " + v)
                    print("\t\t" + str(w))


            print("\n\tAdding const children")
            inject_consts(w.node_ref.left)

            if test_equivalent_by_brute_force(self.get_obf_expr_str(), self.get_gt_expr_str(), exit_on_false=False):
                print("expressions are equivalent.")
            else:
                raise Exception("False equivalence check")


        print("For each wide term, collecting obf candidates: ")
        self.build_wide_addition_term_list()
        num_w_terms_to_use = limiter

        if apply_size_limiter == False:
            num_w_terms_to_use == len(self.all_wide_terms)

        for w in self.all_wide_terms[0:num_w_terms_to_use]:
            print("Executing round on wide term: " + str(w))
            self.v2_run_diversify(w)

        #self.build_wide_addition_term_list()
        if not self.obf_tree.get_size() > 200:
            for w in self.all_wide_terms[0:limiter]:
                self.v2_run_diversify(w)
                print("Wide term info after two diversify rounds: ")

        for w in self.all_wide_terms[0:num_w_terms_to_use]:
            print_traits_for_node(w.node_ref)
            self.v2_obf_rand_bitwise_duplicates(w)

        #self.build_wide_addition_term_list()

        if len(self.all_wide_terms) < 5:
            max = len(self.all_wide_terms)
        for w in self.all_wide_terms[0:limiter]:
            w.apply_mutation_round()
            print("Wide term info after mutation round:")
            print("Total wide terms: " + str(len(self.all_wide_terms)))
            print("Optimizing wide term after mutation round")
            new_w = single_expression_to_tree(str(w.node_ref), optimized=True)
            w.node_ref = new_w
            print_traits_for_node((w.node_ref))
            if self.obf_tree.get_size() > 800:
                break


        num_attempts = 0
        while (self.obf_tree.get_size() < 400 and num_attempts < 4):
            print("Re-running obf:")
            num_attempts += 1
            self.v2_create_wide_terms(1)
            print("For each wide term, collecting obf candidates: ")
            self.build_wide_addition_term_list()
            for w in self.all_wide_terms:
                print("Executing round on wide term: " + str(w))
                self.v2_run_diversify(w)

            self.build_wide_addition_term_list()
            for w in self.all_wide_terms:
                self.v2_run_diversify(w)
                print("Wide term info after two diversify rounds: ")
                print("Whole expression size is: " + str(self.obf_tree.get_size()))

            for w in self.all_wide_terms[0:limiter]:
                print_traits_for_node(w.node_ref)
                self.v2_obf_rand_bitwise_duplicates(w)

            self.build_wide_addition_term_list()
            for w in self.all_wide_terms:
                w.apply_mutation_round()
                print("Wide term info after mutation round:")
                print("Whole expression size is: " + str(self.obf_tree.get_size()))
                print_traits_for_node((w.node_ref))

        if optimize_after:
            self.obf_tree = single_expression_to_tree(str(self.get_obf_expr_str()), optimized=True)
        print("Obfuscator stopping at: " + str(self.get_obf_expr_str()))
        #print("For GT: " + str(self.ground_truth_str))
        return



    def v2_mutate_duplicates(self, wide_term:WideTerm, max_tries=3):
        print("Round: mutate duplicates")
        self.build_wide_addition_term_list()
        duplicates_dict = get_duplicates_dict_for_node(wide_term.node_ref)

        print("\tGetting duplicate bitwise term info")
        duplicate_binnode_strs = [key for key, val in duplicates_dict.items() if val > 1]

        duplicate_binnodes = [x for x in wide_term.bitwise_children if str(x).strip(" ") in duplicate_binnode_strs]
        set_binnodes = []

        for x in duplicate_binnodes:
            if x not in set_binnodes:
                set_binnodes.append(x)

        duplicate_binnodes = set_binnodes
        cur_attempts = 0
        while (cur_attempts < max_tries):
            candidate = duplicate_binnodes.pop()
            cand2 = check_bitwise_nodes_contain_potential_mutators(candidate, duplicate_binnodes)
            if cand2 is None:
                cand2 = check_bitwise_nodes_contain_potential_mutators(candidate, wide_term.bitwise_children)
            else:
                duplicate_binnodes.remove(cand2)

            try:
                if cand2 is None:
                    cand2 = wide_term.bitwise_children.pop()
            except:
                print("Couldn't find candidates for round: v2_mutate_duplicates.")
                print("Wide term is: " + str(wide_term))

            print("\tfetched nodes:")
            print("\t\t" + candidate)
            print("\t\t" + cand2)
            make_nodes_adjacent_using_llvm(candidate, cand2, wide_term)
            ruleset.apply_random_rule(candidate.parent)
            optimize_node(candidate.parent)

            return

    def v2_obf_rand_bitwise_duplicates(self, wide_term:WideTerm):
        self.build_wide_addition_term_list()
        duplicates_dict = get_duplicates_dict_for_node(wide_term.node_ref)

        print("\tGetting duplicate bitwise term info")
        duplicate_binnode_strs = [key for key, val in duplicates_dict.items() if val > 1]

        duplicate_binnodes = [x for x in wide_term.bitwise_children if str(x).strip(" ") in duplicate_binnode_strs]
        set_binnodes = []

        for x in duplicate_binnodes:
            if x not in set_binnodes:
                set_binnodes.append(x)

        duplicate_binnodes = set_binnodes

        print("\tfetched nodes:")
        for x in duplicate_binnodes:
            print("\t\t **: " + str(x))
            print("\t\tAfter obfuscating: ")
            ruleset.apply_random_rule(x)
            print("\t\t" + str(x))
            print("\t\tAfter bitwise distribute: ")
            wide_term.tree_ref.try_distribute()
            print("\t\t" + str(x))

        print(str(wide_term))


    def v2_run_seed(self, wide_term:WideTerm):
        # attempt to obfuscate constants and vars first,
        # then bitwise ops.

        const_children = wide_term.constant_children
        remaining = wide_term.bitwise_children
        remaining.extend(wide_term.variable_children)

        for x in const_children:
            print("In run_seed, obfuscating")
            if len(remaining) > 0:
                print("\t\t const candidate: " + str(x))
                remaining_cand = remaining.pop()
                print("\t\t remaining candidate: " + str(remaining_cand))
                make_nodes_adjacent_using_llvm(x, remaining_cand, wide_term.node_ref)
                ruleset.apply_random_rule(x.parent)

        print("Expression at end of round is: " + str(wide_term.node_ref))
        return


    def v2_run_diversify(self, wide_term:WideTerm):
        # This should probably be a method of WideTerm instead
        print("*** Running diversify round for wide term")
        wide_term.node_ref.assemble_wide_terms()
        wide_term.recalc_term_info()

        # before obfing in general, try obfuscating some bitwise expressions
        #if len(wide_term.bitwise_children) > 0:


        start_expr = str(wide_term.node_ref)
        all_candidates = []
        queue1 = []
        queue2 = []

        all_candidates.extend(wide_term.constant_children)
        all_candidates.extend(wide_term.variable_children)
        # Add smaller bitwise-only children first
        all_candidates.extend([x for x in wide_term.bitwise_children])
        # first, try to obfuscate away the extra added constant children.
        # if we've already done that, then we can shuffle the candidates
        # and select at random.
        if len(wide_term.constant_children) < 2:
            random.shuffle(all_candidates)

        # all bitwise children not in all_candidates
        remaining = [x for x in wide_term.all_same_level_terms if x not in all_candidates]

        if (len(all_candidates) == 0):
            wide_term.node_ref.assemble_wide_terms()
            wide_term.recalc_term_info()

        print("Collected candidates: ")
        random.shuffle(all_candidates)
        for cand in all_candidates:
            print("\t\t\t " + str(cand))

        print("Remaining candidates: " )
        for r in remaining:
            print("\t\t\t + " + str(r))

        print("Splitting into queues")
        all_len = len(all_candidates)
        half_index = floor(all_len / 2)
        queue1 = all_candidates[0:half_index]
        queue2 = all_candidates[half_index:all_len]


        new_wide_term_all_children = remaining
        print("Length of queue 1 is: " + str(len(queue1)))
        print("length of queue 2 is: " + str(len(queue2)))

        iteration = 0
        for i in range(0, (len(queue1))):
            iteration += 1
            if iteration > 4:
                break
            rh = queue2.pop()
            lh = queue1[random.randint(0, len(queue1)-1)]

            max_tries = 3
            cur_tries = 0
            while not check_are_terms_disjoint(rh, lh) or (isinstance(rh, ConstNode) and isinstance(lh, ConstNode)):
                if cur_tries == max_tries or len(queue1) <= 1:
                    break
                print("\t\t\tHit try case with candidates: " + str(rh) + " and " + str(lh))
                print("\t\tLength of queue remaining is: " + str(len(queue1)))
                lh = queue1[random.randint(0, len(queue1)-1)]
                print("\t\t\tAfter new selection, candidates are: " + str(rh) + " and " + str(lh))
                cur_tries += 1


            queue1.remove(lh)

            print("\tObfuscating candidates: " + str(lh) +" and " + str(rh))
            # trying: instead of making adjacent then obfuscating, creating a new add node and obfuscating that
            new_add_node = BinaryOpNode(Operation.ADD, left=lh, right=rh, parent=None)
            ruleset.apply_random_rule(new_add_node)

            print("\tResulting obfuscated node is: " + str(new_add_node))
            print("\tAdding to all new terms for wide node.")
            new_wide_term_all_children.append(new_add_node)

        # construct new wide term node and set its parents
        # if there were an even number of total children, then queue1 will have an extra.
        remaining.extend(queue1)
        remaining.extend(queue2)
        new_expr_tokens = [str(x) for x in new_wide_term_all_children]
        new_expr_str = " + ".join(new_expr_tokens)
        print("\tConstructing new wide term, expression string is: " + new_expr_str)
        new_wide_term_root_node = single_expression_to_tree(new_expr_str).root
        print("\tResulting tree is: " + str(new_wide_term_root_node))
        print("\tReplacing")
        # replace the child nodes, otherwise the tree won't get updated
        wide_term.node_ref.right = new_wide_term_root_node.right
        wide_term.node_ref.left = new_wide_term_root_node.left

        wide_term.node_ref.assemble_wide_terms()
        wide_term.recalc_term_info()
        print("Checking equivalence")
        end_expr = str(wide_term.node_ref)
        if not test_equivalent_by_brute_force(start_expr, end_expr, False):
            raise Exception("False equivalence check")

        return

    def obf_using_pass_algorithm(self, optimize_after=True):
        #print("first: applying seed round: injecting wide terms and constants as needed")
        self.inventory_and_inject_consts()
        print("##### Starting seed round #####")
        self.seed_round()
        # print("obf info: ")
        print("Testing equality after seed round")
        if not test_equivalent_by_brute_force(self.get_obf_expr_str(), self.start_expr_str):
            raise Exception("Results not equivalent")


        print("##### Starting diversification round #####")
        print("Expression is: " + self.get_obf_expr_str())
        self.diversify_round()
        print("Testing equality after diversify round")
        if not test_equivalent_by_brute_force(self.get_obf_expr_str(), self.start_expr_str):
            raise Exception("Results not equivalent")

        # print("Back in main test function: testing equivalency between obf'd tree and original")
        # print(test_equivalent_by_brute_force(str(input_expression), str(obf_inst.obf_tree), True))
        print("##### Starting mutation round #####")
        self.mutate_round()
        print("Testing equality after mutation round")
        if not test_equivalent_by_brute_force(self.get_obf_expr_str(), self.start_expr_str):
            raise Exception("Results not equivalent")

        print("sample wide ter children end of algo: ")
        for w in self.all_wide_terms:
            for i in w.bitwise_children:
                print(str(i))
        if optimize_after:
            try:
                self.obf_tree.root = optimize_node(self.obf_tree)
            except:
                print("Finished obfuscation; optimization returned error or constant. Leaving un-optimized.")


    # for initial round(s)
    def obf_general_non_mutators(self, wide_term):
        num_term_proportion = 0.25
        num_terms_to_select = 0
        # for all vars, constants, and bitwise terms, randomly obf against
        # each other
        candidates = wide_term.bitwise_children + wide_term.variable_children + wide_term.constant_children
        num_terms_to_select = ceil(0.25 * len(candidates))

        print("In obf_non_mutators, starting candidates are: ")
        if (len(candidates) == 0):
            print("no ideal selections; choosing all same-level children instead")
            candidates = wide_term.node_ref.same_level_children
        for c in candidates:
            print("\t\t" + str(c))

        # randomly select # of terms for the given proportion
        # if we selected 0, then set this equal to 1
        if num_terms_to_select == 0: num_terms_to_select = 1

        # copy the wide term.same level children, or work directly with it?
        # should probably work directly, because we are modifying the children directly
        # copy the wide term if we're that concerned

        # for each # iterations (num_terms_to_select):
        # choose term, remove, then scan for others with mutators
        shuffle(candidates)
        selection = candidates.pop()
        second_candidate = None
        for c in candidates:
            if not check_bitwise_nodes_contain_potential_mutators(selection, c):
                second_candidate = c
                break

        if second_candidate is None:  # no potential mutators. Choose a random term and obf.
            if len(candidates) == 0:
                print("Out of candidates. returning")
                return
            second_candidate = candidates.pop()

        print("Candidate list: ")
        for c in candidates:
            print("\t\t " + str(c))
        print("\t\t\tChosen obfuscation terms: " + str(selection) + " and " + str(second_candidate))
        obf_and_simplify_nodes_in_wide_term(selection, second_candidate, wide_term.node_ref, ruleset)
        print("\t\t\tWide term after obfuscation is: " + str(wide_term.node_ref))
        return

    def obf_general(self, wide_term:WideTerm):
        num_term_proportion = 0.25
        num_terms_to_select = 0
        # for all vars, constants, and bitwise terms, randomly obf against
        # each other
        candidates = wide_term.bitwise_children + wide_term.variable_children + wide_term.constant_children
        print("In obf_general, starting candidates are: ")
        for c in candidates:
            print("\t\t" + str(c))

        num_terms_to_select = ceil(0.25 * len(candidates))

        # randomly select # of terms for the given proportion
        # if we selected 0, then set this equal to 1
        if num_terms_to_select == 0: num_terms_to_select = 1

        # copy the wide term.same level children, or work directly with it?
        # should probably work directly, because we are modifying the children directly
        # copy the wide term if we're that concerned

        # for each # iterations (num_terms_to_select):
        # choose term, remove, then scan for others with mutators
        if (len(candidates)) == 0:
            print("out of candidates. returning")
            return
        shuffle(candidates)

        selection = candidates.pop()
        second_candidate = None
        if len(candidates) == 0:
            print("Out of candidates. returning")
            return
        for c in candidates:
            if selection.is_terminal() and c.is_terminal():
                continue

            if check_bitwise_nodes_contain_potential_mutators(selection, c):
                second_candidate = c

        if second_candidate == None: # no potential mutators. Choose a random term and obf.
            second_candidate = candidates.pop()
        print("\t\t\tChosen obfuscation terms: " + str(selection) + " and " + str(second_candidate))
        obf_and_simplify_nodes_in_wide_term(selection, second_candidate, wide_term.node_ref, ruleset)
        print("\t\t\tWide term after obfuscation is: " + str(wide_term.node_ref))
        return


    def inject_wide_terms(self):
        print("Debug: inside new_inject_wide_terms")
        print("Expression at start: " + str(self.obf_tree))
        total_vars = self.obf_tree.all_varnames

        # collect every unique const node instance


        self.obf_tree.convert_subs_to_adds()

        print("All unique constant node instances")
        all_ops = self.obf_tree.get_nodes_as_list()
        raw_list_vars = [x for x in self.obf_tree.get_nodes_as_list() if isinstance(x, VarNode)]
        all_varnodes = [x for x in all_ops if x.is_terminal() and isinstance(x.parent, BinaryOpNode) and (isinstance(x, VarNode) or isinstance(x, UnaryOpNode))]


        print("All collected constant node instances, and their parent nodes:")
        for c in all_varnodes:
            print("\t " + str(c) + ", " + str(c.parent))

        unique_varnodes = [] # list to pull from - check again here because certain nodes like "-d" don't get picked up in all_varnodes
        for c in all_varnodes:
            if c not in all_varnodes:
                unique_varnodes.append(c)
        for c in raw_list_vars:
            if c not in unique_varnodes:
                unique_varnodes.append(c)

        all_binops = []
        try:
            all_binops = [x for x in self.obf_tree.get_binary_ops_as_list() if x.is_bitwise()]
            all_binops = [x.right for x in self.obf_tree.get_binary_ops_as_list() if x.op == Operation.ADD]
        except Exception as e:
            shuffle(all_varnodes)
            max_select = min(4, len(all_varnodes))
            all_binops = all_varnodes[0:max_select]

        print("Attempting injection to leaf node and not parent node")
        shuffle(all_binops)
        limit = 3
        if len(all_binops) < limit:
            limit = len(all_varnodes)
        for c in all_binops[0:limit]:
            print("Currently on varnode: " + str(c))
            tmp = c.parent
            # injection messes up the order of nodes, which is unacceptable with shifts.
            while not (isinstance(tmp, BinaryOpNode)):
                tmp = tmp.parent
            print("tmp is: " + str(tmp))
            if tmp.op == Operation.SHL or tmp.op == Operation.SHR:
                print("hit continue case")
                continue

            print("Before injection: " + str(self.obf_tree))
            print("Injecting consts: ")
            inject_consts(c)

            # new code
            print("Applying obf rule to c.parent (applied const injection)")
            ruleset.apply_random_rule(c.parent)

            c = c.parent
            for a in unique_varnodes:
                if isinstance(a, VarNode) and not c.contains(a):
                    # disjoint_vars.append(a)
                    print("\t\t adding disjoint var " + str(a))
                    inject_vars(a.varname, c)
                    self.obf_tree.set_parents()
                    print("immediately after const and var injection: ")
                    print(self.obf_tree)
                    ruleset.apply_random_rule(c.parent)
                    print("new expr: " + str(self.obf_tree))
                    if test_equivalent_by_brute_force(self.get_obf_expr_str(), self.original_ground_truth_str, exit_on_false=False):
                        print("TRUE")
                        break # break here because once we've modified and obf'd the node, we can't add to it in the same way
                    else:
                        raise Exception("False equivalence check")
                        return

            # new code

            print("Applying obf rule to c.parent (applied const injection)")
            ruleset.apply_random_rule(c.parent)
            self.obf_tree.try_distribute()
            new_parent = c.parent
            self.obf_tree.set_parents()
            if self.obf_tree.get_num_ops() > 40:
                return
            """
            print("New parent node is: " + str(new_parent))
            print("np.right: " + str(new_parent.right)) # right one tends to be the single op
            print("np.left: " + str(new_parent.left))
            print("continuing obf on right")

            inject_consts(new_parent.right)
            self.obf_tree.set_parents()

            print("after new consts, np.right is: " + str(new_parent.right))
            print("np is: " + str(new_parent))
            print("np.right.right.right is: " + str(new_parent.right.right.right))
            #print("np.right.parent.parent is: " + str(new_parent.right.parent.parent))
            ruleset.apply_random_rule(new_parent.right.right.right)
            self.obf_tree.set_parents()
            print("after applying obfuscation, np is: " + str(new_parent))
            print("Optimizing")
            new_parent.left = optimize_node(new_parent.left)
            new_parent.right = optimize_node(new_parent.right)
            self.obf_tree.set_parents()
            print(str(new_parent))
            print("Expression tree after opt: " + str(self.obf_tree))
            print("Attempting obf one of the bitwise nodes")
            ruleset.apply_random_rule(c.parent.left)
            self.obf_tree.set_parents()
            #c.parent = optimize_node(c.parent)
            # end new code
            """
            print("new expr: " + str(self.obf_tree))
            if test_equivalent_by_brute_force(self.get_obf_expr_str(), self.original_ground_truth_str, exit_on_false=False):
                print("TRUE")
            else:
                print("FALSE")
                raise Exception


        #print("Collecting all unique parent node instances: ")
        #const_binop_parents = [x.parent for x in all_varnodes]

        #unique_binop_parents = []
        #for x in const_binop_parents:
        #    if x not in unique_binop_parents:
        #        unique_binop_parents.append(x)

        #for c in unique_binop_parents:
        #    print("\t" + str(c))

        """
        print("Injecting consts, vars for each unique parent node instance")
        for c in unique_binop_parents:
            print("\t" + str(c))
            print("\tDisjoint vars for this term: ")
           # disjoint_vars = []
            for a in all_varnodes:
                if not c.contains(a):
                    #disjoint_vars.append(a)
                    print("\t\t " + str(a))
                    inject_vars(a.varname, c)
            inject_consts(c)
        """

        print("Updated expression: " + str(self.obf_tree))
        print("Testing expression equivalence: ")
        if test_equivalent_by_brute_force(self.get_obf_expr_str(), self.original_ground_truth_str):
            print("TRUE")
        else:
            print("FALSE")
            return

        return


    def old_inject_wide_terms(self, num_to_add=3):
        # get starting # ops
        starting_ops = self.obf_tree.get_binary_ops_as_list()
        num_starting_ops = len(starting_ops)
        wide_remaining_to_add = num_to_add #0.3 * num_starting_ops
        number_added = 0
        total_vars = self.obf_tree.all_varnames
        #total_vars_as_nodes = [VarNode(x, use_literal_name=True) for x in total_vars]
        print("Total vars available in expression are: ", end="")
        for v in total_vars:
            print(v + ", ")

        # find existing binary or arithmetic ops which are not part of wide terms
        # can use contains, which supports terminals or non-terminals
        # problem: we don't want to add constants or vars to the same spot twice
        # for example: x + y + 31 + 22 + -53: don't add again to this term
        while number_added < num_to_add:
            # select random binop nodes until we find one not already part of a wide term
            number_added += 1
            all_binops = self.obf_tree.get_binary_ops_as_list()
            num_binops = len(all_binops)
            rand_binop = all_binops[random.randint(0, len(all_binops) - 1)]
            disjoint_vars = [x for x in total_vars if rand_binop.left.is_terminal() and rand_binop.right.is_terminal() and not rand_binop.contains(x)]
            print("selected binop for adding wide term is: " + str(rand_binop))
            print("disjoint vars are: ")
            for d in disjoint_vars:
                print("\t" + str(d))

            for d in disjoint_vars:
                inject_vars(d, rand_binop)
            inject_consts(rand_binop)
            print("Subexpression after injecting vars, consts is: " + str(rand_binop))

        # first, try adding to existing addition operations.
        add_ops = [x for x in starting_ops if x.op == Operation.ADD]
        while number_added < wide_remaining_to_add and add_ops:
            number_added += 1
            add_ops = [x for x in self.obf_tree.get_binary_ops_as_list() if x.op == Operation.ADD]
            add_op = add_ops[-1]
            inject_consts(add_op)
            print("After injecting constants: " + self.get_obf_expr_str())
            test_equivalent_by_brute_force(self.original_ground_truth_str, self.get_obf_expr_str(), exit_on_false=False)
            # Try to add variables that this term doesn't contain first.
            for v in total_vars:
                if not add_op.contains(ConstNode(v)):
                    inject_vars(v, add_op)
            print("After injecting varnames:" + self.get_obf_expr_str())
            test_equivalent_by_brute_force(self.original_ground_truth_str, self.get_obf_expr_str(), exit_on_false=False)

        # then, select from the rest if we still have more to go
        """
        avail_nodes = self.obf_tree.get_binary_ops_as_list()
        while number_added < wide_remaining_to_add and starting_ops:
            number_added += 1
            cur_op = avail_nodes[randint(0, len(avail_nodes)-1)]
            print("In loop, cur_op is: " + str(cur_op))
            inject_consts(cur_op)
            print("After injecting constants to cur_op: " + str(cur_op))
            test_equivalent_by_brute_force(self.original_ground_truth_str, self.get_obf_expr_str(), exit_on_false=False)
            # Try to add variables that this term doesn't contain first.
            for v in total_vars_as_nodes:
                if not cur_op.contains(v):
                    inject_vars(v.varname, cur_op)
            print("After injecting on random nodes:" + self.get_obf_expr_str())
            test_equivalent_by_brute_force(self.original_ground_truth_str, self.get_obf_expr_str(), exit_on_false=False)
        """


        print("Expression at end of inject wide terms: " + str(self.obf_tree))

        return

    def old_inject_wide_terms(self):
        # This function assumes that subtraction ops have already been converted to addition.
        # meta info: keep track of what we added
        # XXXX
        # XXX
        # XXX


        injection_threshold = 0.40 # the % of binary ops for which to insert wide terms
        # arbitrary, can adjust

        all_binops = self.obf_tree.get_binary_ops_as_list()
        num_binops = len(all_binops)
        target_num = num_binops * injection_threshold

        # create list of binops which are not wide terms
        non_wide_terms = [x for x in all_binops if len(x.same_level_children) < 3]
        existing_add_terms = [x for x in non_wide_terms if x.op == Operation.ADD]

        worklist = []

        if len(existing_add_terms) == 0:
            # no wide terms available. Just try randomly selecting .4 of existing
            # binops.
            worklist = non_wide_terms
        else:
            if len(existing_add_terms) < target_num:
                remaining_terms = [x for x in non_wide_terms if x.op != Operation.ADD]
                difference = target_num - len(existing_add_terms)
                while (difference > 0) and (difference < len(remaining_terms)):
                    difference -= 1
                    existing_add_terms.append(remaining_terms.pop())

            worklist = existing_add_terms

        # for each target wide term, inject disjunct vars and count the add
        # also inject constants and count the constant add
        for i in worklist:
            if (isinstance(i.parent, UnaryOpNode)): continue
            inject_consts(i)
            # get all varnames which are not already in the subtree for i
            i_nodes = i.get_nodes_as_list()
            i_contained_varnames = []
            i_contained_varnames = [str(x) for x in i_nodes if isinstance(x, VarNode)]
            i_contained_varnames = list(set(i_contained_varnames))
            vars_to_use = [v for v in self.obf_tree.all_varnames if v not in i_contained_varnames]

            for v in vars_to_use:
                inject_vars(v, i)
        # disjunct varnames
        #all_varnames = [str(x) for x in all_ops if isinstance(x, VarNode)]
        #self.all_varnames = list(set(self.all_varnames))


    def get_obf_expr_str(self):
        # if expression had "a" or "b" as variables,
        # they were swapped with "g" and "h" because of our implementation...
        # swap back
        ret_str = str(self.obf_tree)
        ret_str = ret_str.replace("g", "a")
        ret_str = ret_str.replace("h", "b")
        return ret_str

    def get_gt_expr_str(self):
        return self.original_ground_truth_str

    ########### Algorithm Passes ###################
    def seed_round(self):
        for w in self.all_wide_terms[0:5]:
            w.apply_seed_round()
        return

    def mutate_round(self):
        limit = 5
        for w in self.all_wide_terms[0:limit]:
            w.apply_mutation_round()
        return

    def diversify_round(self):
        for w in self.all_wide_terms[0:5]:
            w.apply_diversify_round()
        return

    def mutation_round(self):
        pass

    def break_subtree_round(self):

        pass

    def check_heuristics(self):
        max_iterations = 5
        pass



    ########### Heuristics and General Info ###################
    def create_all_terms_dict(self):
        # dictionary: term, number of instances.
        # note that this is purely token-based, so
        # (e + f) != (f + e).
        new_dict = {}
        all_terms = self.obf_tree.get_nodes_as_list()
        for l in all_terms:
            found = False
            for d in new_dict.values():
                if l == d:
                    new_dict[d] += 1
                    found = True
            if not found:
                new_dict[l] = 1

        return new_dict

    def get_percent_wide_term(self):
        # calculate the percentage of all operations which are part of a wide term.
        # Note right now this is double-counting nested wide terms.
        total_count = self.obf_tree.get_size()
        #print("Total count: " + str(total_count))

        wide_term_count = 0.0
        self.build_wide_addition_term_list()
        for w in self.all_wide_terms:
            #print("Current wide term: " + str(w))
            # check whether a parent of this node is a wide term. If so,
            # don't add it to the count.
            parent = w.node_ref.parent
            skip = False
            while parent is not None:
                if isinstance(parent, BinaryOpNode) and len(parent.same_level_children) > 2:
                    skip = True
                    break
                parent = parent.parent
            if not skip:
                wide_term_count += w.node_ref.get_size()

        #print("Wide term count: " + str(wide_term_count))

        if wide_term_count == 0 or total_count == 0:
            return 0

        return (wide_term_count / total_count) * 100.00



    def get_avg_wide_child_size(self):
        count = 0
        running_total = 0.0

        if self.all_wide_terms == []:
            return 0

        for w in self.all_wide_terms:
            running_total += w.get_avg_child_size()
            count += 1
        return running_total / count


    def get_str_wide_term_var_info(self):
        out_str = "\n*** Variable info:"
        for w in self.all_wide_terms:
            missing_vars = w.get_inverse_intersection_tree_variables()
            if len(missing_vars) != 0:
                out_str += "\n" + str(w) + " does not contain all vars, missing: " + ", ".join(missing_vars)

        return out_str