window.COPEER_DATA = window.COPEER_DATA || {};
window.COPEER_DATA["instruction_summary"] = {
 "source": {
  "commit": "cb9312a",
  "main_tex_sha256": "8e2d3c7cbed3535cf6ba877ab7b01e06042ec205f8c97ec74b41c34382cdfb53",
  "label": "tab:instruction-main",
  "main_tex_lines": [
   1095,
   1116
  ],
  "caption": "Counterexample-first search versus sequential review or proof attempt, with a concrete counterexample required in both conditions. Confirmed objections are graded by a model using the reference counterexample. A token ratio below one favors search. Ratios compare summed usage across accepted attempts rather than averaging per-task ratios, and exclude grading and downstream verification. Recorded total tokens are uncached input, cached input, and output (reasoning counted once within output), plus reported auxiliary-model tokens in the 60-statement panel. Opus 5 proof-panel token accounting is provisional."
 },
 "header": [
  "Model",
  "Confirmed objections: Search",
  "Confirmed objections: Sequential",
  "Search / sequential usage: Output ratio [95% interval]",
  "Search / sequential usage: Recorded total-token ratio [95% interval]"
 ],
 "rows": [
  {
   "section": "100 proof inputs per model"
  },
  {
   "model": "Sol",
   "search_confirmed": 95,
   "sequential_confirmed": 93,
   "output_ratio": {
    "value": 0.689,
    "ci95": [
     0.594,
     0.802
    ]
   },
   "recorded_total_ratio": {
    "value": 0.958,
    "ci95": [
     0.833,
     1.083
    ]
   }
  },
  {
   "model": "Gemini",
   "search_confirmed": 84,
   "sequential_confirmed": 89,
   "output_ratio": {
    "value": 0.854,
    "ci95": [
     0.789,
     0.921
    ]
   },
   "recorded_total_ratio": {
    "value": 0.65,
    "ci95": [
     0.441,
     0.941
    ]
   }
  },
  {
   "model": "Opus 5",
   "search_confirmed": 81,
   "sequential_confirmed": 76,
   "output_ratio": {
    "value": 0.714,
    "ci95": [
     0.62,
     0.814
    ]
   },
   "recorded_total_ratio": {
    "value": 0.831,
    "ci95": [
     0.762,
     0.902
    ]
   }
  },
  {
   "section": "60 statement inputs per model"
  },
  {
   "model": "Sol",
   "search_confirmed": 60,
   "sequential_confirmed": 59,
   "output_ratio": {
    "value": 0.593,
    "ci95": [
     0.457,
     0.791
    ]
   },
   "recorded_total_ratio": {
    "value": 0.959,
    "ci95": [
     0.928,
     0.982
    ]
   }
  },
  {
   "model": "Gemini",
   "search_confirmed": 58,
   "sequential_confirmed": 57,
   "output_ratio": {
    "value": 0.739,
    "ci95": [
     0.569,
     0.889
    ]
   },
   "recorded_total_ratio": {
    "value": 0.903,
    "ci95": [
     0.755,
     1.063
    ]
   }
  },
  {
   "model": "Opus",
   "search_confirmed": 60,
   "sequential_confirmed": 60,
   "output_ratio": {
    "value": 0.476,
    "ci95": [
     0.24,
     0.94
    ]
   },
   "recorded_total_ratio": {
    "value": 0.849,
    "ci95": [
     0.685,
     0.983
    ]
   }
  }
 ]
};
