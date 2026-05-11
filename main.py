import random as rd
import tkinter as tk
from tkinter import ttk, messagebox
import math
import time

# game colors - dungeon theme
GAME_COLORS = {
    'dungeon_floor': '#2b2d42',
    'dungeon_wall': '#1a1a2e',
    'explored': '#3d5a80',
    'path_trail': '#ffd60a',
    'hero': '#06ffa5',
    'monster': '#ff006e',
    'ui_bg': '#0f0f0f',
    'ui_panel': '#1a1a2e',
    'ui_accent': '#ffd60a',
    'text_light': '#ffffff',
    'text_gold': '#ffd60a',
    'health_bar': '#06ffa5',
    'danger': '#ff006e',
    'wall_dark': '#16213e',
    'wall_light': '#2c3e50'
}


class GamePathfindingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚔️ DUNGEON PATHFINDER - Quest for the Dragon's Lair")
        self.root.configure(bg=GAME_COLORS['ui_bg'])

        # grid setup - smaller for screen fit
        self.rows = 30
        self.cols = 49
        self.cell_size = 25

        # initialize arrays
        self.grid = None
        self.initialize_grid()

        # hero and monster positions
        self.hero_pos = None
        self.monster_pos = None

        # colors for each cell
        self.cell_colors = None
        self.initialize_cell_colors()

        # what mode are we in
        self.mode = 'block'
        self.selected_algorithm = tk.StringVar(value='BFS')

        # canvas stuff
        self.canvas_cells = None
        self.canvas_objects = {}
        self.initialize_canvas_cells()

        # game stats
        self.nodes_explored = 0
        self.path_length = 0
        self.algorithm_time = 0
        self.hero_health = 100
        self.coins_collected = 0

        # animation flag
        self.is_animating = False

        # build the UI
        self.create_ui()

    def initialize_grid(self):
        # make a 2D grid full of zeros
        self.grid = []
        for i in range(50):
            row = []
            for j in range(50):
                row.append(0)
            self.grid.append(row)

    def initialize_cell_colors(self):
        # track color for each cell
        self.cell_colors = []
        for i in range(50):
            row = []
            for j in range(50):
                row.append('free')
            self.cell_colors.append(row)

    def initialize_canvas_cells(self):
        # store canvas rectangles
        self.canvas_cells = []
        for i in range(50):
            row = []
            for j in range(50):
                row.append(None)
            self.canvas_cells.append(row)

    def create_ui(self):
        # main window setup
        header = tk.Frame(self.root, bg=GAME_COLORS['ui_panel'], height=80)
        header.pack(fill=tk.X, padx=5, pady=(5, 0))
        header.pack_propagate(False)

        self.create_header(header)

        # container for everything below header
        main_container = tk.Frame(self.root, bg=GAME_COLORS['ui_bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # left side panel
        left_panel = tk.Frame(main_container, bg=GAME_COLORS['ui_panel'], width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)

        # right side for game
        game_area = tk.Frame(main_container, bg=GAME_COLORS['ui_bg'])
        game_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_control_panel(left_panel)
        self.create_game_canvas(game_area)

    def create_header(self, parent):
        # title section
        left_section = tk.Frame(parent, bg=GAME_COLORS['ui_panel'])
        left_section.pack(side=tk.LEFT, padx=20, pady=15)

        title = tk.Label(
            left_section,
            text="⚔️ DUNGEON PATHFINDER",
            font=('Arial', 22, 'bold'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['ui_accent']
        )
        title.pack()

        subtitle = tk.Label(
            left_section,
            text="Quest: Find the shortest path to defeat the Dragon!",
            font=('Arial', 9, 'italic'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['text_light']
        )
        subtitle.pack()

        # stats on the right
        stats_container = tk.Frame(parent, bg=GAME_COLORS['ui_panel'])
        stats_container.pack(side=tk.RIGHT, padx=20, pady=10)

        # health display
        health_frame = tk.Frame(stats_container, bg=GAME_COLORS['ui_panel'])
        health_frame.grid(row=0, column=0, padx=15)

        tk.Label(
            health_frame,
            text="❤️ HERO HP",
            font=('Arial', 8, 'bold'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['health_bar']
        ).pack()

        self.health_label = tk.Label(
            health_frame,
            text="100",
            font=('Arial', 16, 'bold'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['health_bar']
        )
        self.health_label.pack()

        # coins display
        coins_frame = tk.Frame(stats_container, bg=GAME_COLORS['ui_panel'])
        coins_frame.grid(row=0, column=1, padx=15)

        tk.Label(
            coins_frame,
            text="💰 COINS",
            font=('Arial', 8, 'bold'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['text_gold']
        ).pack()

        self.coins_label = tk.Label(
            coins_frame,
            text="0",
            font=('Arial', 16, 'bold'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['text_gold']
        )
        self.coins_label.pack()

        # explored tiles
        quest_frame = tk.Frame(stats_container, bg=GAME_COLORS['ui_panel'])
        quest_frame.grid(row=0, column=2, padx=15)

        tk.Label(
            quest_frame,
            text="🗺️ EXPLORED",
            font=('Arial', 8, 'bold'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['ui_accent']
        ).pack()

        self.explored_label = tk.Label(
            quest_frame,
            text="0",
            font=('Arial', 16, 'bold'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['ui_accent']
        )
        self.explored_label.pack()

    def create_control_panel(self, parent):
        # make panel scrollable
        canvas_panel = tk.Canvas(parent, bg=GAME_COLORS['ui_panel'], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas_panel.yview)
        scrollable_frame = tk.Frame(canvas_panel, bg=GAME_COLORS['ui_panel'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_panel.configure(scrollregion=canvas_panel.bbox("all"))
        )

        canvas_panel.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_panel.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas_panel.pack(side="left", fill="both", expand=True)

        # quest log at top
        quest_log = tk.LabelFrame(
            scrollable_frame,
            text="📜 QUEST LOG",
            font=('Arial', 10, 'bold'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['text_gold'],
            relief=tk.FLAT
        )
        quest_log.pack(fill=tk.X, padx=10, pady=8)

        self.quest_text = tk.Label(
            quest_log,
            text="• Place Hero 🦸\n• Mark Dragon 🐲\n• Build walls\n• Choose strategy\n• Begin quest!",
            font=('Arial', 8),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['text_light'],
            justify=tk.LEFT,
            wraplength=220
        )
        self.quest_text.pack(padx=8, pady=8)

        # separator line
        divider = tk.Frame(scrollable_frame, bg=GAME_COLORS['text_gold'], height=1)
        divider.pack(fill=tk.X, padx=10, pady=5)

        # map tools section
        map_tools = tk.LabelFrame(
            scrollable_frame,
            text="🗺️ MAP BUILDER",
            font=('Arial', 10, 'bold'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['text_gold']
        )
        map_tools.pack(fill=tk.X, padx=10, pady=5)

        # grid size controls
        size_frame = tk.Frame(map_tools, bg=GAME_COLORS['ui_panel'])
        size_frame.pack(padx=10, pady=8)

        tk.Label(
            size_frame,
            text="Rows:",
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['text_light'],
            font=('Arial', 9)
        ).grid(row=0, column=0, sticky='w', padx=5)

        self.rows_spinbox = tk.Spinbox(
            size_frame,
            from_=10,
            to=50,
            width=6,
            font=('Arial', 9),
            bg=GAME_COLORS['wall_dark'],
            fg=GAME_COLORS['text_light'],
            relief=tk.FLAT
        )
        self.rows_spinbox.delete(0, tk.END)
        self.rows_spinbox.insert(0, str(self.rows))
        self.rows_spinbox.grid(row=0, column=1, padx=5)

        tk.Label(
            size_frame,
            text="Cols:",
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['text_light'],
            font=('Arial', 9)
        ).grid(row=1, column=0, sticky='w', padx=5, pady=3)

        self.cols_spinbox = tk.Spinbox(
            size_frame,
            from_=10,
            to=50,
            width=6,
            font=('Arial', 9),
            bg=GAME_COLORS['wall_dark'],
            fg=GAME_COLORS['text_light'],
            relief=tk.FLAT
        )
        self.cols_spinbox.delete(0, tk.END)
        self.cols_spinbox.insert(0, str(self.cols))
        self.cols_spinbox.grid(row=1, column=1, padx=5, pady=3)

        # apply button
        apply_btn = tk.Button(
            map_tools,
            text="⚙️ RESIZE",
            command=self.update_grid_size,
            bg=GAME_COLORS['wall_dark'],
            fg=GAME_COLORS['text_light'],
            font=('Arial', 8, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            pady=4
        )
        apply_btn.pack(fill=tk.X, padx=10, pady=(0, 8))
        self.bind_game_hover(apply_btn)

        # mode buttons
        mode_frame = tk.Frame(map_tools, bg=GAME_COLORS['ui_panel'])
        mode_frame.pack(fill=tk.X, padx=10, pady=(0, 8))

        modes = [
            ('🧱 Wall', 'block'),
            ('🦸 Hero', 'start'),
            ('🐲 Dragon', 'goal')
        ]

        for text, mode in modes:
            btn = tk.Button(
                mode_frame,
                text=text,
                command=lambda m=mode: self.set_mode(m),
                bg=GAME_COLORS['wall_dark'],
                fg=GAME_COLORS['text_light'],
                font=('Arial', 8, 'bold'),
                relief=tk.FLAT,
                cursor='hand2',
                pady=4
            )
            btn.pack(fill=tk.X, pady=2)
            self.bind_game_hover(btn)

        divider = tk.Frame(scrollable_frame, bg=GAME_COLORS['text_gold'], height=1)
        divider.pack(fill=tk.X, padx=10, pady=5)

        # algorithm selection
        strategy_frame = tk.LabelFrame(
            scrollable_frame,
            text="⚔️ STRATEGY",
            font=('Arial', 10, 'bold'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['text_gold']
        )
        strategy_frame.pack(fill=tk.X, padx=10, pady=5)

        algorithms = [
            ('🔍 Breadth First (BFS)', 'BFS'),
            ('🌲 Depth First (DFS)', 'DFS'),
            ('💰 Uniform Cost (UCS)', 'UCS'),
            ('🎯 A* Manhattan', 'A_MANHATTAN'),
            ('📐 A* Euclidean', 'A_EUCLIDEAN')
        ]

        for text, value in algorithms:
            rb = tk.Radiobutton(
                strategy_frame,
                text=text,
                variable=self.selected_algorithm,
                value=value,
                bg=GAME_COLORS['ui_panel'],
                fg=GAME_COLORS['text_light'],
                selectcolor=GAME_COLORS['wall_dark'],
                activebackground=GAME_COLORS['ui_panel'],
                activeforeground=GAME_COLORS['ui_accent'],
                font=('Arial', 8),
                cursor='hand2'
            )
            rb.pack(anchor='w', padx=10, pady=2)

        divider = tk.Frame(scrollable_frame, bg=GAME_COLORS['text_gold'], height=1)
        divider.pack(fill=tk.X, padx=10, pady=5)

        # action buttons
        actions = tk.Frame(scrollable_frame, bg=GAME_COLORS['ui_panel'])
        actions.pack(fill=tk.X, padx=10, pady=5)

        self.start_btn = tk.Button(
            actions,
            text="⚔️ BEGIN QUEST!",
            command=self.run_algorithm,
            bg=GAME_COLORS['health_bar'],
            fg='#000000',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            pady=8
        )
        self.start_btn.pack(fill=tk.X, pady=2)

        clear_btn = tk.Button(
            actions,
            text="🔄 Clear Path",
            command=self.clear_path,
            bg=GAME_COLORS['wall_dark'],
            fg=GAME_COLORS['text_light'],
            font=('Arial', 8, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            pady=5
        )
        clear_btn.pack(fill=tk.X, pady=2)
        self.bind_game_hover(clear_btn)

        # reset game button - clears entire grid
        reset_game_btn = tk.Button(
            actions,
            text="🎮 Reset Grid",
            command=self.reset_game,
            bg=GAME_COLORS['danger'],
            fg='#000000',
            font=('Arial', 8, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            pady=5
        )
        reset_game_btn.pack(fill=tk.X, pady=2)

        # pattern generators
        patterns = tk.Frame(scrollable_frame, bg=GAME_COLORS['ui_panel'])
        patterns.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            patterns,
            text="🎲 AUTO-GEN",
            font=('Arial', 8, 'bold'),
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['text_light']
        ).pack(pady=(0, 3))

        pattern_btns = tk.Frame(patterns, bg=GAME_COLORS['ui_panel'])
        pattern_btns.pack()

        maze_btn = tk.Button(
            pattern_btns,
            text="🏰 Maze",
            command=self.generate_maze,
            bg=GAME_COLORS['wall_dark'],
            fg=GAME_COLORS['text_light'],
            font=('Arial', 7, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=12,
            pady=4
        )
        maze_btn.pack(side=tk.LEFT, padx=2)
        self.bind_game_hover(maze_btn)

        random_btn = tk.Button(
            pattern_btns,
            text="🎲 Random",
            command=self.generate_random,
            bg=GAME_COLORS['wall_dark'],
            fg=GAME_COLORS['text_light'],
            font=('Arial', 7, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=12,
            pady=4
        )
        random_btn.pack(side=tk.LEFT, padx=2)
        self.bind_game_hover(random_btn)

        # status text
        self.status_label = tk.Label(
            scrollable_frame,
            text="⚡ Ready for adventure!",
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['ui_accent'],
            font=('Arial', 8, 'italic'),
            wraplength=230,
            justify=tk.CENTER
        )
        self.status_label.pack(pady=8)

        # cost display
        self.cost_label = tk.Label(
            scrollable_frame,
            text="💎 Quest Cost: -",
            bg=GAME_COLORS['ui_panel'],
            fg=GAME_COLORS['text_gold'],
            font=('Arial', 9, 'bold')
        )
        self.cost_label.pack(pady=5)

    def create_game_canvas(self, parent):
        # canvas container
        canvas_frame = tk.Frame(parent, bg=GAME_COLORS['dungeon_wall'], relief=tk.RIDGE, bd=3)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg=GAME_COLORS['dungeon_floor'],
            highlightthickness=0
        )

        # scrollbars
        h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # mouse events
        self.canvas.bind('<Button-1>', self.canvas_click)
        self.canvas.bind('<B1-Motion>', self.canvas_drag)

        self.draw_grid()

    def draw_grid(self):
        # clear everything first
        self.canvas.delete('all')

        # set scroll region
        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size
        self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))

        # draw each cell
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # default color
                color = GAME_COLORS['dungeon_floor']

                # check cell state
                if self.cell_colors[i][j] == 'blocked':
                    color = GAME_COLORS['dungeon_wall']
                elif self.cell_colors[i][j] == 'visited':
                    color = GAME_COLORS['explored']
                elif self.cell_colors[i][j] == 'path':
                    color = GAME_COLORS['path_trail']

                # create rectangle
                cell = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=GAME_COLORS['wall_dark'],
                    width=1
                )
                self.canvas_cells[i][j] = cell

                # draw wall sprite if blocked
                if self.cell_colors[i][j] == 'blocked':
                    self.draw_wall(i, j)
                # draw hero or monster if needed
                elif self.hero_pos and self.hero_pos[0] == i and self.hero_pos[1] == j:
                    self.draw_hero(i, j)
                elif self.monster_pos and self.monster_pos[0] == i and self.monster_pos[1] == j:
                    self.draw_monster(i, j)

    def draw_wall(self, row, col):
        # draw brick wall emoji
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2

        self.canvas.create_text(
            x, y,
            text="🧱",
            font=('Arial', int(self.cell_size * 0.7)),
            tags='wall'
        )

    def draw_hero(self, row, col):
        # calculate center position
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        size = self.cell_size // 3

        # draw circle behind
        self.canvas.create_oval(
            x - size, y - size, x + size, y + size,
            fill=GAME_COLORS['hero'],
            outline='#ffffff',
            width=2,
            tags='hero'
        )

        # draw emoji
        self.canvas.create_text(
            x, y,
            text="🦸",
            font=('Arial', int(self.cell_size * 0.6)),
            tags='hero'
        )

    def draw_monster(self, row, col):
        # calculate position
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        size = self.cell_size // 3

        # circle background
        self.canvas.create_oval(
            x - size, y - size, x + size, y + size,
            fill=GAME_COLORS['monster'],
            outline='#ffffff',
            width=2,
            tags='monster'
        )

        # dragon emoji
        self.canvas.create_text(
            x, y,
            text="🐲",
            font=('Arial', int(self.cell_size * 0.6)),
            tags='monster'
        )

    def canvas_click(self, event):
        # get grid coordinates from click
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        col = int(canvas_x // self.cell_size)
        row = int(canvas_y // self.cell_size)

        # make sure in bounds
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.handle_cell_click(row, col)

    def canvas_drag(self, event):
        # only for wall mode
        if self.mode == 'block':
            self.canvas_click(event)

    def handle_cell_click(self, row, col):
        # handle different modes
        if self.mode == 'block':
            # toggle wall
            if self.grid[row][col] == 0:
                self.grid[row][col] = 1
                self.cell_colors[row][col] = 'blocked'
            else:
                self.grid[row][col] = 0
                self.cell_colors[row][col] = 'free'
                # remove wall sprite by redrawing cell
                self.canvas.delete('wall')
            self.update_cell(row, col)
            # redraw grid to update all walls properly
            self.draw_grid()

        elif self.mode == 'start':
            # place hero
            if self.hero_pos:
                # remove old hero
                old_row, old_col = self.hero_pos
                self.hero_pos = None
                self.grid[old_row][old_col] = 0
                self.cell_colors[old_row][old_col] = 'free'
                self.update_cell(old_row, old_col)
            # set new position
            self.hero_pos = (row, col)
            self.grid[row][col] = 0
            self.cell_colors[row][col] = 'free'
            self.canvas.delete('hero')
            self.update_cell(row, col)
            self.draw_hero(row, col)
            self.status_label.configure(text=f"🦸 Hero placed at ({row}, {col})")

        elif self.mode == 'goal':
            # place dragon
            if self.monster_pos:
                # remove old dragon
                old_row, old_col = self.monster_pos
                self.monster_pos = None
                self.grid[old_row][old_col] = 0
                self.cell_colors[old_row][old_col] = 'free'
                self.update_cell(old_row, old_col)
            # set new dragon
            self.monster_pos = (row, col)
            self.grid[row][col] = 0
            self.cell_colors[row][col] = 'free'
            self.canvas.delete('monster')
            self.update_cell(row, col)
            self.draw_monster(row, col)
            self.status_label.configure(text=f"🐲 Dragon at ({row}, {col})")

    def update_cell(self, row, col):
        # update single cell color
        color = GAME_COLORS['dungeon_floor']

        if self.cell_colors[row][col] == 'blocked':
            color = GAME_COLORS['dungeon_wall']
        elif self.cell_colors[row][col] == 'visited':
            color = GAME_COLORS['explored']
        elif self.cell_colors[row][col] == 'path':
            color = GAME_COLORS['path_trail']

        if self.canvas_cells[row][col]:
            self.canvas.itemconfig(self.canvas_cells[row][col], fill=color)

        # redraw wall sprite if blocked
        if self.cell_colors[row][col] == 'blocked':
            self.draw_wall(row, col)

    def set_mode(self, mode):
        # change edit mode
        self.mode = mode
        mode_names = {
            'block': '🧱 Building walls...',
            'start': '🦸 Place your hero',
            'goal': '🐲 Mark the dragon'
        }
        self.status_label.configure(text=mode_names[mode])

    def update_grid_size(self):
        # resize grid
        try:
            new_rows = int(self.rows_spinbox.get())
            new_cols = int(self.cols_spinbox.get())

            if 10 <= new_rows <= 50 and 10 <= new_cols <= 50:
                self.rows = new_rows
                self.cols = new_cols
                self.draw_grid()
                self.status_label.configure(text=f"🗺️ Map: {new_rows}×{new_cols}")
            else:
                messagebox.showerror("Invalid Size", "Map size: 10×10 to 50×50")
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter valid numbers")

    def clear_path(self):
        # only clear visited and path cells
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cell_colors[i][j] in ['visited', 'path']:
                    self.cell_colors[i][j] = 'free'
                    self.update_cell(i, j)

        # redraw hero
        self.canvas.delete('hero')
        self.canvas.delete('coin')
        if self.hero_pos:
            self.draw_hero(self.hero_pos[0], self.hero_pos[1])

        self.status_label.configure(text="🔄 Path cleared")
        self.cost_label.configure(text="💎 Quest Cost: -")
        self.explored_label.configure(text="0")

    def reset_game(self):
        # clear entire grid including walls
        for i in range(self.rows):
            for j in range(self.cols):
                self.grid[i][j] = 0
                self.cell_colors[i][j] = 'free'
                self.update_cell(i, j)

        # remove hero and dragon
        self.canvas.delete('hero')
        self.canvas.delete('monster')
        self.canvas.delete('coin')
        self.hero_pos = None
        self.monster_pos = None

        # reset stats
        self.hero_health = 100
        self.coins_collected = 0
        self.health_label.configure(text="100")
        self.coins_label.configure(text="0")
        self.explored_label.configure(text="0")
        self.cost_label.configure(text="💎 Quest Cost: -")

        self.status_label.configure(text="🎮 Game reset! Ready to start new quest")

    def reset_grid(self):
        # clear everything
        for i in range(50):
            for j in range(50):
                self.grid[i][j] = 0
                self.cell_colors[i][j] = 'free'

        self.hero_pos = None
        self.monster_pos = None
        self.hero_health = 100
        self.coins_collected = 0

        self.health_label.configure(text="100")
        self.coins_label.configure(text="0")
        self.explored_label.configure(text="0")

        self.draw_grid()
        self.status_label.configure(text="🗑️ Dungeon reset")

    def generate_maze(self):
        # clear first
        self.reset_grid()

        # create maze pattern
        for i in range(self.rows):
            for j in range(self.cols):
                if i % 2 == 1 and j % 2 == 1:
                    continue
                if rd.random() < 0.35:
                    self.grid[i][j] = 1
                    self.cell_colors[i][j] = 'blocked'
                    self.update_cell(i, j)

        self.status_label.configure(text="🏰 Dungeon maze generated!")
        self.root.update()

    def generate_random(self):
        # clear first
        self.reset_grid()

        # random walls
        for i in range(self.rows):
            for j in range(self.cols):
                if rd.random() < 0.28:
                    self.grid[i][j] = 1
                    self.cell_colors[i][j] = 'blocked'
                    self.update_cell(i, j)

        self.status_label.configure(text="🎲 Random dungeon created!")
        self.root.update()

    def bind_game_hover(self, button):
        # hover effects for buttons
        def on_enter(e):
            button['bg'] = GAME_COLORS['ui_accent']
            button['fg'] = '#000000'

        def on_leave(e):
            current_text = button.cget('text')
            if '⚔️' in current_text:
                button['bg'] = GAME_COLORS['health_bar']
            elif '🗑️' in current_text or '🎮' in current_text:
                button['bg'] = GAME_COLORS['danger']
            else:
                button['bg'] = GAME_COLORS['wall_dark']
                button['fg'] = GAME_COLORS['text_light']

        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)

    def animate_hero_movement(self, path, algorithm_cost=None):
        # check if path exists
        if not path or len(path) == 0:
            return

        self.is_animating = True
        self.canvas.delete('hero')
        self.canvas.delete('coin')

        coins = 0

        # move hero step by step
        for idx in range(len(path)):
            if not self.is_animating:
                break

            row, col = path[idx]

            # redraw hero at new position
            self.canvas.delete('hero')
            self.draw_hero(row, col)

            # add coin if not start or goal
            if (row, col) != self.hero_pos and (row, col) != self.monster_pos:
                x = col * self.cell_size + self.cell_size // 2
                y = row * self.cell_size + self.cell_size // 2

                self.canvas.create_text(
                    x, y,
                    text="💰",
                    font=('Arial', int(self.cell_size * 0.4)),
                    fill=GAME_COLORS['text_gold'],
                    tags='coin'
                )

                coins += 1
                self.coins_collected = coins
                self.coins_label.configure(text=str(coins))

            self.root.update()
            time.sleep(0.1)  # animation delay

        self.is_animating = False

        # quest complete
        self.status_label.configure(text="🏆 QUEST COMPLETE!")

        # show result
        if algorithm_cost is not None:
            messagebox.showinfo("Victory!",
                                f"🎉 Hero defeated the Dragon!\n💰 Coins collected: {coins}\n💎 Path Cost: {algorithm_cost}$")
        else:
            messagebox.showinfo("Victory!", f"🎉 Hero defeated the Dragon!\n💰 Coins collected: {coins}")

    def run_algorithm(self):
        # check if hero and dragon are placed
        if not self.hero_pos:
            messagebox.showwarning("Missing Hero", "Place the hero first! 🦸")
            return
        if not self.monster_pos:
            messagebox.showwarning("Missing Dragon", "Mark the dragon location! 🐲")
            return

        # clear old path
        self.clear_path()

        algo = self.selected_algorithm.get()

        self.status_label.configure(text=f"⚔️ {algo} in progress...")
        self.root.update()

        start_time = time.time()

        # run selected algorithm
        if algo == "BFS":
            result = self.bfs()
            if result:
                path, cost = result
                self.animate_hero_movement(path)
        elif algo == "DFS":
            result = self.dfs()
            if result:
                path, cost = result
                self.animate_hero_movement(path)
        elif algo == "UCS":
            result = self.ucs()
            if result:
                path, cost = result
                self.animate_hero_movement(path, algorithm_cost=cost)
        elif algo == "A_MANHATTAN":
            result = self.astar(heuristic_type="manhattan")
            if result:
                path, cost = result
                self.animate_hero_movement(path, algorithm_cost=cost)
        elif algo == "A_EUCLIDEAN":
            result = self.astar(heuristic_type="euclidean")
            if result:
                path, cost = result
                self.animate_hero_movement(path, algorithm_cost=cost)



    #ALGOS IMPLEMENTATIONS

    #BFS ALGORITHM

    def bfs(self):
        rows = self.rows
        cols = self.cols
        start =  self.hero_pos
        goal = self.monster_pos
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        parent = [[(-1, -1) for _ in range(cols)] for _ in range(rows)]
        queuecap = rows * cols
        queue = [None for _ in range(queuecap)]
        front = 0
        rear = 0
        #add the first entry to the queue and move the rear
        y, x = start
        queue[rear] = (y, x)
        rear += 1
        visited[y][x] = True
        #array to define the directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        done = False
        numnodes = 0
        #the main loop will run till the queue isnt empty
        while front != rear:
            y, x = queue[front]
            front += 1
            numnodes += 1
            #if goal is found, the algo should stop
            if (y, x) == goal:
                done = True
                break
            #traverse through all the neighbours
            for dy, dx in directions:
                ny = y + dy
                nx= x + dx
                if 0 <= ny < rows and 0 <= nx < cols:
                    #only valid neighbours are added
                    if self.grid[ny][nx] == 0 and not visited[ny][nx]:
                        visited[ny][nx] = True
                        queue[rear] = (ny, nx)
                        rear += 1
                        #to be able to backtract to where we came from the parent is added to the list
                        parent[ny][nx] = (y, x)
                        #visualize side by side
                        if (ny, nx) != start and (ny, nx) != goal:
                            self.visualize_visited(ny, nx)
        #incase there wsa no path found before the loop ended
        if done == False:
            self.clear_path()
            self.status_label.configure(text="No path to dragon!")
            self.explored_label.configure(text=str(numnodes))
            messagebox.showinfo("No Path", "Dragon is unreachable!")
            return None

        #to make the final path
        maxcap = rows * cols
        path = [None for _ in range(maxcap)]
        legth = 0
        current = goal
        while current != start:
            path[legth] = current
            legth += 1
            current = parent[current[0]][current[1]]
        path[legth] = start
        legth += 1
        #now it will start from the start to construct the full path
        reversed = [None for _ in range(legth)]
        i = 0
        while i < legth:
            reversed[i] = path[legth - 1 - i]
            i += 1
        self.explored_label.configure(text=str(numnodes))
        self.root.update()
        return ([reversed[i] for i in range(legth) if reversed[i] is not None], None)

#DFS ALGORITM

    def dfs(self):
        rows = self.rows
        cols = self.cols
        start_pos = self.hero_pos
        goal_pos = self.monster_pos
        grid = self.grid
        # the listed to mark visited and the parents are initialized
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        parent = [[(-1, -1) for _ in range(cols)] for _ in range(rows)]
        # stack manually implemented
        stackcap = rows * cols
        stack = [None for _ in range(stackcap)]
        top = -1
        # push the starting coords onto the stack
        y, x = start_pos
        top += 1
        stack[top] = (y, x)
        visited[y][x] = True
        done = False
        # to devide the direction of movement
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        numnodes = 0

        # main loop will run till the stack isnt empty
        while top != -1:
            y, x = stack[top]
            top -= 1
            numnodes += 1
            if (y, x) == goal_pos:
                done = True
                break
            # loop through all the directions
            temp = 0
            while temp < 4:
                dy, dx = directions[temp]
                new_y = y + dy
                new_x = x + dx
                if 0 <= new_y < rows and 0 <= new_x < cols:
                    if grid[new_y][new_x] == 0 and not visited[new_y][new_x]:
                        visited[new_y][new_x] = True
                        parent[new_y][new_x] = (y, x)
                        top += 1
                        stack[top] = (new_y, new_x)

                        if (new_y, new_x) != start_pos and (new_y, new_x) != goal_pos:
                            self.visualize_visited(new_y, new_x)
                temp += 1

        if done == False:
            self.clear_path()
            self.status_label.configure(text="No path to dragon found")
            self.explored_label.configure(text=str(numnodes))
            messagebox.showinfo("No Path", "Dragon is unreachable!")
            return None
        # then i will make the path
        maxcap = rows * cols
        path = [None for _ in range(maxcap)]
        legth = 0
        current = goal_pos
        while current != start_pos:
            path[legth] = current
            legth += 1
            current = parent[current[0]][current[1]]

        path[legth] = start_pos
        legth += 1
        # then reveerse it to start from the starting coordinate
        reversed = [None for _ in range(legth)]
        i = 0
        while i < legth:
            reversed[i] = path[legth - 1 - i]
            i += 1
        self.explored_label.configure(text=str(numnodes))
        self.root.update()
        # this funtion will return the reversed path starting from start
        return ([reversed[i] for i in range(legth) if reversed[i] is not None], None)

#UCS ALGORITHM
    def ucs(self):
        rows = self.rows
        cols = self.cols
        start = self.hero_pos
        goal = self.monster_pos
        # initial data structures initialized
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        parent = [[(-1, -1) for _ in range(cols)] for _ in range(rows)]
        grid_cost = [[0 for _ in range(cols)] for _ in range(rows)]
        cost_so_far = [[float('inf') for _ in range(cols)] for _ in range(rows)]
        # the cost is defined randomly from 1 to 10
        for i in range(rows):
            for j in range(cols):
                if self.grid[i][j] == 0:
                    grid_cost[i][j] = rd.randint(1, 10)
                else:
                    grid_cost[i][j] = 0
        # manually created priority queue
        totalcap = rows * cols
        pqueue = [None for _ in range(totalcap)]
        # in the start the front and rear are both 0
        front = 0
        rear = 0
        y, x = start
        pqueue[rear] = (y, x, 0)
        rear += 1
        cost_so_far[y][x] = 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        done = False
        numnodes = 0
        while front != rear:
            # first i need to find the node with the minimum most cost to extract it
            minind = front
            mincost = None
            i = front
            while i < rear:
                if pqueue[i] is not None:  # check only if there is an entry in the queue
                    if mincost is None or pqueue[i][2] < mincost:
                        mincost = pqueue[i][2]
                        minind = i
                i += 1
            if mincost is None:
                break
            # then extract the minimum one from the queue
            y, x, cumulcost = pqueue[minind]
            pqueue[minind] = pqueue[rear - 1]
            pqueue[rear - 1] = None
            rear -= 1
            if visited[y][x]:
                continue
            visited[y][x] = True
            numnodes += 1
            # then visualize the path alongside to show the user
            if (y, x) != start and (y, x) != goal:
                self.visualize_visited(y, x)
            if (y, x) == goal:
                done = True
                break
                # then travese through neighbours to add the valid ones to the queue
            for dy, dx in directions:
                ny = y + dy
                nx = x + dx
                if 0 <= ny < rows and 0 <= nx < cols:
                    if self.grid[ny][nx] == 0:
                        ncost = cumulcost + grid_cost[ny][nx]
                        if ncost < cost_so_far[ny][nx]:
                            cost_so_far[ny][nx] = ncost
                            parent[ny][nx] = (y, x)
                            pqueue[rear] = (ny, nx, ncost)
                            rear += 1
        if done:
            # calculaye the price and the path
            maxcap = rows * cols
            path = [None for _ in range(maxcap)]
            legth = 0
            current = goal
            totalcost = 0
            while current != start:
                path[legth] = current
                legth += 1
                cy, cx = current
                totalcost += grid_cost[cy][cx]
                current = parent[cy][cx]
            path[legth] = start
            legth += 1
            reversed_path = [None for _ in range(legth)]
            i = 0
            while i < legth:
                reversed_path[i] = path[legth - 1 - i]
                i += 1
            self.explored_label.configure(text=str(numnodes))
            self.cost_label.configure(text=f"Quest Cost: {totalcost}$")
            self.root.update()
            return ([reversed_path[i] for i in range(legth) if reversed_path[i] is not None], totalcost)
        else:
            self.clear_path()
            self.explored_label.configure(text=str(numnodes))
            self.status_label.configure(text="No path to dragon!")
            messagebox.showinfo("UCS", "Dragon is unreachable!")
            return None

#A* ALGORITHM
    def astar(self, heuristic_type="manhattan"):
        rows = self.rows
        cols = self.cols
        start = self.hero_pos
        goal = self.monster_pos
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        parent = [[(-1, -1) for _ in range(cols)] for _ in range(rows)]
        g_cost = [[float('inf') for _ in range(cols)] for _ in range(rows)]
        closed = [[False for _ in range(cols)] for _ in range(rows)]
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        #then make a list to define the open (not visited ones)
        opencap = rows * cols
        openlist = [None for _ in range(opencap)]
        front = 0
        rear = 0
        sy, sx = start
        gy, gx = goal
        g_cost[sy][sx] = 0
        #calculation of h
        if heuristic_type == "manhattan":
            h = abs(sy - gy) + abs(sx - gx)
            #for eculedian:
        else:
            h = ((sy - gy) ** 2 + (sx - gx) ** 2) ** 0.5
        f = g_cost[sy][sx] + h
        openlist[rear] = (sy, sx, g_cost[sy][sx], h, f)
        rear += 1
        visited[sy][sx] = True
        done = False
        numnodes = 0
        #running the main loop
        while front != rear:
            #finidng the minimum f and extracting it
            minind = front
            minf = None
            ming = None
            i = front
            while i < rear:
                if openlist[i] is not None:
                    if minf is None or \
                       openlist[i][4] < minf or \
                       (openlist[i][4] == minf and openlist[i][2] < ming):  #tiebreaker using smaller g done
                        minf = openlist[i][4]
                        ming = openlist[i][2]
                        minind = i
                i += 1
            #incase there is no minf meaning the algo ended hence break
            if minf is None:
                break
            y, x, g, h, f = openlist[minind]
            openlist[minind] = openlist[rear - 1]
            openlist[rear - 1] = None
            rear -= 1
            closed[y][x] = True
            numnodes += 1
            if (y, x) != start and (y, x) != goal:
                self.visualize_visited(y, x)
            if (y, x) == goal:
                done = True
                break
                #then traverse and find valid neighbours
            for dy, dx in directions:
                ny = y + dy
                nx = x + dx
                if 0 <= ny < rows and 0 <= nx < cols:
                    if self.grid[ny][nx] == 0:
                        if closed[ny][nx]:
                            continue
                        new_g = g + 1
                        #calculation by adding the heuristic
                        if heuristic_type == "manhattan":
                            new_h = abs(ny - gy) + abs(nx - gx)
                        else:
                            new_h = ((ny - gy) ** 2 + (nx - gx) ** 2) ** 0.5
                        new_f = new_g + new_h
                        if not visited[ny][nx] or new_g < g_cost[ny][nx]:
                            visited[ny][nx] = True
                            g_cost[ny][nx] = new_g
                            parent[ny][nx] = (y, x)
                            openlist[rear] = (ny, nx, new_g, new_h, new_f)
                            rear += 1
        if not done:
            self.clear_path()
            self.explored_label.configure(text=str(numnodes))
            self.status_label.configure(text="No path to dragon!")
            messagebox.showinfo("A*", "Dragon is unreachable!")
            return None
        #then make the path again
        maxcap = rows * cols
        path = [None for _ in range(maxcap)]
        legth = 0
        totalcost = 0
        current = goal
        while current != start:
            path[legth] = current
            cy, cx = current
            totalcost += 1
            legth += 1
            current = parent[cy][cx]
        path[legth] = start
        legth += 1
        reversed = [None for _ in range(legth)]
        i = 0
        while i < legth:
            reversed[i] = path[legth - 1 - i]
            i += 1
        self.explored_label.configure(text=str(numnodes))
        self.root.update()
        return ([reversed[i] for i in range(legth) if reversed[i] is not None], totalcost)

    #to visualize the path
    def visualize_visited(self, row, col):
        if self.cell_colors[row][col] not in ['blocked', 'start', 'goal']:
            self.cell_colors[row][col] = 'visited'
            self.update_cell(row, col)
            self.root.update()


def main():
    root = tk.Tk()
    window_width = 1400
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    app = GamePathfindingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
