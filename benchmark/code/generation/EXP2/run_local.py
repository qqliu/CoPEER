#!/usr/bin/env python3
"""Offline CCL lanes with exact weight pins and bounded, durable one-item dispatch.

--prepare-weights creates a manifest before freeze, without importing vLLM.
Inference requires --split and --approved-freeze; no automatic stopped-lane resume.

v4: every attempt carries attempt_class. The DISPATCH receipt is the boundary: a
failure before it (context preflight, tokenizer/worker error while preparing the
prompt) is a SETUP_FAILURE with no reservation and no charge and never looks like
a model answer; a failure after it is a physical attempt (TRANSPORT_FAILURE keeps
the single retry; BUDGET_EXHAUSTED and CONTRACT_VIOLATION are never retried).
Holds, consumed attempts and the carryover are the accounting layer's: check_holds()
re-reads lane/STOP.json and EXP/HOLD.json before every model load and, inside
reserve(), before EVERY reservation; a receipted tag is never dispatched again.

Local families (2026-09-22): the four remaining portfolio families are further
MODELS entries pinned to their validated single-GPU serving profiles. A spec may
name the files its checkpoint must carry (Kimi has no tokenizer.json: its
tokenizer is checkpoint code over tiktoken.model), extra engine arguments
(trust_remote_code, max_num_seqs, max_num_batched_tokens), chat-template kwargs
(GLM's enable_thinking); a spec's weight manifest lives beside the experiment
like the accepted lanes' (a test may point manifest_dir elsewhere). The
16000-token output allowance, the wall caps, the token caps and the attempt
classes are shared with the two accepted lanes: a prompt that does not fit
max_model_len - MAX_OUTPUT is a SETUP_FAILURE, never truncated.
"""
import argparse
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import queue
import signal
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import EXP, LOCAL_FAMILY_KEYS, MAX_OUTPUT, build_prompt, freeze_hash, load_items, read, safe, sha
from lane_accounting import (ATTEMPT_CLASSES, HOLD_NAME, MAX_PHYSICAL_ATTEMPTS, LaneAccounting, LaneHeld, LaneStopped,
                             attempt_receipts)

REQUIRED_FILES = ("config.json", "tokenizer_config.json", "tokenizer.json", "model.safetensors.index.json")
PORTFOLIO_MODELS = ("<repository>/experiments/single_model_bugbank/counterexample_search_critic/services"
                    "/portfolio_glm_kimi_v1/models")   # the official GLM/Kimi downloads (acquisition.json pins repo, revision and hashes)
