import sys
import subprocess
import os
from src.ExpressionTree import *

opt_path = "/usr/local/bin/opt"
clang_path = "clang2"

def create_c_function_text(expr_string, expr_name):
    # function name = 'mba' + expr_name
    expr_name = expr_name.strip()
    expr_name = expr_name.replace(" ", "_")
    first_line = "int mba_" + expr_name + "(int x, int y, int z, int a, int b, int c, int d, int e, int f, int g, int h, int t) { \n\n"

    # int + function_name + param list + {
    retline = "return " + expr_string + ";\n\n"
    last_line = "}"

    return first_line + retline + last_line

def create_promba_c_function_text(expr_string, expr_num):
    # function name = 'mba' + expr_name
    first_line = "int target_" + str(expr_num) + "(int x, int y, int z, int a, int b, int c, int d, int e, int f, int g, int h, int t) { \n\n"

    # int + function_name + param list + {
    retline = "return " + expr_string + ";\n\n"
    last_line = "}"

    return first_line + retline + last_line



def create_c_text_single_expr(expression, expr_name="generic"):

    return create_c_function_text(expr_name, expression)


def get_llvm_ir_single_expr(expression, expr_name="generic", optimized=False):
    # echo "testing" | clang -x c  -Xclang -disable-llvm-passes -O0 -S -disable-O0-optnone -emit-llvm - -o /dev/stdout

    func_text = create_c_function_text(expression, expr_name)
    #LLVM_command = "clang -x c  -Xclang -disable-llvm-passes -O0 -S -disable-O0-optnone -emit-llvm - -o /dev/stdout"

    # command = f'/usr/bin/clang {filename}.c -Xclang -disable-llvm-passes -O0 -S -disable-O0-optnone -emit-llvm -o {optnone_intermediate_filename}.ll'
    #
    #     devnull = open(os.devnull, 'w')
    #     subprocess.run(command, shell="True")
    # TD: find safer way to do this
    #prepend_command = "echo \" " + func_text + "\"" + LLVM_command
    prepend_command = f'echo \"{func_text}\" | {clang_path} -x c  -Xclang -disable-llvm-passes -O0 -S -disable-O0-optnone -emit-llvm - -o /dev/stdout'
    result = subprocess.run(prepend_command, shell="True", capture_output=True, text=True)

    ir_text = result.stdout
    #stripped_ir_text = ""
    #for line in ir_text:
    #    if line[0] == ';' or line[0] == 'a':
    #        mod_line = line.replace("optnone", "")
    #        stripped_ir_text += mod_line
    #    else:
    #        stripped_ir_text += line
    stripped_ir_text = result.stdout.replace("optnone", "")

    return stripped_ir_text



#### samples
mba_long = """
  %10 = alloca i32, align 4
  %11 = alloca i32, align 4
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  %14 = alloca i32, align 4
  %15 = alloca i32, align 4
  %16 = alloca i32, align 4
  %17 = alloca i32, align 4
  %18 = alloca i32, align 4
  store i32 %0, ptr %10, align 4
  store i32 %1, ptr %11, align 4
  store i32 %2, ptr %12, align 4
  store i32 %3, ptr %13, align 4
  store i32 %4, ptr %14, align 4
  store i32 %5, ptr %15, align 4
  store i32 %6, ptr %16, align 4
  store i32 %7, ptr %17, align 4
  store i32 %8, ptr %18, align 4
  %19 = load i32, ptr %10, align 4
  %20 = load i32, ptr %11, align 4
  %21 = sub nsw i32 0, %20
  %22 = load i32, ptr %11, align 4
  %23 = load i32, ptr %11, align 4
  %24 = xor i32 %23, -1
  %25 = load i32, ptr %11, align 4
  %26 = xor i32 %25, -1
  %27 = load i32, ptr %11, align 4
  %28 = xor i32 %27, -1
  %29 = load i32, ptr %11, align 4
  %30 = sub nsw i32 0, %29
  %31 = and i32 %28, %30
  %32 = xor i32 %31, -1
  %33 = xor i32 %32, -1
  %34 = load i32, ptr %11, align 4
  %35 = xor i32 %34, -1
  %36 = load i32, ptr %11, align 4
  %37 = sub nsw i32 0, %36
  %38 = or i32 %35, %37
  %39 = xor i32 %38, -1
  %40 = xor i32 %39, -1
  %41 = add nsw i32 %33, %40
  %42 = sub nsw i32 0, %41
  %43 = add nsw i32 %26, %42
  %44 = or i32 %24, %43
  %45 = or i32 %22, %44
  %46 = xor i32 %45, -1
  %47 = add nsw i32 %21, %46
  %48 = sub nsw i32 0, %47
  %49 = add nsw i32 %19, %48
  ret i32 %49
  """



