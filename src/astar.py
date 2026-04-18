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

    def __lt__(self, other):
        return self.f_score < other.f_score

    def get_neighbors(self, nodes):
        rows = len(nodes)
        cols = len(nodes[0])
        directions = [[1, 0], [1, 1], [0, 1], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
        neighbors = []
        for dx, dy in directions:
            nx = self.x + dx
            ny = self.y + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                neighbors.append(nodes[ny][nx])
        return neighbors


def create_nodes_from_grid(grid):
    rows = len(grid)
    cols = len(grid[0])
    nodes = []
    for y in range(rows):
        row = []
        for x in range(cols):
            is_obstacle = grid[y][x][1]
            node = Node(x, y, is_obstacle)
            row.append(node)
        nodes.append(row)
    return nodes

def distance(node1, node2):
    dx = abs(node1.x - node2.x)
    dy = abs(node1.y - node2.y)
    return 1.414 * min(dx, dy) + abs(dx - dy)

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

def find_nearest_walkable(nodes, target_x, target_y):
    """
    If the target cell is a wall (e.g. a building), find the nearest
    adjacent walkable cell to path towards instead.
    """
    rows = len(nodes)
    cols = len(nodes[0])
    target_node = nodes[target_y][target_x]

    if target_node.type != 'wall':
        return target_node  # Target is already walkable

    # BFS outward from target to find nearest walkable neighbour
    visited = set()
    queue = [(target_x, target_y)]
    visited.add((target_x, target_y))
    directions = [[1, 0], [1, 1], [0, 1], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]

    while queue:
        cx, cy = queue.pop(0)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) not in visited and 0 <= nx < cols and 0 <= ny < rows:
                visited.add((nx, ny))
                candidate = nodes[ny][nx]
                if candidate.type != 'wall':
                    return candidate  # Found nearest walkable cell
                queue.append((nx, ny))

    return None  # No walkable cell found at all

def a_star(grid, start_coords, end_coords):
    nodes = create_nodes_from_grid(grid)
    start_node = nodes[start_coords[1]][start_coords[0]]

    # if end cell is a wall, reroute to nearest walkable neighbour
    end_node = find_nearest_walkable(nodes, end_coords[0], end_coords[1])
    if end_node is None:
        return []

    if start_node == end_node:
        return []

    open_set = []
    in_open_set = set()  # O(1) membership check
    counter = 0
    came_from = {}

    start_node.g_score = 0
    start_node.f_score = h_score(start_node, end_node)
    heapq.heappush(open_set, (start_node.f_score, counter, start_node))
    in_open_set.add((start_node.x, start_node.y))
    closed_set = set()

    while open_set:
        _, _, current = heapq.heappop(open_set)
        in_open_set.discard((current.x, current.y))

        if current == end_node:
            return reconstruct_path(came_from, current)

        closed_set.add(current)

        for neighbor in current.get_neighbors(nodes):
            if neighbor in closed_set or neighbor.type == 'wall':
                continue

            tentative_g_score = current.g_score + distance(current, neighbor)

            if tentative_g_score < neighbor.g_score:
                came_from[(neighbor.x, neighbor.y)] = current
                neighbor.g_score = tentative_g_score
                neighbor.f_score = neighbor.g_score + h_score(neighbor, end_node)

                if (neighbor.x, neighbor.y) not in in_open_set:
                    counter += 1
                    heapq.heappush(open_set, (neighbor.f_score, counter, neighbor))
                    in_open_set.add((neighbor.x, neighbor.y))
                # ✅ Fix Bug 2: if already in open set, re-push with updated score
                else:
                    counter += 1
                    heapq.heappush(open_set, (neighbor.f_score, counter, neighbor))

    return []  # No path found