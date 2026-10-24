# Corrected v2 exploratory cohort: exact source package

The selected-item status searches used the 2026-09-03 cutoff. The corrected v2 pool was frozen on 2026-09-04 after a pre-launch recheck found that one unselected v1 item had already been resolved. The deterministic selection was rerun from the corrected pool without solver, auditor, model, or BugBank access; the same six items remained selected. They appear below in selection-rank order. Source text in fenced blocks is copied from the authors' arXiv TeX source; only TeX line wrapping has been retained. Explanatory notes outside the fences are curation notes, not source quotations.

## 1. `arxiv:2511.02892v1#Problem 2.1`

Primary source: *Open problems of the 33rd Workshop on Cycles and Colourings*, arXiv:2511.02892v1, PDF p. 3, `https://arxiv.org/pdf/2511.02892v1`.

Source-file locator: `PROBLEMS25/Dvorak.tex`, lines 11--34 in the v1 source archive.

Verbatim model, definition, and final statement:

```tex
Let us consider a random 4-regular graph $G$, defined as the union of two uniformly random cycles on the same vertex
set\footnote{Strictly speaking, this is a multigraph; but $G$ is simple with constant probability, and thus this does not affect
the problem.  Moreover, one could think that considering uniformly random 4-regular graphs (say arising from the configuration model) would be more natural.
However, a uniformly random 4-regular graph a.a.s. has two disjoint Hamiltonian cycles~\cite{twoham}, and thus this again does not
play any role in the proposed problem. Another a.a.s. equivalent model one could consider is the union of four uniformly random perfect matchings.}.
Such a graph $G$ is a.a.s. 3-colorable~\cite{threecol}, but it is an open question whether $G$ is
also a.a.s. \emph{3-choosable}, i.e., properly colorable for all assignments of lists of three allowed colors to vertices.

A natural approach to resolving this is by using the Alon-Tarsi method~\cite{alontarsi}:  Consider the \emph{graph
polynomial} $P_G=\prod_{uv\in E(G)} (u-v)$ of a graph $G$, whose variables correspond to the vertices of $G$.
\begin{boxedtheorem}[Alon and Tarsi~\cite{alontarsi}]
Let $G$ be a graph, let $k$ be a positive integer and let $f:V(G)\to \{0,\ldots,k-1\}$ be any function.
If the coefficient of $P_G$ at the monomial $\prod_{v\in V(G)} v^{f(v)}$ is non-zero, then $G$ is $k$-choosable.
\end{boxedtheorem}
Note that the graph polynomial $P_G$ is uniform and every monomial which appears in it with a non-zero coefficient
has the same total degree, equal to $|E(G)|$.  Hence, in our (4-regular) setting, the only relevant monomial is $\prod_{v\in V(G)} v^2$.

\begin{boxedproblem}\label{dvorak1}
    Let $G$ be a random 4-regular graph.  Is it true that the coefficient of $P_G$ at $\prod_{v\in V(G)} v^2$ is a.a.s. non-zero?
\end{boxedproblem}

It is relatively easy to check that (in the two Hamiltonian cycles model) the expected value of the coefficient is zero.
Hence, to prove the claim, one would need some anti-concentration inequality.  Conversely, to disprove it, one would
need to show that the coefficient is tightly concentrated on its expected value.
```

Interpretation needed for a formal target: “a.a.s.” means that the probability tends to one as the number of vertices tends to infinity, in the two-uniformly-random-cycles model fixed by the source.

## 2. `arxiv:2603.29571v1#Conjecture 22`

Primary source: *Randomstrasse101: Open Problems of 2025*, arXiv:2603.29571v1, PDF p. 8, `https://arxiv.org/pdf/2603.29571v1`.

Source-file locator: `2025-MUBandZauner-Afonso.tex`, lines 2--14 in the v1 source archive.

Verbatim definition, open-status context, and final statement:

```tex
Finite frame theory is the source of many beautiful questions. A remarkable example concerns the existence of Mutually Unbiased Bases,  objects of interest in Quantum Physics (see~\cite{McNulty2024-MUBs} for a review).

\begin{definition}[Mutually Unbiased Bases]
    Two orthonormal bases $\{v_1, \dots, v_d\}, \{w_1, \dots, w_d\} \subset \mathbb{C}^d$ are called \emph{mutually unbiased} if $|\langle v_i, w_j \rangle| = 1 / \sqrt{d}$ for all $i, j$. Let $\mathrm{MUB}(d)$ denote the largest possible number of (simultaneously) mutually unbiased bases (MUBs) in $\mathbb{C}^d$.
\end{definition}

In~\cite{Bandyopadhyay2002-MUBs} it is shown that $\mathrm{MUB}(d)\leq d+1$ and that equality is achieved when $d$ is a prime power. For $d$ not a prime power, the problem of determining $\mathrm{MUB}(d)$ is still open. The smallest open instance is particularly well known for being a tantalizing open problem that has remained open (see Open Problem 6.2 in~\cite{Afonso10L42P}).

\begin{conjecture}
    Let $\mathrm{MUB}(d)$ denote the largest possible number of (simultaneously) mutually unbiased bases (MUBs) in $\mathbb{C}^d$. We have $\mathrm{MUB}(6)<7$.
\end{conjecture}
```

## 3. `arxiv:2603.29571v1#Conjecture 26`

Primary source: *Randomstrasse101: Open Problems of 2025*, arXiv:2603.29571v1, PDF p. 9, `https://arxiv.org/pdf/2603.29571v1`.

Source-file locators: Paley/localization and statement in `2025-Paley-Afonso.tex`, lines 1--20; the preserved Lovász theta definition extract in `2025-LovaszCirculant-Daniil.tex`, lines 140--159 (the displayed theta formula itself is on lines 151--157).

Verbatim Paley graph, localization, empirical-status context, and final statement:

```tex
Given a prime number $p$ such that $p \equiv 1 \pmod{4}$ the Paley graph on $p$ nodes $G_p$ is the graph where nodes $i$ and $j$ are connected if $i-j$ is a quadratic residue modulo $p$. This graph is a regular graph with degree $\frac{p-1}{2}$ and it is believed to have many pseudo-random properties (mimicking in many ways a uniformly random regular graph of the same degree, or even a $G(n,1/2)$). See~\cite{Kunisky-2023-SpectralPseudorandomnessPaleyClique} for a nice overview aligned with the topic of this post.

Let $\omega(G_p)$ denote the clique number of $G_p$ i.e. the size of the largest set of nodes that are all pairwise connected by an edge.

We start with the notion of localization~\cite{MMP-2019-LPCliquesPaley,Kunisky-2023-SpectralPseudorandomnessPaleyClique}: Let $G_{p,1}$ denote the induced subgraph on the vertices adjacent to the node 0, which we call the 1-localization. Because the 1-localization does not depend on the node picked (see~\cite{Kunisky-2023-SpectralPseudorandomnessPaleyClique}) we have $\omega(G_p) \leq \omega(G_{p,1}) + 1 \leq \vartheta(\overline{G_p})+1$. It was observed empirically in \cite{MMP-2019-LPCliquesPaley} that $\vartheta(\overline{G_{p,1}}) \sim \sqrt{p/2}$, which would recover the Hanson-Petridis bound (also, note that $G_{p,1}$ is a circulant graph and so the SDP corresponding to $\vartheta(\overline{G_{p,1}})$ reduces to an LP).

\begin{conjecture}
    $\vartheta(\overline{G_{p,1}}) \sim \sqrt{p/2}$ (for $p \equiv 1 \pmod{4}$ prime) where $G_{p,1}$ is the 1-localization of the Paley Graph described above.
\end{conjecture}
```

Verbatim Lovász theta definition used by this source:

```tex
Lov\'asz number is a natural semidefinite programming (SDP) relaxation for~\Cref{def:alpha}:

\begin{equation}
\label{def:ltn}
    \vartheta(G) := \max_{X \in \mathbb{R}^{n \times n}}
    \Big\{\sum_{i, j} X_{ij} \text{, such that } X \succeq 0, \mathrm{Tr}\,X = 1, \text{ and } X_{ij} = 0\text{ for all }(i, j) \in E(G)\Big\}.
\end{equation}
```

Scope made explicit by the source: the asymptotic is as `p` tends to infinity through primes congruent to 1 modulo 4. `overline{G}` denotes graph complement.

## 4. `arxiv:2603.29571v1#Conjecture 17`

Primary source: *Randomstrasse101: Open Problems of 2025*, arXiv:2603.29571v1, PDF p. 4, `https://arxiv.org/pdf/2603.29571v1`.

Source-file locator: `2025-LovaszCirculant-Daniil.tex`, lines 140--168.