mba_post_opt = """%10 = alloca i32, align 4
  %11 = alloca i32, align 4
  store i32 %0, ptr %10, align 4
  store i32 %1, ptr %11, align 4
  %.neg3 = add i32 %0, 1
  %.not = xor i32 %1, -1
  %12 = and i32 %0, %.not
  %.not1 = xor i32 %1, -1
  %13 = and i32 %0, %.not1
  %14 = add i32 %0, %12
  %15 = add i32 %0, %13
  %16 = add i32 %14, %15
  %17 = sub i32 -2, %16
  %.not2 = xor i32 %1, -1
  %18 = and i32 %0, %.not2
  %.neg = add i32 %.neg3, %18
  %19 = or i32 %17, %.neg
  %20 = load i32, ptr %10, align 4
  %21 = shl nsw i32 %20, 1
  %22 = load i32, ptr %11, align 4
  %23 = and i32 %22, %20
  %24 = add i32 %23, %20
  %.neg4.neg = sub i32 %21, %24
  %25 = add i32 %19, -1
  %26 = add i32 %.neg4.neg, %20
  %27 = and i32 %25, %26
  %28 = sub nsw i32 %27, %20
  %29 = xor i32 %28, %22
  ret i32 %29"""

store_sample = "store i32 %0, ptr %10, align 4"

short_sample = """%10 = add nsw i32 %0, %1
  ret i32 %10"""

single_line = "%10 = add nsw i32 %0, %1"
ret_line = "ret i32 %10"



def create_node(body, def_dict:dict, parent=None):
    # recursive cases until we hit a name with no dictionary def, in which case it's a parameter or a constant
    # look up the ir_varname in the dict, and build the node for it correspondingly
    # unary: sub 0, x
    #        xor x, -1
    # binary:
    #       add %4, %5 <- these two require lookups
    #

    if isinstance(body, str):
        body = [body]


    if (len(body) == 1):
        ir_name = body[0]
        # constant, varname, or another expression
        if ir_name[0] == "%":
            if ir_name in def_dict.keys():
                return create_node(def_dict[ir_name], def_dict)
            else:
                # parameter
                return VarNode(ir_name)
        else:
            # constant
            return ConstNode(ir_name)

    # multiple operands, process each one individually; there should be 3 items in the list
    # get operation, LH, RH
    if len(body) != 3:
        print("Error processing IR expression: " + str(body))
        exit(0)

    operation = body[0]
    left = body[2]
    right = body[1]

    # unary ops are encoded a special way, we have to detect them.
    # bitwise negation = xor op1, -1
    # bitwise negation = sub op1, 0

    if (operation == "xor" and left == "-1"):
        return UnaryOpNode(Operation.B_NEGATE, create_node([right], def_dict))

    if (operation == "sub" and right == "0"):
        # Further simplification: if the created node is a negation, then this is equivalent to the node +1.
        # For instance: -~%0 is equivalent to %0 + 1.
        target = create_node([left], def_dict)
        if isinstance(target, UnaryOpNode):
            if target.op == Operation.B_NEGATE:
                return BinaryOpNode(Operation["ADD"], create_node([right], def_dict), ConstNode("1"))
        else:
            return UnaryOpNode(Operation.ARITH_NEG, create_node([left], def_dict))

    # binary ops
    if operation == "ashr":
        operation = "shr"
    if operation == "sdiv":
        operation = "div"
    return BinaryOpNode(Operation[operation.upper()], create_node([right], def_dict), create_node([left], def_dict))


def build_tree(ret_val, def_dict):
    #return create_node(ret_val, def_dict)
    newtree = ExpressionTree(create_node(ret_val, def_dict))
    newtree.set_parents()

    return newtree

