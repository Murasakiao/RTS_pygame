import math

from src.astar import PathStatus, a_star, h_score


def open_grid(width, height):
    return [[(0, 0) for _ in range(width)] for _ in range(height)]


def test_a_star_returns_coordinate_path_and_octile_heuristic():
    result = a_star(open_grid(3, 3), (0, 0), (2, 2))

    assert result.status is PathStatus.FOUND
    assert result.path[0] == (0, 0)
    assert result.path[-1] == (2, 2)
    assert all(isinstance(cell, tuple) for cell in result.path)
    assert math.isclose(h_score((0, 0), (2, 2)), 2 * math.sqrt(2))


def test_a_star_reports_already_there_without_treating_it_as_failure():
    result = a_star(open_grid(2, 2), (1, 1), (1, 1))

    assert result.status is PathStatus.ALREADY_THERE
    assert result.succeeded
    assert result.path == ((1, 1),)
    assert bool(result)


def test_a_star_rejects_invalid_and_blocked_inputs():
    grid = open_grid(2, 2)
    grid[0][0] = (0, 1)
    grid[1][1] = (0, 1)

    assert a_star(grid, (0, 0), (1, 0)).reason == "start_blocked"
    assert a_star(open_grid(2, 2), (0, 0), (2, 0)).status is PathStatus.INVALID_INPUT
    assert a_star(open_grid(2, 2), (0, 0), (1, 1)).status is PathStatus.FOUND
    assert a_star(grid, (1, 0), (1, 1)).reason == "goal_blocked"
    assert a_star([], (0, 0), (0, 0)).status is PathStatus.INVALID_INPUT


def test_a_star_does_not_cut_across_blocked_diagonal_corner():
    grid = open_grid(2, 2)
    grid[0][1] = (0, 1)
    grid[1][0] = (0, 1)

    result = a_star(grid, (0, 0), (1, 1))

    assert result.status is PathStatus.UNREACHABLE
    assert result.reason == "no_route"


def test_a_star_does_not_replace_a_blocked_goal_with_a_nearby_cell():
    grid = open_grid(3, 3)
    grid[1][1] = (0, 1)

    result = a_star(grid, (0, 0), (1, 1))

    assert result.status is PathStatus.UNREACHABLE
    assert result.reason == "goal_blocked"