MODELS = {
    "qwen3_32b": {"path": "<workspace>/serving/models/qwen3_32b", "max_model_len": 40960,
                  "sampling": {"temperature": 0.6, "top_p": 0.95, "top_k": 20, "seed": 20260921},
                  "note": "thinking mode on (chat-template default); vendor-recommended sampling, fixed seed"},
    "gemma3_27b": {"path": "<workspace>/serving/models/gemma3_27b", "max_model_len": 65536,
                   "sampling": {"temperature": 0.0, "seed": 20260921}, "note": "greedy"},
    # Local families (2026-09-22): context = the validated profile's context_limit (never above the checkpoint config),
    # sampling = the profile's with the fixed seed, engine_args = the extra arguments the profile's service passed to vLLM.
    # A profile's --reasoning-parser is an OpenAI-server option, not an engine argument: this runner keeps the raw
    # completion and parses only the visible answer after </think>. Manifests live beside the experiment (EXPERIMENT_FROZEN_FILES).
    "deepseek_r1_qwen_32b": {"path": "<workspace>/serving/models/deepseek_r1_qwen_32b", "max_model_len": 32768,
                             "sampling": {"temperature": 0.6, "top_p": 0.95, "seed": 20260921}, "engine_args": {},
                             "required_files": REQUIRED_FILES,
                             "note": "DeepSeek-R1-Distill-Qwen-32B (Qwen2ForCausalLM); the chat template ends the prompt with <think>, so the "
                                     "completion is reasoning up to </think> and only the text after it is parsed; profile sampling (equals "
                                     "generation_config), fixed seed; no extra engine arguments"},
    "phi4": {"path": "<workspace>/serving/models/phi4", "max_model_len": 16384,
             "sampling": {"temperature": 0.6, "top_p": 0.95, "seed": 20260921}, "engine_args": {"trust_remote_code": True},
             "required_files": REQUIRED_FILES,
             "note": "Phi-4 (Phi3ForCausalLM); no thinking mode; profile sampling, fixed seed; the profile's --trust-remote-code is replicated "
                     "although the checkpoint carries no custom code; the native 16384 context leaves 384 prompt tokens beside the shared "
                     "16000-token output allowance, so nearly every prompt is a SETUP_FAILURE recorded as a miss, never truncated"},
    "glm47_flash": {"path": PORTFOLIO_MODELS + "/glm47_flash", "max_model_len": 32768,
                    "sampling": {"temperature": 1.0, "top_p": 0.95, "seed": 20260921},
                    "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192}, "chat_template_kwargs": {"enable_thinking": True},
                    "required_files": REQUIRED_FILES + ("chat_template.jinja",),
                    "note": "GLM-4.7-Flash (Glm4MoeLiteForCausalLM, zai-org/GLM-4.7-Flash@7dd20894a642a0aa287e9827cb1a1f7f91386b67); thinking on "
                            "through chat_template_kwargs as the profile served it (the template ends the prompt with <|assistant|><think>; only "
                            "the text after </think> is parsed); profile sampling, fixed seed; profile engine arguments --max-num-seqs 1 "
                            "--max-num-batched-tokens 8192"},
    "kimi_linear_48b_a3b_instruct": {"path": PORTFOLIO_MODELS + "/kimi_linear_48b_a3b_instruct", "max_model_len": 32768,
                                     "sampling": {"temperature": 0.6, "top_p": 0.95, "seed": 20260921},
                                     "engine_args": {"trust_remote_code": True, "max_num_seqs": 1, "max_num_batched_tokens": 8192},
                                     "required_files": ("config.json", "model.safetensors.index.json", "tokenizer_config.json", "tiktoken.model",
                                                        "tokenization_kimi.py", "chat_template.jinja", "configuration_kimi.py", "modeling_kimi.py",
                                                        "special_tokens_map.json"),
                                     "note": "Kimi-Linear-48B-A3B-Instruct (KimiLinearForCausalLM, moonshotai/Kimi-Linear-48B-A3B-Instruct@"
                                             "e1df551a447157d4658b573f9a695d57658590e9); Instruct template without a thinking switch; the tokenizer "
                                             "is the checkpoint's TikTokenTokenizer (tokenization_kimi.py over tiktoken.model, no tokenizer.json) "
                                             "and needs trust_remote_code: the generic fallback changes token ids; the custom code files are bound by "
                                             "the manifest; profile sampling, fixed seed; profile engine arguments --max-num-seqs 1 "
                                             "--max-num-batched-tokens 8192"},
    # Epoch 2: seventeen model-card profiles; their manifests live beside the experiment.
    'gpt_oss_120b': {"path": "<workspace>/serving/models/gpt_oss_120b", "max_model_len": 131072,
                     "system_prompt_placement": "native_developer",
                     "system_prompt_deviation": "Native Harmony template renders benchmark system instructions in its developer block and inserts the current date in its system block.",
                     "sampling": {"temperature": 0.6, "top_p": 0.95, "seed": 20260921},
                     "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192}, "chat_template_kwargs": {"reasoning_effort": "medium"},
                     "required_files": REQUIRED_FILES + ("chat_template.jinja",), "note": "gpt-oss-120b (GptOssForCausalLM, openai/gpt-oss-120b; MoE weights MXFP4 in config quantization_config, 61 GB on "
                             "disk); context 131072 = config max_position_embeddings (yarn over 4096), under 100 GB so not capped; the "
                             "harmony chat template takes reasoning_effort (default medium) and renders the harness system prompt as the "
                             "developer '# Instructions' block; the template stamps the run date (strftime_now) into the system turn; the model "
                             "answers in harmony channels (analysis, then final) without </think>, so the whole completion is parsed by the "
                             "last-candidates-object rule; README.md and generation_config.json give no temperature/top_p, so the fallback "
                             "T 0.6 / top_p 0.95 applies with the fixed seed; engine arguments max_num_seqs 1, max_num_batched_tokens 8192; "
                             "no custom code, trust_remote_code not set"},
    'gpt_oss_20b': {"path": "<workspace>/serving/models/gpt_oss_20b", "max_model_len": 131072,
                    "system_prompt_placement": "native_developer",
                    "system_prompt_deviation": "Native Harmony template renders benchmark system instructions in its developer block and inserts the current date in its system block.",
                    "sampling": {"temperature": 0.6, "top_p": 0.95, "seed": 20260921},
                    "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192}, "chat_template_kwargs": {"reasoning_effort": "medium"},
                    "required_files": REQUIRED_FILES + ("chat_template.jinja",), "note": "gpt-oss-20b (GptOssForCausalLM, openai/gpt-oss-20b; MXFP4 MoE weights, 13 GB on disk); context 131072 = config "
                            "max_position_embeddings; same harmony template as gpt-oss-120b (reasoning_effort medium, system prompt rendered "
                            "as the developer block, run date stamped, no </think>: whole completion parsed); README.md and generation_config.json "
                            "give no temperature/top_p, fallback T 0.6 / top_p 0.95, fixed seed; engine arguments max_num_seqs 1, "
                            "max_num_batched_tokens 8192; no custom code"},
    'qwen3_8_27b': {"path": "<workspace>/serving/models/qwen3_8_27b", "max_model_len": 131072,
                    "sampling": {"temperature": 1.0, "top_p": 0.95, "top_k": 20, "seed": 20260921},
                    "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192}, "chat_template_kwargs": {"enable_thinking": True},
                    "required_files": REQUIRED_FILES + ("chat_template.jinja", "vocab.json", "merges.txt"), "note": "Qwen3.8-27B (Qwen3_5ForConditionalGeneration, Qwen/Qwen3.8-27B; bf16 dense hybrid linear/full attention with a "
                            "vision tower, 52 GB on disk); context 131072 = min(text_config max_position_embeddings 262144, 131072); thinking on "
                            "through enable_thinking (the template's default; it also applies its default reasoning_effort 'xhigh', rendered as a "
                            "sentence in the system turn) and the prompt ends with <think>, so only the text after </think> is parsed; sampling = "
                            "README.md 'Thinking Mode' recommendation T 1.0, top_p 0.95, top_k 20 (min_p 0, presence_penalty 0 and "
                            "repetition_penalty 1 are the engine defaults), fixed seed; engine arguments max_num_seqs 1, max_num_batched_tokens "
                            "8192; no custom code"},
    'qwen3_6_35b_a3b': {"path": "<workspace>/serving/models/qwen3_6_35b_a3b", "max_model_len": 131072,
                        "sampling": {"temperature": 1.0, "top_p": 0.95, "top_k": 20, "presence_penalty": 1.5, "seed": 20260921},
                        "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192}, "chat_template_kwargs": {"enable_thinking": True},
                        "required_files": REQUIRED_FILES + ("chat_template.jinja", "vocab.json", "merges.txt"), "note": "Qwen3.6-35B-A3B (Qwen3_5MoeForConditionalGeneration, Qwen/Qwen3.6-35B-A3B; bf16 MoE hybrid attention with a "
                                "vision tower, 67 GB on disk); context 131072 = min(text_config max_position_embeddings 262144, 131072); thinking on "
                                "through enable_thinking (the template's default; prompt ends with <think>, only the text after </think> is parsed); "
                                "sampling = README.md 'Thinking mode for general tasks' T 1.0, top_p 0.95, top_k 20, presence_penalty 1.5 (min_p 0 "
                                "and repetition_penalty 1 are the engine defaults), fixed seed; engine arguments max_num_seqs 1, "
                                "max_num_batched_tokens 8192; no custom code"},
    'qwen3_5_122b_a10b': {"path": "<workspace>/serving/models/qwen3_5_122b_a10b", "max_model_len": 65536,
                          "sampling": {"temperature": 1.0, "top_p": 0.95, "top_k": 20, "presence_penalty": 1.5, "seed": 20260921},
                          "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192, "tensor_parallel_size": 2}, "chat_template_kwargs": {"enable_thinking": True},
                          "required_files": REQUIRED_FILES + ("chat_template.jinja", "vocab.json", "merges.txt"), "note": "Qwen3.5-122B-A10B (Qwen3_5MoeForConditionalGeneration, Qwen/Qwen3.5-122B-A10B; bf16 MoE hybrid attention with "
                                  "a vision tower, 234 GB on disk); context 65536 = the cap for a checkpoint over 100 GB (native text_config "
                                  "max_position_embeddings 262144); The bf16 shards (251 GB) exceed one B200; this "
                                  "lane uses tensor_parallel_size 2 with run_local_tp2.sbatch and no quantization; thinking on through enable_thinking (template "
                                  "default; only the text after </think> is parsed); sampling = README.md 'Thinking mode for general tasks' T 1.0, "
                                  "top_p 0.95, top_k 20, presence_penalty 1.5, fixed seed; engine arguments max_num_seqs 1, max_num_batched_tokens "
                                  "8192; no custom code"},
    'phi4_reasoning_plus': {"path": "<workspace>/serving/models/phi4_reasoning_plus", "max_model_len": 32768,
                            "system_prompt_placement": "prepend_frozen_system_to_user",
                            "system_prompt_deviation": "Native template discards role=system; frozen benchmark system instructions are prepended verbatim to the user turn. Native vendor system prompt is retained.",
                            "sampling": {"temperature": 0.8, "top_p": 0.95, "top_k": 50, "seed": 20260921},
                            "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192},
                            "required_files": REQUIRED_FILES + ("vocab.json",), "note": "Phi-4-reasoning-plus (Phi3ForCausalLM, microsoft/Phi-4-reasoning-plus; bf16 dense, 28 GB on disk); context "
                                    "32768 = config max_position_embeddings (README 'Context length 32k'), leaving 16768 prompt tokens beside the "
                                    "shared 16000-token output allowance; reasons by default: the chat template (inside tokenizer_config.json) "
                                    "hard-codes Microsoft's reasoning system prompt (<think> ... </think> then the solution) and DISCARDS any "
                                    "role=system message, so this lane prepends the exact benchmark system instructions to the user turn while "
                                    "retaining the native vendor system prompt; only text after </think> is parsed; sampling = README.md 'inference must use' T 0.8, "
                                    "top_k 50, top_p 0.95 (= generation_config.json), fixed seed; engine arguments max_num_seqs 1, "
                                    "max_num_batched_tokens 8192; no custom code, trust_remote_code not set"},
    'gemma4_31b': {"path": "<workspace>/serving/models" + "/gemma4_31b", "max_model_len": 131072,
                   "sampling": {"temperature": 1.0, "top_p": 0.95, "top_k": 64, "seed": 20260921},
                   "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192}, "chat_template_kwargs": {"enable_thinking": True},
                   "required_files": REQUIRED_FILES + ("chat_template.jinja", "processor_config.json"), "note": "Gemma 4 31B-it (Gemma4ForConditionalGeneration, google/gemma-4-31B-it@842da3794eaa0b77d5f08bae87a17459d91ff475; "
                           "text-only prompts through the multimodal class vLLM 0.29 registers, whose processor reads processor_config.json); "
                           "context 131072 = min(text_config.max_position_embeddings 262144, 131072), 62.6 GB bf16 checkpoint; sampling = the "
                           "model card's Best Practices (= generation_config.json): temperature 1.0, top_p 0.95, top_k 64; thinking on through "
                           "chat_template_kwargs enable_thinking (the template's default is false): the first system turn opens with <|think|> "
                           "and the prompt ends <|turn>model\\n; the model closes its reasoning with <channel|>, not </think>, so the universal "
                           "</think> split is inert and the parser's last-candidates-object rule applies to the whole completion; engine "
                           "arguments --max-num-seqs 1 --max-num-batched-tokens 8192; no custom code"},
    'gemma4_26b_a4b': {"path": "<workspace>/serving/models" + "/gemma4_26b_a4b", "max_model_len": 131072,
                       "sampling": {"temperature": 1.0, "top_p": 0.95, "top_k": 64, "seed": 20260921},
                       "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192}, "chat_template_kwargs": {"enable_thinking": True},
                       "required_files": REQUIRED_FILES + ("chat_template.jinja", "processor_config.json"), "note": "Gemma 4 26B-A4B-it (Gemma4ForConditionalGeneration, MoE, google/gemma-4-26B-A4B-it@"
                               "4d7ae4984b7db7de8f8457170b3f1a419ee76d52; same template, tokenizer and card guidance as gemma4_31b); context "
                               "131072 = min(text_config.max_position_embeddings 262144, 131072), 51.6 GB bf16 checkpoint; sampling = the model "
                               "card's Best Practices (= generation_config.json): temperature 1.0, top_p 0.95, top_k 64; thinking on through "
                               "chat_template_kwargs enable_thinking (template default false; reasoning closes with <channel|>, so the </think> "
                               "split is inert and the whole completion is parsed by the last-candidates-object rule); engine arguments "
                               "--max-num-seqs 1 --max-num-batched-tokens 8192; no custom code"},
    'glm45_air_fp8': {"path": "<workspace>/serving/models" + "/glm45_air_fp8", "max_model_len": 65536,
                      "sampling": {"temperature": 0.6, "top_p": 0.95, "seed": 20260921},
                      "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192}, "chat_template_kwargs": {"enable_thinking": True},
                      "required_files": REQUIRED_FILES + ("chat_template.jinja",), "note": "GLM-4.5-Air-FP8 (Glm4MoeForCausalLM, zai-org/GLM-4.5-Air-FP8@f9a9c5acf5e543cd24d659a056c5dbcda78ffcfc; "
                              "compressed-tensors float-quantized weights per config quantization_config, loaded by vLLM's compressed-tensors "
                              "path; the runner's dtype bfloat16 is the activation dtype); context 65536: native max_position_embeddings "
                              "131072, but the checkpoint is 112.6 GB (> 100 GB), so the one-B200 cap applies; sampling = the fallback "
                              "temperature 0.6 / top_p 0.95 (neither the model card nor generation_config.json recommends any); thinking on "
                              "through chat_template_kwargs enable_thinking, the kwarg the card names for vLLM (also the template's default: "
                              "the prompt ends <|assistant|>, the completion is <think>reasoning</think> answer and only the text after "
                              "</think> is parsed); engine arguments --max-num-seqs 1 --max-num-batched-tokens 8192; no custom code"},
    'nemotron3_super_120b_a12b_fp8': {"path": "<workspace>/serving/models" + "/nemotron3_super_120b_a12b_fp8", "max_model_len": 65536,
                                      "sampling": {"temperature": 1.0, "top_p": 0.95, "seed": 20260921},
                                      "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192},
                                      "chat_template_kwargs": {"enable_thinking": True},
                                      "required_files": REQUIRED_FILES + ("chat_template.jinja", "special_tokens_map.json", "hf_quant_config.json"),
                                      "note": "NVIDIA-Nemotron-3-Super-120B-A12B-FP8 (NemotronHForCausalLM, hybrid Mamba/latent-MoE/attention, "
                                              "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8@744b1880a37996c5d56bf454ae164dfd74d77c4e; modelopt "
                                              "FP8 weights per config quantization_config and hf_quant_config.json); context 65536: native "
                                              "max_position_embeddings 262144, but the checkpoint is 128.4 GB (> 100 GB); sampling = the model "
                                              "card (temperature 1.0, top_p 0.95 'across all tasks and serving backends', = "
                                              "generation_config.json); thinking on through chat_template_kwargs enable_thinking (the "
                                              "template's default too): the prompt ends <|im_start|>assistant\\n<think>\\n and only the text "
                                              "after </think> is parsed; the card's low_effort kwarg is not passed; the checkpoint's "
                                              "configuration_nemotron_h.py / modeling_nemotron_h.py (config auto_map) are not needed, "
                                              "transformers 5.17 has the native nemotron_h config and vLLM 0.29 its own NemotronHForCausalLM, "
                                              "so trust_remote_code is not set (the .py files are still bound by the manifest); engine "
                                              "arguments --max-num-seqs 1 --max-num-batched-tokens 8192"},
    'nemotron35_lightning_30b_a3b': {"path": "<workspace>/serving/models" + "/nemotron35_lightning_30b_a3b", "max_model_len": 131072,
                                     "sampling": {"temperature": 1.0, "top_p": 0.95, "seed": 20260921},
                                     "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192},
                                     "chat_template_kwargs": {"enable_thinking": True},
                                     "required_files": REQUIRED_FILES + ("chat_template.jinja", "special_tokens_map.json"), "note": "NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 (NemotronHForCausalLM, hybrid Mamba/MoE/attention, "
                                             "nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16@a9904d24bcc1d289a1950fa9d2b978c47cf903b9; "
                                             "65.8 GB bf16 checkpoint; the config lists layers_block_type, from which transformers' native "
                                             "NemotronHConfig derives the hybrid_override_pattern vLLM reads); context 131072 = "
                                             "min(max_position_embeddings 262144, 131072); sampling = the model card's Recommended Sampling "
                                             "(temperature 1.0, top_p 0.95, = generation_config.json); thinking on through chat_template_kwargs "
                                             "enable_thinking (the template's default too): the prompt ends <|im_start|>assistant\\n<think>\\n "
                                             "and only the text after </think> is parsed; no custom code (the checkpoint carries no .py file); "
                                             "engine arguments --max-num-seqs 1 --max-num-batched-tokens 8192"},
    'deepseek_v4_flash_dspark': {"path": "<workspace>/serving/models" + "/deepseek_v4_flash_dspark", "max_model_len": 65536,
                                 "sampling": {"temperature": 1.0, "top_p": 1.0, "seed": 20260921},
                                 "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192, "tensor_parallel_size": 2,
                                                 "tokenizer_mode": "deepseek_v4"},
                                 "chat_template_kwargs": {"enable_thinking": True, "reasoning_effort": "low"},
                                 "required_files": REQUIRED_FILES, "note": "DeepSeek-V4-Flash-DSpark (DeepseekV4ForCausalLM, deepseek-ai/DeepSeek-V4-Flash-DSpark@"
                                         "62af8fffb2f7030cac4de2f0169f5b8d1101b646; 166.9 GB of fp8 e4m3 weights per config quantization_config "
                                         "(128x128 blocks, ue8m0 scales) plus the DSpark draft module, which is not used: no speculative config "
                                         "is passed); does not fit one B200, so tensor_parallel_size 2: NEEDS THE TWO-GPU JOB SCRIPT "
                                         "(run_local.sbatch and run_local_large.sbatch request one GPU); context 65536 (native 1048576; the "
                                         "checkpoint is over 100 GB); sampling = the model card's local-deployment recommendation "
                                         "(temperature 1.0, top_p 1.0, = generation_config.json); the checkpoint ships no Jinja chat template "
                                         "(its encoding is the Python reference encoding/encoding_dsv4.py), and vLLM 0.29 selects "
                                         "tokenizer_mode deepseek_v4 for this architecture (passed explicitly), whose apply_chat_template "
                                         "renders through vLLM's bundled deepseek_v4_encoding.encode_messages and returns plain token ids: "
                                         "enable_thinking selects thinking_mode 'thinking' (the prompt ends <\uff5cAssistant\uff5c><think>, "
                                         "only the text after </think> is parsed) and reasoning_effort 'low' selects the empty effort prefix, "
                                         "i.e. the vendor's standard Think High encoding; without it vLLM's wrapper defaults reasoning_effort "
                                         "to 'high', which its encoder maps to the vendor's Think Max system prefix (the card wants >= 384K "
                                         "context for that mode); engine arguments --max-num-seqs 1 --max-num-batched-tokens 8192; no custom code"},
    'magistral_small_2509': {"path": "<workspace>/serving/models/magistral_small_2509", "max_model_len": 131072,
                             "sampling": {"temperature": 0.7, "top_p": 0.95, "seed": 20260921},
                             "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192, "tokenizer_mode": "mistral"},
                             "required_files": ("config.json", "model.safetensors.index.json", "tekken.json", "params.json", "SYSTEM_PROMPT.txt"),
                             "note": "Magistral-Small-2509 (Mistral3ForConditionalGeneration, mistralai/Magistral-Small-2509@"
                                     "a31cc96ab10cf19bc42c628fedf1e359e0853c49); context 131072 = text_config.max_position_embeddings (the card: "
                                     "128k window, keep it at 128k); sampling temperature 0.7 top_p 0.95 = the card's recommendation and "
                                     "generation_config.json, fixed seed; the checkpoint has no tokenizer.json/tokenizer_config.json, only "
                                     "tekken.json (tekken v13) and params.json: transformers 5.17 loads MistralCommonBackend (mistral_common), and "
                                     "vLLM needs tokenizer_mode mistral (the auto mode would also detect tekken.json; the explicit value pins it); "
                                     "reasoning is switched on by the card's SYSTEM_PROMPT.txt ([THINK]...[/THINK]), not by a template kwarg, and "
                                     "the frozen system prompt is not replaced, so no chat_template_kwargs; the universal </think> split is inert "
                                     "for [/THINK]; consolidated.safetensors (Mistral-format duplicate of the 10 indexed shards) is hashed but "
                                     "vLLM loads only the indexed shards; no quantization_config; dtype bfloat16"},
    'seed_oss_36b': {"path": "<workspace>/serving/models/seed_oss_36b", "max_model_len": 131072,
                     "sampling": {"temperature": 1.1, "top_p": 0.95, "seed": 20260921},
                     "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192}, "chat_template_kwargs": {"thinking_budget": -1},
                     "required_files": REQUIRED_FILES + ("chat_template.jinja",),
                     "note": "Seed-OSS-36B-Instruct (SeedOssForCausalLM, ByteDance-Seed/Seed-OSS-36B-Instruct@"
                             "497f1dca95ebdec98e41d517b9f060ee753c902f); context min(524288 max_position_embeddings, 131072) = 131072; "
                             "sampling temperature 1.1 top_p 0.95 = the card's recommendation and generation_config.json, fixed seed; thinking "
                             "on through chat_template_kwargs thinking_budget=-1 (the template's unlimited-thinking mode, also its default; "
                             "thinking_budget=0 would close the <seed:think> block in the prompt and switch thinking off); the completion is "
                             "<seed:think>reasoning</seed:think> answer, and the universal </think> split is inert for </seed:think>; "
                             "TokenizersBackend, no custom code; no quantization_config; dtype bfloat16"},
    'olmo3_32b_think': {"path": "<workspace>/serving/models/olmo3_32b_think", "max_model_len": 65536,
                        "sampling": {"temperature": 0.6, "top_p": 0.95, "seed": 20260921},
                        "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192},
                        "required_files": REQUIRED_FILES + ("chat_template.jinja",),
                        "note": "Olmo-3-32B-Think (Olmo3ForCausalLM, allenai/Olmo-3-32B-Think@f2edda15216e738ef2bb73771e11890e152b2112); "
                                "context 65536 = max_position_embeddings (YaRN rope_scaling in config.json); sampling temperature 0.6 top_p 0.95 "
                                "= the card's recommended settings and generation_config.json, fixed seed; the template always ends the prompt "
                                "with <|im_start|>assistant\\n<think> (no switch) and appends ' You do not currently have access to any "
                                "functions. <functions></functions>' to the system message; completion = reasoning </think> answer, only the "
                                "text after </think> is parsed; TokenizersBackend, no custom code; no quantization_config; dtype bfloat16"},
    'skywork_or1_32b': {"path": "<workspace>/serving/models/skywork_or1_32b", "max_model_len": 32768,
                        "sampling": {"temperature": 0.6, "top_p": 0.95, "seed": 20260921},
                        "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192},
                        "required_files": REQUIRED_FILES,
                        "note": "Skywork-OR1-32B (Qwen2ForCausalLM, Skywork/Skywork-OR1-32B@8545e72b0bcb20bd08193400bc75b4ff6ccb300a), a "
                                "DeepSeek-R1-Distill-Qwen-32B / Qwen2.5-32B derivative; context 32768: config.json says 131072 with rope_scaling "
                                "null (Qwen2.5's native 32768; 131072 needs YaRN), the same choice as the accepted DeepSeek-R1-Distill lane; "
                                "sampling: neither the card nor generation_config.json prescribes any, so the stated fallback 0.6 / 0.95, fixed "
                                "seed; the DeepSeek-style template always ends the prompt with <|Assistant|><think>\\n (no switch); completion "
                                "= reasoning </think> answer, only the text after </think> is parsed; Qwen2Tokenizer (tokenizer_config says "
                                "LlamaTokenizer; model_max_length 16384 is a warning only); no custom code; no quantization_config; dtype bfloat16"},
    'openmath_nemotron_32b': {"path": "<workspace>/serving/models/openmath_nemotron_32b", "max_model_len": 32768,
                              "sampling": {"temperature": 0.6, "top_p": 0.95, "seed": 20260921},
                              "engine_args": {"max_num_seqs": 1, "max_num_batched_tokens": 8192},
                              "required_files": REQUIRED_FILES,
                              "note": "OpenMath-Nemotron-32B (Qwen2ForCausalLM, nvidia/OpenMath-Nemotron-32B@"
                                      "bc78382d1594995c5202c25d20630a10c10b9707), finetuned from Qwen2.5-32B; context 32768: config.json says "
                                      "131072 with rope_scaling null and the card says 'up to 131,072', but Qwen2.5 pretrains at 32768 and 131072 "
                                      "needs YaRN, so the native 32768 is used like the accepted DeepSeek-R1-Distill lane; sampling: neither the "
                                      "card nor generation_config.json prescribes any, so the stated fallback 0.6 / 0.95, fixed seed; ChatML "
                                      "template without a thinking switch, prompt ends <|im_start|>assistant\\n; the model reasons inline (CoT "
                                      "mode) without think tags, so the whole completion is parsed; Qwen2Tokenizer; no custom code; no "
                                      "quantization_config; dtype bfloat16"},
}

