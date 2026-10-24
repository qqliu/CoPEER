window.COPEER_DATA = window.COPEER_DATA || {};
window.COPEER_DATA["open_problem_retrieval"] = {
 "source": {
  "commit": "cb9312a",
  "main_tex_sha256": "8e2d3c7cbed3535cf6ba877ab7b01e06042ec205f8c97ec74b41c34382cdfb53",
  "label": "tab:historical_retrieval",
  "main_tex_lines": [
   1680,
   1698
  ],
  "caption": "Paired-search components comparing BugBank retrieval (B) against a self-critique/audit condition (P). Component model token usage (B / P): Original $16,449,383 / 17,590,589$; Hard $1,683,108 / 2,050,662$; Continuation (incremental) $19,577,279 / 20,301,967$; Exploratory $1,370,760 / 1,710,782$; Targeted $1,372,591 / 1,436,842$."
 },
 "header": [
  "Component",
  "Paired units",
  "Audited-full (B / P)",
  "Both",
  "B-only / P-only",
  "Neither"
 ],
 "rows": [
  {
   "component": "Distinct targets, final endpoints",
   "paired_units": 36,
   "audited_full_b_p": {
    "pair": [
     12,
     11
    ]
   },
   "both": 11,
   "b_only_p_only": {
    "pair": [
     1,
     0
    ]
   },
   "neither": 24
  },
  {
   "component": "Protocol stages, descriptive",
   "paired_units": 58,
   "audited_full_b_p": {
    "pair": [
     12,
     11
    ]
   },
   "both": 11,
   "b_only_p_only": {
    "pair": [
     1,
     0
    ]
   },
   "neither": 46
  },
  {
   "component": "Original run",
   "paired_units": 31,
   "audited_full_b_p": {
    "pair": [
     9,
     8
    ]
   },
   "both": 8,
   "b_only_p_only": {
    "pair": [
     1,
     0
    ]
   },
   "neither": 22
  },
  {
   "component": "Hard-target run",
   "paired_units": 5,
   "audited_full_b_p": {
    "pair": [
     0,
     0
    ]
   },
   "both": 0,
   "b_only_p_only": {
    "pair": [
     0,
     0
    ]
   },
   "neither": 5
  },
  {
   "component": "Fixed-point continuation",
   "paired_units": 22,
   "audited_full_b_p": {
    "pair": [
     3,
     3
    ]
   },
   "both": 3,
   "b_only_p_only": {
    "pair": [
     0,
     0
    ]
   },
   "neither": 19
  },
  {
   "component": "Exploratory cohort",
   "paired_units": 6,
   "audited_full_b_p": {
    "pair": [
     0,
     0
    ]
   },
   "both": 0,
   "b_only_p_only": {
    "pair": [
     0,
     0
    ]
   },
   "neither": 6
  },
  {
   "component": "Targeted stress test",
   "paired_units": 6,
   "audited_full_b_p": {
    "pair": [
     1,
     1
    ]
   },
   "both": 1,
   "b_only_p_only": {
    "pair": [
     0,
     0
    ]
   },
   "neither": 5
  }
 ]
};
