def validate_ingredients(ingredients: str) -> str:
    valid_keywords = ("fire", "water", "earth", "air")
    if any(word in ingredients for word in valid_keywords):
        return (f"{ingredients} - VALID")
    else:
        return (f"{ingredients} - INVALID")
