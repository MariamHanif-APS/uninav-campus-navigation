import math
import tkinter as tk
from tkinter import font as tkfont


# ─────────────────────────────────────────────
#  KD-Tree Core
# ─────────────────────────────────────────────

class KDNode:
    def __init__(self, coordinates, name, building_type):
        self.coordinates = tuple(coordinates)
        self.name = name
        self.building_type = building_type
        self.left = None
        self.right = None


class KDTree:
    def __init__(self, k=2):
        self.root = None
        self.k = k

    def insert(self, coordinates, name, building_type):
        self.root = self._insert_recursive(self.root, coordinates, name, building_type, 0)

    def _insert_recursive(self, node, coordinates, name, building_type, depth):
        if not node:
            return KDNode(coordinates, name, building_type)
        if node.coordinates == tuple(coordinates):
            return node
        axis = depth % self.k
        if coordinates[axis] < node.coordinates[axis]:
            node.left = self._insert_recursive(node.left, coordinates, name, building_type, depth + 1)
        else:
            node.right = self._insert_recursive(node.right, coordinates, name, building_type, depth + 1)
        return node

    def get_all_nodes(self):
        nodes = []
        self._collect_all(self.root, nodes)
        return nodes

    def _collect_all(self, node, nodes):
        if not node:
            return
        nodes.append(node)
        self._collect_all(node.left, nodes)
        self._collect_all(node.right, nodes)

    def find_by_name(self, name):
        name = name.lower().strip()
        for node in self.get_all_nodes():
            if node.name.lower() == name:
                return node
        for node in self.get_all_nodes():
            if name in node.name.lower():
                return node
        return None

    def nearest_neighbor(self, target_coordinates):
        best_node, best_dist = self._nearest_recursive(
            self.root, tuple(target_coordinates), 0, None, float('inf')
        )
        return best_node

    def _nearest_recursive(self, node, target, depth, best_node, best_dist):
        if not node:
            return best_node, best_dist
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(node.coordinates, target)))
        if dist < best_dist:
            best_dist = dist
            best_node = node
        axis = depth % self.k
        if target[axis] < node.coordinates[axis]:
            good_side, bad_side = node.left, node.right
        else:
            good_side, bad_side = node.right, node.left
        best_node, best_dist = self._nearest_recursive(good_side, target, depth + 1, best_node, best_dist)
        if abs(target[axis] - node.coordinates[axis]) < best_dist:
            best_node, best_dist = self._nearest_recursive(bad_side, target, depth + 1, best_node, best_dist)
        return best_node, best_dist


# ─────────────────────────────────────────────
#  Direction Logic
# ─────────────────────────────────────────────

def get_directions(start_coords, end_coords):
    dx = end_coords[0] - start_coords[0]
    dy = end_coords[1] - start_coords[1]
    distance = round(math.sqrt(dx ** 2 + dy ** 2), 1)
    steps = []
    if dx != 0 and dy != 0:
        steps.append(("RIGHT" if dx > 0 else "LEFT", abs(dx), "horizontal"))
        steps.append(("AHEAD (north)" if dy > 0 else "BACK (south)", abs(dy), "vertical"))
    elif dx != 0:
        steps.append(("RIGHT" if dx > 0 else "LEFT", abs(dx), "horizontal"))
    elif dy != 0:
        steps.append(("AHEAD (north)" if dy > 0 else "BACK (south)", abs(dy), "vertical"))
    else:
        steps.append(("already here", 0, "none"))
    return steps, distance


# ─────────────────────────────────────────────
#  Campus Data
# ─────────────────────────────────────────────

