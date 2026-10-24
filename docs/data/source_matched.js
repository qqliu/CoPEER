window.COPEER_DATA = window.COPEER_DATA || {};
window.COPEER_DATA["source_matched"] = {
 "source": {
  "commit": "cb9312a",
  "main_tex_sha256": "8e2d3c7cbed3535cf6ba877ab7b01e06042ec205f8c97ec74b41c34382cdfb53",
  "label": "tab:reference-sensitivity",
  "main_tex_lines": [
   1574,
   1581
  ],
  "caption": "The 22 source-matched cases from the instruction study. Counts compare search with sequential review with a counterexample required, under the common September grades. Ratios compare accepted solver-attempt token sums. Intervals use the paired 20,000-resample analysis described in Section [ref:app:primary-witness-accounting]."
 },
 "header": [
  "Model",
  "Catches",
  "Δ catches (pp)",
  "Output ratio",
  "Recorded total-token ratio"
 ],
 "rows": [
  {
   "model": "GPT-5.6 Sol",
   "catches": {
    "pair": [
     22,
     21
    ]
   },
   "delta_catches_pp": {
    "value": 4.5,
    "ci95": [
     0.0,
     13.6
    ]
   },
   "output_ratio": {
    "value": 0.759,
    "ci95": [
     0.633,
     0.919
    ]
   },
   "recorded_total_ratio": {
    "value": 0.986,
    "ci95": [
     0.981,
     0.993
    ]
   }
  },
  {
   "model": "Gemini 3.1 Pro",
   "catches": {
    "pair": [
     21,
     20
    ]
   },
   "delta_catches_pp": {
    "value": 4.5,
    "ci95": [
     -9.1,
     18.2
    ]
   },
   "output_ratio": {
    "value": 0.721,
    "ci95": [
     0.626,
     0.819
    ]
   },
   "recorded_total_ratio": {
    "value": 0.909,
    "ci95": [
     0.863,
     0.951
    ]
   }
  },
  {
   "model": "Opus 5",
   "catches": {
    "pair": [
     19,
     19
    ]
   },
   "delta_catches_pp": {
    "value": 0.0,
    "ci95": [
     -13.6,
     13.6
    ]
   },
   "output_ratio": {
    "value": 0.703,
    "ci95": [
     0.627,
     0.784
    ]
   },
   "recorded_total_ratio": {
    "value": 0.948,
    "ci95": [
     0.866,
     1.031
    ]
   }
  }
 ]
};
