window.COPEER_DATA = window.COPEER_DATA || {};
window.COPEER_DATA["claims60_sensitivity"] = {
 "source": {
  "commit": "cb9312a",
  "main_tex_sha256": "8e2d3c7cbed3535cf6ba877ab7b01e06042ec205f8c97ec74b41c34382cdfb53",
  "label": "tab:claims60-all-sensitivities",
  "main_tex_lines": [
   2418,
   2455
  ],
  "caption": "Claims60 instruction and subset sensitivity. S denotes search; F full proof attempt, O ordinary early stop, and W early stop requiring a witness. Counts use preserved grades; token ratios are S/comparator. Tool-free means no recorded additional execution in either paired cell. Exclusions are descriptive. Opus tool use is unrecorded, so no tool-free row is inferred. Output is the target model; recorded total tokens include every model reported in the accepted receipt."
 },
 "header": [
  "Model",
  "Arm",
  "Subset",
  "n",
  "Catches S/C",
  "Output",
  "Recorded total"
 ],
 "rows": [
  {
   "model": "Sol",
   "arm": "F",
   "subset": "All",
   "n": 60,
   "catches_s_c": {
    "pair": [
     60,
     59
    ]
   },
   "output_ratio": 0.544,
   "recorded_total_ratio": 0.954
  },
  {
   "model": "Sol",
   "arm": "F",
   "subset": "No hint",
   "n": 47,
   "catches_s_c": {
    "pair": [
     47,
     47
    ]
   },
   "output_ratio": 0.507,
   "recorded_total_ratio": 0.949
  },
  {
   "model": "Sol",
   "arm": "F",
   "subset": "Tool-free",
   "n": 60,
   "catches_s_c": {
    "pair": [
     60,
     59
    ]
   },
   "output_ratio": 0.544,
   "recorded_total_ratio": 0.954
  },
  {
   "model": "Sol",
   "arm": "F",
   "subset": "Both exclusions",
   "n": 47,
   "catches_s_c": {
    "pair": [
     47,
     47
    ]
   },
   "output_ratio": 0.507,
   "recorded_total_ratio": 0.949
  },
  {
   "model": "Sol",
   "arm": "O",
   "subset": "All",
   "n": 60,
   "catches_s_c": {
    "pair": [
     60,
     42
    ]
   },
   "output_ratio": 1.347,
   "recorded_total_ratio": 1.015
  },
  {
   "model": "Sol",
   "arm": "O",
   "subset": "No hint",
   "n": 47,
   "catches_s_c": {
    "pair": [
     47,
     36
    ]
   },
   "output_ratio": 1.26,
   "recorded_total_ratio": 1.011
  },
  {
   "model": "Sol",
   "arm": "O",
   "subset": "Tool-free",
   "n": 60,
   "catches_s_c": {
    "pair": [
     60,
     42
    ]
   },
   "output_ratio": 1.347,
   "recorded_total_ratio": 1.015
  },
  {
   "model": "Sol",
   "arm": "O",
   "subset": "Both exclusions",
   "n": 47,
   "catches_s_c": {
    "pair": [
     47,
     36
    ]
   },
   "output_ratio": 1.26,
   "recorded_total_ratio": 1.011
  },
  {
   "model": "Sol",
   "arm": "W",
   "subset": "All",
   "n": 60,
   "catches_s_c": {
    "pair": [
     60,
     59
    ]
   },
   "output_ratio": 0.593,
   "recorded_total_ratio": 0.959
  },
  {
   "model": "Sol",
   "arm": "W",
   "subset": "No hint",
   "n": 47,
   "catches_s_c": {
    "pair": [
     47,
     46
    ]
   },
   "output_ratio": 0.535,
   "recorded_total_ratio": 0.951
  },
  {
   "model": "Sol",
   "arm": "W",
   "subset": "Tool-free",
   "n": 60,
   "catches_s_c": {
    "pair": [
     60,
     59
    ]
   },
   "output_ratio": 0.593,
   "recorded_total_ratio": 0.959
  },
  {
   "model": "Sol",
   "arm": "W",
   "subset": "Both exclusions",
   "n": 47,
   "catches_s_c": {
    "pair": [
     47,
     46
    ]
   },
   "output_ratio": 0.535,
   "recorded_total_ratio": 0.951
  },
  {
   "model": "Gemini",
   "arm": "F",
   "subset": "All",
   "n": 60,
   "catches_s_c": {
    "pair": [
     58,
     42
    ]
   },
   "output_ratio": 0.858,
   "recorded_total_ratio": 1.031
  },
  {
   "model": "Gemini",
   "arm": "F",
   "subset": "No hint",
   "n": 47,
   "catches_s_c": {
    "pair": [
     46,
     37
    ]
   },
   "output_ratio": 0.768,
   "recorded_total_ratio": 1.028
  },
  {
   "model": "Gemini",
   "arm": "F",
   "subset": "Tool-free",
   "n": 59,
   "catches_s_c": {
    "pair": [
     57,
     42
    ]
   },
   "output_ratio": 0.844,
   "recorded_total_ratio": 0.968
  },
  {
   "model": "Gemini",
   "arm": "F",
   "subset": "Both exclusions",
   "n": 46,
   "catches_s_c": {
    "pair": [
     45,
     37
    ]
   },
   "output_ratio": 0.742,
   "recorded_total_ratio": 0.947
  },
  {
   "model": "Gemini",
   "arm": "O",
   "subset": "All",
   "n": 60,
   "catches_s_c": {
    "pair": [
     58,
     43
    ]
   },
   "output_ratio": 1.275,
   "recorded_total_ratio": 1.21
  },
  {
   "model": "Gemini",
   "arm": "O",
   "subset": "No hint",
   "n": 47,
   "catches_s_c": {
    "pair": [
     46,
     36
    ]
   },
   "output_ratio": 1.13,
   "recorded_total_ratio": 1.235
  },
  {
   "model": "Gemini",
   "arm": "O",
   "subset": "Tool-free",
   "n": 59,
   "catches_s_c": {
    "pair": [
     57,
     43
    ]
   },
   "output_ratio": 1.352,
   "recorded_total_ratio": 1.046
  },
  {
   "model": "Gemini",
   "arm": "O",
   "subset": "Both exclusions",
   "n": 46,
   "catches_s_c": {
    "pair": [
     45,
     36
    ]
   },
   "output_ratio": 1.198,
   "recorded_total_ratio": 1.027
  },
  {
   "model": "Gemini",
   "arm": "W",
   "subset": "All",
   "n": 60,
   "catches_s_c": {
    "pair": [
     58,
     57
    ]
   },
   "output_ratio": 0.739,
   "recorded_total_ratio": 0.903
  },
  {
   "model": "Gemini",
   "arm": "W",
   "subset": "No hint",
   "n": 47,
   "catches_s_c": {
    "pair": [
     46,
     45
    ]
   },
   "output_ratio": 0.689,
   "recorded_total_ratio": 0.942
  },
  {
   "model": "Gemini",
   "arm": "W",
   "subset": "Tool-free",
   "n": 57,
   "catches_s_c": {
    "pair": [
     56,
     55
    ]
   },
   "output_ratio": 0.654,
   "recorded_total_ratio": 0.923
  },
  {
   "model": "Gemini",
   "arm": "W",
   "subset": "Both exclusions",
   "n": 45,
   "catches_s_c": {
    "pair": [
     45,
     44
    ]
   },
   "output_ratio": 0.61,
   "recorded_total_ratio": 0.915
  },
  {
   "model": "Opus",
   "arm": "F",
   "subset": "All",
   "n": 60,
   "catches_s_c": {
    "pair": [
     60,
     60
    ]
   },
   "output_ratio": 0.888,
   "recorded_total_ratio": 0.983
  },
  {
   "model": "Opus",
   "arm": "F",
   "subset": "No hint",
   "n": 47,
   "catches_s_c": {
    "pair": [
     47,
     47
    ]
   },
   "output_ratio": 0.845,
   "recorded_total_ratio": 0.977
  },
  {
   "model": "Opus",
   "arm": "O",
   "subset": "All",
   "n": 60,
   "catches_s_c": {
    "pair": [
     60,
     60
    ]
   },
   "output_ratio": 1.355,
   "recorded_total_ratio": 1.043
  },
  {
   "model": "Opus",
   "arm": "O",
   "subset": "No hint",
   "n": 47,
   "catches_s_c": {
    "pair": [
     47,
     47
    ]
   },
   "output_ratio": 1.275,
   "recorded_total_ratio": 1.034
  },
  {
   "model": "Opus",
   "arm": "W",
   "subset": "All",
   "n": 60,
   "catches_s_c": {
    "pair": [
     60,
     60
    ]
   },
   "output_ratio": 0.476,
   "recorded_total_ratio": 0.849
  },
  {
   "model": "Opus",
   "arm": "W",
   "subset": "No hint",
   "n": 47,
   "catches_s_c": {
    "pair": [
     47,
     47
    ]
   },
   "output_ratio": 0.396,
   "recorded_total_ratio": 0.809
  }
 ]
};