assert all("manifest_dir" not in MODELS[key] and MODELS[key]["max_model_len"] > MAX_OUTPUT for key in LOCAL_FAMILY_KEYS)
ATTEMPT_WALL_SECONDS = 600   # v3 addendum: doubled with the output cap
SETUP_WALL_SECONDS = 600
PREPARE_WALL_SECONDS = 60
CALL_TOKEN_CAP = 120000
LANE_TOKEN_CAP = 10000000
UNKNOWN_CHARGE = 40000
TRANSPORT_LIMIT = 10
MANIFEST_SCHEMA = "ccl-local-weights-sha256/v1"
ATTEMPT_TAGS = ("attempt_1", "attempt_2")   # the attempt and its single transport retry; a third tag does not exist
assert len(ATTEMPT_TAGS) == MAX_PHYSICAL_ATTEMPTS


class PromptSetupError(RuntimeError):
    """Tokenizer/worker failure before any generation: a SETUP_FAILURE, never an attempt."""
    worker_usable = False


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp.%d" % os.getpid())
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def file_stamp(path):
    st = Path(path).stat()
    return [st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns]


def required_files(spec):
    """The files a lane's checkpoint must carry: the default set, or the spec's own (Kimi: tiktoken.model plus custom code)."""
    return tuple(spec.get("required_files", REQUIRED_FILES))


