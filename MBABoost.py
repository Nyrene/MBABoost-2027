import argparse

from fontTools.misc.cython import returns

import src.LLVMTools
from src.Obfuscator import Obfuscator
import subprocess

# If you have clang or opt installed in non-default locations, please specify them here.
src.LLVMTools.opt_path = "/usr/local/bin/opt"
src.LLVMTools.clang_path = "clang"


if __name__ == "__main__":

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description='Stronger MBA expression generator using bitwise identities.')

    if subprocess.run(src.LLVMTools.opt_path + " --version", shell="False", capture_output=True, text=True).stderr:
        print("Error: could not find opt. Please install it, or specify the path to it at the top of this file(MBABoost.py).")
        exit(0)

    if subprocess.run(src.LLVMTools.clang_path + " --version", shell="False", capture_output=True, text=True).stderr:
        print("Error: could not find clang. Please install it, or specify the path to it at the top of this file(MBABoost.py).")
        exit(0)

    # Add positional arguments
    parser.add_argument('ground_truth', type=str, help='Input expression, enclosed in quotes')
    #parser.add_argument('num2', type=int, help='The second number')

    # Parse the command - line arguments
    args = parser.parse_args()

    # Calculate and print the sum
    print("Input expression is: " + args.ground_truth)


    print("Starting obfuscation")
    obf_inst = Obfuscator(args.ground_truth)
    try_count = 0
    while try_count < 3:
        try:
            obf_inst.v2_run_obf()
            break
        except Exception as e:
            print("Exception occurred, or expression in progress did not pass equivalence checks.")
            print("Exception is: " + str(e))
            exit(0)
            print("Retrying (" + str(try_count) + "/3")
            try_count += 1
            continue



    print("\n\n**************************************************")
    print("\n For ground truth: " + args.ground_truth)
    print("\n\n" + "Final output: " + obf_inst.get_obf_expr_str())
    print("\n\n**************************************************")