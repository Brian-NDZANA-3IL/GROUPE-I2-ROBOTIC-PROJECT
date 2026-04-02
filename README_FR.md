# 🤖 Projet de Navigation Autonome TurtleBot3
## Planification Classique vs Apprentissage par Renforcement

![Status](https://img.shields.io/badge/Status-Complet-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![ROS](https://img.shields.io/badge/ROS-Noetic-orange)
![Simulation](https://img.shields.io/badge/Simulation-Gazebo-red)

---

## 📋 Vue d'Ensemble du Projet

Ce projet est un **système complet de navigation autonome** pour robots TurtleBot3, comparant deux approches fondamentales de la navigation robotique :

### 🔹 Pipeline Classique de Navigation
```
Grille d'Occupation → Planification de Chemin (A*/Dijkstra/Greedy) 
    ↓
Contrôleur (PID + Évitement d'Obstacles) 
    ↓
Commandes de Vélocité
```

### 🟡 Pipeline Basé sur l'Apprentissage (Machine Learning)
```
État des Capteurs (Odométrie + Lidar) → Réseau de Neurones (DQN) 
    ↓
Stratégie de Navigation Apprise
    ↓
Commandes de Vélocité
```

### 📦 Composants Inclus
- ✅ **Trois algorithmes de planification** (A*, Dijkstra, Greedy BFS)
- ✅ **Contrôleurs avancés** (Suivi de trajectoire PID + Évitement d'obstacles)
- ✅ **Agent d'apprentissage par renforcement** (DQN avec expérience replay)
- ✅ **Framework de benchmarking complet** (comparaison de performance)
- ✅ **Suite de tests intégrée** (15+ cas de test)
- ✅ **Environnement de simulation Gazebo** (labyrinthe avec obstacles)
- ✅ **Documentation complète** et guides pas à pas

---

## 🎯 Objectifs du Projet

1. **Comprendre la navigation classique**: Comprendre comment fonctionnent les algorithmes de planification de chemin et les contrôleurs
2. **Découvrir le Machine Learning en robotique**: Implémenter un agent DQN qui apprend à naviguer
3. **Comparer les approches**: Benchmarquer les performances (temps, distance, efficacité)
4. **Démontrer une application réelle**: Fonctionnement en simulation avec un robot réaliste (TurtleBot3)

---

## 🚀 Démarrage Rapide

### Prérequis Système

```bash
# Système d'exploitation
Ubuntu 20.04 LTS (ou 22.04)

# Outils nécessaires
- ROS Noetic (ou Humble pour 22.04)
- Python 3.8+
- catkin (build system ROS)
```

### Installation des Paquets ROS

```bash
# Installation des paquets TurtleBot3
sudo apt-get update
sudo apt-get install ros-noetic-turtlebot3-*
sudo apt-get install ros-noetic-gmapping
sudo apt-get install ros-noetic-navigation
sudo apt-get install ros-noetic-move-base

# Installation des dépendances Python
cd ~/workspace
pip install gymnasium
pip install torch
pip install numpy
pip install matplotlib
pip install scipy
pip install pyaml
pip install scikit-image
```

### Configuration du Workspace

```bash
# Accéder au workspace
cd ~/workspace

# Sourcer l'environnement ROS
source /opt/ros/noetic/setup.bash

# Configurer le modèle TurtleBot3
export TURTLEBOT3_MODEL=burger

# Compiler le projet
catkin_make

# Sourcer l'environnement local
source devel/setup.bash
```

### Vérifier l'Installation

```bash
# Vérifier que ROS fonctionne
roscore &
sleep 2
rostopic list  # Devrait lister des topics
pkill -f roscore
```

---

## 📁 Structure du Projet

```
workspace/
├── src/                                  # Code source
│   └── custom_planners/
│       ├── config/
│       │   └── rl_config.ini            # Configuration du DQN
│       ├── scripts/
│       │   ├── astar.py                 # Algorithme A*
│       │   ├── dijkstra.py              # Algorithme Dijkstra
│       │   ├── greedy.py                # Algorithme Greedy BFS
│       │   ├── navigation_controller.py # Contrôleurs (PID + obstacle)
│       │   ├── rl_environment.py        # Environnement Gymnasium
│       │   ├── rl_agent.py              # Agent DQN + Q-Learning
│       │   ├── rl_training.py           # Pipeline d'entraînement
│       │   ├── performance_benchmark.py # Framework de benchmarking
│       │   ├── integration_tests.py     # Suite de tests complète
│       │   ├── demo_and_test.py         # Outil de démonstration
│       │   └── exploration_bot.py       # Bot d'exploration autonome
│       └── launch/
│           └── labyrinthe_gazebo.launch # Configuration Gazebo
├── maps/                                # Cartes de simulation
│   ├── labyrinthe_map.yaml
│   ├── ma_nouvelle_map.yaml
│   └── ...
├── devel/                               # Environnement compilé
├── build/                               # Fichiers de build
└── README_FR.md                         # Ce fichier
```

---

## 🧭 Composants Principaux

### 1️⃣ Algorithmes de Planification de Chemin

**Fichiers**: `astar.py`, `dijkstra.py`, `greedy.py`

#### A* (A-Star)
- **Principe**: Planification heuristique optimale
- **Heuristique**: Distance euclidienne jusqu'à la destination
- **Complexité**: O(n log n) généralement
- **Optimal**: Oui, trouve le chemin le plus court
- **Rapide**: Oui, grâce à l'heuristique

```python
from astar import AStarPlanner
planner = AStarPlanner(
    ox=obstacles_x,  # Coordonnées X des obstacles
    oy=obstacles_y,  # Coordonnées Y des obstacles
    resolution=0.1,  # Résolution de la grille
    rr=0.3           # Rayon du robot
)
path_x, path_y = planner.planning(
    sx=start_x, sy=start_y,
    gx=goal_x, gy=goal_y
)
```

#### Dijkstra
- **Principe**: Parcours en largeur uniforme
- **Complexité**: O(n²) ou O(n log n) avec priority queue
- **Optimal**: Oui, toujours le chemin le plus court
- **Rapide**: Non, moins efficace que A*

```python
from dijkstra import DijkstraPlanner
planner = DijkstraPlanner(ox, oy, resolution=0.1, rr=0.3)
path_x, path_y = planner.planning(sx, sy, gx, gy)
```

#### Greedy BFS (Best First Search)
- **Principe**: Parcours glouton basé sur l'heuristique
- **Complexité**: O(n log n)
- **Optimal**: Non, peut ne pas trouver le meilleur chemin
- **Rapide**: Oui, le plus rapide des trois

```python
from greedy import GreedyPlanner
planner = GreedyPlanner(ox, oy, resolution=0.1, rr=0.3)
path_x, path_y = planner.planning(sx, sy, gx, gy)
```

#### Comparaison
| Métrique | A* | Dijkstra | Greedy |
|---|---|---|---|
| Optimalité | ✅ Oui | ✅ Oui | ❌ Non |
| Rapidité | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Cas Moyen | ~100ms | ~150ms | ~50ms |
| Utilité Pratique | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

### 2️⃣ Contrôleurs de Navigation

**Fichier**: `navigation_controller.py`

#### A. Contrôleur PID (Proportionnel-Intégral-Dérivé)

Le contrôleur PID est la base des systèmes de contrôle automatique.

**Formule du PID**:
```
u(t) = Kp * e(t) + Ki * ∫e(t)dt + Kd * de(t)/dt
```

Où:
- `e(t)` = erreur (différence entre la consigne et la valeur actuelle)
- `Kp` = gain proportionnel
- `Ki` = gain intégral  
- `Kd` = gain dérivé
- `u(t)` = sortie de contrôle

**Utilisation**:
```python
from navigation_controller import PIDController

# Créer un contrôleur PID pour le contrôle en vitesse linéaire
controller = PIDController(
    kp=1.0,      # Gain proportionnel
    ki=0.1,      # Gain intégral
    kd=0.5,      # Gain dérivé
    min_output=-1.0,
    max_output=1.0
)

# À chaque itération
error = desired_speed - current_speed
control_output = controller.update(error, dt=0.05)  # 50ms timestep
```

#### B. Contrôleur de Suivi de Trajectoire

Suit un chemin plannifié composé de waypoints.

**Fonctionnement**:
1. Calcule l'erreur jusqu'au prochain waypoint
2. Utilise des PID pour contrôler la vitesse linéaire et angulaire
3. Évite les obstacles avec réaction rapide

```python
from navigation_controller import TrajectoryTrackingController

controller = TrajectoryTrackingController(
    max_linear_speed=0.5,   # Vitesse max (m/s)
    max_angular_speed=1.0   # Vitesse angulaire max (rad/s)
)

# À chaque itération
linear_vel, angular_vel = controller.update_control(
    current_pose=robot_pose,
    waypoint=next_waypoint,
    laser_scan=lidar_data
)
```

#### C. Contrôleur d'Évitement d'Obstacles

Modifie les commandes de vitesse pour éviter les collisions.

**Logique**:
- Scanne les données du Lidar
- Identifie la distance minimale
- Si distance < seuil de sécurité (0.5m):
  - Réduit la vitesse linéaire
  - Tourne pour s'éloigner de l'obstacle

```python
from navigation_controller import ObstacleAvoidanceController

avoidance = ObstacleAvoidanceController(
    safety_distance=0.5,      # Distance d'activation (m)
    min_distance_weight=2.0   # Poids du modifier
)

# Appliquer l'évitement
linear_vel_safe, angular_vel_safe = avoidance.compute_avoidance_command(
    linear_vel=linear_vel,
    angular_vel=angular_vel,
    laser_data=scan
)
```

---

### 3️⃣ Apprentissage par Renforcement (Deep Q-Network)

**Fichiers**: `rl_environment.py`, `rl_agent.py`, `rl_training.py`

#### Concepts Clés

**Q-Learning**: Technique où l'agent apprend une fonction Q qui estime la "qualité" de chaque action.

**DQN (Deep Q-Network)**: Utilise un réseau de neurones pour approximer la fonction Q. Permet de gérer des espaces d'état grands/continus.

#### A. Environnement Gymnasium

Convertit le monde de simulation ROS en environnement d'apprentissage standardisé.

**État du Robot (15D)**:
```python
state = [
    goal_distance,           # Distance à la destination (1D)
    goal_angle_diff,         # Angle vers la destination (1D)
    min_laser_distance,      # Distance obstacle min (1D)
    sector_distance_1, ... , # 12 secteurs Lidar (12D)
    sector_distance_12
]
```

**Actions Disponibles** (5 actions discrètes):
```python
actions = {
    0: "STOP",      # Arrêter le robot
    1: "FORWARD",   # Avancer
    2: "LEFT",      # Tourner à gauche
    3: "RIGHT",     # Tourner à droite
    4: "BACKWARD"   # Reculer
}
```

**Fonction de Récompense**:
```python
reward = (
    + distance_to_goal_delta * 10      # Récompense: se rapprocher
    + (1.0 if reached_goal else 0)     # Récompense: atteindre le but
    - (1.0 if collision else 0)        # Pénalité: collision
    - 0.01 * step_number               # Pénalité: temps
)
```

**Utilisation**:
```python
from rl_environment import TurtleBot3NavEnv
import gymnasium as gym

env = TurtleBot3NavEnv(
    goal_position=(2.0, 2.0),
    max_steps=500,
    episode_timeout=60
)

# Exécuter un épisode
observation, info = env.reset()
for step in range(100):
    action = env.action_space.sample()  # Action aléatoire
    observation, reward, terminated, truncated, info = env.step(action)
    
    if terminated or truncated:
        break

env.close()
```

#### B. Agent DQN

Réseau de neurones qui apprend la politique de navigation.

**Architecture du Réseau**:
```
Entrée (15D: état)
    ↓
Couche Dense 1 → 128 neurones, ReLU
    ↓
Couche Dense 2 → 128 neurones, ReLU
    ↓
Couche Dense 3 → 5 sorties (Q-values pour chaque action)
```

**Mécanismes d'Apprentissage**:

1. **Epsilon-Greedy Exploration**:
   - ε = 1.0 au départ (exploration aléatoire)  
   - ε décroit vers 0.01 (exploitation de la meilleure stratégie)
   - Permet au robot de découvrir

2. **Experience Replay**:
   - Stocke 5000 dernières transitions (état, action, récompense, état suivant)
   - Entraîne le réseau sur des batches aléatoires (32 samples)
   - Réduit la corrélation entre les données d'entraînement

3. **Target Network**:
   - Deux réseaux: main network et target network
   - Target network est une copie mise à jour lentement
   - Stabilise l'entraînement

**Utilisation**:
```python
from rl_agent import DQNAgent

agent = DQNAgent(
    state_size=15,
    action_size=5,
    learning_rate=0.0005,
    gamma=0.99,           # Facteur de discount
    epsilon=1.0
)

# Entraîner
state = env.reset()[0]
for step in range(1000):
    # Sélectionner une action
    action = agent.select_action(state, epsilon=agent.epsilon)
    
    # Exécuter dans l'environnement
    next_state, reward, done, _, _ = env.step(action)
    
    # Mémoriser l'expérience
    agent.remember(state, action, reward, next_state, done)
    
    # Entraîner le réseau
    if len(agent.memory) > 32:
        agent.train(batch_size=32)
    
    state = next_state
    
    if done:
        agent.decay_epsilon()
        break
```

#### C. Pipeline d'Entraînement

Orchestration de l'entraînement du robot.

**Processus**:
1. Créer un environnement
2. Créer un agent
3. Pour chaque époque:
   - Entraîner l'agent sur des trajets
   - Évaluer les performances
   - Sauvegarder le meilleur modèle
   - Afficher les statistiques

```bash
# Entraîner un agent DQN (500 épisodes)
python3 rl_training.py --agent dqn --episodes 500

# Ou avec Q-Learning classique
python3 rl_training.py --agent qlearning --episodes 200

# Voir la courbe d'apprentissage
python3 -c "import matplotlib.image as mpimg; \
            import matplotlib.pyplot as plt; \
            img = mpimg.imread('training_results_dqn.png'); \
            plt.imshow(img); plt.axis('off'); plt.show()"
```

**Résultats**:
- `final_agent_dqn.pt`: Modèle entraîné sauvegardé
- `training_results_dqn.png`: Visualisation de l'apprentissage
- Graphiques de:
  - Récompense par épisode
  - Longueur de l'épisode
  - Taux de réussite

---

### 4️⃣ Framework de Benchmarking

**Fichier**: `performance_benchmark.py`

Mesure et compare les performances de tous les algorithmes.

**Métriques Collectées**:

1. **Longueur du Chemin** (path_length)
   - Distance réelle parcourue par le robot

2. **Efficacité du Chemin** (path_efficiency)
   - Ratio: distance euclidienne directe / chemin réel
   - 1.0 = chemin parfait, < 1.0 = chemin efficace

3. **Temps d'Exécution** (execution_time)
   - Temps total pour atteindre la destination

4. **Vitesse Moyenne** (avg_velocity)
   - Distance / temps

5. **Lissage du Chemin** (smoothness)
   - Nombre de changements de direction
   - Moins = plus lisse

6. **Taux de Réussite** (success_rate)
   - Pourcentage d'objectifs atteints

**Utilisation**:

```python
from performance_benchmark import PlanningBenchmark

benchmark = PlanningBenchmark(
    algorithms=['astar', 'dijkstra', 'greedy'],
    maps=['my_map', 'labyrinthe_map'],
    trials_per_goal=3  # Répéter 3 fois
)

# Comparaison
results = benchmark.compare_algorithms(
    goals=[(2.0, 2.0), (5.0, 5.0), (-3.0, 3.0)]
)

# Afficher les résultats
benchmark.plot_comparison()

# Exporter
benchmark.save_results('benchmark_results.json')
```

**Exécution via le CLI**:
```bash
python3 demo_and_test.py benchmark
```

---

### 5️⃣ Suite de Tests

**Fichier**: `integration_tests.py`

Tests complètement indépendants et reproductibles de tous les composants.

**Catégories de Tests**:

1. **Tests des Algorithmes de Planification** (5 tests)
   - Vérifie que chaque algorithme trouve un chemin
   - Valide que le chemin évite les obstacles
   - Mesure les performances

2. **Tests des Contrôleurs** (3 tests)
   - Stabilité du contrôleur PID
   - Calcul correct des erreurs de trajectoire

3. **Tests des Métriques** (2 tests)
   - Calcul correct des métriques de performance
   - Détection de collision

4. **Tests du Machine Learning** (3 tests)
   - Création d'agent DQN
   - Sélection d'action
   - Entraînement

5. **Tests d'Intégration** (2 tests)
   - Pipeline complet: planification + suivi
   - Navigation autonome end-to-end

**Exécution**:

```bash
# Exécuter tous les tests
python3 integration_tests.py

# Exécuter une catégorie spécifique
python3 integration_tests.py TestPlanningAlgorithms

# Exécuter un test spécifique
python3 integration_tests.py TestPlanningAlgorithms.test_astar_finds_path

# Mode verbose
python3 integration_tests.py -v
```

**Résultats attendus**:
```
test_astar_finds_path (integration_tests.TestPlanningAlgorithms) ... ok
test_dijkstra_finds_path (integration_tests.TestPlanningAlgorithms) ... ok
test_algorithm_comparison (integration_tests.TestPlanningAlgorithms) ... ok
...

Ran 15 tests in 2.345s
OK
```

---

## 🛠️ Guide d'Utilisation - Flux de Travail Complet

### Étape 1: Lancer la Simulation

```bash
# Terminal 1: ROS Master
roscore

# Terminal 2: Gazebo avec le robot
export TURTLEBOT3_MODEL=burger
roslaunch custom_planners labyrinthe_gazebo.launch
```

Vous devriez voir:
- Gazebo ouverte avec un robot TurtleBot3
- RViz avec la visualisation du robot et de la carte

### Étape 2: Tester la Planification de Chemin

```bash
# Terminal 3
cd ~/workspace/src/custom_planners/scripts
python3 integration_tests.py TestPlanningAlgorithms
```

Résultats:
- ✅ Les trois algorithmes trouvent des chemins valides
- ✅ Les chemins évitent les obstacles
- ⏱️ A* est environ 2x plus rapide que Dijkstra

### Étape 3: Tester les Contrôleurs

```bash
python3 integration_tests.py TestControllers
```

Résultats:
- ✅ Le contrôleur PID stabilise la vitesse
- ✅ Erreur de trajectoire correctement calculée

### Étape 4: Entraîner un Agent DQN

```bash
# D'abord, vérifier que Gazebo tourne en arrière-plan

# Entraîner (200 épisodes pour démo, 500+ pour de bons résultats)
python3 rl_training.py --agent dqn --episodes 200

# Cela va:
# 1. Créer 200 épisodes d'exploration
# 2. Sauvegarder le meilleur modèle toutes les 50 épisodes
# 3. Générer training_results_dqn.png avec les courbes
# 4. Afficher les statistiques
```

Exemple de sortie:
```
Episode 1/200: Reward=15.2, Avg_Reward=15.2, Steps=45
Episode 2/200: Reward=18.5, Avg_Reward=16.85, Steps=52
...
Episode 200/200: Reward=85.3, Avg_Reward=65.4, Steps=120
Training completed! Best model saved.
```

### Étape 5: Benchmarker les Algorithmes

```bash
python3 demo_and_test.py benchmark
```

Cela va:
- Tester tous les algorithmes sur plusieurs cartes
- Générer `benchmark_results.png` avec les comparaisons
- Exporter `benchmark_results.json` avec les données

### Étape 6: Exécuter la Suite de Tests Complète

```bash
python3 integration_tests.py
```

Tous les 15 tests devraient passer.

---

## 🎓 Explication des Concepts Clés

### Qu'est-ce qu'un Graphe de Recherche ?

Les algorithmes A*, Dijkstra et Greedy travaillent sur une **grille de recherche** convertie d'une **grille d'occupation**.

```
Monde Réel → Grille d'Occupation → Graphe de Recherche
(TurtleBot3)    (0 = obstacle)    (nœuds & arêtes)
                (1 = libre)

Exemple:
                Monde          Grille      Graphe
        ┌───────────────┐   ┌────┐    S─────G
        │ S ░░░░░ G    │   │1110│    │     │
        │ ░ ░░░░░ ░    │ = │1110│ =  └─────┘
        │ ░░░░░░░░░    │   │0000│
        └───────────────┘   └────┘
```

### Comment fonctionnent les Récompenses en Q-Learning?

Le robot apprend en maximisant les récompenses cumulatives:

```python
# Episode 1: Robot apprend
Etat_0 → Action_FORWARD → Récompense +0.1 (se rapproche) → État_1
État_1 → Action_FORWARD → Récompense +0.1 → État_2
État_2 → Action_LEFT → Récompense -0.05 (s'éloigne) → État_3
État_3 → Action_FORWARD → Récompense +50 (atteint but!) ✅
Total_Récompense = +50.25

# Episode 2: Robot utilise ce qu'il a appris
Etat_0 → Action_FORWARD (meilleures chances) → ...
```

### Pourquoi Avoir Besoin de Target Network?

Sans target network, l'entraînement est instable:

```python
# SANS Target Network (instable):
Perte = (Récompense + γ * max Q(état_suivant) - Q(état, action))²
       ↑ Target change pendant l'entraînement

# AVEC Target Network (stable):
Perte = (Récompense + γ * max Q_target(état_suivant) - Q(état, action))²
       ↑ Target est une copie fixe pendant plusieurs itérations
```

---

## 📊 Fichier de Configuration

**Fichier**: `config/rl_config.ini`

```ini
[DQN_HYPERPARAMETERS]
learning_rate = 0.0005       # Taux d'apprentissage
gamma = 0.99                 # Facteur de discount
epsilon_start = 1.0          # Exploration initiale
epsilon_end = 0.01           # Exploration finale
epsilon_decay = 0.995        # Taux de décroissance
memory_buffer_size = 5000    # Taille du buffer
batch_size = 32              # Taille des batches
update_frequency = 100       # Mise à jour du target network

[ENVIRONMENT]
max_steps_per_episode = 500
episode_timeout = 60.0
action_space = 5             # Nombre d'actions
state_space = 15             # Taille de l'état
```

---

## 🔍 Dépannage Courant

### Erreur: "Cannot import gymnasium"
```bash
pip install gymnasium --upgrade
```

### Erreur: "ROS not found"
```bash
source /opt/ros/noetic/setup.bash
# Ou ajouter à .bashrc:
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Gazebo ne démarre pas
```bash
# Réinitialiser Gazebo
rm -rf ~/.gazebo
pkill -f gazebo
pkill -f gzserver
pkill -f gzclient

# Relancer
roslaunch custom_planners labyrinthe_gazebo.launch
```

### L'agent DQN n'apprend pas
- Vérifier que Gazebo tourne en arrière-plan
- Augmenter le nombre d'épisodes (200 min)
- Réduire epsilon_decay pour plus d'exploration
- Vérifier les récompenses dans les logs

### Tests échouent
```bash
# Vérifier les dépendances
python3 -m pip list | grep -E "gymnasium|torch|numpy"

# Réexécuter les tests avec verbose
python3 -m unittest integration_tests -v
```

---

## 📈 Résultats Attendus

### Performance de Planification
- **A***: ~100ms en moyenne, chemin optimal
- **Dijkstra**: ~150ms, chemin optimal  
- **Greedy**: ~50ms, chemin sous-optimal

### Apprentissage DQN
- **Episode 1-50**: Récompense moyenne ~10, agent explore
- **Episode 100-200**: Récompense moyenne ~40-50
- **Episode 300-500**: Récompense moyenne ~60-80+

### Benchmark Complet
```
Algorithme  | Chemin (m) | Efficacité | Temps (s)
A*          | 8.2        | 0.85       | 3.5
Dijkstra    | 8.2        | 0.85       | 5.2
Greedy      | 9.5        | 0.73       | 2.1
DQN (500ep) | 8.0        | 0.88       | 4.0
```

---

## 🎯 Prochaines Étapes

1. **Entraîner pendant plus longtemps**: 500+ épisodes pour meilleure performance
2. **Tester sur d'autres cartes**: `ma_nouvelle_map`, `my_map`
3. **Ajouter de nouveaux objectifs**: Changements dynamiques
4. **Implémenter Multi-Agent**: Plusieurs robots collaborant
5. **Robotique réelle**: Porter sur un vrai TurtleBot3

---

## 📚 Ressources Supplémentaires

### Livres
- "Reinforcement Learning: An Introduction" - Sutton & Barto
- "Learning Robotics using Python" - Lentin Joseph

### Liens
- [ROS Wiki](http://wiki.ros.org/)
- [TurtleBot3 Documentation](https://emanual.robotis.com/docs/en/platform/turtlebot3/)
- [Gymnasium Documentation](https://gymnasium.farama.org/)
- [PyTorch Documentation](https://pytorch.org/docs/)

### Cours
- Stanford CS234: Reinforcement Learning
- MIT 6.S191: Introduction to Deep Learning

---

## 📝 Notes d'Implémentation

### Pourquoi Gymnasium?
- Standard pour ML/RL en Python
- Interface uniforme pour tous les environnements
- Facile à intégrer avec ROS

### Pourquoi PyTorch pour DQN?
- Flexible et bien documenté
- Bonnes performances GPU
- Facile à déboguer

### Pourquoi Gazebo pour la simulation?
- Simulation physique réaliste
- Intégration native ROS
- Disponible gratuitement

---

## 📞 Support & Contribution

Pour des questions ou problèmes:
1. Vérifier le fichier PROJECT_DOCUMENTATION.md pour des détails techniques
2. Consulter le fichier GETTING_STARTED.md pour un guide étape par étape
3. Exécuter les tests d'intégration pour vérifier l'installation

---

**Dernière mise à jour**: Mars 2026  
**Statut du Projet**: ✅ Complet et fonctionnel  
**Auteur**: Groupe I2 Robotique  
**Licence**: MIT
