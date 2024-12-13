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

    def get_neighbors(self, grid):
        rows = len(grid)
        cols = len(grid[0])
        directions = [[1, 0], [1, 1], [0, 1], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
        neighbors = []
        for direction in directions:
            neighbor_x = self.x + direction[0]
            neighbor_y = self.y + direction[1]
            if 0 <= neighbor_x < cols and 0 <= neighbor_y < rows:
                neighbors.append(Node(neighbor_x, neighbor_y, grid[neighbor_y][neighbor_x][1]))
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

def distance(node1, node2):
    return math.sqrt(math.pow(node1.x - node2.x, 2) + math.pow(node1.y - node2.y, 2))

def h_score(start, end):
    dx = abs(end.x - start.x)
    dy = abs(end.y - start.y)
    return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)

def reconstruct_path(grid, came_from, current):
    path = [current]
    current_key = str(current.x) + ' ' + str(current.y)
    while current_key in came_from:
        current = came_from[current_key]
        current_key = str(current.x) + ' ' + str(current.y)
        path.insert(0, current)
    return path

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
            return reconstruct_path(nodes, came_from, current)

        if current in closed_set:
            continue

        closed_set.add(current)

        for neighbor in current.get_neighbors(grid):
            if neighbor in closed_set or neighbor.type == 'wall':
                continue

            tentative_g_score = current.g_score + (distance(current, neighbor) if neighbor.type == 'road' else float('inf'))

            if neighbor not in [item[1] for item in open_set]:
                neighbor.f_score = tentative_g_score + h_score(neighbor, end_node)
                heapq.heappush(open_set, (neighbor.f_score, neighbor))
            elif tentative_g_score < neighbor.g_score:
                neighbor.g_score = tentative_g_score
                neighbor.f_score = tentative_g_score + h_score(neighbor, end_node)
                # Updating within the heap is not handled efficiently by heapq.  A more sophisticated heap
                # implementation (like a Fibonacci heap) would be needed for optimal performance in large grids.

    return None # No path found

