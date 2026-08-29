# multilinear-sat (résumé en français)

Un solveur SAT par relaxation continue, en C++20, avec un backend CUDA et un backend CPU
(OpenMP) qui calculent la même chose à partir de la même graine. Chaque clause devient son
énergie multilinéaire (de Fourier) sur le cube [-1, 1]^n ; des milliers de points de départ
aléatoires descendent en parallèle sur la somme, avec inertie, un coup de bruit concentré sur
les variables des clauses violées, et des redémarrages de Luby. Toute réponse est un
certificat : SATISFIABLE n'est imprimé qu'après vérification qu'un point arrondi satisfait
chaque clause. Le solveur ne conclut jamais UNSAT.

La version 0.2 ajoute la recherche locale par lots comme polissage de chaque redémarrage
(WalkSAT/SKC, probSAT, Schöning, Metropolis, depuis un point uniforme, tout-faux, la montée
de gradient ou la boucle tiltée), les contraintes de parité du format XNF prises telles
quelles (un monôme de Walsh dans l'énergie, une bascule dans la marche), et deux
postérieurs sur UNSAT qui ne deviennent jamais un verdict ; `benchmark/findings-walk/` donne ce que
tout cela mesure. C'est d'abord une bibliothèque (statique, sans Python), faite pour être
liée à d'autres codes C++, avec une ligne de commande pour mesurer.

Ce qui n'est pas prétendu : sur le 3-SAT aléatoire uniforme, il ne bat ni probSAT ni CaDiCaL ;
`benchmark/results.md` donne la comparaison mesurée. Les relaxations continues gagnent là où
les encodages CNF coûtent (cardinalité, XOR, MaxCut pondéré) ; ces contraintes sont la
version suivante. Revue de littérature : `literature/review.md` ; méthode et coût :
`method/README.md` ; construction et usage : `README.md`.
