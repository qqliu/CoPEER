window.COPEER_DATA = window.COPEER_DATA || {};
window.COPEER_DATA["localization_main"] = {
 "source": {
  "commit": "cb9312a",
  "main_tex_sha256": "8e2d3c7cbed3535cf6ba877ab7b01e06042ec205f8c97ec74b41c34382cdfb53",
  "label": "tab:localization",
  "main_tex_lines": [
   869,
   895
  ],
  "caption": "Reference-line selection on the 100 primary inputs of the human-approved core. Both Hit@1 and Hit@3 count responses that do not meet the rules as misses. \"Met rules\" counts responses that follow the response and execution rules (required format, token budget, and no disallowed tool use or extra turns). The token column reports recorded primary input and output tokens (lower bound). The thirteenth configuration, Haiku, has two reporting views shown in Appendix [ref:app:certified-localization], which gives all 13 configurations, token components, and failure modes."
 },
 "columns": [
  "Model configuration",
  "First choice is a reference line Hit@1 (%) [95% CI]",
  "Reference line in top three Hit@3 (%) [95% CI]",
  "Recorded total tokens (lower bound)",
  "Met rules (of 100)"
 ],
 "rows": [
  {
   "name": "Sonnet 5",
   "hit1": {
    "value": 61.0,
    "ci95": [
     52.0,
     69.6
    ]
   },
   "hit3": {
    "value": 76.0,
    "ci95": [
     67.7,
     83.7
    ]
   },
   "recorded_total_tokens": 697281,
   "met_rules_of_100": 96,
   "kind": "model"
  },
  {
   "name": "Opus 5.5",
   "hit1": {
    "value": 68.0,
    "ci95": [
     59.8,
     76.2
    ]
   },
   "hit3": {
    "value": 85.0,
    "ci95": [
     78.6,
     91.0
    ]
   },
   "recorded_total_tokens": 510187,
   "met_rules_of_100": 96,
   "kind": "model"
  },
  {
   "name": "DeepSeek R1 Qwen",
   "hit1": {
    "value": 22.0,
    "ci95": [
     14.4,
     30.1
    ]
   },
   "hit3": {
    "value": 28.0,
    "ci95": [
     20.0,
     36.4
    ]
   },
   "recorded_total_tokens": 428199,
   "met_rules_of_100": 87,
   "kind": "model"
  },
  {
   "name": "Gemma 3 27B",
   "hit1": {
    "value": 26.0,
    "ci95": [
     18.3,
     33.7
    ]
   },
   "hit3": {
    "value": 44.0,
    "ci95": [
     35.7,
     52.1
    ]
   },
   "recorded_total_tokens": 340082,
   "met_rules_of_100": 100,
   "kind": "model"
  },
  {
   "name": "GLM 4.5 Air",
   "hit1": {
    "value": 10.0,
    "ci95": [
     4.9,
     16.0
    ]
   },
   "hit3": {
    "value": 11.0,
    "ci95": [
     5.8,
     17.2
    ]
   },
   "recorded_total_tokens": 1658280,
   "met_rules_of_100": 23,
   "kind": "model"
  },
  {
   "name": "GPT-OSS 120B",
   "hit1": {
    "value": 49.0,
    "ci95": [
     39.6,
     58.3
    ]
   },
   "hit3": {
    "value": 60.0,
    "ci95": [
     51.0,
     69.0
    ]
   },
   "recorded_total_tokens": 450420,
   "met_rules_of_100": 97,
   "kind": "model"
  },
  {
   "name": "GPT-OSS 20B",
   "hit1": {
    "value": 43.0,
    "ci95": [
     34.3,
     52.0
    ]
   },
   "hit3": {
    "value": 47.0,
    "ci95": [
     37.8,
     56.6
    ]
   },
   "recorded_total_tokens": 708462,
   "met_rules_of_100": 89,
   "kind": "model"
  },
  {
   "name": "Kimi Linear",
   "hit1": {
    "value": 14.0,
    "ci95": [
     7.2,
     21.4
    ]
   },
   "hit3": {
    "value": 27.0,
    "ci95": [
     19.0,
     35.7
    ]
   },
   "recorded_total_tokens": 241035,
   "met_rules_of_100": 94,
   "kind": "model"
  },
  {
   "name": "Nemotron 3.5 Lightning",
   "hit1": {
    "value": 27.0,
    "ci95": [
     19.0,
     35.6
    ]
   },
   "hit3": {
    "value": 27.0,
    "ci95": [
     18.8,
     35.4
    ]
   },
   "recorded_total_tokens": 1676079,
   "met_rules_of_100": 41,
   "kind": "model"
  },
  {
   "name": "Nemotron 3 Super",
   "hit1": {
    "value": 48.0,
    "ci95": [
     40.2,
     56.1
    ]
   },
   "hit3": {
    "value": 48.0,
    "ci95": [
     40.2,
     56.0
    ]
   },
   "recorded_total_tokens": 740935,
   "met_rules_of_100": 90,
   "kind": "model"
  },
  {
   "name": "Gemini 3.1 Pro",
   "hit1": {
    "value": 73.0,
    "ci95": [
     65.1,
     80.6
    ]
   },
   "hit3": {
    "value": 85.0,
    "ci95": [
     78.2,
     91.2
    ]
   },
   "recorded_total_tokens": 1446420,
   "met_rules_of_100": 93,
   "kind": "model"
  },
  {
   "name": "GPT-5.6 Luna",
   "hit1": {
    "value": 63.0,
    "ci95": [
     54.6,
     71.1
    ]
   },
   "hit3": {
    "value": 74.0,
    "ci95": [
     66.7,
     80.8
    ]
   },
   "recorded_total_tokens": 390142,
   "met_rules_of_100": 97,
   "kind": "model"
  },
  {
   "name": "TF-IDF centroid similarity",
   "hit1": {
    "value": 18.0,
    "ci95": [
     11.0,
     25.3
    ]
   },
   "hit3": null,
   "recorded_total_tokens": null,
   "met_rules_of_100": null,
   "kind": "baseline"
  },
  {
   "name": "Random-line expectation",
   "hit1": {
    "value": 6.7,
    "ci95": [
     5.7,
     7.8
    ]
   },
   "hit3": null,
   "recorded_total_tokens": null,
   "met_rules_of_100": null,
   "kind": "baseline"
  }
 ]
};
