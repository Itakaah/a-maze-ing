# CLAUDE.md — Projet A-Maze-ing (École 42)

## Contexte du projet

Ce projet est un générateur de labyrinthes en Python, réalisé dans le cadre du cursus École 42. Le sujet complet est disponible dans `subject.pdf` à la racine du projet — lis-le intégralement avant de commencer.

**Le code sera évalué en peer-evaluation : je dois pouvoir expliquer chaque ligne.** Toute ta production doit donc privilégier la clarté et la simplicité sur l'élégance ou la concision. C'est la règle absolue de ce projet.

## Priorité n°1 : simplicité avant tout

- Préfère TOUJOURS la solution la plus simple à comprendre, même si elle est plus longue ou moins "pythonique"
- Pas de compréhensions de liste imbriquées, pas de one-liners denses, pas de astuces de langage avancées (walrus operator, unpacking complexe, etc.) si une boucle classique fait la même chose plus clairement
- Pas de métaprogrammation, pas de décorateurs custom, pas de design patterns sophistiqués non nécessaires
- Si une bibliothèque tierce simplifie le code mais le rend moins transparent (ex: une lib qui fait la génération de labyrinthe à ma place), NE PAS l'utiliser — la logique doit être écrite et comprise par moi
- Quand tu hésites entre deux approches, choisis celle qu'un développeur débutant comprendrait en relisant le code, pas celle qu'un expert trouverait élégante

## Règles de code obligatoires (imposées par le sujet)

- Python 3.10+
- Respect strict de flake8
- Type hints sur tous les paramètres, retours, et variables si pertinent
- mypy doit passer sans erreur avec les flags : `--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`
- Docstrings PEP 257 (style Google) sur CHAQUE fonction et classe — pas seulement les principales
- Gestion d'erreurs systématique avec try/except, jamais de crash non géré
- Context managers pour tout fichier ouvert
- Aucun magic number — toutes les constantes nommées en haut du fichier concerné
- Une fonction = une seule responsabilité, ~25-30 lignes maximum par fonction
- Noms de variables et fonctions explicites et complets (pas de `x`, `tmp`, `val`, `i` sauf en boucle simple)

## Structure du projet à respecter

```
.
├── a_maze_ing.py          # Point d'entrée obligatoire (nom imposé)
├── config.txt             # Fichier de config par défaut
├── Makefile
├── README.md
├── .gitignore
├── mazegen-1.0.0-py3-none-any.whl   # Package buildé (ou .tar.gz)
├── pyproject.toml         # Pour le build du package
├── mazegen/                # Module réutilisable
│   ├── __init__.py
│   └── generator.py        # Classe MazeGenerator
├── src/                     # Logique du programme principal (séparée du module réutilisable)
│   ├── config_parser.py
│   ├── maze_model.py
│   ├── generation.py
│   ├── pattern_42.py
│   ├── solver.py
│   ├── output_writer.py
│   ├── renderer.py
│   └── menu.py
└── tests/                   # Tests non soumis mais utiles pour valider
```

Chaque fichier dans `src/` a une seule responsabilité claire (son nom l'indique). Ne mets jamais deux responsabilités différentes dans le même fichier.

## Exigences fonctionnelles du sujet (résumé — voir subject.pdf pour le détail complet)

1. **Configuration** : parser `config.txt` (KEY=VALUE, commentaires `#`), valider WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT. Gérer toute erreur proprement avec message clair.

2. **Génération** : labyrinthe aléatoire avec seed reproductible. Chaque cellule a 0 à 4 murs (N/E/S/O). Encodage hexadécimal : bit 0=Nord, bit 1=Est, bit 2=Sud, bit 3=Ouest (1=fermé). Murs cohérents entre cellules voisines. Pas de zone ouverte plus large que 2×2. Si PERFECT=True, un seul chemin entrée→sortie.

3. **Pattern "42"** : doit apparaître visuellement, formé de cellules entièrement fermées. Si la taille du labyrinthe ne le permet pas, afficher un message d'erreur console et continuer sans bloquer.

4. **Fichier de sortie** : grille hexadécimale ligne par ligne, puis ligne vide, puis coordonnées entrée, coordonnées sortie, chemin le plus court en lettres N/E/S/O. Toutes les lignes finissent par `\n`.

5. **Rendu visuel ASCII terminal** : afficher murs, entrée, sortie, chemin. Menu interactif : régénérer, afficher/cacher chemin, changer couleur des murs, quitter.

6. **Module réutilisable** : classe `MazeGenerator` dans un module standalone, packagé en `mazegen-*.whl` ou `.tar.gz`, installable par pip, avec documentation d'usage (instanciation, paramètres, accès à la structure et à la solution).

7. **Makefile** : règles `install`, `run`, `debug`, `clean`, `lint` (avec les flags exacts du sujet), `lint-strict` (optionnel).

8. **README.md** : première ligne en italique avec le format imposé, sections Description / Instructions / Resources (incluant usage de l'IA), structure du config file, algorithme choisi et justification, partie réutilisable, gestion d'équipe.

## Algorithme de génération recommandé

Utilise le **Recursive Backtracker** (DFS avec pile) pour la génération de base — c'est l'algorithme le plus simple à comprendre, à expliquer, et à déboguer parmi les options valides (Prim, Kruskal, Recursive Backtracker). Implémente-le de façon itérative avec une pile explicite plutôt que récursive, pour éviter tout risque de dépassement de pile sur de grands labyrinthes et pour que le flux d'exécution soit plus facile à suivre pas à pas.

## Méthode de travail attendue

1. **Avant de coder** : confirme que tu as lu `subject.pdf` en entier et liste les points du sujet qui nécessitent le plus d'attention (validation des contraintes, pattern 42, format de sortie exact).

2. **Construis dans cet ordre**, en testant chaque brique avant de passer à la suivante :
   config parser → modèle de données → génération → pattern 42 → validation → solveur BFS → écriture fichier → rendu ASCII → menu interactif → extraction du module réutilisable → packaging → README

3. **Après chaque module créé** : exécute `flake8` et `mypy` dessus immédiatement, ne laisse pas les erreurs s'accumuler.

4. **Écris des tests simples** (pytest) au fur et à mesure pour valider chaque brique, même si non soumis — ça sécurise les briques suivantes.

5. **À la fin** : relis l'intégralité du code et vérifie chaque exigence du sujet une par une (fais une checklist explicite des points du sujet et coche-les).

6. **Ne anticipe pas de fonctionnalités bonus** (multi-algorithmes, animation) tant que la partie obligatoire n'est pas 100% complète et testée.

## Ce que je veux que tu m'expliques en fin de tâche

À la fin de l'implémentation complète, fournis-moi un résumé qui m'explique, fichier par fichier :
- Ce que fait chaque module en 2-3 phrases
- Les choix techniques principaux et pourquoi (notamment le choix de l'algorithme)
- Les points du sujet qui nécessitent une attention particulière en soutenance (zones où un évaluateur posera probablement des questions)

Ce résumé doit me permettre de réviser le projet avant ma défense sans avoir à tout relire ligne par ligne.