import math
import heapq

class Node:
    def __init__(self, x, y, is_obstacle):
        self.x = x
        self.y = y
        self.type = 'wall' if is_obstacle else 'road'
        self.g_score = float('inf')
        self.f_score = float('inf')

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __lt__(self, other):  # Implement __lt__ for heapq comparisons
        return self.f_score < other.f_score

    def get_neighbors(self, nodes): # Add nodes as argument
        rows = len(nodes)
        cols = len(nodes[0])
        directions = [[1, 0], [1, 1], [0, 1], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
        neighbors = []
        for dx, dy in directions:
            nx = self.x + dx
            ny = self.y + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                neighbors.append(nodes[ny][nx]) # Use nodes to get neighbors
        return neighbors


def create_nodes_from_grid(grid):
    rows = len(grid)
    cols = len(grid[0])
    nodes = []
    for y in range(rows):
        row = []
        for x in range(cols):
            is_obstacle = grid[y][x][1]  # Check occupancy for obstacle status
            node = Node(x, y, is_obstacle)
            row.append(node)
        nodes.append(row)
    return nodes

# Returns distance between two nodes
def distance(node1, node2):
    dx = abs(node1.x - node2.x)
    dy = abs(node1.y - node2.y)
    return 1.414 * min(dx, dy) + abs(dx - dy)  # Octile distance

# Measures distance from node to endpoint with nodes only being able to travel vertically, horizontally, or diagonally
# def h_score(start, end):
#     x_dist = abs(end.x - start.x)
#     y_dist = abs(end.y - start.y)
#     diagonal_steps = min(x_dist, y_dist)
#     straight_steps = y_dist + x_dist - 2 * diagonal_steps
#     return diagonal_steps * math.sqrt(2) + straight_steps

# Modified h_score function using Manhattan distance
def h_score(start, end):
    return abs(end.x - start.x) + abs(end.y - start.y)

def reconstruct_path(came_from, current):
    path = [current]
    current_key = (current.x, current.y)
    while current_key in came_from:
        current = came_from[current_key]
        current_key = (current.x, current.y)
        path.insert(0, current)
    return path

# Performs the pathfinding algorithm. start are end are (x, y) tuples
# Credit: https://en.wikipedia.org/wiki/A*_search_algorithm
def a_star(grid, start_coords, end_coords):
    nodes = create_nodes_from_grid(grid)
    start_node = nodes[start_coords[1]][start_coords[0]]
    end_node = nodes[end_coords[1]][end_coords[0]]

    open_set = []
    heapq.heappush(open_set, (start_node.f_score, start_node))
    closed_set = set()
    came_from = {}

    start_node.g_score = 0
    start_node.f_score = h_score(start_node, end_node)

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end_node:
            return reconstruct_path(came_from, current)

        closed_set.add(current)

        for neighbor in current.get_neighbors(nodes):
            if neighbor in closed_set or neighbor.type == 'wall':
                continue

            tentative_g_score = current.g_score + distance(current, neighbor)

            if neighbor not in [item[1] for item in open_set]:
                neighbor.g_score = tentative_g_score
                neighbor.f_score = neighbor.g_score + h_score(neighbor, end_node) # Tie-breaker removed
                heapq.heappush(open_set, (neighbor.f_score, neighbor))
            elif tentative_g_score < neighbor.g_score:
                came_from[(neighbor.x, neighbor.y)] = current
                neighbor.g_score = tentative_g_score
                neighbor.f_score = neighbor.g_score + h_score(neighbor, end_node) # Tie-breaker removed


