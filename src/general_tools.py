import random


def test_func(x, y):
    print(str(x + y))

def test_equivalent_by_brute_force(expr1, expr2, exit_on_false=False, print_out=True):
    random.seed()
    if print_out:
        print("\tIn test equivalence function, given:")
        print("\te1: " + expr1)
        print("\te2: " + expr2)
    #e1 = ast.parse(expr1)
    #e2 = ast.parse(expr2)

    for i in range(0, 1000):
        x = random.randint(0, 1000)
        y = random.randint(0, 1000)
        c = random.randint(0, 1000)
        t = random.randint(0, 1000)
        d = random.randint(0, 1000)
        e = random.randint(0, 1000)
        f = random.randint(0, 1000)
        a = random.randint(0, 1000)
        b = random.randint(0, 1000)
        z = random.randint(0, 1000)
        g = random.randint(0, 1000)
        h = random.randint(0, 1000)
        try:
            res1 = eval(expr1)
        except Exception as e:
            print("Couldn't eval expression: " + str(expr1))
            print("\t exception: " + str(e))
            return False

        try:
            res2 = eval(expr2)
        except Exception as e2:
            print("Couldn't eval expression: " + str(expr2))
            print("\t exception: " + str(e2))
            return False

        if res1 != res2:
            if print_out:
                #print("For inputs: " + str(x) + ", " + str(y))
                print("False results, outputs: " + str(res1) + " " + str(res2))
            if exit_on_false:
                exit(0)
            return False

    #print("No mismatches found, expressions are equal")
    return True

def gen_random_constants():
    first = random.randint(-200, 0)
    second = random.randrange(0, 150)
    third = (second + first) * -1

    #print("Selected numbers are: " + str(first) + ", " + str(second) + ",  " + str(third))
    return (first, second, third)

#def print_llvm_rule_results():
#    print("Original: x + y")
#    r_add_2 = "(x ^ y) + 2 * (x & y)"
#    print("Rule: " + r_add_2)
#
#    print("Result" + str(single_expression_to_tree(r_add_2)))
#
#    return


def parse_str_from_GAMBA_output(stdout_str):
    gamba_out = stdout_str
    for l in stdout_str.split("\n"):
        if "simplified" in l:
            key_str = "simplified to"
            index = l.find("simplified to")
            gamba_out = l[index+len(key_str):len(l)]
            gamba_out = gamba_out.replace("\n", "")
            gamba_out = gamba_out.lstrip()
            #gamba_out = l.replace("*** ... simplified to", "")
            break

    return gamba_out

def parse_str_from_MSYNTH_output(stdout_str):
    msynth_out = stdout_str

    for l in stdout_str.split("\n"):
        if "simplified" in l:
            msynth_out = l
            msynth_out = l.replace("simplified:", "")
            msynth_out = msynth_out.rstrip()
            #print("inside if statement: " + msynth_out)
            break
    #print("debugging msynth function: stdout_str is: " + stdout_str)
   # print("returning: " + msynth_out)
    return msynth_out

