#!/usr/bin/env python3

def main() -> None:
    """Demonstrate list, dict, and set comprehensions."""
    print("=== Game Analytics Dashboard ===")
    players = ["alice", "bob", "charlie", "diana"]
    scores = {"alice": 2300, "bob": 1800, "charlie": 2150, "diana": 2050}
    achievements = {
        "alice": [
            "first_kill", "level_10", "boss_slayer",
            "speed_demon", "collector"
        ],
        "bob": ["first_kill", "level_10", "treasure_hunter"],
        "charlie": [
            "level_10", "boss_slayer", "perfectionist", "speed_demon",
            "collector", "first_kill", "treasure_hunter"
        ],
        "diana": ["first_kill", "level_10"]
    }
    regions = ["north", "east", "central", "north", "east"]
    print("=== List Comprehension Examples ===")
    high_scorers = [p for p in players if scores[p] > 2000]
    print(f"High scorers (>2000): {high_scorers}")
    doubled_scores = [scores[p] * 2 for p in players]
    print(f"Scores doubled: {doubled_scores}")
    active_players = [p for p in players if len(achievements[p]) >= 3]
    print(f"Active players: {active_players}")
    print("=== Dict Comprehension Examples ===")
    player_scores = {p: scores[p] for p in players}
    print(f"Player scores: {player_scores}")
    score_categories = {
        "high": len([s for s in scores.values() if s >= 2200]),
        "medium": len([s for s in scores.values() if 2000 <= s < 2200]),
        "low": len([s for s in scores.values() if s < 2000]),
    }
    print(f"Score categories: {score_categories}")
    achievement_counts = {p: len(achievements[p]) for p in players}
    print(f"Achievement counts: {achievement_counts}")
    print("=== Set Comprehension Examples ===")
    unique_players = {p for p in players}
    print(f"Unique players: {unique_players}")
    unique_achievements = {a for plist in achievements.values() for a in plist}
    print(f"Unique achievements: {unique_achievements}")
    active_regions = {r for r in regions}
    print(f"Active regions: {active_regions}")
    print("=== Combined Analysis ===")
    total_players = len(players)
    print(f"Total players: {total_players}")
    total_unique_ach = len(unique_achievements)
    print(f"Total unique achievements: {total_unique_ach}")
    avg_score = sum(scores.values()) / len(scores)
    print(f"Average score: {avg_score}")
    top_player = max(scores, key=lambda p: scores[p])
    print(
        f"Top performer: {top_player} "
        f"({scores[top_player]} points, "
        f"{len(achievements[top_player])} achievements)"
    )


if __name__ == "__main__":
    main()
