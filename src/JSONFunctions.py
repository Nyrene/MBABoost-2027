from json import JSONDecodeError

from src.ExpressionTree import ExpressionTree
import json
from enum import Enum
import time

#filepaths
OUT_FOLDER = "../scratch-space-delete/" # switch this when done with testing
TEST_FILENAME = "testing_json.txt"

# these files have the traits info
traits_mbaobf_linear_filepath = "datasets/mba-traits/mbaobf_linear.txt"
traits_mbaobf_poly_filepath = "datasets/mba-traits/mbaobf_poly.txt"
traits_qsynth_filepath = "datasets/mba-traits/qsynth.txt"
traits_floki_filepath = "datasets/mba-traits/floki.txt"
traits_loki_filepath = "datasets/mba-traits/loki.txt"


class DatasetKeywords(Enum):
    SIZE = "size"
    ORIG_MBA = "original mba"
    OPT_MBA = "optimized mba"
    DEOBF_MBA = "deobfuscated mba"
    GT_OPT_TRAITS = "optimized gt traits"
    GT = "ground truth"
    OPT_GT = "optimized ground truth"
    ALT_PERC = "% alternated"
    UNIQUE_PERC = "% unique"
    CSE_PERC = "% cse"
    NUM_EQ_SUBTREES = "num equivalent subtrees to GT"
    EQ_SUBTREES_PERC = "% equivalent subtrees"
    SIZE_INCREASE_PERC_FROM_GT = "% size mba increase from GT "
    SIZE_REDUC_PERC = "% size reduction" # filename/info will indicate from what to what

    DICT_MBA_TRAITS = "traits"

    # names of sub-dictionaries in opt file
    DICT_OPT_GT = "optimized gt traits"
    DICT_OPT_MBA = "optimized mba traits"
    TRUE = "true"
    FALSE = "false"

    # tool output
    #TD: rename this TOOL_OUTPUT. SIMPLIFIED_MBA is extremely confusing here,
    # this is the unparsed result. # rename all the keys in the JSON file.
    SIMPLIFIED_MBA = "tool output"
    PARSED_MBA_STR = "deobf mba expression"
    PERC_SIZE_CHANGE_DEOBF_FROM_MBA = "% size change from MBA"
    # SIZE_INCREASE_PERC_FROM_GT reuse trait from MBA traits dict

    # deobf errors
    DEOBF_ERROR_PRESENT = "Tool error"
    DEOBF_ERROR_TIMEOUT = "error: tool timed out"
    DEOBF_ERROR_EXCLUDE = "result excluded from dataset because optimized ground truth has single var or no ops"
    DEOBF_ERROR_FAILED = "error: tool errored unsolveable"
    DEOBF_ERROR_OTHER = "error: unspecified"
    DEOBF_ERROR_UNSUPPORTED_OP = "MBABoost eval script cannot process exponentiation"

    # errors
    OPT_ERROR = "optimization error"


    # tool names
    GAMBA = "GAMBA"
    MSYNTH = "MSYNTH"
    PROMBA = "PROMBA"

def save_dataset_dictionary(input_dict, filename):
    print("Saving dictionary to file: " + filename)
    with open(filename, 'w') as filehandle:
        json.dump(input_dict, filehandle, indent=3)

    return




def load_data(filename):
    with open(filename, 'r') as filehandle:
        dataset_dict = json.load(filehandle)
    return dataset_dict



# testing it out
#sample_dict = {1: "one", 2: "two", 3: "three"}
#save_dataset_dictionary(sample_dict, OUT_FOLDER + TEST_FILENAME)

#loaded = load_data(OUT_FOLDER + TEST_FILENAME)
#print(json.dumps(loaded))