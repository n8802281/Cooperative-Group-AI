# Cooperative Group AI Project
A tactical multi-agent simulation game using K-Means clustering and Cooperative A* pathfinding.

---

## 🧩 Overview

**Cooperative Group AI Project** is a prototype simulation game built with Python and Pygame that demonstrates multi-agent coordination for real-time strategic pursuit. The player (a green block) must avoid being caught by AI agents dynamically assigned one of three roles: **Chaser**, **Blocker**, or **Helper**.

Roles are reassigned at fixed intervals or when an agent respawns, using **K-Means clustering** based on agent spatial distribution. Agents use **Cooperative A\*** for pathfinding to avoid collisions and coordinate effectively.

This project emphasizes tactical role switching, path planning under terrain cost constraints, and emergent AI behavior—without any learning model.

---

## 🎯 Game Goal

The player's objective is to achieve the highest possible score.

- You earn points by surviving each turn.
- Use the **Spacebar** skill to eliminate nearby AI agents and gain bonus points.
- If you are caught by an AI, your score will be reduced.

Strategic movement, skillful terrain usage, and well-timed eliminations are key to maximizing your score.

---

## 🎮 Controls

| Key             | Action                                           |
|-----------------|--------------------------------------------------|
| ↑↓←→ (Arrow Keys) | Move player (green block)                        |
| W / A / S / D    | Throw a mud zone in that direction               |
| Spacebar         | Clear all terrain and AI agents around the player |

---

## 🧠 AI Architecture

### Role Assignment (via K-Means)
- **Chaser**: Tracks the player’s current location.
- **Blocker**: Predicts potential player routes and intercepts them by building walls.
- **Helper**: Assists Chaser by applying pressure or influencing terrain costs.

### Cooperative A\* Pathfinding
- Each AI agent plans routes while referencing a shared reservation table to avoid path overlap.
- All agents replan paths and evaluate targets every frame for real-time reactivity.

---

## 🌍 Terrain System

- **Mud**: Temporarily slows down movement. Both player and AI are delayed by 1 turn when stepping on mud.
- **Water**: Delays movement by 2 turns if stepped on.
- **Wall**: Completely impassable for both player and AI.

Terrain is dynamically modified during gameplay by both the player and AI, and is considered in pathfinding decisions.

---

## 🛠 Installation

### Requirements

- Python 3.7+
- pygame

### Install dependencies

```bash
pip install pygame
```
### Run the game

```bash
python main.py
```

---

## 📁 Files

| File                        | Description                                  |
|-----------------------------|----------------------------------------------|
| `main.py`                   | Main loop and simulation entry point         |
| `cooperative_astar.py`      | Multi-agent pathfinding (Coop A*)            |
| `npc_clustering.py`         | K-Means clustering for role distribution     |
| `pygame_running_and_display.py` | Rendering, UI, and screen update handling   |

---

## 📜 License

This project is released under the MIT License.

---

## 🎓 Reference & Credits

Inspired by the [GDC talk “Death Stranding: An AI Postmortem”](https://youtu.be/yqZE5O8VPAU), particularly the discussion of AI coordination and terrain-aware pathfinding. This project explores an alternative approach based on role-based coordination, simple clustering, and dynamic decision logic—without machine learning.

---

## 📌 Additional Notes

- Designed to illustrate **multi-agent strategy**, **terrain adaptation**, and **asynchronous role control**.
```
