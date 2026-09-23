import pytest

from src.game import can_afford, deduct_cost


def test_can_afford_uses_zero_for_missing_resources():
    assert can_afford({"gold": 10, "wood": 5}, {}, 10) is False
    assert can_afford({"gold": 10, "wood": 5}, {"wood": 5}, 10) is True


def test_can_afford_does_not_use_gold_for_non_gold_costs():
    assert can_afford({"stone": 5}, {"wood": 100}, 100) is False


def test_deduct_cost_updates_gold_and_resource_balances():
    resources = {"wood": 20}

    gold = deduct_cost(
        {"gold": 15, "wood": 7, "food": 0},
        resources,
        40,
    )

    assert gold == 25
    assert resources == {"wood": 13, "food": 0}


def test_deduct_cost_is_atomic_when_balance_is_insufficient():
    resources = {"wood": 20}

    with pytest.raises(ValueError):
        deduct_cost({"gold": 15, "wood": 30}, resources, 40)

    assert resources == {"wood": 20}
