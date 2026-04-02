# 📖 GETTING STARTED - Step by Step Guide

## Pour les Étudiants: Comment Comprendre et Présenter Ce Projet

### Table des Matières
1. [Jour 1: Comprendre la structure](#jour-1-comprendre-la-structure)
2. [Jour 2: Tester les algorithmes de planning](#jour-2-tester-les-algorithmes-de-planning)
3. [Jour 3: Explorer la navigation et le contrôle](#jour-3-explorer-la-navigation-et-le-contrôle)
4. [Jour 4: Reinforcement Learning](#jour-4-reinforcement-learning)
5. [Jour 5: Benchmarking et comparaison](#jour-5-benchmarking-et-comparaison)
6. [Jour 6: Préparer la présentation](#jour-6-préparer-la-présentation)

---

## Jour 1: Comprendre la Structure

### Objectif
Avoir une vue d'ensemble du projet et se familiariser avec l'organisation des fichiers.

### Tâches

**1. Lire la vue d'ensemble (15 min)**
```bash
cd ~/workspace
cat README_COMPLETE.md          # Vue d'ensemble
cat PROJECT_DOCUMENTATION.md    # Guide complet
```

**2. Voir la structure du projet (5 min)**
```bash
cd ~/workspace/src/custom_planners/scripts
python3 demo_and_test.py structure
```

**3. Comprendre l'architecture (20 min)**
Ouvrir `PROJECT_DOCUMENTATION.md` et lire la section "Architecture":
- Qu'est-ce que la navigation classique?
- Qu'est-ce que la navigation par RL?
- Comment les deux approches se connectent?

**4. Inspecter les fichiers clés (15 min)**
```bash
# Voir les en-têtes et premiers commentaires
head -20 astar.py              # Comprendre la structure d'un planner
head -30 rl_agent.py           # Comprendre l'agent RL
head -20 navigation_controller.py  # Comprendre le contrôleur
```

### 📸 Screenshots à Prendre
- Terminal montrant la structure du projet
- L'architecture du système (à partir de PROJECT_DOCUMENTATION.md)

### ✅ Checklist Jour 1
- [ ] Lu README_COMPLETE.md
- [ ] Lu PROJECT_DOCUMENTATION.md (sections 1-2)
- [ ] Compris la structure du projet
- [ ] Identifié les 5 composants principaux
- [ ] Répondu à "Quelle est la différence entre A* et Dijkstra?"

---

## Jour 2: Tester les Algorithmes de Planning

### Objectif
Tester et comprendre les trois algorithmes de planification de chemin.

### Tâches

**1. Préparation de l'environnement (5 min)**
```bash
cd ~/workspace
source devel/setup.bash
export TURTLEBOT3_MODEL=burger
```

**2. Lancer ROS et Gazebo (10 min)**
```bash
# Terminal 1
roscore

# Terminal 2
roslaunch custom_planners labyrinthe_gazebo.launch
```
Attendre que Gazebo se charge avec le robot et les obstacles.

**3. Tester les algorithmes (10 min)**
```bash
# Terminal 3
cd src/custom_planners/scripts
python3 integration_tests.py TestPlanningAlgorithms
```

**4. Comprendre les résultats (20 min)**
- Qu'est-ce que "path efficiency"?
- Quel algorithme est le plus rapide?
- Quel algorithme donne le plus court chemin?

**5. Analyser le code (15 min)**
```bash
# Lire et comprendre A*
less astar.py

# Points clés à identifier:
# - La fonction heuristique
# - Comment les voisins sont générés
# - Comment le chemin est reconstruit
```

### 📸 Screenshots à Prendre
1. Terminal affichant les résultats des tests (3 algorithmes)
2. RViz montrant un chemin planifié
3. Comparaison des 3 chemins (vous pouvez exécuter 3 fois chacun)

### 💡 Questions à Répondre
1. Pourquoi A* est plus rapide que Dijkstra?
2. Pourquoi Greedy est plus rapide que A* mais potentiellement moins bon?
3. Si vous aviez besoin du chemin le plus court, quel algorithme choisiriez-vous?

### ✅ Checklist Jour 2
- [ ] ROS et Gazebo d'accord
- [ ] Tests de planning exécutés avec succès
- [ ] Comprendre le résultat de chaque algorithme
- [ ] Réponses aux 3 questions ci-dessus

---

## Jour 3: Explorer la Navigation et le Contrôle

### Objectif
Comprendre comment le robot suit le chemin planifié et évite les obstacles.

### Tâches

**1. Lire sur le contrôle (10 min)**
```bash
cd ~/workspace
grep -A 30 "class PIDController" src/custom_planners/scripts/navigation_controller.py
```

**2. Tester le contrôleur (10 min)**
```bash
# Terminal 3 (scripts)
python3 integration_tests.py TestControllers
```

**3. Explorer la SLAM (20 min)**

*Lire le guide:*
```bash
cat PROJECT_DOCUMENTATION.md | grep -A 30 "Test 2: SLAM Mapping"
```

*Tester SLAM:*
```bash
# Terminal 3
roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=gmapping

# Terminal 4 (nouveau)
python3 exploration_bot.py
```

Laissez le robot explorer automatiquement pendant 2-3 minutes.

**4. Sauvegarder la carte (5 min)**
```bash
rosrun map_server map_saver -f ~/workspace/maps/test_generated_map
```

**5. Analyser les performances (15 min)**
```bash
# Lire le code du contrôleur
less navigation_controller.py

# Questions:
# - Comment le PID corrige l'erreur de trajectoire?
# - Comment l'évitement d'obstacles modifie-t-il la vitesse?
# - Quelle est la fréquence de contrôle (Hz)?
```

### 📸 Screenshots à Prendre
1. RViz montrant le processus de SLAM
2. Carte générée par gmapping
3. Terminal montrant les résultats des tests de contrôleur
4. Terminal montrant la progression de l'exploration

### 💡 Questions à Répondre
1. Qu'est-ce que le "cross-track error"?
2. Comment un contrôleur PID ajuste-t-il la vitesse angulaire?
3. Pourquoi est-ce important d'avoir une bonne détection d'obstacles?

### ✅ Checklist Jour 3
- [ ] Tests de contrôleur exécutés
- [ ] SLAM mapping testé
- [ ] Carte générée et sauvegardée
- [ ] Code du contrôleur compris
- [ ] Réponses aux 3 questions

---

## Jour 4: Reinforcement Learning

### Objectif
Entraîner un agent DQN et comprendre comment il apprend la navigation.

### Tâches

**1. Lire sur le RL (15 min)**
```bash
cat PROJECT_DOCUMENTATION.md | grep -A 50 "Component Guide" | grep -A 40 "3. Reinforcement Learning"
```

**2. Comprendre l'environnement RL (10 min)**
```bash
# Lire les 50 premières lignes de rl_environment.py
head -50 src/custom_planners/scripts/rl_environment.py

# Questions:
# - Qu'est-ce que l'état (state space)?
# - Qu'est-ce que les actions?
# - Comment la récompense est-elle calculée?
```

**3. Entraîner un agent (15 min)**

Toujours dans le même terminal Gazebo/ROS:
```bash
# Terminal 3
cd ~/workspace/src/custom_planners/scripts
python3 rl_training.py --agent dqn --episodes 30
```

Cela prendra environ 3-5 minutes.

**4. Analyser les résultats (10 min)**
```bash
# Voir les graphiques
ls -la training_results_dqn.png

# Ouvrir avec un lecteur d'images
eog training_results_dqn.png  # ou 'feh' ou 'display'

# Questions:
# - Comment la récompense évolue-t-elle?
# - Quel est le taux de succès final?
# - À quels points le taux de convergence ralentit-il?
```

**5. Comprendre le réseau de neurones (10 min)**
```bash
# Lire la structure du réseau
less rl_agent.py
# Chercher: "class DQNNetwork"

# Questions:
# - Combien de couches cachées?
# - Quelle est la taille d'entrée/sortie?
# - Quel est la fonction d'activation?
```

**6. Entraîner avec plus d'épisodes (optionnel) (20 min)**
```bash
# Pour de meilleurs résultats (sur un ordinateur puissant):
python3 rl_training.py --agent dqn --episodes 100
```

### 📸 Screenshots à Prendre
1. Terminal montrant l'entraînement en cours
2. Graphiques final training_results_dqn.png (4 sous-plots)
3. Sortie finale montrant le résumé de l'entraînement

### 💡 Questions à Répondre
1. Quelle est la différence entre un réseau Q et un réseau cible (target)?
2. Pourquoi utilise-t-on "experience replay"?
3. Comment l'exploration (epsilon) change-t-elle pendant l'entraînement?
4. Quel est le taux d'epsilon decay?

### ✅ Checklist Jour 4
- [ ] Compris l'environnement RL
- [ ] Entraîné un agent visant 30 épisodes
- [ ] Analysé les graphiques de convergence
- [ ] Compris l'architecture du réseau
- [ ] Réponses aux 4 questions

---

## Jour 5: Benchmarking et Comparaison

### Objectif
Comparer les performance de tous les algorithmes et paradigmes.

### Tâches

**1. Configurer le benchmark (5 min)**
Lire le fichier de configuration:
```bash
less src/custom_planners/config/rl_config.ini
```

**2. Exécuter les benchmarks (15 min)**
```bash
# Terminal 3
python3 performance_benchmark.py --algorithms astar,dijkstra,greedy --trials 2
```

Cela prendra environ 10-15 minutes selon votre ordinateur.

**3. Analyser les résultats (15 min)**
```bash
# Voir les résultats
cat benchmark_results.json | python3 -m json.tool

# Ouvrir les graphiques
eog benchmark_results.png  # ou autre lecteur d'images
```

**4. Créer un tableau de comparaison (15 min)**

Créer un fichier `comparison_table.md`:
```bash
cat > ~/workspace/COMPARISON_RESULTS.md << 'EOF'
# Comparaison des Algorithmes

## Résultats de Performance

| Métrique | A* | Dijkstra | Greedy | DQN |
|----------|-----|----------|--------|------|
| Efficacité du chemin (%) | XX | XX | XX | XX |
| Temps d'exécution (ms) | XX | XX | XX | XX |
| Taux de succès (%) | XX | XX | XX | XX |
| Collisions | XX | XX | XX | XX |

_Remplir avec vos résultats_
EOF
```

**5. Analyse comparative (20 min)**

Répondre à ces questions:
1. Quel algorithme est le plus rapide en termes de temps d'exécution?
2. Quel algorithme donne le chemin le plus court?
3. Quels sont les compromis (trade-offs) entre les algorithmes?
4. Comment le RL se compare-t-il aux méthodes classiques?

### 📸 Screenshots à Prendre
1. Terminal montrant le benchmark en cours
2. benchmark_results.png (graphiques de comparaison)
3. Terminal montrant les statistiques finales
4. Votre tableau de comparaison

### ✅ Checklist Jour 5
- [ ] Benchmarks exécutés
- [ ] Résultats analysés
- [ ] Tableau de comparaison rempli
- [ ] Réponses aux 5 questions ci-dessus

---

## Jour 6: Préparer la Présentation

### Objectif
Préparer tous les matériaux pour la présentation de 20 minutes.

### Tâches

**1. Utiliser le checklist de préparation (5 min)**
```bash
cd ~/workspace/src/custom_planners/scripts
python3 demo_and_test.py prepare
```

**2. Rassembler les screenshots (20 min)**

Créer un dossier pour les images:
```bash
mkdir -p ~/workspace/presentation_images
```

Copier tous les screenshots pris:
```bash
cp *.png ~/workspace/presentation_images/
cp benchmark_results.json ~/workspace/presentation_images/
```

**3. Créer les slides (45 min)**

Voici la structure recommandée pour PowerPoint/Google Slides:

```
SLIDE 1: Titre
- Robot Navigation: Classical Planning vs Reinforcement Learning
- Noms, Date, Université

SLIDE 2: Problème et Objectifs
- Point 1: Implémenter deux approches de navigation
- Point 2: Comparer leurs performances
- Point 3: Analyser les compromis

SLIDE 3: Architecture Système
- Diagramme (image du PROJECT_DOCUMENTATION.md)
- 2 voies: Classique et RL

SLIDE 4-5: Algorithmes de Planning
- A* (avec pseudocode simplifié)
- Dijkstra
- Greedy Best-First
- Comparaison

SLIDE 6: Contrôleur PID
- Équation du PID
- Comment ça marche
- Photo RViz

SLIDE 7: Évitement d'Obstacles
- Détection laser
- Champs de potentiel
- Modulation de vitesse

SLIDE 8: Environnement RL
- État (15D)
- Actions (5)
- Récompense

SLIDE 9: Architecture DQN
- Diagramme du réseau
- Experience replay
- Target network

SLIDE 10: Résultats d'Entraînement
- Graphiques de convergence
- Taux de succès
- Récompense par épisode

SLIDE 11: Benchmarking
- benchmark_results.png
- Tableau de comparaison

SLIDE 12: Analyse
- Points forts de chaque approche
- Compromis
- Recommandations

SLIDE 13: Conclusion
- Résumé des apprentissages
- Points clés
- Les questions?
```

**4. Tester la démonstration live (30 min)**

```bash
# Tester que tout fonctionne:
# Terminal 1: roscore
# Terminal 2: roslaunch custom_planners labyrinthe_gazebo.launch
# Terminal 3: roslaunch custom_planners rviz.launch
# Terminal 4: python3 integration_tests.py TestPlanningAlgorithms
```

**5. Préparer les notes de présentation (30 min)**

Créer un fichier `presentation_notes.md`:
```bash
cat > ~/workspace/PRESENTATION_NOTES.md << 'EOF'
# Notes de Présentation (20 minutes)

## 0:00-2:00 Aperçu du Système
"Bonjour, aujourd'hui nous présentons un système complet de navigation autonome..."
[Points clés]

## 2:00-4:00 Environnement de Simulation
"Nous avons créé un environnement réaliste dans Gazebo..."
[Montrer RViz]

## 4:00-7:00 Algorithmes de Planning
"Nous avons implémenté trois algorithmes différents..."
[Montrer résultats des tests]

[Continuer pour chaque section...]
EOF
```

**6. Groupe entier: Accord sur qui présente quoi (20 min)**

Suggéré:
- **Étudiant 1**: Aperçu + Algorithmes de Planning
- **Étudiant 2**: Contrôle + Navigation
- **Étudiant 3**: RL + Benchmarking + Conclusions

Mais chacun doit pouvoir expliquer toute partie si demandé!

### 📸 Screenshots Spéciaux pour Slides
1. Architecture du système
2. Graphiques de benchmark
3. Courbes de convergence RL
4. RViz montrant un chemin planifié
5. Comparaison visuelle des trois algorithmes

### ✅ Checklist Jour 6
- [ ] Checklist de préparation consulté
- [ ] Screenshots rassemblés
- [ ] Slides créées (13+ slides)
- [ ] Démonstration live testée
- [ ] Notes de présentation écrites
- [ ] Distribution des rôles de présentation
- [ ] Timing vérifié (< 20 minutes)
- [ ] Questions potentielles préparées

---

## 🎓 FAQ - Ce Que Vous Devez Être Capable d'Expliquer

### Algorithmes de Planning
**Q: Quelle est la différence entre A* et Dijkstra?**
A: A* utilise une heuristique pour guider la recherche, Dijkstra explore uniformément.

**Q: Pourquoi Greedy est plus rapide?**
A: Il utilise seulement l'heuristique, pas le coût réel (glouton).

**Q: A* est-il toujours optimal?**
A: Oui, si l'heuristique est admissible (ne surestime jamais).

### Navigation et Contrôle
**Q: Comment fonctionne un contrôleur PID?**
A: Trois termes: P (proportionnel), I (intégral), D (dérivée).

**Q: Qu'est-ce que l'évitement d'obstacles?**
A: Réduire la vitesse en cas d'obstacles détectés par le lidar.

**Q: Qu'est-ce que le "cross-track error"?**
A: La distance perpendiculaire entre le robot et le chemin désiré.

### Reinforcement Learning
**Q: Comment marche le DQN?**
A: Le réseau apprend Q-values par expérience répétée et mise à jour.

**Q: Pourquoi exp replay est important?**
A: Décorréler les données d'entraînement pour une convergence meilleure.

**Q: Comment la récompense est définie?**
A: distance_progress - collision_penalty + goal_bonus - step_cost

### Comparaison
**Q: Quand utiliser classique vs RL?**
A: Classique = rapide, déterministe. RL = adaptatif, apprend.

**Q: Y a-t-il une meilleure approche?**
A: Dépend du contexte. Idéalement, hybride.

---

## 📋 Final Checklist Avant La Présentation

**La Semaine Avant:**
- [ ] Slides finalisées et testées
- [ ] Démonstration live testée 3x
- [ ] Notes d'orateur préparées
- [ ] Rôles de présentation clairs

**Le Jour Même:**
- [ ] Arriver 15 min en avance
- [ ] Tester vidéoprojecteur + système de son
- [ ] Lancer ROS et Gazebo
- [ ] Avoir RViz ouvert et prêt
- [ ] Vérifier la connexion du wifi/réseau
- [ ] Avoir un backup des slides sur clé USB
- [ ] Mettre les téléphones en silence

**Pendant la Présentation:**
- [ ] Parler clair et assez fort
- [ ] Regarder le public, pas les slides
- [ ] Laisser du temps pour les questions
- [ ] Préparer à expliquer chaque algorithme
- [ ] Montrer les résultats réels (ne pas inventer)

---

## 🚀 Prêt pour Présenter!

Vous avez maintenant:
✅ Compris la théorie (A*, Dijkstra, DQN)
✅ Testé le code et les algorithmes
✅ Comparé les performances
✅ Préparé une présentation
✅ Rassemblé les preuves

**Time to shine! Bonne chance à votre présentation! 🎤**

---

**Version:** 1.0  
**Dernière mise à jour:** 31 mars 2026
