# Executable witness checking

The complete 604-task frame includes every input, every saved search result, all 351 saved witness-check judgments, and available generated witness/checker programs. Searches found 351 proposed witnesses and reported 12 exhaustive finite searches, 221 inconclusive searches, and 20 claims outside the finite-refutation setting. Separately written checkers confirmed 348 proposed witnesses and rejected three.

Run `python studies/executable_checks/replay.py` (Python 3.9+, standard library) to reproduce these counts from individual result files. The replay checks saved results and does not execute generated programs. `checkers/<record>/` supplies the archived Python/JSON artifacts for inspecting the mathematical checks. Record filenames replace spaces with underscores. `source/` contains the original search/driver source with author machine paths anonymized. The complete original input frame and all unsuccessful outcomes remain included.
