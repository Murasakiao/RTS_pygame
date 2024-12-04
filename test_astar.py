import unittest
from src.astar import a_star, Node

class TestAStar(unittest.TestCase):

    def test_pathfinding(self):
        # Example grid (0: passable, 1: obstacle)
        from src.astar import create_grid
        grid = create_grid(4, 4, [(1, 1), (2, 2)])
        start = grid[0][0]
        end = grid[3][3]
        start.grid = grid
        end.grid = grid

        path = a_star(grid, start, end)

        # Assert that a path was found
        self.assertIsNotNone(path)

        # Assert the path is correct (example)
        expected_path = [(0, 0), (1, 0), (1, 1), (2, 2), (3, 3)]
        self.assertEqual([(node.x, node.y) for node in path], expected_path)

if __name__ == '__main__':
    unittest.main()
