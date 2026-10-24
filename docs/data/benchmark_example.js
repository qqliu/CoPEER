window.COPEER_DATA = window.COPEER_DATA || {};
window.COPEER_DATA["benchmark_example"] = {
 "source": {
  "commit": "cb9312a",
  "main_tex_sha256": "8e2d3c7cbed3535cf6ba877ab7b01e06042ec205f8c97ec74b41c34382cdfb53",
  "label": "fig:benchmark-example",
  "main_tex_lines": [
   915,
   951
  ],
  "caption": "A primary localization input with a false intermediate deduction at line 5 (reddit_learnmath_dm6itc). The critic does not see the held-out reference evidence and selects line 5 first. The witness refutes the identity at line 5; the theorem itself is true."
 },
 "record_id": "reddit_learnmath_dm6itc",
 "numbered_lines_total": 10,
 "excerpt_lines": [
  {
   "line": 1,
   "tex": "Q1: Suppose a function has the property that whenever \"x\" is in the domain of \"f\", then so is \"-x\". Show that f can be written as the sum of an even function and an odd function."
  },
  {
   "line": 3,
   "tex": "By definition, an even function has the equation $f(x) = f(-x)$ and by definition, an odd function satisfies the equation $f(-x) = -f(x)$."
  },
  {
   "line": 5,
   "tex": "Therefore, f can be written such that $f(x) = f(-x) + (-f(x))$."
  }
 ],
 "recorded_selection": {
  "model": "GPT-OSS 20B",
  "candidates": [
   5,
   7
  ],
  "hit1": 1,
  "hit3": 1
 },
 "reference_line": 5,
 "witness_tex": "$D=\\{-1,1\\}$, $f \\equiv 1$, $x=1$. Then $f(1)=1$ while $f(-1)+(-f(1)) = 1 - 1 = 0 \\neq 1$.",
 "lean_statement_text": "The domain is closed under negation, 1 belongs to it, and $f(1) \\neq f(-1) + (-f(1))$."
};