def model_files(path, required=REQUIRED_FILES):
    """Include shards, tokenizer vocabulary, configuration, chat templates and any checkpoint (tokenizer/model) code."""
    root = Path(path)
    suffixes = {".safetensors", ".bin", ".json", ".model", ".txt", ".jinja", ".py"}
    files = sorted(p.name for p in root.iterdir() if p.is_file() and p.suffix in suffixes)
    index = json.loads((root / "model.safetensors.index.json").read_text())
    shards = set(index["weight_map"].values())
    if not shards or any(Path(s).name != s or s not in files for s in shards):
        raise ValueError("weight index has missing/non-root shards")
    if not set(required).issubset(files):
        raise ValueError("required model/tokenizer files missing: " + ", ".join(sorted(set(required) - set(files))))
    return files


def digest_file(path):
    before = file_stamp(path)
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        while block := f.read(8 * 1024 * 1024):
            h.update(block)
    if before != file_stamp(path):
        raise ValueError("model file changed during hashing: " + str(path))
    return h.hexdigest(), before


def assert_unfrozen(exp):
    """Manifest preparation must stop once any freeze or critic output appears."""
    for p in Path(exp).rglob("*"):
        if not p.is_file():
            continue
        name = p.name.lower()
        if (name.startswith("freeze") or name.startswith("frozen") or name.startswith("results")
                or name.startswith("dispatch_") or name in {"record.json", "dispatch.json", "stop.json"}):
            raise RuntimeError("freeze/output exists; preparation stopped: " + str(p))