def build_ir_dict(ins_text_list, def_dict):
    for l in ins_text_list.split("\n"):
        l = l.strip()
        if "alloca" in l or l == "\n" or len(l) == 0 or l == ' ':
            continue
        name, expr_pieces = parse_instruction(l)
        def_dict[name] = expr_pieces


    #print(def_dict)
    return def_dict


def parse_instruction(ins_text):
    # return tuple: operation, arg1, arg2 if it exists; as strings
    # also, build the dictionary as we go
    # ex: %48 = sub nsw i32 0, %47
    # store_sample = "store i32 %0, ptr %10, align 4"
    #
    # short_sample = """%10 = add nsw i32 %0, %1
    #                   ret i32 %10"""
    #ir_var, ir_def = ins_text.split(" = ")

    #ins_text = ins_text.strip()

    # we're expecting either a store, a ret,  or a x = x format
    #components = ins_text.split(" ")
    if "store" in ins_text:
        pieces = ins_text.split(" ")
        names = [i for i in pieces if i[0].lower() == "%"]
        names = [i.replace(",", "") for i in names]
        return (names[1], [names[0]])

    if "ret" in ins_text:
        #print("debug ret string: " + ins_text)
        pieces = ins_text.split(" ")
        for p in pieces:
            if p[0] == '%':
                p = p.strip(",")

        return ("ret", pieces[2])

    # past the two special cases, now try for a " = " instruction

    name = None
    body = None

    try:
        name, body = ins_text.split(" = ")
    except:
        print("Couldn't parse string: " + ins_text)


    # # %19 = load i32, ptr %10, align 4
    if "load" in ins_text:
        pieces = body.split(" ")
        for p in pieces:
            if p[0] == '%':
                p = p.strip(",")
                return (name, [p])
        # if we got to the end of this loop and haven't returned, something is wrong
        print("Error: while processing load instruction in parse_instruction, no varname parsed")
        print("Exiting.")
        exit(0)

    # operations
    # format: split on commas, then spaces
    # the last element at the end of each comma-split list is the varname.
    comma_pieces = None
    try:
        comma_pieces = body.split(",")
    except:
        print("Couldn't split on comma: " + comma_pieces)

    left = comma_pieces[0].split(" ")[-1]
    right = comma_pieces[1].split(" ")[-1]
    operation = body.split(" ")[0]

    return name, [operation, left, right]


def get_expr_tree_from_ir_body(ir_text):
    cur_ir_dict = {}
    build_ir_dict(ir_text, cur_ir_dict)
    tree = build_tree(cur_ir_dict["ret"], cur_ir_dict)
    return tree


def get_all_funcs_with_mba_in_name_from_ll_file(ir_full_text):
    mba_func_dict = {}
    # load file text into memory
    cur_func_text = ""
    cur_func_name = ""
    capture = False
    lines = ir_full_text.split("\n")
    for line in lines:
        line += "\n"
        if "mba_" in line and "define" in line:
            start_index = line.index("@")
            end_index = line.index("(")
            func_name = line[start_index+1:end_index]
            capture = True
            continue # skip the prototype, continue to next line

        if "ret" in line:
            capture = False
            cur_func_text += line
            mba_func_dict[func_name] = cur_func_text
            cur_func_text = ""

        if capture == True:
            cur_func_text += line

    return mba_func_dict


def single_expression_to_tree(expression, name="generic", optimized=False):
    result = get_llvm_ir_single_expr(expression, name, optimized)
    opts=[]
    if optimized:
        opts = ["gvn", "instcombine<no-verify-fixpoint>"]
        result = run_opts_on_ll_text(result, opts)

    mba_dict = get_all_funcs_with_mba_in_name_from_ll_file(result)
    lifted = get_expr_tree_from_ir_body(mba_dict["mba_" + name])

    return lifted


def run_opts_on_ll_text(ll_full_text, opt_list):
    opt_passes_str = ','.join(opt_list)

    #opt_command = f'echo \'{ll_full_text}\' | /usr/local/bin/opt -S -passes="{opt_passes_str}"'
    opt_command = f'echo \'{ll_full_text}\' | {opt_path} -S -passes="{opt_passes_str}"'
    subprocess.run(opt_command, shell="True", capture_output=True, text=True)

    devnull = open(os.devnull, 'w')
    # subprocess.run(opt_command, shell="True", stdout=devnull, stderr=devnull)
    result = subprocess.run(opt_command, shell="True", capture_output=True , text=True)
    return result.stdout

