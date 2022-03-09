# CS6120 Advanced Compiler A6: SSA

This repository contains the pass to transform Bril program to SSA form and then transfrom back from SSA. There are two set of test cases: `ssa_roundtrip` and `to_ssa`. The first one does a roundtrip and then check the execution result with `brili`. The second test set convert program to SSA form then uses a script `is_ssa.py` to check if the result is in SSA form.

## Usage
```
❯ python main.py -h
usage: main.py [-h] [-from-ssa] [-to-ssa] [-roundtrip] [-visualize]
               [-f FILENAME]

optional arguments:
  -h, --help   show this help message and exit
  -from-ssa    Convert SSA-form program to original
  -to-ssa      Convert program to SSA form
  -roundtrip   Convert program to SSA form then convert it back
  -visualize   visualize results
  -f FILENAME  json file
```

Run with Bril utilities:

```
$ bril2json < *.bril | python main.py {-arg} 
```

To run all tests with `turnt`: 
```
❯ turnt to_ssa/*.bril
❯ turnt ssa_roundtrip/*.bril
```