BUILDINGS = [
    # (x, y),  name,  type
    # x = left-right (higher = east/right)
    # y = up-down (higher = north/towards courts)
    ((8,  1),  "Gate 2",                    "entrance"),
    ((12, 1),  "Gate 4",                    "entrance"),
    ((6,  3),  "Cafe 2 Go",                 "food"),
    ((8,  3),  "Sync",                      "food"),
    ((14, 3),  "Fries",                     "food"),
    ((10, 4),  "Sky Dhaba",                 "food"),
    ((12, 4),  "Tapal",                     "food"),
    ((9,  5),  "Baithak",                   "social"),
    ((11, 5),  "Mehfil",                    "social"),
    ((8,  6),  "Math Lab",                  "academic"),
    ((11, 6),  "Circuits Lab",              "academic"),
    ((14, 6),  "Communication Systems Lab", "academic"),
    ((9,  7),  "Design Studio",             "academic"),
    ((12, 7),  "Projects Lab",              "academic"),
    ((7,  8),  "Film Studio",               "academic"),
    ((15, 8),  "Horizon",                   "academic"),
    ((8,  9),  "Auditorium",                "academic"),
    ((13, 9),  "Casim Computing Lab",       "academic"),
    ((10, 10), "Library",                   "academic"),
    ((16, 11), "IDEAL",                     "academic"),
    ((6,  11), "Tariq Rafi Hall",           "hall"),
    ((13, 11), "Soorty Hall",               "hall"),
    ((12, 12), "Student Lounge",            "social"),
    ((10, 13), "Music Room",                "hall"),
    ((7,  14), "Zen Garden",                "recreation"),
    ((12, 15), "Amphitheater",              "recreation"),
    ((8,  17), "Gymnasium",                 "recreation"),
    ((10, 18), "Courts",                    "recreation"),
]

TYPE_COLORS = {
    "academic":   "#4A90D9",
    "food":       "#27AE60",
    "social":     "#16A085",
    "recreation": "#C0392B",
    "hall":       "#7F8C8D",
    "entrance":   "#E67E22",
}

TYPE_LABEL = {
    "academic":   "Academic",
    "food":       "Food & Cafe",
    "social":     "Social",
    "recreation": "Recreation",
    "hall":       "Halls & Rooms",
    "entrance":   "Entrance / Gate",
}


# ─────────────────────────────────────────────
#  GUI Application
# ─────────────────────────────────────────────

class UniNavApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UniNav — Campus Navigation")
        self.root.configure(bg="#F5F5F0")
        self.root.resizable(True, True)

        # KD-Tree
        self.tree = KDTree(k=2)
        for coords, name, btype in BUILDINGS:
            self.tree.insert(coords, name, btype)

        # Map scaling
        self.pad = 40
        self.map_w = 520
        self.map_h = 580
        self.min_x = 5
        self.max_x = 18
        self.min_y = 0
        self.max_y = 19

        # State
        self.from_node = None
        self.to_node = None
        self.hovered = None
        self.building_items = {}   # name -> canvas item ids
        self.dot_items = {}        # name -> (oval_id, label_id)
        self.path_id = None
        self.from_marker = None
        self.to_marker = None
        self.from_label_id = None
        self.to_label_id = None

        self._build_ui()
        self._draw_map()

    # ── Layout ──────────────────────────────

    def _build_ui(self):
        # Fonts
        self.f_title  = tkfont.Font(family="Helvetica", size=15, weight="bold")
        self.f_label  = tkfont.Font(family="Helvetica", size=10)
        self.f_small  = tkfont.Font(family="Helvetica", size=9)
        self.f_step   = tkfont.Font(family="Helvetica", size=10)
        self.f_bold   = tkfont.Font(family="Helvetica", size=10, weight="bold")

        # Main container
        main = tk.Frame(self.root, bg="#F5F5F0")
        main.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Left panel
        left = tk.Frame(main, bg="#F5F5F0", width=240)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))
        left.pack_propagate(False)

        # Title
        tk.Label(left, text="UniNav", font=self.f_title,
                 bg="#F5F5F0", fg="#1A1A1A").pack(anchor="w", pady=(0, 2))
        tk.Label(left, text="Campus Navigation System",
                 font=self.f_small, bg="#F5F5F0", fg="#888").pack(anchor="w", pady=(0, 14))

        # ── Input card ──
        card1 = tk.Frame(left, bg="white", relief="flat",
                         highlightbackground="#E0E0E0", highlightthickness=1)
        card1.pack(fill=tk.X, pady=(0, 10))
        inner1 = tk.Frame(card1, bg="white")
        inner1.pack(fill=tk.X, padx=12, pady=12)

        tk.Label(inner1, text="Where do you want to go?",
                 font=self.f_label, bg="white", fg="#555").pack(anchor="w")
        self.dest_var = tk.StringVar()
        self.dest_var.trace_add("write", self._on_dest_type)
        self.dest_entry = tk.Entry(inner1, textvariable=self.dest_var,
                                   font=self.f_label, relief="flat",
                                   bg="#F8F8F6", fg="#1A1A1A",
                                   insertbackground="#1A1A1A")
        self.dest_entry.pack(fill=tk.X, ipady=6, pady=(4, 0))
        self.dest_entry.bind("<Return>", lambda e: self.from_entry.focus())

        self.dest_hint = tk.Label(inner1, text="", font=self.f_small,
                                  bg="white", fg="#4A90D9", wraplength=200, justify="left")
        self.dest_hint.pack(anchor="w", pady=(2, 0))

        tk.Frame(inner1, bg="#EFEFEF", height=1).pack(fill=tk.X, pady=8)

        tk.Label(inner1, text="Where are you now?",
                 font=self.f_label, bg="white", fg="#555").pack(anchor="w")
        self.from_var = tk.StringVar()
        self.from_var.trace_add("write", self._on_from_type)
        self.from_entry = tk.Entry(inner1, textvariable=self.from_var,
                                   font=self.f_label, relief="flat",
                                   bg="#F8F8F6", fg="#1A1A1A",
                                   insertbackground="#1A1A1A")
        self.from_entry.pack(fill=tk.X, ipady=6, pady=(4, 0))
        self.from_entry.bind("<Return>", lambda e: self._find_route())

        self.from_hint = tk.Label(inner1, text="", font=self.f_small,
                                  bg="white", fg="#4A90D9", wraplength=200, justify="left")
        self.from_hint.pack(anchor="w", pady=(2, 0))

        self.error_label = tk.Label(inner1, text="", font=self.f_small,
                                    bg="white", fg="#E74C3C", wraplength=200, justify="left")
        self.error_label.pack(anchor="w", pady=(4, 0))

        btn = tk.Button(inner1, text="Get Directions →",
                        font=self.f_bold, bg="#2C3E50", fg="white",
                        relief="flat", cursor="hand2", padx=12, pady=7,
                        command=self._find_route,
                        activebackground="#1A252F", activeforeground="white")
        btn.pack(fill=tk.X, pady=(10, 0))

        # ── Directions card ──
        card2 = tk.Frame(left, bg="white", relief="flat",
                         highlightbackground="#E0E0E0", highlightthickness=1)
        card2.pack(fill=tk.X, pady=(0, 10))
        inner2 = tk.Frame(card2, bg="white")
        inner2.pack(fill=tk.X, padx=12, pady=12)

        tk.Label(inner2, text="Directions", font=self.f_bold,
                 bg="white", fg="#1A1A1A").pack(anchor="w", pady=(0, 6))

        self.dir_frame = tk.Frame(inner2, bg="white")
        self.dir_frame.pack(fill=tk.X)

        self._show_placeholder()

        # ── Legend card ──
        card3 = tk.Frame(left, bg="white", relief="flat",
                         highlightbackground="#E0E0E0", highlightthickness=1)
        card3.pack(fill=tk.X)
        inner3 = tk.Frame(card3, bg="white")
        inner3.pack(fill=tk.X, padx=12, pady=10)

        tk.Label(inner3, text="Legend", font=self.f_bold,
                 bg="white", fg="#1A1A1A").pack(anchor="w", pady=(0, 6))

        for btype, color in TYPE_COLORS.items():
            row = tk.Frame(inner3, bg="white")
            row.pack(anchor="w", pady=1)
            dot = tk.Canvas(row, width=12, height=12, bg="white",
                            highlightthickness=0)
            dot.pack(side=tk.LEFT, padx=(0, 6))
            dot.create_oval(2, 2, 10, 10, fill=color, outline="")
            tk.Label(row, text=TYPE_LABEL[btype], font=self.f_small,
                     bg="white", fg="#444").pack(side=tk.LEFT)

        # Special markers
        for color, label in [("#E74C3C", "You are here (S)"), ("#27AE60", "Destination (E)")]:
            row = tk.Frame(inner3, bg="white")
            row.pack(anchor="w", pady=1)
            dot = tk.Canvas(row, width=12, height=12, bg="white", highlightthickness=0)
            dot.pack(side=tk.LEFT, padx=(0, 6))
            dot.create_oval(2, 2, 10, 10, fill=color, outline="")
            tk.Label(row, text=label, font=self.f_small,
                     bg="white", fg="#444").pack(side=tk.LEFT)

        # ── Map panel (right) ──
        map_frame = tk.Frame(main, bg="white", relief="flat",
                             highlightbackground="#E0E0E0", highlightthickness=1)
        map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        map_header = tk.Frame(map_frame, bg="white")
        map_header.pack(fill=tk.X, padx=12, pady=(10, 0))
        tk.Label(map_header, text="CAMPUS MAP", font=self.f_small,
                 bg="white", fg="#999").pack(side=tk.LEFT)
        tk.Label(map_header, text="N ↑  (Courts at top · Entrance at bottom)",
                 font=self.f_small, bg="white", fg="#BBB").pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(map_frame, bg="#FAFAF7",
                                width=self.map_w, height=self.map_h,
                                highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # Tooltip
        self.tooltip = tk.Label(self.root, text="", font=self.f_small,
                                bg="#2C3E50", fg="white",
                                padx=8, pady=4, relief="flat")

    # ── Map Drawing ─────────────────────────

    def _coord_to_px(self, x, y):
        px = self.pad + (x - self.min_x) / (self.max_x - self.min_x) * (self.map_w - 2 * self.pad)
        py = self.map_h - self.pad - (y - self.min_y) / (self.max_y - self.min_y) * (self.map_h - 2 * self.pad)
        return px, py

    def _draw_map(self):
        c = self.canvas
        c.delete("all")
        self.building_items = {}

        # Grid lines
        for gx in range(self.min_x, self.max_x + 1):
            px, _ = self._coord_to_px(gx, 0)
            c.create_line(px, 0, px, self.map_h, fill="#EBEBEB", width=1)
        for gy in range(self.min_y, self.max_y + 1):
            _, py = self._coord_to_px(0, gy)
            c.create_line(0, py, self.map_w, py, fill="#EBEBEB", width=1)

        # North / South labels
        c.create_text(self.map_w // 2, 12, text="▲  COURTS / GYMNASIUM  (North)",
                      font=self.f_small, fill="#BBBBAA")
        c.create_text(self.map_w // 2, self.map_h - 12,
                      text="▼  MAIN ENTRANCE  (South)",
                      font=self.f_small, fill="#BBBBAA")

        # Path placeholder
        self.path_id = None
        self.from_marker = None
        self.to_marker = None
        self.from_label_id = None
        self.to_label_id = None

        # Buildings
        r = 8
        for coords, name, btype in BUILDINGS:
            px, py = self._coord_to_px(*coords)
            color = TYPE_COLORS.get(btype, "#888")

            oval = c.create_oval(px - r, py - r, px + r, py + r,
                                 fill=color, outline="white", width=1.5,
                                 tags=("building", name))
            lbl = c.create_text(px, py + r + 8, text=name,
                                 font=self.f_small, fill="#444",
                                 tags=("blabel", name))
            self.building_items[name] = (oval, lbl, px, py)

    def _draw_route(self, from_node, to_node):
        c = self.canvas

        # Remove old route
        if self.path_id:
            c.delete(self.path_id)
        if self.from_marker:
            c.delete(self.from_marker)
            c.delete(self.from_label_id)
        if self.to_marker:
            c.delete(self.to_marker)
            c.delete(self.to_label_id)

        fx, fy = self._coord_to_px(*from_node.coordinates)
        tx, ty = self._coord_to_px(*to_node.coordinates)

        # L-shaped path: horizontal then vertical
        mid_x = tx
        mid_y = fy

        self.path_id = c.create_line(fx, fy, mid_x, mid_y, tx, ty,
                                      fill="#E74C3C", width=2.5,
                                      dash=(8, 4), arrow=tk.LAST,
                                      arrowshape=(10, 12, 4))

        # From marker (red S)
        rm = 11
        self.from_marker = c.create_oval(fx - rm, fy - rm, fx + rm, fy + rm,
                                          fill="#E74C3C", outline="white", width=2)
        self.from_label_id = c.create_text(fx, fy, text="S",
                                            font=tkfont.Font(family="Helvetica", size=9, weight="bold"),
                                            fill="white")

        # To marker (green E)
        self.to_marker = c.create_oval(tx - rm, ty - rm, tx + rm, ty + rm,
                                        fill="#27AE60", outline="white", width=2)
        self.to_label_id = c.create_text(tx, ty, text="E",
                                          font=tkfont.Font(family="Helvetica", size=9, weight="bold"),
                                          fill="white")

        # Raise markers above everything
        c.tag_raise(self.path_id)
        c.tag_raise(self.from_marker)
        c.tag_raise(self.from_label_id)
        c.tag_raise(self.to_marker)
        c.tag_raise(self.to_label_id)

    # ── Route Finding ────────────────────────

    def _find_route(self):
        dest_val = self.dest_var.get().strip()
        from_val = self.from_var.get().strip()
        self.error_label.config(text="")

        if not dest_val:
            self.error_label.config(text="Please enter a destination.")
            return
        if not from_val:
            self.error_label.config(text="Please enter your current location.")
            return

        to_node = self.tree.find_by_name(dest_val)
        from_node = self.tree.find_by_name(from_val)

        if not to_node:
            sugg = self._get_suggestions(dest_val)
            msg = f'"{dest_val}" not found.'
            if sugg:
                msg += " Try: " + ", ".join(sugg[:2])
            self.error_label.config(text=msg)
            return

        if not from_node:
            sugg = self._get_suggestions(from_val)
            msg = f'"{from_val}" not found.'
            if sugg:
                msg += " Try: " + ", ".join(sugg[:2])
            self.error_label.config(text=msg)
            return

        if from_node.coordinates == to_node.coordinates:
            self.error_label.config(text="You are already there!")
            return

        self.from_node = from_node
        self.to_node = to_node

        self._draw_route(from_node, to_node)
        self._show_directions(from_node, to_node)

    def _show_directions(self, from_node, to_node):
        # Clear old directions
        for w in self.dir_frame.winfo_children():
            w.destroy()

        steps, distance = get_directions(from_node.coordinates, to_node.coordinates)

        # From → To header
        header = tk.Frame(self.dir_frame, bg="white")
        header.pack(fill=tk.X, pady=(0, 8))
        tk.Label(header, text=from_node.name, font=self.f_bold,
                 bg="white", fg="#E74C3C").pack(side=tk.LEFT)
        tk.Label(header, text=" → ", font=self.f_label,
                 bg="white", fg="#999").pack(side=tk.LEFT)
        tk.Label(header, text=to_node.name, font=self.f_bold,
                 bg="white", fg="#27AE60").pack(side=tk.LEFT)

        # Distance badge
        dist_frame = tk.Frame(self.dir_frame, bg="#EAF4EC",
                              relief="flat")
        dist_frame.pack(anchor="w", pady=(0, 8))
        tk.Label(dist_frame, text=f"  ~{distance} units away  ",
                 font=self.f_small, bg="#EAF4EC", fg="#1E8449").pack(padx=4, pady=2)

        # Steps
        for i, (direction, amount, kind) in enumerate(steps):
            if kind == "none":
                tk.Label(self.dir_frame, text="You are already here!",
                         font=self.f_step, bg="white", fg="#27AE60").pack(anchor="w")
            else:
                row = tk.Frame(self.dir_frame, bg="white")
                row.pack(fill=tk.X, pady=3)

                num_lbl = tk.Label(row,
                                   text=f" {i+1} ",
                                   font=tkfont.Font(family="Helvetica", size=9, weight="bold"),
                                   bg="#2C3E50", fg="white")
                num_lbl.pack(side=tk.LEFT, padx=(0, 8))

                arrow = "→" if kind == "horizontal" else "↑" if "north" in direction.lower() else "↓"
                text = f"{arrow}  Head {direction} for {amount} block(s)"
                tk.Label(row, text=text, font=self.f_step,
                         bg="white", fg="#2C3E50", anchor="w").pack(side=tk.LEFT)

    def _show_placeholder(self):
        for w in self.dir_frame.winfo_children():
            w.destroy()
        tk.Label(self.dir_frame,
                 text="Enter a destination and your\ncurrent location above.",
                 font=self.f_small, bg="white", fg="#AAAAAA",
                 justify="left").pack(anchor="w")

    # ── Autocomplete hints ───────────────────

    def _get_suggestions(self, query):
        query = query.lower().strip()
        if not query:
            return []
        results = []
        for node in self.tree.get_all_nodes():
            if node.name.lower().startswith(query):
                results.append(node.name)
        for node in self.tree.get_all_nodes():
            if query in node.name.lower() and node.name not in results:
                results.append(node.name)
        return results[:4]

    def _on_dest_type(self, *args):
        val = self.dest_var.get()
        sugg = self._get_suggestions(val)
        if sugg and val:
            self.dest_hint.config(text="Suggestions: " + ", ".join(sugg))
        else:
            self.dest_hint.config(text="")

    def _on_from_type(self, *args):
        val = self.from_var.get()
        sugg = self._get_suggestions(val)
        if sugg and val:
            self.from_hint.config(text="Suggestions: " + ", ".join(sugg))
        else:
            self.from_hint.config(text="")

    # ── Mouse Interaction ────────────────────

    def _get_building_at(self, mx, my):
        for name, (oval, lbl, px, py) in self.building_items.items():
            if abs(mx - px) < 14 and abs(my - py) < 14:
                return name
        return None

    def _on_mouse_move(self, event):
        name = self._get_building_at(event.x, event.y)
        if name:
            # Highlight
            if self.hovered and self.hovered != name:
                self._unhighlight(self.hovered)
            self.hovered = name
            self._highlight(name)

            # Tooltip
            btype = next((b[2] for b in BUILDINGS if b[1] == name), "")
            self.tooltip.config(text=f"{name}  ·  {TYPE_LABEL.get(btype, btype)}")
            x = self.canvas.winfo_rootx() + event.x + 12
            y = self.canvas.winfo_rooty() + event.y - 28
            self.tooltip.place(x=x - self.root.winfo_rootx(),
                               y=y - self.root.winfo_rooty())
            self.tooltip.lift()
        else:
            if self.hovered:
                self._unhighlight(self.hovered)
                self.hovered = None
            self.tooltip.place_forget()

    def _on_mouse_leave(self, event):
        if self.hovered:
            self._unhighlight(self.hovered)
            self.hovered = None
        self.tooltip.place_forget()

    def _on_canvas_click(self, event):
        name = self._get_building_at(event.x, event.y)
        if name:
            # Fill dest first, then from
            if not self.dest_var.get():
                self.dest_var.set(name)
            elif not self.from_var.get():
                self.from_var.set(name)
            else:
                self.dest_var.set(name)

    def _highlight(self, name):
        if name in self.building_items:
            oval, lbl, px, py = self.building_items[name]
            r = 11
            self.canvas.coords(oval, px - r, py - r, px + r, py + r)
            self.canvas.itemconfig(lbl, font=self.f_bold, fill="#1A1A1A")

    def _unhighlight(self, name):
        if name in self.building_items:
            oval, lbl, px, py = self.building_items[name]
            r = 8
            self.canvas.coords(oval, px - r, py - r, px + r, py + r)
            self.canvas.itemconfig(lbl, font=self.f_small, fill="#444")


# ─────────────────────────────────────────────
#  Run
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("860x640")
    root.minsize(700, 540)
    app = UniNavApp(root)
    root.mainloop()
