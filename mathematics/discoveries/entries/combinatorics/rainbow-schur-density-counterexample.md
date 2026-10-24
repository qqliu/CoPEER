# A rainbow Schur coloring of asymptotic density nine twenty-seconds

> Deposition record dated 11 September 2026. Read [later mathematical and attribution updates](../../README.md#later-updates) alongside this original record.

## Object

A Schur triple is an ordered triple $(x,y,z)\in[n]^3$ with $x+y=z$;
it is rainbow if its three entries have pairwise different colors. Exchanging
$x$ and $y$ gives a distinct triple when $x\ne y$. For every integer $m\ge1$,
set $n=22m$ and define

$$
c_m(k)=\begin{cases}
1,&k\text{ even},\\
2,&k\text{ odd and }(k\le8m\text{ or }k>20m),\\
3,&k\text{ odd and }8m<k\le20m.
\end{cases}
$$

The color class sizes are $11m$, $5m$, and $6m$ respectively. The color-2
odds consist of a lower block of size $4m$ and an upper block of size $m$.

## What it kills

Parczyk and Spiegel conjectured that their asymptotic density lower bound
$2/5$ is tight, immediately after Theorem 1 in the journal version
(Theorem 1.1 in arXiv v2). Its upper-bound component says

$$
\forall\varepsilon>0\ \exists N\ \forall n\ge N\ \forall c:[n]\to\{1,2,3\},
\qquad R(c)\le(2/5+\varepsilon)\binom n2,
$$

where $R(c)$ counts rainbow ordered Schur triples. This family disproves
that original asymptotic claim. The finite instance $m=1$ alone would not
disprove an eventual asymptotic bound; the full unbounded family is essential.
The separate uniqueness assertion is not an independently resolved target here.

## Why it works

There are exactly $\sum_{z=2}^n(z-1)=\binom n2$ ordered Schur triples,
including the non-rainbow diagonal cases $x=y$. This is the source's normalization.

For mixed-parity addends, a rainbow triple has an even addend of color 1 and
two odd entries of different colors. Given any color-2 odd $u$ and color-3
odd $v$, write $a=\min(u,v)$, $z=\max(u,v)$, and $e=z-a$. Then $e$ is a
positive even integer and exactly two associated triples are $(a,e,z)$ and
$(e,a,z)$. Conversely every mixed-parity rainbow triple determines this pair
of odd entries uniquely. Consequently the mixed-parity contribution is
$2(5m)(6m)=60m^2$.

For two odd addends, the sum is even and has color 1; the addends must have
colors 2 and 3. The high color-2 block cannot contribute: its smallest possible
sum with color 3 is $(20m+1)+(8m+1)>22m$. The remaining two addends are

$$
2i-1\quad(1\le i\le4m),\qquad
8m+2j-1\quad(1\le j\le6m).
$$

Their sum lies in $[22m]$ exactly when $i+j\le7m+1$. For $1\le i\le m+1$
all $6m$ choices of $j$ work. For $m+2\le i\le4m$ there are $7m+1-i$
choices. Thus the number of cross-color pairs is

$$
6m(m+1)+\sum_{i=m+2}^{4m}(7m+1-i)
=6m(m+1)+\frac{(3m-1)9m}{2}
=\frac{39m^2+3m}{2}.
$$

The two addends have different colors, hence are distinct, so each pair has
two orientations. Odd-odd triples therefore contribute $39m^2+3m$.
Even-even triples cannot be rainbow. These cases exhaust all possibilities,
giving $R(c_m)=99m^2+3m$.

The exact density is

$$
\frac{R(c_m)}{\binom{22m}{2}}
=\frac{99m+3}{242m-11}
=\frac9{22}+\frac{165}{22(242m-11)}
\longrightarrow\frac9{22}.
$$

In particular it exceeds $9/22=90/220>89/220=2/5+1/220$ for every $m\ge1$.
Fixing $\varepsilon=1/220$, for any proposed threshold $N$ choose an integer
$m\ge\max(1,\lceil N/22\rceil)$. Then $22m\ge N$ and the asserted upper
bound fails. This negates its exact quantifiers.

## Debugging uses

Use the coloring to check proposed $2/5$ upper bounds and arguments that
restrict the odd numbers to two contiguous color blocks. Use its exact
parity counts to catch missing orientations, dropped boundary terms, and
normalization by $n^2$ in place of $\binom n2$.

## Remarks

The historical discovery appears in the **neutral baseline** for record
`ext5_rainbow_schur_density_two_fifths` in run
`open_frontier_paired_extension_v5r1_20260904`: `gpt-5.6-sol`, reasoning effort
`max`, completed 2026-09-04. The baseline audit and both subsequent arm audits
report `FULLY_RESOLVES_TARGET`, with all six claims `VERIFIED`. This attribution
does not establish an Astra discovery or a discovery caused by BugBank retrieval.
No new Sol calls were made for this entry.

The self-contained argument above establishes the entire family. The new
[exact Python checker](../../certificates/discoveries_20260910/rainbow_schur_check.py)
independently enumerates all ordered Schur triples for $m=1,\ldots,80$, checks
the populations, parity contributions, pair correspondence, and exact rational
gap. Run `python3 certificates/discoveries_20260910/rainbow_schur_check.py`
from the repository root. Finite enumeration supplements the hand proof;
there is no Lean formalization or external proof-assistant certificate.
The sharp optimum is not determined, and novelty beyond the dated source
search and historical artifacts is not certified. The entry remains `draft`.

## References

- Olaf Parczyk and Christoph Spiegel, *An Unsure Note on an Un-Schur Problem*,
  Electronic Journal of Combinatorics **33**(1) (2026), P1.45,
  [DOI 10.37236/13554](https://doi.org/10.37236/13554).
  [Primary arXiv v2 text](https://arxiv.org/html/2410.22024v2): the unnumbered
  conjecture after Theorem 1.1 and Section 2's ordered-triple definition.
- [Provenance and SHA-256 bindings](../../certificates/discoveries_20260910/rainbow_schur_provenance.json)
  identify the source record, archived source PDF, neutral baseline, audits,
  execution state, and original independent checker. The source package's
  title field says "Rainbow Schur triples: Things we cannot do"; the citation
  above uses the actual primary-source title without changing the old record.