def weights_manifest_path(model_key, exp=EXP, spec=None):
    """Beside the experiment for every lane; a spec's manifest_dir (a synthetic checkpoint's temporary experiment in tests) overrides it."""
    directory = (spec or {}).get("manifest_dir") or exp
    return Path(directory) / ("weights_manifest_" + model_key + ".json")


def prepare_weights(model_key, spec, exp=EXP):
    assert_unfrozen(exp)
    dest = weights_manifest_path(model_key, exp, spec)
    if dest.exists():
        raise RuntimeError("weight manifest already exists; refusing to replace it")
    root = Path(spec["path"])
    inventory = model_files(root, required_files(spec))
    entries = []
    for name in inventory:
        digest, stamp = digest_file(root / name)
        entries.append({"path": name, "bytes": stamp[2], "sha256": digest, "stat_at_hash": stamp})
        print("hashed", model_key, name, stamp[2], flush=True)
    if model_files(root, required_files(spec)) != inventory:
        raise RuntimeError("model inventory changed while hashing")
    for entry in entries:
        if file_stamp(root / entry["path"]) != entry["stat_at_hash"]:
            raise RuntimeError("model file changed before manifest publication")
    manifest = {"schema": MANIFEST_SCHEMA, "model_key": model_key,
                "model_path": str(root.resolve()), "created_utc": time.strftime("%FT%TZ", time.gmtime()),
                "binding": "SHA256 of actual weight shards and inference/tokenizer/config/template files",
                "total_bytes": sum(e["bytes"] for e in entries), "files": entries}
    assert_unfrozen(exp)
    if dest.exists():
        raise RuntimeError("another process published the manifest; refusing to replace it")
    atomic_json(dest, manifest)
    return manifest


def verify_weights(model_key, spec, exp=EXP):
    """Rehash bytes on invocation; the mutable download metadata is not trusted."""
    path = weights_manifest_path(model_key, exp, spec)
    blob = path.read_bytes()
    manifest = json.loads(blob)
    root = Path(spec["path"])
    if (manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("model_key") != model_key
            or manifest.get("model_path") != str(root.resolve())):
        raise ValueError("weight manifest identity mismatch")
    entries = manifest["files"]
    if model_files(root, required_files(spec)) != [e["path"] for e in entries]:
        raise ValueError("model file inventory differs from frozen manifest")
    stamps = {}
    for entry in entries:
        digest, stamp = digest_file(root / entry["path"])
        if digest != entry["sha256"] or stamp[2] != entry["bytes"]:
            raise ValueError("frozen weight hash mismatch: " + entry["path"])
        stamps[entry["path"]] = stamp
    assert_weight_stamps(spec, stamps)
    ident = {"manifest_file": path.name, "manifest_sha256": sha(blob), "model_key": model_key,
             "model_path": str(root.resolve()), "files": len(entries), "total_bytes": manifest["total_bytes"],
             "verification": "all contents SHA256-verified before model load; stat/inventory checked before/after each item"}
    return ident, stamps


def assert_weight_stamps(spec, stamps):
    root = Path(spec["path"])
    if model_files(root, required_files(spec)) != sorted(stamps):
        raise RuntimeError("model inventory changed during run")
    if any(file_stamp(root / name) != stamp for name, stamp in stamps.items()):
        raise RuntimeError("model file changed during run")


def template_messages(messages, system_prompt_placement=None):
    """Preserve the frozen instructions when a native template discards role=system.

    The Phi reasoning template supplies its own vendor system prompt. Its declared
    adaptation places our exact system text before the unchanged user prompt;
    ordinary lanes and Harmony's native developer mapping keep their messages.
    """
    if system_prompt_placement != "prepend_frozen_system_to_user":
        return messages
    if len(messages) != 2 or [m.get("role") for m in messages] != ["system", "user"]:
        raise PromptSetupError("system-placement adaptation requires exactly the frozen system and user turns")
    return [{"role": "user", "content": messages[0]["content"] + "\n\n" + messages[1]["content"]}]


