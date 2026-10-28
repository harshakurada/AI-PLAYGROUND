# AI Playground

A simple Streamlit app with two modules from Unit I of the AI syllabus. All algorithms are
written from scratch in plain Python.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501.

## Modules

| Module | Topics | File |
|---|---|---|
| 🗺️ Search | Problem formulation, BFS, DFS, heuristics, Greedy best-first, A* on the Romania map | `search.py` |
| ❌⭕ Game playing | Adversarial search, Minimax, Alpha-Beta pruning, played as Tic-tac-toe | `game.py` |

`app.py` is the user interface.

## Results to check against the textbook (AIMA)

- Greedy best-first from Arad: Arad → Sibiu → Fagaras → Bucharest (450 km)
- A* from Arad: Arad → Sibiu → Rimnicu Vilcea → Pitesti → Bucharest (418 km, optimal)
- Tic-tac-toe with perfect play is a draw; Alpha-Beta picks the same moves as Minimax with far fewer nodes
