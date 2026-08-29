Thank you for reviewing the artifact for MBABoost!


# Requirements and Setup
Python requirements can be found in requirements.txt.

To install:
Optionally, start a virtual environment, and then run:
``` 
pip3 install -r requirements.txt
```

or, depending on your system:
```
pip install -r requirements.txt
```

MBABoost also requires a recent version of Clang. This project used Apple Clang version 15.0, but any recent version should work.

# Usage:

To generate an MBA expression for a given ground truth, use the mbaboost.py script in this base folder. MBABoost supports expressions which contain all basic arithmetic operations (*, +, -, /) and bitwise operators (|, ^, &, ~, <<, >>).

Please note that MBABoost supports a limited set of variable names: a, b, c, d, e, f, t, x, y, z. 

``` example:

mbaboost.py "x + y" 
```

MBABoost, by default, expects ```opt``` to be installed in /usr/bin/opt. If this, or Clang, are installed in non-default locations, pleased set them using the following variables at the top of mbaboost.py:

```
src.LLVMTools.opt_path = "/usr/local/bin/opt"
src.LLVMTools.clang_path = "clang"

```


# Evaluation datasets
The datasets for our paper are stored as follows:

datasets/

    - original-mba-dataset-files/ // The comparison dataset files from prior works

    - mba-traits // the results of our analysis of each expression for both MBABoost and prior works, stored in JSON format. The origin of each dataset  (MBABoost-generated or original) is indicated in the filename.

    - optimized-mba // the LLVM-optimized form of each MBA expression, stored in JSON format.

    - tool-output // the raw output of each tool run on the datasets, stored in JSON format.

    - analysis-tool-output // the lifted MBA expression and analysis results for the tool output.
