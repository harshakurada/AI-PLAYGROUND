"""Module 1 - Problem solving by searching, on the Romania road map (AIMA ch. 3).

Problem formulation
  State:       the city we are in
  Initial:     the chosen start city
  Actions:     drive along a road to a neighbouring city
  Goal test:   city == Bucharest
  Path cost:   sum of road distances (km)
"""
import heapq
from collections import deque

ROADS = [
    ("Arad", "Zerind", 75), ("Arad", "Sibiu", 140), ("Arad", "Timisoara", 118),
    ("Zerind", "Oradea", 71), ("Oradea", "Sibiu", 151), ("Timisoara", "Lugoj", 111),
    ("Lugoj", "Mehadia", 70), ("Mehadia", "Drobeta", 75), ("Drobeta", "Craiova", 120),
    ("Craiova", "Rimnicu Vilcea", 146), ("Craiova", "Pitesti", 138),
    ("Sibiu", "Fagaras", 99), ("Sibiu", "Rimnicu Vilcea", 80),
    ("Rimnicu Vilcea", "Pitesti", 97), ("Fagaras", "Bucharest", 211),
    ("Pitesti", "Bucharest", 101), ("Bucharest", "Giurgiu", 90),
    ("Bucharest", "Urziceni", 85), ("Urziceni", "Hirsova", 98), ("Hirsova", "Eforie", 86),
    ("Urziceni", "Vaslui", 142), ("Vaslui", "Iasi", 92), ("Iasi", "Neamt", 87),
]

# Heuristic h(n): straight-line distance to Bucharest (admissible - never overestimates).
SLD = {
    "Arad": 366, "Bucharest": 0, "Craiova": 160, "Drobeta": 242, "Eforie": 161,
    "Fagaras": 176, "Giurgiu": 77, "Hirsova": 151, "Iasi": 226, "Lugoj": 244,
    "Mehadia": 241, "Neamt": 234, "Oradea": 380, "Pitesti": 100, "Rimnicu Vilcea": 193,
    "Sibiu": 253, "Timisoara": 329, "Urziceni": 80, "Vaslui": 199, "Zerind": 374,
}

GOAL = "Bucharest"

# Map positions (from the AIMA code), used only for drawing.
LOCATIONS = {
    "Arad": (91, 492), "Bucharest": (400, 327), "Craiova": (253, 288), "Drobeta": (165, 299),
    "Eforie": (562, 293), "Fagaras": (305, 449), "Giurgiu": (375, 270), "Hirsova": (534, 350),
    "Iasi": (473, 506), "Lugoj": (165, 379), "Mehadia": (168, 339), "Neamt": (406, 537),
    "Oradea": (131, 571), "Pitesti": (320, 368), "Rimnicu Vilcea": (233, 410), "Sibiu": (207, 457),
    "Timisoara": (94, 410), "Urziceni": (456, 350), "Vaslui": (509, 444), "Zerind": (108, 531),
}

GRAPH = {}
for a, b, d in ROADS:
    GRAPH.setdefault(a, {})[b] = d
    GRAPH.setdefault(b, {})[a] = d
CITIES = sorted(GRAPH)


def path_cost(path):
    return sum(GRAPH[a][b] for a, b in zip(path, path[1:]))


def _result(path, expanded):
    return {"path": path, "cost": path_cost(path) if path else None, "expanded": expanded}


def bfs(start, goal=GOAL):
    """Uninformed: expand the shallowest node first (FIFO queue)."""
    if start == goal:
        return _result([start], [start])
    frontier, reached, expanded = deque([[start]]), {start}, []
    while frontier:
        path = frontier.popleft()
        expanded.append(path[-1])
        for nxt in GRAPH[path[-1]]:
            if nxt not in reached:
                if nxt == goal:
                    return _result(path + [nxt], expanded)
                reached.add(nxt)
                frontier.append(path + [nxt])
    return _result(None, expanded)


def dfs(start, goal=GOAL):
    """Uninformed: expand the deepest node first (LIFO stack)."""
    frontier, visited, expanded = [[start]], set(), []
    while frontier:
        path = frontier.pop()
        city = path[-1]
        if city in visited:
            continue
        visited.add(city)
        expanded.append(city)
        if city == goal:
            return _result(path, expanded)
        for nxt in sorted(GRAPH[city], reverse=True):
            if nxt not in visited:
                frontier.append(path + [nxt])
    return _result(None, expanded)


def _best_first(start, goal, f):
    """Expand the node with the lowest f(path) first (priority queue)."""
    frontier, best_g, expanded = [(f([start]), [start])], {start: 0}, []
    while frontier:
        _, path = heapq.heappop(frontier)
        city = path[-1]
        if city in expanded:
            continue
        expanded.append(city)
        if city == goal:
            return _result(path, expanded)
        for nxt in GRAPH[city]:
            new = path + [nxt]
            g = path_cost(new)
            if nxt not in best_g or g < best_g[nxt]:
                best_g[nxt] = g
                heapq.heappush(frontier, (f(new), new))
    return _result(None, expanded)


def greedy(start, goal=GOAL):
    """Informed: f(n) = h(n). Fast, but not optimal."""
    return _best_first(start, goal, lambda p: SLD[p[-1]])


def astar(start, goal=GOAL):
    """Informed: f(n) = g(n) + h(n). Optimal when h is admissible."""
    return _best_first(start, goal, lambda p: path_cost(p) + SLD[p[-1]])


ALGORITHMS = {"BFS": bfs, "DFS": dfs, "Greedy best-first": greedy, "A*": astar}

# (complete?, optimal?, time, space) with b = branching factor, d = depth of the shallowest goal,
# m = maximum depth
PROPERTIES = {
    "BFS": ("Yes", "Only if all step costs are equal", "O(b^d)", "O(b^d)"),
    "DFS": ("No (on infinite graphs)", "No", "O(b^m)", "O(bm)"),
    "Greedy best-first": ("No (on infinite graphs)", "No", "O(b^m)", "O(b^m)"),
    "A*": ("Yes", "Yes (admissible h)", "Exponential", "Exponential"),
}
