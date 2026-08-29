# multilinear-sat (en français)

Un solveur SAT par relaxation continue et recherche locale par lots : une bibliothèque C++20
avec un backend CUDA et un backend CPU (OpenMP) qui calculent la même chose à partir de la
même graine. Chaque tour du lot est une amorce puis un polissage : des milliers de fentes
partent d'un point aléatoire, du tout-faux, d'une courte montée de gradient projetée sur
l'énergie multilinéaire (de Fourier) de la formule, ou de la boucle d'échantillonnage
tiltée, puis marchent (WalkSAT/SKC, probSAT, Schöning ou Metropolis) depuis le point arrondi,
avec des redémarrages selon la suite de Luby. Toute réponse est un certificat : le solveur
n'imprime SATISFIABLE qu'après avoir vérifié qu'une affectation satisfait chaque ligne. Il ne
conclut jamais UNSAT ; il rapporte deux postérieurs, des nombres sur les redémarrages échoués
et jamais un verdict. La version 0.2 lit le k-CNF (DIMACS) et le XNF (lignes `x`, parités
impaires) : une parité est un monôme de Walsh dans l'énergie et une bascule dans la marche.

**Ce qui n'est pas prétendu.** Sur le 3-SAT aléatoire uniforme, le gradient seul ne bat ni
probSAT ni CaDiCaL (`benchmark/results.md`), et la marche est l'algorithme de probSAT, plus
lente par chaîne que sa boucle réglée à la main ; ce que le lot rapporte, ce que chaque amorce
rapporte par redémarrage, ce que vaut le postérieur face à kissat, et ce que fait la parité
native sur MM-Challenge-1 sont mesurés dans `benchmark/findings-walk/`, quoi qu'ils montrent.
Le code n'est encore publié nulle part ; `CITATION.cff` laisse son champ de dépôt vide
jusque-là.

## Ce qu'il y a ici

| Dossier | Rôle |
|---|---|
| `solver/`, `cli/`, `tests/` | la bibliothèque (formule avec lignes de parité, énergies, aléa par hachage, la marche, l'amorce tiltée, les deux backends, la boucle de tours, les postérieurs), sa ligne de commande DIMACS et XNF, et la suite doctest |
| [`gaussian_surrogate/`](gaussian_surrogate/README.md) | le carnet de recherche Python de l'étude de l'objectif : la variance du nombre de clauses satisfaites aide-t-elle la montée (elle atterrit plus près et coûte 3 à 86 fois plus par pas), la boucle tiltée, les amorces tarifées avec un noyau limité par les lancements ; ses conclusions dans `findings.md` et `findings-tilted/` |
| [`literature/`](literature/README.md) | sept revues, chacune un dossier d'étapes de thèse aux références vérifiées, et l'index |
| [`method/`](method/README.md) | la méthode telle que construite, les deux notes de conception (la conception proposée), et `algorithm.md`, la variante survivante écrite en pseudo-code avec le nombre derrière chaque choix |
| [`benchmark/`](benchmark/README.md) | chaque mesure avec sa provenance (commande, graine, commit, empreinte du binaire, état du GPU), les conclusions de la marche, et `arms/` : les variantes tarifées sur un même protocole, le front de dominance et les variantes rejetées avec leurs nombres |

## Construire

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release          # backend CUDA si nvcc est trouvé
    cmake --build build -j
    ctest --test-dir build --output-on-failure

`-DMULTILINEAR_SAT_CUDA=OFF` ne construit que le backend CPU. Avec une chaîne CUDA hors du
chemin par défaut, passer `-DCMAKE_CUDA_COMPILER=/chemin/vers/nvcc`. Requiert CMake 3.24, un
compilateur C++20, et en option OpenMP et CUDA 12. Le carnet Python tourne dans tout
environnement avec torch, numpy et pytest : `python -m pytest gaussian_surrogate/tests -q`.

## Utiliser

    ./build/multilinear-sat instance.cnf --seed-kind uniform --polish-flips 2500    # la marche seule (la forme de probSAT)
    ./build/multilinear-sat instance.cnf --seed-steps 200 --polish-flips 2500       # la montée, puis la marche
    ./build/multilinear-sat instance.xnf --seed-kind all-false --polish-flips 100000 --batch-size 1024
    # imprime "c json {...}" avec les statistiques du tour, puis "s SATISFIABLE" et des lignes "v ..."
    # (code de sortie 10) ou "s UNKNOWN" (code de sortie 0)

`--run-limit N` achève N tours du lot entier au lieu de s'arrêter au premier certificat et
compte chaque issue de polissage, ce qui est la mesure de la probabilité de succès par
redémarrage. `--rigorous-fraction X` fait marcher une part du lot selon la règle de Schöning
depuis des départs uniformes pendant 3n bascules ; leurs échecs alimentent le postérieur
rigoureux, les autres le postérieur Beta. Chaque réglage vit dans `solver/configuration.hpp`
et a une option de ligne de commande du même nom.

Depuis C++ :

```cpp
#include "formula.hpp"
#include "solver.hpp"
using namespace multilinear_sat;
Formula formula = read_dimacs("instance.xnf");     // DIMACS ou XNF ; ou make_formula(n, clauses, parities)
SolverConfiguration configuration;                 // chaque réglage, avec sa valeur par défaut
configuration.seed_kind = SeedKind::Uniform;       // Uniform, AllFalse, Ascent ou Tilted
configuration.polish_flips = 2500;                 // bascules par fente et par tour, fois luby(tour)
configuration.walk.walk_rule = WalkRule::ProbSat;  // Skc, ProbSat, Schoening ou Metropolis
SolveResult result = solve(formula, configuration);
if (result.status == Status::Satisfiable) {
    // result.assignment[v] vaut +1 (vrai) ou -1 (faux) pour la variable v + 1
}
```

Pour l'intégrer à un autre projet CMake, `add_subdirectory(multilinear-sat)` (ou
FetchContent) et `target_link_libraries(votre_cible PRIVATE multilinear_sat)` ; les tests et
la ligne de commande ne sont construits que lorsque ce projet est le projet racine.

## Citation et licence

MIT. Citer le logiciel (`CITATION.cff`) avec FourierSAT (Kyrillidis, Shrivastava, Vardi,
Zhang, AAAI 2020), dont il implémente la relaxation ; la lignée GPU continue avec
FastFourierSAT (Cen, Zhang, Fong, AAAI 2025), dont le corollaire 2 est le gradient de parité.
Les règles de la marche sont WalkSAT/SKC (Selman, Kautz, Cohen 1994), probSAT (Balint,
Schöning, SAT 2012) et l'algorithme de Schöning (FOCS 1999) ; les poids recuits sont ceux de
Neal (2001). Mentions tierces dans `NOTICE`. `README.md` dit la même chose en anglais.
