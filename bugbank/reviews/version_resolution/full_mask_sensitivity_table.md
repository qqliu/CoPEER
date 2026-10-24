Denominators: 191 = earlier primary inputs; 173 = minus the semantic-review mask (31 ids); 170 = minus the combined mask (34 ids). The selection column refers to the earlier 191-input reporting selection (13 views), not the current 12-row main table. Haiku views: EXP1 = retained-notices view; EXP5 = outage-continuation view.

| View | in earlier 191-input reporting selection | 191 Hit@1 | 173 Hit@1 | 170 Hit@1 | 191 Hit@3 | 173 Hit@3 | 170 Hit@3 |
|---|---|---|---|---|---|---|---|
| Haiku 4.5, retained-notices view (session-limit notices kept as recorded answers) | no | 58 (30.4%) | 50 (28.9%) | 49 (28.8%) | 72 (37.7%) | 64 (37.0%) | 63 (37.1%) |
| EXP1__claude-sonnet-5 | yes | 122 (63.9%) | 111 (64.2%) | 108 (63.5%) | 143 (74.9%) | 131 (75.7%) | 128 (75.3%) |
| EXP2__claude-opus-5-5 | yes | 126 (66.0%) | 117 (67.6%) | 114 (67.1%) | 155 (81.2%) | 141 (81.5%) | 138 (81.2%) |
| EXP2__local_deepseek_r1_qwen_32b | yes | 48 (25.1%) | 42 (24.3%) | 42 (24.7%) | 57 (29.8%) | 50 (28.9%) | 50 (29.4%) |
| EXP2__local_gemma3_27b | yes | 55 (28.8%) | 49 (28.3%) | 48 (28.2%) | 87 (45.5%) | 78 (45.1%) | 77 (45.3%) |
| EXP2__local_glm45_air_fp8 | yes | 15 (7.9%) | 13 (7.5%) | 13 (7.6%) | 18 (9.4%) | 15 (8.7%) | 15 (8.8%) |
| EXP2__local_gpt_oss_120b | yes | 84 (44.0%) | 76 (43.9%) | 75 (44.1%) | 99 (51.8%) | 90 (52.0%) | 89 (52.4%) |
| EXP2__local_gpt_oss_20b | yes | 79 (41.4%) | 72 (41.6%) | 71 (41.8%) | 88 (46.1%) | 78 (45.1%) | 77 (45.3%) |
| EXP2__local_kimi_linear_48b_a3b_instruct | yes | 21 (11.0%) | 18 (10.4%) | 18 (10.6%) | 51 (26.7%) | 45 (26.0%) | 44 (25.9%) |
| EXP2__local_nemotron35_lightning_30b_a3b | yes | 54 (28.3%) | 48 (27.7%) | 47 (27.6%) | 55 (28.8%) | 49 (28.3%) | 48 (28.2%) |
| EXP2__local_nemotron3_super_120b_a12b_fp8 | yes | 95 (49.7%) | 87 (50.3%) | 86 (50.6%) | 95 (49.7%) | 87 (50.3%) | 86 (50.6%) |
| EXP4__gemini-3.1-pro | yes | 137 (71.7%) | 126 (72.8%) | 124 (72.9%) | 153 (80.1%) | 141 (81.5%) | 139 (81.8%) |
| EXP4__gpt-5.6-luna | yes | 122 (63.9%) | 112 (64.7%) | 109 (64.1%) | 142 (74.3%) | 130 (75.1%) | 127 (74.7%) |
| Haiku 4.5, outage-continuation view (the view used in the earlier main table) | yes | 97 (50.8%) | 86 (49.7%) | 85 (50.0%) | 121 (63.4%) | 110 (63.6%) | 109 (64.1%) |

| View | 255 Hit@1 | 230 Hit@1 | 227 Hit@1 | 255 Hit@3 | 230 Hit@3 | 227 Hit@3 |
|---|---|---|---|---|---|---|
| Haiku 4.5, retained-notices view (session-limit notices kept as recorded answers) | 87 (34.1%) | 78 (33.9%) | 77 (33.9%) | 108 (42.4%) | 97 (42.2%) | 96 (42.3%) |
| EXP1__claude-sonnet-5 | 166 (65.1%) | 152 (66.1%) | 149 (65.6%) | 202 (79.2%) | 185 (80.4%) | 182 (80.2%) |
| EXP2__claude-opus-5-5 | 178 (69.8%) | 163 (70.9%) | 160 (70.5%) | 216 (84.7%) | 195 (84.8%) | 192 (84.6%) |
| EXP2__local_deepseek_r1_qwen_32b | 79 (31.0%) | 69 (30.0%) | 69 (30.4%) | 91 (35.7%) | 80 (34.8%) | 80 (35.2%) |
| EXP2__local_gemma3_27b | 86 (33.7%) | 76 (33.0%) | 75 (33.0%) | 133 (52.2%) | 118 (51.3%) | 117 (51.5%) |
| EXP2__local_glm45_air_fp8 | 22 (8.6%) | 18 (7.8%) | 18 (7.9%) | 28 (11.0%) | 23 (10.0%) | 23 (10.1%) |
| EXP2__local_gpt_oss_120b | 126 (49.4%) | 114 (49.6%) | 113 (49.8%) | 152 (59.6%) | 138 (60.0%) | 137 (60.4%) |
| EXP2__local_gpt_oss_20b | 119 (46.7%) | 108 (47.0%) | 107 (47.1%) | 132 (51.8%) | 118 (51.3%) | 117 (51.5%) |
| EXP2__local_kimi_linear_48b_a3b_instruct | 46 (18.0%) | 40 (17.4%) | 40 (17.6%) | 97 (38.0%) | 86 (37.4%) | 85 (37.4%) |
| EXP2__local_nemotron35_lightning_30b_a3b | 81 (31.8%) | 72 (31.3%) | 71 (31.3%) | 83 (32.5%) | 74 (32.2%) | 73 (32.2%) |
| EXP2__local_nemotron3_super_120b_a12b_fp8 | 143 (56.1%) | 131 (57.0%) | 130 (57.3%) | 145 (56.9%) | 132 (57.4%) | 131 (57.7%) |
| EXP4__gemini-3.1-pro | 190 (74.5%) | 172 (74.8%) | 170 (74.9%) | 215 (84.3%) | 196 (85.2%) | 194 (85.5%) |
| EXP4__gpt-5.6-luna | 178 (69.8%) | 162 (70.4%) | 159 (70.0%) | 200 (78.4%) | 182 (79.1%) | 179 (78.9%) |
| Haiku 4.5, outage-continuation view (the view used in the earlier main table) | 141 (55.3%) | 126 (54.8%) | 125 (55.1%) | 175 (68.6%) | 158 (68.7%) | 157 (69.2%) |
