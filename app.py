"""AI Playground: Search & Game Playing - Streamlit front end.  Run:  streamlit run app.py"""
import pandas as pd
import streamlit as st

import game
import search

st.set_page_config(page_title="AI Playground", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1250px;}
.hero {background: linear-gradient(120deg, #4f46e5, #7c3aed 55%, #db2777);
       color: #fff; padding: 26px 32px; border-radius: 18px; margin-bottom: 8px;}
.hero h1 {color: #fff; margin: 0; font-size: 2.2rem; padding: 0;}
.hero p {margin: 6px 0 0 0; opacity: .9; font-size: 1.05rem;}
.chip {display: inline-block; padding: 4px 12px; margin: 3px 2px; border-radius: 999px;
       background: rgba(79,70,229,.12); border: 1px solid rgba(79,70,229,.35);
       font-size: .92rem; font-weight: 600;}
.chip.start {background: rgba(249,115,22,.18); border-color: rgba(249,115,22,.5);}
.chip.goal {background: rgba(34,197,94,.18); border-color: rgba(34,197,94,.5);}
.arrow {opacity: .5; margin: 0 2px;}
.status {text-align: center; font-size: 1.3rem; font-weight: 700; padding: 12px;
         border-radius: 12px; margin-bottom: 12px;}
.status.turn {background: rgba(79,70,229,.10);}
.status.win {background: rgba(34,197,94,.18);}
.status.lose {background: rgba(239,68,68,.16);}
.status.draw {background: rgba(234,179,8,.18);}
.stTabs [data-baseweb="tab"] {font-size: 1.05rem; padding: 10px 18px;}
div[data-testid="stMetric"] {background: rgba(127,127,127,.07); border-radius: 12px;
                             padding: 12px 16px;}
</style>
<div class="hero">
  <h1>🧠 AI Playground</h1>
  <p>Unit I · Problem solving by searching and adversarial search</p>
</div>
""", unsafe_allow_html=True)

tab_search, tab_game = st.tabs(["🗺️  Search: Romania map", "🎮  Game playing: Tic-tac-toe"])

# ================================================================ search
with tab_search:
    left, right = st.columns([1, 1.7], gap="large")
    with left:
        with st.container(border=True):
            st.markdown("#### 🚗 Find a route to Bucharest")
            start = st.selectbox("Start city", search.CITIES, index=search.CITIES.index("Arad"))
            algo = st.segmented_control("Algorithm", list(search.ALGORITHMS), default="A*")
            algo = algo or "A*"
        res = search.ALGORITHMS[algo](start)
        expanded = res["expanded"]

        m1, m2, m3 = st.columns(3)
        m1.metric("Cost (km)", res["cost"] if res["path"] else "-")
        m2.metric("Expanded", len(expanded))
        m3.metric("Stops", len(res["path"]) - 1 if res["path"] else "-")

        if res["path"]:
            chips = []
            for i, city in enumerate(res["path"]):
                kind = "start" if i == 0 else "goal" if city == search.GOAL else ""
                chips.append(f'<span class="chip {kind}">{city}</span>')
            st.markdown("**Route found**<br>" + '<span class="arrow">→</span>'.join(chips),
                        unsafe_allow_html=True)
        else:
            st.error("No path found.")

        step = st.slider("Replay the search: expansion step", 1, len(expanded), len(expanded))
        st.caption(f"Step {step}: expanding **{expanded[step - 1]}**. "
                   f"Order so far: {', '.join(expanded[:step])}")

    with right:
        done = step == len(expanded)
        shown = set(expanded[:step])
        on_path = set(zip(res["path"], res["path"][1:])) if res["path"] and done else set()
        dot = ['graph { layout=neato; bgcolor="transparent"; splines=true;',
               'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, '
               'color="#64748b", penwidth=1.2, margin="0.08,0.04"];',
               'edge [color="#94a3b8", fontname="Helvetica", fontsize=9, fontcolor="#64748b"];']
        for city, (x, y) in search.LOCATIONS.items():
            if city == expanded[step - 1] and not done:
                fill = "#facc15"
            elif city == start:
                fill = "#fb923c"
            elif city == search.GOAL:
                fill = "#4ade80"
            elif city in shown:
                fill = "#a5b4fc"
            else:
                fill = "#f8fafc"
            dot.append(f'"{city}" [pos="{x / 60:.2f},{y / 60:.2f}!", fillcolor="{fill}", '
                       f'label="{city}\\nh={search.SLD[city]}"];')
        for a, b, d in search.ROADS:
            hot = (a, b) in on_path or (b, a) in on_path
            dot.append(f'"{a}" -- "{b}" [label="{d}"'
                       + (', color="#e11d48", penwidth=4, fontcolor="#e11d48"' if hot else '') + '];')
        dot.append("}")
        with st.container(border=True):
            st.graphviz_chart("\n".join(dot), width="stretch")
            st.caption("🟧 start · 🟩 goal · 🟨 being expanded · 🟪 already expanded · "
                       "red line = route found · h = straight-line distance to Bucharest")

    st.markdown("#### 📊 Compare all four algorithms")
    rows = []
    for name, fn in search.ALGORITHMS.items():
        r = fn(start)
        complete, optimal, time_c, space_c = search.PROPERTIES[name]
        rows.append({"Algorithm": name, "Cost (km)": r["cost"], "Nodes expanded": len(r["expanded"]),
                     "Route": " → ".join(r["path"]), "Complete?": complete, "Optimal?": optimal,
                     "Time": time_c, "Space": space_c})
    best = min(r["Cost (km)"] for r in rows)
    df = pd.DataFrame(rows).set_index("Algorithm")
    st.dataframe(df.style.apply(
        lambda col: ["background-color: rgba(34,197,94,.22)" if v == best else "" for v in col],
        subset=["Cost (km)"]), width="stretch")
    st.caption("Green = cheapest route. From Arad, Greedy rushes via Fagaras (450 km) while A* "
               "finds the optimal route via Rimnicu Vilcea and Pitesti (418 km).")

    with st.expander("📘 Problem formulation"):
        st.markdown("""
| Component | Value |
|---|---|
| State | the current city |
| Initial state | the start city |
| Actions | drive to a neighbouring city |
| Goal test | city = Bucharest |
| Path cost | total km driven |
| Heuristic h(n) | straight-line distance to Bucharest (admissible) |

- **BFS** expands the shallowest node first (FIFO queue).
- **DFS** expands the deepest node first (LIFO stack).
- **Greedy best-first** expands the node with the smallest **h(n)**.
- **A\\*** expands the node with the smallest **f(n) = g(n) + h(n)**.
""")

# ================================================================ game
with tab_game:
    ss = st.session_state
    if "board" not in ss:
        ss.board, ss.stats, ss.score, ss.counted = [""] * 9, None, {"You": 0, "Computer": 0, "Draws": 0}, False

    def computer_move():
        stats = {name: fn(ss.board) for name, fn in game.ALGORITHMS.items()}
        ss.board[stats[ss.ai_algo][0]] = "O"
        ss.stats = stats

    def play(i):
        if ss.board[i] or game.winner(ss.board):
            return
        ss.board[i] = "X"
        if not game.winner(ss.board):
            computer_move()

    def new_game():
        ss.board, ss.stats, ss.counted = [""] * 9, None, False
        if ss.ai_first:
            computer_move()

    over = game.winner(ss.board)
    if over and not ss.counted:
        ss.score[{"X": "You", "O": "Computer", "Draw": "Draws"}[over]] += 1
        ss.counted = True
    line = game.winning_line(ss.board) or ()

    # Big board: style each square according to what is in it.
    css = [".st-key-board button {height: 118px; border-radius: 16px; border-width: 2px;}",
           ".st-key-board button p {font-size: 3.4rem; font-weight: 800; line-height: 1;}",
           ".st-key-board button:disabled {opacity: 1; cursor: default;}"]
    for i, v in enumerate(ss.board):
        color = {"X": "#4f46e5", "O": "#db2777"}.get(v)
        if color:
            css.append(f".st-key-cell{i} button p {{color: {color};}}")
        if i in line:
            css.append(f".st-key-cell{i} button {{background: rgba(34,197,94,.25); "
                       f"border-color: #22c55e;}}")
    st.markdown("<style>" + "\n".join(css) + "</style>", unsafe_allow_html=True)

    g1, g2 = st.columns([1, 1.15], gap="large")
    with g1:
        status = {"X": ("win", "🎉 You win!"), "O": ("lose", "🤖 The computer wins!"),
                  "Draw": ("draw", "🤝 Draw. A perfect player can't be beaten.")}
        kind, text = status.get(over, ("turn", "Your turn: you are <b style='color:#4f46e5'>X</b>"))
        st.markdown(f'<div class="status {kind}">{text}</div>', unsafe_allow_html=True)
        with st.container(key="board"):
            for r in range(3):
                cols = st.columns(3)
                for c in range(3):
                    i = r * 3 + c
                    cols[c].button(ss.board[i] or " ", key=f"cell{i}", on_click=play, args=(i,),
                                   disabled=bool(ss.board[i] or over), width="stretch")
        s1, s2, s3 = st.columns(3)
        s1.metric("You", ss.score["You"])
        s2.metric("Computer", ss.score["Computer"])
        s3.metric("Draws", ss.score["Draws"])

    with g2:
        with st.container(border=True):
            st.markdown("#### ⚙️ Settings")
            st.segmented_control("Computer uses", list(game.ALGORITHMS), default="Alpha-Beta pruning",
                                 key="ai_algo", required=True)
            st.toggle("Computer plays first", key="ai_first")
            st.button("🔄 New game", on_click=new_game, type="primary", width="stretch")

        with st.container(border=True):
            st.markdown("#### 🔎 Search for the computer's last move")
            if ss.stats:
                (mm_move, mm_val, mm), (_, _, ab) = ss.stats["Minimax"], ss.stats["Alpha-Beta pruning"]
                k1, k2 = st.columns(2)
                k1.metric("Minimax nodes", f"{mm:,}")
                k2.metric("Alpha-Beta nodes", f"{ab:,}", f"-{100 - 100 * ab // mm}% nodes",
                          delta_color="inverse")
                st.progress(ab / mm, text=f"Alpha-Beta searched {ab / mm:.0%} of the Minimax tree")
                verdict = ("computer can force a win" if mm_val > 0 else
                           "you could still win" if mm_val < 0 else "best play leads to a draw")
                st.caption(f"Chosen square: {mm_move + 1} (1-9, left to right, top to bottom) · "
                           f"value {mm_val}: {verdict}.")
            else:
                st.caption("Make a move and the computer's search statistics appear here.")

        with st.expander("📘 How it works", expanded=False):
            st.markdown("""
- **Minimax:** the computer (MAX) assumes you (MIN) always play your best move, and picks the
  move with the highest guaranteed value.
- **Alpha-Beta pruning:** keeps the best values found so far (α for MAX, β for MIN) and skips any
  branch that can't change the decision. Same result, far fewer nodes.
- **Value** > 0 means the computer can force a win, 0 means a draw, < 0 means you could win.
""")
