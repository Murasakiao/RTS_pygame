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

# g score, estimated distance

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
    return math.sqrt(math.pow(node1.x - node2.x, 2) + math.pow(node1.y - node2.y, 2))

def h_score(start, end):
    dx = abs(end.x - start.x)
    dy = abs(end.y - start.y)
    return dx + dy + (math.sqrt(2) - 2) * min(dx, dy) + (start.x + start.y) * 0.001

def reconstruct_path(grid, came_from, current):
    path = [current]
    current_key = str(current.x) + ' ' + str(current.y)
    while current_key in came_from:
        current = came_from[current_key]
        current_key = str(current.x) + ' ' + str(current.y)
        path.insert(0, current)
    return path

# Performs the pathfinding algorithm. start are end are (x, y) tuples
# Credit: https://en.wikipedia.org/wiki/A*_search_algorithm
def a_star(grid, start_coords, end_coords):
    nodes = create_nodes_from_grid(grid)
    start_node = nodes[start_coords[1]][start_coords[0]]
    end_node = nodes[end_coords[1]][end_coords[0]]

    open_set = []
    heapq.heappush(open_set, (start_node.f_score, start_node)) # Use heapq
    closed_set = set() # Use a set
    came_from = {}

    start_node.g_score = 0
    start_node.f_score = h_score(start_node, end_node)

    print(f"Start Node: ({start_node.x}, {start_node.y}), End Node: ({end_node.x}, {end_node.y})")

    while open_set:
        print(f"Open Set: {[f'({item[1].x}, {item[1].y}, f={item[0]:.2f})' for item in open_set]}")
        _, current = heapq.heappop(open_set) # Get node with lowest f_score
        print(f"Current Node: ({current.x}, {current.y}), g_score: {current.g_score:.2f}, f_score: {current.f_score:.2f}")

        if current == end_node:
            print("Goal Reached!")
            return reconstruct_path(nodes, came_from, current)

        if current in closed_set: # Check after popping
            print(f"Node ({current.x}, {current.y}) already in closed set, skipping.")
            continue

        closed_set.add(current)
        print(f"Closed Set: {[f'({node.x}, {node.y})' for node in closed_set]}")

        for neighbor in current.get_neighbors(grid): # Pass grid to get_neighbors
            if neighbor in closed_set or neighbor.type == 'wall':
                print(f"Neighbor ({neighbor.x}, {neighbor.y}) is a wall or in closed set, skipping.")
                continue

            tentative_g_score = current.g_score + distance(current, neighbor)
            print(f"  Neighbor ({neighbor.x}, {neighbor.y}), tentative_g_score: {tentative_g_score:.2f}")

            if neighbor not in [item[1] for item in open_set]:  # Correctly access the node
                neighbor.f_score = tentative_g_score + h_score(neighbor, end_node)
                heapq.heappush(open_set, (neighbor.f_score, neighbor))
                print(f"    Neighbor ({neighbor.x}, {neighbor.y}) added to open set, f_score: {neighbor.f_score:.2f}")
            elif tentative_g_score > neighbor.g_score:
                print(f"    Shorter path to ({neighbor.x}, {neighbor.y}) not found, skipping.")
                continue
            else:
                print(f"    Found a better path to ({neighbor.x}, {neighbor.y})")
                came_from[str(neighbor.x) + ' ' + str(neighbor.y)] = current
                neighbor.g_score = tentative_g_score
                neighbor.f_score = neighbor.g_score + h_score(neighbor, end_node)
                print(f"    Updated g_score: {neighbor.g_score:.2f}, f_score: {neighbor.f_score:.2f}")

def lowest_f_score(node_list):
    final_node = None
    for node in node_list:
        if not final_node or node.f_score < final_node.f_score:
            final_node = node
    return final_node
