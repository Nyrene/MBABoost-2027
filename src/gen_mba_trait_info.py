from src.LLVMTools import single_expression_to_tree
from src.ExtraTreeFunctions import *
from src.EvalFunctions import *
from time import time
from src.JSONFunctions import *


""" structure:
{ number {
            mba: 
            gt:
            traits: {
                        percent_cse:
                        ...
                    }

          }
}
"""


def gen_traits_for_file(filename):
    dataset_dict:dict = load_data(filename)

    for k, v in dataset_dict.items():
        print("On entry: " + k)
        v["traits"] = gen_mba_traits_sub_dict(v[DatasetKeywords.ORIG_MBA.value], v[DatasetKeywords.GT.value])

    save_dataset_dictionary(dataset_dict, filename)

def gen_full_entry_mba_traits(mba, gt=None):
    entry = {}
    entry[DatasetKeywords.ORIG_MBA.value] = mba
    if not gt is None:
        entry[DatasetKeywords.GT.value] = gt

    entry[DatasetKeywords.DICT_MBA_TRAITS.value] = gen_mba_traits_sub_dict(mba, gt)

    return entry

def gen_mba_traits_sub_dict(mba, gt=None):
    mba_tree = mba

    # can accept node or string
    if (isinstance(mba, str)):
        mba_tree = single_expression_to_tree(mba)

    new_dict = {}
    new_dict[DatasetKeywords.SIZE.value] = mba_tree.get_size()
    new_dict[DatasetKeywords.ALT_PERC.value] = get_percent_alternated(mba_tree)
    new_dict[DatasetKeywords.UNIQUE_PERC.value] = get_percentage_unique(mba_tree)
    new_dict[DatasetKeywords.CSE_PERC.value] = get_percentage_cse(mba_tree)

    # things that require the GT
    if not gt is None and gt != "":
        gt_tree = gt
        if (isinstance(gt, str)):
            gt_tree = single_expression_to_tree(gt)
        new_dict[DatasetKeywords.NUM_EQ_SUBTREES.value] = len(get_equivalent_synth_terms(gt_tree, mba_tree))
        #new_dict[DatasetKeywords.EQ_SUBTREES_PERC.value] = get_percentage_equivalent_synth_terms(gt_tree, mba_tree)
        new_dict[DatasetKeywords.SIZE_INCREASE_PERC_FROM_GT.value] = calc_percent_size_increase_node1_to_node2(gt_tree, mba_tree)

    return new_dict

def print_traits_for_node(input_mba, gt=None):
    print_output_dict(gen_mba_traits_sub_dict(input_mba, gt))
    return

def print_output_dict(input_dict):
    print(json.dumps(input_dict, indent=3))
    return

# testing out the traits dictionary
"""
sample_mba = "(x + y) * (3 & x)"
gt = "(3 & x) * 8"


result_dict = output_traits_for_mba_as_dict(sample_mba, gt).items()
for k, v in result_dict:
    print(k + ": " + str(v))
"""

"""
print("generating dataset info: ")
start = time.time()
print("Start time: " + str(start))

print("MBAObf Linear")
gen_traits_for_file(traits_mbaobf_linear_filepath)
print("MBAObf poly")
gen_traits_for_file(traits_mbaobf_poly_filepath)
print("QSynth")
gen_traits_for_file(traits_qsynth_filepath)
print("loki")
gen_traits_for_file(traits_loki_filepath)
#gen_traits_for_file(input_floki_filepath) LLVM throws poison values for a lot of the
                                # expressions in this dataset; run will not succeed

end = time.time()
print("Done! Current time: " + str(end))
elapsed = end - start
print("Elapsed time: " + str(elapsed))
"""