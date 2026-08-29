# References

The author's working notes (August 2026) are the source of [origin.md](origin.md); they are not
public.

- C. H. Papadimitriou. On selecting a satisfying truth assignment. FOCS 1991.
- U. Schöning. A probabilistic algorithm for k-SAT and constraint satisfaction problems.
  FOCS 1999.
- B. Selman, H. Kautz, B. Cohen. Noise strategies for improving local search. AAAI 1994.
  (WalkSAT)
- A. Balint, U. Schöning. Choosing probability distributions for stochastic local search and
  the role of make versus break. SAT 2012. (probSAT)
- A. Kyrillidis, A. Shrivastava, M. Y. Vardi, Z. Zhang. FourierSAT: a Fourier expansion-based
  algebraic framework for solving hybrid Boolean constraints. AAAI 2020. arXiv:1912.01032.
- A. Kyrillidis, M. Y. Vardi, Z. Zhang. On continuous local BDD-based search for hybrid SAT
  solving. AAAI 2021. arXiv:2012.07983. (GradSAT)
- Y. Cen, Z. Zhang, X. Fong. Massively parallel continuous local search for hybrid SAT solving
  on GPUs. AAAI 2025. arXiv:2308.15020. (FastFourierSAT)
- M. Mézard, G. Parisi, R. Zecchina. Analytic and algorithmic solution of random
  satisfiability problems. Science 297, 2002. (Survey Propagation)
- M. Ercsey-Ravasz, Z. Toroczkai. Optimization hardness as transient chaos in an analog
  approach to constraint satisfaction. Nature Physics 7, 2011.
- L. H. Y. Chen, Q.-M. Shao. Normal approximation under local dependence. Annals of
  Probability 32(3), 2004.
- R. Arratia, L. Goldstein, L. Gordon. Two moments suffice for Poisson approximations: the
  Chen-Stein method. Annals of Probability 17(1), 1989. (the bound in regimes.md)
- H. E. Daniels. Saddlepoint approximations in statistics. Annals of Mathematical Statistics
  25, 1954.
- R. Lugannani, S. Rice. Saddle point approximation for the distribution of the sum of
  independent random variables. Advances in Applied Probability 12, 1980.
- T. Plefka. Convergence condition of the TAP equation for the infinite-ranged Ising spin glass
  model. Journal of Physics A 15, 1982. (the expansion around the product measure)
- J. S. Yedidia, W. T. Freeman, Y. Weiss. Constructing free-energy approximations and
  generalized belief propagation algorithms. IEEE Transactions on Information Theory 51(7),
  2005. (the Bethe / pair approximation)
- R. O'Donnell. Analysis of Boolean Functions. Cambridge University Press, 2014.
- D. P. Williamson, D. B. Shmoys. The Design of Approximation Algorithms. Cambridge University
  Press, 2011, chapter 5. (a multilinear polynomial attains its maximum at a vertex)
- M. Chavira, A. Darwiche. On probabilistic inference by weighted model counting. Artificial
  Intelligence 172, 2008. (P(all satisfied) under the product measure is a weighted model count)
- J. Xu, Z. Zhang, T. Friedman, Y. Liang, G. Van den Broeck. A semantic loss function for deep
  learning with symbolic knowledge. ICML 2018. arXiv:1711.11157. (the exact objective, descended)
- R. Y. Rubinstein. The cross-entropy method for combinatorial and continuous optimization.
  Methodology and Computing in Applied Probability 1, 1999. (the sampled skeleton)
- H. Wang, N. Yan, C. Li, P. Li. Unsupervised learning for combinatorial optimization with
  principled objective relaxation. NeurIPS 2022. arXiv:2207.05984. (entry-wise concavity)
- R. Bissacot, R. Fernández, A. Procacci, B. Scoppola. An improvement of the Lovász local lemma
  via cluster expansion. Combinatorics, Probability and Computing 20, 2011. arXiv:0910.1824.
  (the pair closure's published form)
- H. Jonsson, B. Söderberg. An information-based neural approach to constraint satisfaction.
  Neural Computation 13, 2001. arXiv:cond-mat/0105319. (a k-SAT annealer whose free energy is
  deliberately not the mean-field one; the nearest ancestor)

The full, verified bibliography of the 2026-08-29 review is
`../../literature/gaussian-like-objectives/references.bib`.