def prompt_token_ids(tok, messages, template_kwargs=None, system_prompt_placement=None):
    """Chat-template prompt as a plain, non-empty list of int token ids.

    transformers 5 returns a BatchEncoding from apply_chat_template(tokenize=True)
    unless return_dict=False. len() of that mapping is 2 and vLLM iterates its
    string keys: the TypeError that ended all 20 v3 local attempts in < 0.4 s.
    Anything but real token ids is refused here, before any reservation.
    template_kwargs are a lane's chat_template_kwargs (GLM's enable_thinking),
    rendered exactly as its serving profile rendered them.
    """
    ids = tok.apply_chat_template(template_messages(messages, system_prompt_placement), add_generation_prompt=True,
                                 tokenize=True, return_dict=False, **(template_kwargs or {}))
    if not isinstance(ids, list) or not ids:
        raise PromptSetupError("chat template must return a non-empty list of token ids, got %s of length %s"
                               % (type(ids).__name__, len(ids) if hasattr(ids, "__len__") else "?"))
    bad = [t for t in ids if not isinstance(t, int) or isinstance(t, bool) or t < 0]
    if bad:
        raise PromptSetupError("chat template returned %d non-token entries, first %r (%s)"
                               % (len(bad), bad[0], type(bad[0]).__name__))
    return ids


def _serve(conn, tok, generate, template_kwargs=None, system_prompt_placement=None):
    """Answer parent requests; separate from the vLLM import so tests can drive it without a model."""
    ids = None
    while True:
        job = conn.recv()
        if job["kind"] == "stop":
            return
        if job["kind"] == "prepare":
            ids = None
            try:
                ids = prompt_token_ids(tok, job["messages"], template_kwargs, system_prompt_placement)
            except Exception as exc:
                # SETUP_FAILURE of this item only: nothing was dispatched and the loaded model stays usable.
                conn.send({"kind": "prepare_error", "error_type": type(exc).__name__, "error": str(exc)[:2000]})
                continue
            conn.send({"kind": "prepared", "prompt_tokens": len(ids)})
        elif job["kind"] == "generate" and ids is not None:
            result = generate(ids)
            conn.send({"kind": "result", "answer": result.text,
                       "output_tokens": len(result.token_ids), "finish_reason": result.finish_reason})
            ids = None
        else:
            raise RuntimeError("invalid parent request")


def _worker(conn, spec):
    os.setsid()  # vLLM descendants are terminated together on a wall-cap kill.
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", VLLM_NO_USAGE_STATS="1", DO_NOT_TRACK="1")
    try:
        import vllm
        from vllm import LLM, SamplingParams
        llm = LLM(model=spec["path"], max_model_len=spec["max_model_len"], dtype="bfloat16",
                  gpu_memory_utilization=0.90, seed=20260921, enable_prefix_caching=False, **spec.get("engine_args", {}))
        tok = llm.get_tokenizer()
        sampling = SamplingParams(max_tokens=MAX_OUTPUT, **spec["sampling"])
        def generate(ids):
            results = llm.generate([{"prompt_token_ids": ids}], sampling, use_tqdm=False)
            if len(results) != 1 or len(results[0].outputs) != 1:
                raise RuntimeError("unexpected vLLM result count")
            return results[0].outputs[0]
        conn.send({"kind": "ready", "vllm": vllm.__version__})
        _serve(conn, tok, generate, spec.get("chat_template_kwargs"), spec.get("system_prompt_placement"))
    except BaseException as exc:
        try:
            conn.send({"kind": "error", "error_type": type(exc).__name__, "error": str(exc)[:2000]})
        except (BrokenPipeError, EOFError, OSError):
            pass
    finally:
        conn.close()


