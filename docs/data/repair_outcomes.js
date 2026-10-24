window.COPEER_DATA = window.COPEER_DATA || {};
window.COPEER_DATA["repair_outcomes"] = {
 "source": {
  "commit": "cb9312a",
  "main_tex_sha256": "8e2d3c7cbed3535cf6ba877ab7b01e06042ec205f8c97ec74b41c34382cdfb53",
  "label": "tab:repair_outcomes",
  "main_tex_lines": [
   1604,
   1620
  ],
  "caption": "First-attempt checker-accepted submissions on 16 source-derived repair tasks."
 },
 "header": [
  "Solver",
  "Condition",
  "PASS",
  "FAIL",
  "Absent"
 ],
 "rows": [
  {
   "solver": "Claude Opus 5.5",
   "condition": "A",
   "pass": 15,
   "fail": 0,
   "absent": 1
  },
  {
   "solver": "Claude Opus 5.5",
   "condition": "B",
   "pass": 15,
   "fail": 0,
   "absent": 1
  },
  {
   "solver": "Claude Sonnet 5",
   "condition": "A",
   "pass": 13,
   "fail": 3,
   "absent": 0
  },
  {
   "solver": "Claude Sonnet 5",
   "condition": "B",
   "pass": 15,
   "fail": 1,
   "absent": 0
  },
  {
   "solver": "GPT-OSS 120B",
   "condition": "A",
   "pass": 1,
   "fail": 10,
   "absent": 5
  },
  {
   "solver": "GPT-OSS 120B",
   "condition": "B",
   "pass": 2,
   "fail": 8,
   "absent": 6
  }
 ]
};
