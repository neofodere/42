#!/usr/bin/env python3
import sys


def parse_inventory(args: list[str]) -> dict[str, int]:
    """Parse CLI items into a quantity dictionary."""
    inventory: dict[str, int] = {}
    for arg in args:
        if (":" not in arg):
            continue
        name, qty = arg.split(":")
        try:
            inventory.update({name: int(qty)})
        except ValueError:
            continue
    return (inventory)


def total_items(inv: dict[str, int]) -> int:
    """Return total quantity of all items."""
    return (sum(inv.values()))


def most_abundant(inv: dict[str, int]) -> tuple[str, int]:
    """Return the item with highest quantity."""
    return (max(inv.items(), key=lambda x: x[1]))


def least_abundant(inv: dict[str, int]) -> tuple[str, int]:
    """Return the item with lowest quantity."""
    return (min(inv.items(), key=lambda x: x[1]))


def categorize_items(
        inv: dict[str, int]) -> tuple[dict[str, int], dict[str, int]]:
    """Return moderate and scarce item categories."""
    moderate: dict[str, int] = {}
    scarce: dict[str, int] = {}
    for name, qty in inv.items():
        if (qty >= 4):
            moderate.update({name: qty})
        else:
            scarce.update({name: qty})
    return (moderate, scarce)


def restock_list(inv: dict[str, int]) -> list[str]:
    """Return items needing restock."""
    return ([name for name, qty in inv.items() if qty <= 1])


def main() -> None:
    """Analyze inventory data using dictionaries."""
    args = sys.argv[1:]
    inventory = parse_inventory(args)
    print("=== Inventory System Analysis ===")
    total = total_items(inventory)
    print(f"Total items in inventory: {total}")
    print(f"Unique item types: {len(inventory)}")
    print("=== Current Inventory ===")
    for name, qty in sorted(
        inventory.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        percent = (qty / total) * 100
        print(f"{name}: {qty} units ({percent:.1f}%)")
    print("=== Inventory Statistics ===")
    most_name, most_qty = most_abundant(inventory)
    least_name, least_qty = least_abundant(inventory)
    print(f"Most abundant: {most_name} ({most_qty} units)")
    print(f"Least abundant: {least_name} ({least_qty} units)")
    print("=== Item Categories ===")
    moderate, scarce = categorize_items(inventory)
    print(f"Moderate: {moderate}")
    print(f"Scarce: {scarce}")
    print("=== Management Suggestions ===")
    print(f"Restock needed: {restock_list(inventory)}")
    print("=== Dictionary Properties Demo ===")
    print(f"Dictionary keys: {list(inventory.keys())}")
    print(f"Dictionary values: {list(inventory.values())}")
    print(f"Sample lookup - 'sword' in inventory: {'sword' in inventory}")


if __name__ == "__main__":
    main()
