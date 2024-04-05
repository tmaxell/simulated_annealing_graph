import tkinter as tk
from tkinter import ttk
import networkx as nx
import math
from itertools import permutations
import random
import numpy as np

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Поиск кратчайшего гамильтонова цикла")

        self.graph = nx.Graph()
        self.nodes = []
        self.edges = []
        self.start_node = None

        self.canvas = tk.Canvas(self.root, width=600, height=400)
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.add_node)
        self.canvas.bind("<Button-2>", self.start_edge)

        self.frame = ttk.Frame(self.root)
        self.frame.pack()

        self.find_cycle_button = ttk.Button(self.frame, text="Поиск цикла", command=self.find_cycle)
        self.find_cycle_button.grid(row=0, column=0)

        self.clear_button = ttk.Button(self.frame, text="Очистить полотно", command=self.clear_canvas)
        self.clear_button.grid(row=0, column=1)

        self.table = ttk.Treeview(self.frame, columns=("start", "end", "weight"), show="headings")
        self.table.heading("start", text="Начальная вершина")
        self.table.heading("end", text="Конечная вершина")
        self.table.heading("weight", text="Вес ребра")
        self.table.grid(row=1, column=0, columnspan=2)

        self.node_count = 1

    def add_node(self, event):
        x, y = event.x, event.y
        node = f"({x}, {y})"
        if node not in self.nodes:
            self.graph.add_node(node)
            self.nodes.append(node)
            self.table.insert("", "end", values=(node, "", ""))
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="black")
            self.canvas.create_text(x, y, text=str(self.node_count), fill="white")
            self.node_count += 1

    def start_edge(self, event):
        x, y = event.x, event.y
        closest_node = None
        min_distance = float('inf')
        for node in self.nodes:
            nx, ny = map(int, node.strip("()").split(", "))
            distance = ((x - nx) ** 2 + (y - ny) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_node = node
        if closest_node:
            if self.start_node is None:
                self.start_node = closest_node
            else:
                end_node = closest_node
                weight = min_distance
                if (self.start_node, end_node) not in self.edges and (end_node, self.start_node) not in self.edges:
                    self.graph.add_edge(self.start_node, end_node, weight=weight)
                    self.edges.append((self.start_node, end_node, weight))
                    self.table.insert("", "end", values=(self.start_node, end_node, f"{weight:.2f}"))
                    x1, y1 = map(int, self.start_node.strip("()").split(", "))
                    x2, y2 = map(int, end_node.strip("()").split(", "))
                    self.canvas.create_line(x1, y1, x2, y2, fill="blue")
                self.start_node = None

    def find_cycle(self):
        if len(self.nodes) < 3:
            print("Недостаточно вершин для построения цикла")
            return

        # Имитация отжига
        T_init = 1000  # Начальная температура
        T_min = 0.02  # Минимальная температура
        cooling_rate = 0.999  # Коэффициент охлаждения

        current_solution = self.nodes
        best_solution = self.nodes
        best_cost = self.calculate_cost(best_solution)

        T = T_init
        while T > T_min:
            new_solution = self.get_neighbor(current_solution)
            new_cost = self.calculate_cost(new_solution)

            delta_E = new_cost - best_cost
            if delta_E < 0 or random.random() < np.exp(-delta_E / T):
                current_solution = new_solution
                best_solution = new_solution
                best_cost = new_cost

            T *= cooling_rate

        print("Кратчайший гамильтонов цикл:", best_solution)
        print("Стоимость всего пути:", best_cost)

        self.canvas.delete("cycle")
        for i in range(len(best_solution) - 1):
            x1, y1 = map(int, best_solution[i].strip("()").split(", "))
            x2, y2 = map(int, best_solution[i+1].strip("()").split(", "))
            self.canvas.create_line(x1, y1, x2, y2, fill="red", arrow=tk.LAST, tags="cycle")
        x1, y1 = map(int, best_solution[-1].strip("()").split(", "))
        x2, y2 = map(int, best_solution[0].strip("()").split(", "))
        self.canvas.create_line(x1, y1, x2, y2, fill="red", arrow=tk.LAST, tags="cycle")

        self.table.insert("", "end", values=("Итоговая стоимость пути:", "", f"{best_cost:.2f}"))

    def clear_canvas(self):
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()
        self.canvas.delete("all")
        self.table.delete(*self.table.get_children())
        self.node_count = 1

    def distance(self, node1, node2):
        x1, y1 = map(int, node1.strip("()").split(", "))
        x2, y2 = map(int, node2.strip("()").split(", "))
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def calculate_cost(self, solution):
        total_cost = 0
        for i in range(len(solution) - 1):
            total_cost += self.distance(solution[i], solution[i+1])
        total_cost += self.distance(solution[-1], solution[0])
        return total_cost

    def get_neighbor(self, solution):
        # Swap two random nodes to get a neighbor solution
        neighbor = solution[:]
        index1, index2 = random.sample(range(len(neighbor)), 2)
        neighbor[index1], neighbor[index2] = neighbor[index2], neighbor[index1]
        return neighbor

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