Verbatim graph model, status context, and final statement:

```tex
Lov\'asz number is a natural semidefinite programming (SDP) relaxation for~\Cref{def:alpha}:

\begin{equation}
\label{def:ltn}
    \vartheta(G) := \max_{X \in \mathbb{R}^{n \times n}}
    \Big\{\sum_{i, j} X_{ij} \text{, such that } X \succeq 0, \mathrm{Tr}\,X = 1, \text{ and } X_{ij} = 0\text{ for all }(i, j) \in E(G)\Big\}.
\end{equation}

An interesting question is to characterize the Lov\'asz number for random graphs.
A well-known family of random graphs is the Erd\H{o}s-R\'enyi random graphs \(G(n, p)\). Here, \(n\) denotes the number of vertices, and \(0 \leq p \leq 1\) is the probability parameter. To sample a graph from \(G(n, p)\), for each pair of vertices \(i \neq j \in [n]\), one adds an edge independently with probability \(p\). The random graphs \(G(n, p)\) are ubiquitous in mathematics; for instance, they are used in combinatorics to lower bound \emph{Ramsey} numbers. There are several results on the Lov\'asz number for Erd\H{o}s-R\'enyi random graphs \(G(n, p)\) (see~\cite{juhasz1982asymptotic,coja2005lovasz,aroranote}). However, the precise asymptotics of the Lov\'asz number for \(G(n, 1/2)\) is still open.

\begin{conjecture}
    Let \(G\) be distributed as \(G(n, 1/2)\). Then,
    \begin{equation}
        \mathbb{E} \vartheta(G) = (1 + o(1))\sqrt{n}.
    \end{equation}
\end{conjecture}
```

Scope: the asymptotic is `n -> infinity`; expectation is over the independently sampled edges of `G(n,1/2)`.

## 5. `arxiv:2511.02892v1#Problem 5.1`

Primary source: *Open problems of the 33rd Workshop on Cycles and Colourings*, arXiv:2511.02892v1, PDF p. 6, `https://arxiv.org/pdf/2511.02892v1`.

Source-file locator: `PROBLEMS25/Luzar.tex`, lines 21--37 in the v1 source archive.

Verbatim definition, context, and final statement:

```tex
A proper coloring of vertices where in the open neighborhood of every vertex exactly $k$ colors appear
is $k$-homogeneous coloring~\cite{JanMad15}.
Clearly, a graph admits $1$-homogeneous coloring if and only if it is bipartite.
Much more interesting is $2$-homogeneous coloring.
For bipartite cubic graphs, it is known that they admit a $2$-homogeneous coloring with at most $6$ colors~\cite{JanLuzMadaSot17}.
On the other hand, there are cubic graphs that do not admit a homogeneous $2$-coloring;
e.g., consider the graph containing as a subgraph a triangular prism with one edge of a triangle subdivided.

Two questions naturally arise; namely, which cubic graphs admit a $2$-homogeneous coloring,
and what is the minimum number of colors sufficient to color any cubic graph that admits a $2$-homogeneous coloring.
Based on some preliminary research%with R. Sot\'{a}k
, we propose the following two conjectures.

\begin{boxedproblem}\label{luzar1}
	If a cubic graph admits a $2$-homogeneous coloring,
	then $4$ colors are always sufficient.
\end{boxedproblem}
```

Standard terminology made explicit for a formal target: cubic means every vertex has degree 3; the open neighborhood of a vertex contains its adjacent vertices and not the vertex itself; proper means adjacent vertices have different colors. The source says “4 colors are sufficient,” so a coloring using at most four colors is intended.

## 6. `arxiv:2603.29571v1#Conjecture 28`

Primary source: *Randomstrasse101: Open Problems of 2025*, arXiv:2603.29571v1, PDF p. 10, `https://arxiv.org/pdf/2603.29571v1`.

Source-file locator: `2025-Paley-Afonso.tex`, lines 1--5 and 30--35.

Verbatim Paley graph and final-statement context:

```tex
Given a prime number $p$ such that $p \equiv 1 \pmod{4}$ the Paley graph on $p$ nodes $G_p$ is the graph where nodes $i$ and $j$ are connected if $i-j$ is a quadratic residue modulo $p$. This graph is a regular graph with degree $\frac{p-1}{2}$ and it is believed to have many pseudo-random properties (mimicking in many ways a uniformly random regular graph of the same degree, or even a $G(n,1/2)$). See~\cite{Kunisky-2023-SpectralPseudorandomnessPaleyClique} for a nice overview aligned with the topic of this post.

Let $\omega(G_p)$ denote the clique number of $G_p$ i.e. the size of the largest set of nodes that are all pairwise connected by an edge.

There is another approach to to use convex relaxation to potentially improve over upper bounds on the $
\omega(G_p)$. Recall that the Lovasz $\vartheta$ function can be viewed a as degree-2 Sum-of-Squares relaxation of the clique (or independence) number. A fascinating question is whether the degree-4 Sum-of-Squares relaxation significantly improves on the $\sqrt{p}$ bound, perhaps even improving over the state of the art (see~\cite{KY-2022-PaleyDegree4SOS} for a precise construction of this relaxation). There have been several encouraging numerical experiments (for this and other SDPs)~\cite{KY-2022-PaleyDegree4SOS,kobzar2023revisiting,wang2024lower}. We particularly note that the numerical experiments in~\cite{KY-2022-PaleyDegree4SOS} suggest even a polynomial improvement may be possible, although the authors prove that it cannot improve beyond $\Omega(p^{\frac13})$.

\begin{conjecture}
    There exists $\varepsilon>0$ such that the Sum-of-Squares relaxation of degree 4 for the clique number of the Paley graph gives a bound of $O(p^{\frac12-\varepsilon})$.
\end{conjecture}
```

The conjecture's cited primary definition is Kunisky and Yu, *A degree 4 sum-of-squares lower bound for the clique number of the Paley graph*, arXiv:2211.02713v2, PDF pp. 7--8, `https://arxiv.org/pdf/2211.02713v2`. The preserved supporting extract is `main.tex`, lines 228--371; equation `degree_4_SOS` itself is on lines 339--356. Its degree-4 program, copied verbatim, is:

```tex
On the other hand, once the degree increases to $2d = 4$, the resulting SDP is not as well understood.
This SDP, which we study in the remainder of the paper, takes the form
\begin{equation}
\label{degree_4_SOS}
    \SOS_{4}(G) = \left\{
    \begin{array}{ll}
    \text{maximize} & \sum_{i = 1}^n M^{0, 1}_{\emptyset, i} \\
    \text{subject to} & M^{r, c} \in \RR^{\binom{[n]}{r} \times \binom{[n]}{c}} \text{ for } r, c \in \{0, 1, 2\}, \\
    & M^{r, c}_{S, T} \text{ depends only on } S \cup T, \\
    & M^{r, c}_{S, T} = 0 \text{ whenever } S \cup T \notin \mathcal{K}(G), \\
    & M = \begin{bmatrix}
    1 & M^{0, 1} & M^{0, 2} \\
    M^{1, 0} & M^{1, 1} & M^{1,2}\\
    M^{2, 0} & M^{2,1} & M^{2,2}
\end{bmatrix} \succeq 0
\end{array}
    \right\}.
\end{equation}
```

Here `[n]={1,...,n}`, `binom([n],r)` denotes the r-element subsets of the vertex set, and `K(G)` is the family of cliques of `G` (all stated in the cited paper's immediately preceding setup). The source context fixes `p -> infinity` through primes `p congruent to 1 mod 4`. Thus the exact target is: there exists a fixed epsilon greater than zero and constants `C,p0` such that `SOS_4(G_p) <= C p^(1/2-epsilon)` for every such prime `p>=p0`.

## Source-archive provenance

- arXiv:2511.02892v1 source archive: `../paired_open_problem_exploratory_sources_v2/sources/arxiv_2511_02892v1/source.tar`, SHA-256 `35bd441323a652d6fc315a5777bce6a4db8cee2c1379e15cd57eb052f78b8873`.
- arXiv:2603.29571v1 source archive: `../paired_open_problem_exploratory_sources_v2/sources/arxiv_2603_29571v1/source.tar`, SHA-256 `99e0968bf51fbbb36ba8b3d3412e7dc6eb8c7f5a1b617fbb2acace2aeef08bdc`.
- arXiv:2211.02713v2 supporting source archive: `../paired_open_problem_exploratory_sources_v2/sources/arxiv_2211_02713v2/source.tar`, SHA-256 `a770245577dea575745269080cd7eb428c73781dfcb294725332dc3a15060019`.

No source wording in the fenced blocks was silently repaired. In particular, the source's typos and double spaces remain where copied.
