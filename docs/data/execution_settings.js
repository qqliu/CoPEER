window.COPEER_DATA = window.COPEER_DATA || {};
window.COPEER_DATA["execution_settings"] = {
 "source": {
  "commit": "cb9312a",
  "main_tex_sha256": "8e2d3c7cbed3535cf6ba877ab7b01e06042ec205f8c97ec74b41c34382cdfb53",
  "label": "tab:ccl-execution-settings",
  "main_tex_lines": [
   2644,
   2668
  ],
  "caption": "Saved execution settings for the 13 model configurations. Every attempt has a 16,000-token output allowance and a 600-second wall limit, with the interface-specific enforcement described below. $T$ is temperature and $p$ is top-$p$; local generation uses vLLM 0.29.0 and seed 20260921. \"n.r.\" means the hosted CLI's numeric context-window limit was not recorded. Context limits, output-budget enforcement and recovery rules are specified below. Available version receipts agree across the initial, correction and recovery passes."
 },
 "header": [
  "Model",
  "Context tokens",
  "Generation setting",
  "Configured execution interface"
 ],
 "rows": [
  {
   "model": "Haiku 4.5",
   "context_tokens": {
    "value": null,
    "note": "not recorded"
   },
   "generation_setting": "Medium effort",
   "interface": "Claude CLI 2.1.275"
  },
  {
   "model": "Sonnet 5",
   "context_tokens": {
    "value": null,
    "note": "not recorded"
   },
   "generation_setting": "Medium effort",
   "interface": "Claude CLI 2.1.275"
  },
  {
   "model": "Opus 5.5",
   "context_tokens": {
    "value": null,
    "note": "not recorded"
   },
   "generation_setting": "Medium effort",
   "interface": "Claude CLI 2.1.280"
  },
  {
   "model": "DeepSeek R1 Qwen",
   "context_tokens": 32768,
   "generation_setting": "$T=0.6$, $p=0.95$",
   "interface": "Local vLLM"
  },
  {
   "model": "Gemma 3 27B",
   "context_tokens": 65536,
   "generation_setting": "Greedy",
   "interface": "Local vLLM"
  },
  {
   "model": "GLM 4.5 Air",
   "context_tokens": 65536,
   "generation_setting": "$T=0.6$, $p=0.95$; thinking",
   "interface": "Local vLLM"
  },
  {
   "model": "GPT-OSS 120B",
   "context_tokens": 131072,
   "generation_setting": "$T=0.6$, $p=0.95$; medium",
   "interface": "Local vLLM"
  },
  {
   "model": "GPT-OSS 20B",
   "context_tokens": 131072,
   "generation_setting": "$T=0.6$, $p=0.95$; medium",
   "interface": "Local vLLM"
  },
  {
   "model": "Kimi Linear",
   "context_tokens": 32768,
   "generation_setting": "$T=0.6$, $p=0.95$",
   "interface": "Local vLLM"
  },
  {
   "model": "Nemotron 3.5 Lightning",
   "context_tokens": 131072,
   "generation_setting": "$T=1.0$, $p=0.95$; thinking",
   "interface": "Local vLLM"
  },
  {
   "model": "Nemotron 3 Super",
   "context_tokens": 65536,
   "generation_setting": "$T=1.0$, $p=0.95$; thinking",
   "interface": "Local vLLM"
  },
  {
   "model": "Gemini 3.1 Pro",
   "context_tokens": {
    "value": null,
    "note": "not recorded"
   },
   "generation_setting": "Low effort",
   "interface": "agy 1.2.8"
  },
  {
   "model": "GPT-5.6 Luna",
   "context_tokens": {
    "value": null,
    "note": "not recorded"
   },
   "generation_setting": "Medium effort",
   "interface": "Codex CLI 0.155.1"
  }
 ]
};