class Worker:
    def __init__(self, spec, setup_timeout=SETUP_WALL_SECONDS, target=_worker):
        ctx = multiprocessing.get_context("spawn")
        self.conn, child = ctx.Pipe()
        self.proc = ctx.Process(target=target, args=(child, spec))
        self.proc.start()
        child.close()
        try:
            ready = self.receive(setup_timeout)
            if ready.get("kind") != "ready":
                raise RuntimeError("model setup failed: " + json.dumps(ready))
            self.version = ready.get("vllm")
        except BaseException:
            self.close()
            raise

    def receive(self, seconds):
        # poll() only guarantees the first bytes of a message. recv() can still
        # block on a partial frame, so supervise the complete receive operation.
        received = queue.Queue(maxsize=1)
        def read_message():
            try:
                received.put((True, self.conn.recv()))
            except BaseException as exc:
                received.put((False, exc))
        reader = threading.Thread(target=read_message, daemon=True)
        reader.start()
        try:
            success, value = received.get(timeout=max(0, seconds))
        except queue.Empty as exc:
            raise TimeoutError("local worker wall cap") from exc
        if not success:
            raise value
        return value

    def prepare(self, messages):
        self.conn.send({"kind": "prepare", "messages": messages})
        result = self.receive(PREPARE_WALL_SECONDS)
        count = result.get("prompt_tokens")
        if result.get("kind") != "prepared" or not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            error = PromptSetupError("prompt preparation failed: " + json.dumps(result))
            error.worker_usable = result.get("kind") == "prepare_error"
            raise error
        return count

    def generate(self, seconds=ATTEMPT_WALL_SECONDS):
        self.conn.send({"kind": "generate"})
        return self.receive(seconds)

    def close(self, force=False):
        if self.proc.is_alive():
            try:
                if os.getpgid(self.proc.pid) == self.proc.pid:
                    os.killpg(self.proc.pid, signal.SIGKILL if force else signal.SIGTERM)
                else:
                    self.proc.kill() if force else self.proc.terminate()
            except ProcessLookupError:
                pass
            self.proc.join(3)
        try:
            os.killpg(self.proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        if self.proc.is_alive():
            self.proc.kill()
        self.proc.join(3)
        self.conn.close()


def attempt_result(result, prompt_tokens, seconds, reservation_tokens):
    """Keep measured usage and conservative budget charges separate; class every attempt.

    One dispatched generation is exactly one of: VALID_ANSWER (natural stop within
    MAX_OUTPUT), BUDGET_EXHAUSTED (finish_reason "length": an intention-to-treat
    miss), CONTRACT_VIOLATION (the worker's result breaks the one-generation
    contract) or TRANSPORT_FAILURE (no result). An empty natural completion is
    VALID_ANSWER with measured usage; parsing determines the scored miss.
    Only TRANSPORT_FAILURE is eligible for the single retry.
    """
    def unknown(attempt_class, hard_stop, evidence):
        return {"attempt_class": attempt_class, "valid_protocol": False, "usage_known": False,
                "usage": {"total_attributable_tokens": None, "observed_lower_bound": 0},
                "budget_charge_tokens": reservation_tokens, "transport_failure": attempt_class == "TRANSPORT_FAILURE",
                "wall_seconds": seconds, "hard_stop": hard_stop, "worker_error": evidence}, ""
    if result.get("kind") != "result":
        return unknown("TRANSPORT_FAILURE", {"reason": result.get("reason", "worker_error")}, result)
    count, text, finish = result.get("output_tokens"), result.get("answer"), result.get("finish_reason")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0 or not isinstance(text, str):
        # The answer of a malformed result is not evidence; keep only its shape.
        return unknown("CONTRACT_VIOLATION", {"reason": "contract_violation", "detail": "malformed_worker_result"},
                       {"kind": "result", "output_tokens": repr(count)[:100], "answer_type": type(text).__name__,
                        "finish_reason": repr(finish)[:100]})
    total = prompt_tokens + count
    if count > MAX_OUTPUT:
        attempt_class = "CONTRACT_VIOLATION"
        hard_stop = {"reason": "contract_violation", "detail": "output_tokens_exceed_max_output",
                     "output_tokens": count, "max_output_tokens": MAX_OUTPUT}
    elif finish == "length":
        attempt_class = "BUDGET_EXHAUSTED"   # also when the text is empty: a spent budget is never retried
        hard_stop = {"reason": "output_budget_exhausted", "finish_reason": finish,
                     "output_tokens": count, "max_output_tokens": MAX_OUTPUT}
    elif finish != "stop":
        attempt_class = "CONTRACT_VIOLATION"
        hard_stop = {"reason": "contract_violation", "detail": "unexpected_finish_reason", "finish_reason": repr(finish)[:100]}
    else:
        attempt_class, hard_stop = "VALID_ANSWER", None
    assert attempt_class in ATTEMPT_CLASSES   # the shared vocabulary of lane_accounting, score and both runners
    return {"attempt_class": attempt_class, "valid_protocol": attempt_class == "VALID_ANSWER", "usage_known": True,
            "usage": {"total_attributable_tokens": total, "observed_lower_bound": total,
                      "prompt_tokens": prompt_tokens, "output_tokens": count},
            "budget_charge_tokens": total, "transport_failure": attempt_class == "TRANSPORT_FAILURE",
            "wall_seconds": seconds, "finish_reason": finish, "hard_stop": hard_stop}, text


def retry_eligible(attempt):
    """Only a TRANSPORT_FAILURE may use the single retry; receipts older than v4 state transport_failure directly."""
    if "attempt_class" in attempt:
        return attempt["attempt_class"] == "TRANSPORT_FAILURE"
    return attempt.get("transport_failure") is True


def retry_suppressed_by(exc):
    return {"reason": "hold_prevents_retry" if isinstance(exc, LaneHeld) else "lane_stop_prevents_retry",
            "detail": str(exc)[:1000]}


def consumed_attempts(acct, out_dir, record_id):
    """A.2: {tag: receipted attempt} of an unfinished item; these tags are never dispatched again.

    The accounting layer refuses a DISPATCH without an ATTEMPT receipt (a call of
    unknown extent: LaneAccounting.reconcile_interrupted has to close it first).
    Receipts of another item, freeze or tag scheme are refused here.
    """
    consumed = dict(acct.consumed_attempts(out_dir))
    for tag, dispatch, _ in attempt_receipts(out_dir):
        if (tag not in ATTEMPT_TAGS or dispatch.get("record_id") != record_id
                or dispatch.get("freeze_sha256") != acct.freeze_sha256):
            acct.stop("consumed_attempt_identity_mismatch", {"path": str(out_dir), "tag": tag,
                      "recovery": "reconcile explicitly; a consumed attempt is never rerun"})
            raise LaneStopped(acct.summary()["stopped"])
    return consumed


def run_lane(model_key, split, approved_freeze):
    from common import parse_candidates_audit
    h, _ = freeze_hash()
    if approved_freeze != h:
        raise RuntimeError("freeze hash mismatch")
    spec = MODELS[model_key]
    model = "local_" + model_key
    lane = Path(EXP) / "runs" / model
    worker = None
    if (Path(EXP) / HOLD_NAME).exists():
        # Refuse to start without a trace: no lane lock, no weight hashing, no model load.
        raise LaneHeld("experiment hold: " + str(Path(EXP) / HOLD_NAME))
    # The lane cap binds active cost plus archived carryover; without CARRYOVER.json the lane refuses to run.
    with LaneAccounting(EXP, model, h, lane_cap=LANE_TOKEN_CAP, per_attempt_reservation=CALL_TOKEN_CAP,
                        transport_limit=TRANSPORT_LIMIT, require_carryover=True) as acct:
        if split == "evaluation":
            acct.pilot_gate(load_items("pilot"))
        items = [it for it in load_items(split) if not (lane / safe(it["record_id"]) / "record.json").exists()]
        retained = {}
        if split == "evaluation" and acct.attempt_epoch is not None:
            retained = acct.attempt_epoch.historical_evaluation_exclusions()
            items = [it for it in items if it["record_id"] not in retained]
            if retained:
                print(json.dumps({"historical_evaluation_retained": retained, "model": model}, sort_keys=True), flush=True)
        if not items:
            if split == "pilot":
                acct.pilot_gate(load_items("pilot"))
            elif retained:
                atomic_json(lane / "LANE_evaluation.json", {"model_key": model_key, "split": split,
                            "freeze_sha256": h, "finished_utc": time.strftime("%FT%TZ", time.gmtime()),
                            "accounting": acct.summary(), "historical_evaluation_retained": retained,
                            "historical_evaluation_excluded_count": len(retained),
                            "current_epoch_record_count": sum((lane / safe(it["record_id"]) / "record.json").is_file()
                                                              for it in load_items(split)),
                            "historical_reporting": "lifetime_evaluation joins archived records; unreconciled dispatches remain missing outcomes"})
            return
        ident, stamps = verify_weights(model_key, spec)
        if freeze_hash()[0] != h:
            raise RuntimeError("freeze changed during weight verification")
        system = read("prompt_system.txt").strip()
        try:
            for item in items:
                assert_weight_stamps(spec, stamps)
                if freeze_hash()[0] != h:
                    raise RuntimeError("freeze changed during lane")
                out_dir = lane / safe(item["record_id"])
                prompt = build_prompt(item)
                messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
                attempts, answer, prompt_tokens = [], "", None
                setup_failure = retry_suppressed = None
                version = None
                consumed = consumed_attempts(acct, out_dir, item["record_id"])
                dispatched_here = False
                for attempt_number, tag in enumerate(ATTEMPT_TAGS, 1):
                    if tag in consumed:
                        # A.2: never start a consumed tag afresh. Only a receipted
                        # TRANSPORT_FAILURE leaves an allowance (the next tag); the
                        # answer of any other consumed attempt cannot be recovered here.
                        if not retry_eligible(consumed[tag]):
                            acct.stop("consumed_attempt_without_record", {"record_id": item["record_id"], "tag": tag,
                                      "recovery": "reconcile explicitly; a consumed attempt is never rerun"})
                            raise LaneStopped(acct.summary()["stopped"])
                        attempts.append(consumed[tag])
                        continue
                    try:
                        acct.check_holds()   # A.3, before a model load is spent on a held lane; reserve() looks again
                    except LaneStopped as exc:
                        # The accounting layer halts on ordinary receipts without a record, so an
                        # attempt made in this invocation is closed; otherwise the item is left as
                        # the restore accepted it and keeps its allowance.
                        if not dispatched_here or isinstance(exc, LaneHeld):
                            raise   # a HOLD never converts a retry-eligible transport failure into a miss: restore resumes the allowance
                        retry_suppressed = retry_suppressed_by(exc)
                        break
                    if worker is None:
                        started_setup = time.monotonic()
                        setup_path = lane / ("SETUP_%d.json" % time.time_ns())
                        setup = {"freeze_sha256": h, "model": model, "setup_wall_cap": SETUP_WALL_SECONDS,
                                 "status": "STARTED", "benchmark_calls_during_setup": 0}
                        atomic_json(setup_path, setup)
                        try:
                            worker = Worker(spec)
                            if worker.version != "0.29.0":
                                raise RuntimeError("vLLM version differs from frozen 0.29.0: " + str(worker.version))
                        except BaseException as exc:
                            setup.update(status="FAILED", wall_seconds=time.monotonic() - started_setup,
                                         error_type=type(exc).__name__, error=str(exc)[:1000])
                            atomic_json(setup_path, setup)
                            acct.stop("local_model_setup_failure", setup)
                            raise
                        setup.update(status="READY", wall_seconds=time.monotonic() - started_setup, vllm=worker.version)
                        atomic_json(setup_path, setup)
                    version = worker.version
                    started = time.monotonic()
                    blocked = None
                    try:
                        prompt_tokens = worker.prepare(messages)
                    except (PromptSetupError, TimeoutError, EOFError, OSError) as exc:
                        prompt_tokens = None   # never record a count that was not a real tokenization
                        blocked = {"detail": "prompt_preparation_failed", "error_type": type(exc).__name__,
                                   "error": str(exc)[:1000]}
                        if not getattr(exc, "worker_usable", False):
                            worker.close(force=True)
                            worker = None
                    if blocked is None:
                        request_upper_bound = prompt_tokens + MAX_OUTPUT
                        # A failed local attempt is charged the greater of its exact
                        # token bound and the protocol's 40k unknown-usage floor.
                        reservation = max(UNKNOWN_CHARGE, request_upper_bound)
                        if request_upper_bound > spec["max_model_len"]:
                            blocked = {"detail": "prompt_exceeds_context_with_output_cap", "prompt_tokens": prompt_tokens,
                                       "max_output_tokens": MAX_OUTPUT, "max_model_len": spec["max_model_len"]}
                        elif reservation > CALL_TOKEN_CAP:
                            blocked = {"detail": "call_token_cap_prevents_attempt", "prompt_tokens": prompt_tokens,
                                       "max_output_tokens": MAX_OUTPUT, "call_token_cap": CALL_TOKEN_CAP}
                    if blocked is not None:
                        # Before the DISPATCH receipt: no reservation, no charge, no attempt.
                        if attempts:
                            retry_suppressed = {"reason": "setup_failure", **blocked}
                        else:
                            setup_failure = blocked
                        break
                    try:
                        ticket = acct.reserve(str(out_dir), item["record_id"], split, tag, reservation_tokens=reservation)
                    except LaneStopped as exc:
                        if not dispatched_here or isinstance(exc, LaneHeld):
                            raise   # a HOLD never converts a retry-eligible transport failure into a miss: restore resumes the allowance
                        retry_suppressed = retry_suppressed_by(exc)
                        break
                    dispatched_here = True
                    try:
                        try:
                            result = worker.generate(seconds=max(0, ATTEMPT_WALL_SECONDS - (time.monotonic() - started)))
                        except (TimeoutError, EOFError, OSError) as exc:
                            result = {"kind": "error", "reason": "wall_cap" if isinstance(exc, TimeoutError) else "worker_transport_failure",
                                      "error_type": type(exc).__name__}
                        if result.get("kind") != "result":
                            # Enforce the wall stop BEFORE fsync/accounting: a slow
                            # filesystem must not let a timed-out GPU call continue.
                            worker.close(force=True)
                            worker = None
                        attempt, answer = attempt_result(result, prompt_tokens, time.monotonic() - started, reservation)
                        attempt["attempt_number"] = attempt_number
                        attempts.append(attempt)
                        acct.complete_attempt(ticket, attempt)
                    except BaseException:
                        # SIGTERM, preemption or a harness fault with the DISPATCH open: the tag is
                        # consumed and stays durable; only reconcile_interrupted can close it.
                        acct.stop("dispatch_interrupted", {"record_id": item["record_id"], "tag": tag})
                        raise
                    assert_weight_stamps(spec, stamps)
                    if attempt["attempt_class"] == "CONTRACT_VIOLATION":
                        # Only a harness fault can produce this locally: it is recorded
                        # as a miss and the lane stops (the worker is closed on the way out).
                        acct.stop("local_contract_violation", attempt["hard_stop"])
                    if not retry_eligible(attempt):
                        break
                    if worker is not None:
                        worker.close()
                        worker = None
                    if acct.summary()["stopped"]:
                        break
                # Qwen, DeepSeek-R1 and GLM close their reasoning with </think>: only the visible answer after it is parsed;
                # the full completion stays in answer.txt and counts against the output allowance.
                visible = answer.split("</think>")[-1] if "</think>" in answer else answer
                parsed = parse_candidates_audit(visible, item)
                attempt_class = attempts[-1]["attempt_class"] if attempts else "SETUP_FAILURE"
                rec = {"record_id": item["record_id"], "split": split, "requested_model": model,
                       "freeze_sha256": h, "weights_identity": ident, "sampling": spec["sampling"],
                       "max_output_tokens_per_request": MAX_OUTPUT, "prompt_tokens": prompt_tokens,
                       "attempts": attempts, "attempt_class": attempt_class, "valid_protocol": attempt_class == "VALID_ANSWER",
                       "transport_failure": attempt_class == "TRANSPORT_FAILURE",
                       "hard_stop": attempts[-1].get("hard_stop") if attempts else {"reason": "setup_failure", **setup_failure},
                       "candidates": parsed["candidates"], "candidate_parse": parsed,
                       "answer_sha256": sha(answer), "prompt_sha256": sha(prompt), "vllm": version}
                for key in ("engine_args", "chat_template_kwargs", "system_prompt_placement", "system_prompt_deviation"):
                    if key in spec:
                        rec[key] = spec[key]   # local families: what the worker passed to the engine and to the chat template
                if retry_suppressed:
                    rec["retry_suppressed"] = retry_suppressed
                if not attempts:
                    rec.update(usage_known=True, total_attributable_tokens=0,
                               budget_charge_tokens=0, usage_origin="preflight_no_inference")
                acct.write_record(str(out_dir), rec, answer)
                print(model, split, item["record_id"], "persisted", flush=True)
                if acct.summary()["stopped"]:
                    raise LaneStopped(acct.summary()["stopped"])
            atomic_json(lane / ("LANE_%s.json" % split), {"model_key": model_key, "split": split,
                        "freeze_sha256": h, "finished_utc": time.strftime("%FT%TZ", time.gmtime()),
                        "accounting": acct.summary(), "historical_evaluation_retained": retained,
                        "historical_evaluation_excluded_count": len(retained),
                        "current_epoch_record_count": sum((lane / safe(it["record_id"]) / "record.json").is_file()
                                                          for it in load_items(split)),
                        "historical_reporting": "lifetime_evaluation joins archived records; unreconciled dispatches remain missing outcomes"})
            if split == "pilot":
                acct.pilot_gate(load_items("pilot"))
        except LaneStopped:
            raise
        except BaseException as exc:
            interrupted = isinstance(exc, (KeyboardInterrupt, SystemExit))
            acct.stop("runner_interrupted" if interrupted else "local_runner_failure", {"type": type(exc).__name__, "message": str(exc)[:1000]})
            raise
        finally:
            if worker is not None:
                worker.close()


def main():
    def terminate(signum, frame):
        raise KeyboardInterrupt("termination signal %s" % signum)
    signal.signal(signal.SIGTERM, terminate)
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-key", required=True, choices=sorted(MODELS))
    ap.add_argument("--prepare-weights", action="store_true")
    ap.add_argument("--split", choices=["pilot", "evaluation"])
    ap.add_argument("--approved-freeze")
    args = ap.parse_args()
    if args.prepare_weights:
        if args.split or args.approved_freeze:
            ap.error("manifest preparation must be separate from inference")
        prepare_weights(args.model_key, MODELS[args.model_key])
    else:
        if not args.split or not args.approved_freeze:
            ap.error("inference requires --split and --approved-freeze")
        run_lane(args.model_key, args.split, args.approved_freeze)


if __name__ == "__main__":
    main()
