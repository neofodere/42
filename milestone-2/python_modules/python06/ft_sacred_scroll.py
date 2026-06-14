import alchemy
import alchemy.elements as elements

print("=== Sacred Scroll Mastery ===\n")
print("Testing direct module access:")
print("alchemy.elements.create_fire():", elements.create_fire())
print("alchemy.elements.create_water():", elements.create_water())
print("alchemy.elements.create_earth():", elements.create_earth())
print("alchemy.elements.create_air():", elements.create_air())
print("\nTesting package-level access (controlled by __init__.py):")

try:
    print("alchemy.create_fire():", alchemy.create_fire())
except AttributeError as err_msg:
    print("alchemy.create_fire(): AttributeError -", err_msg)
try:
    print("alchemy.create_water():", alchemy.create_water())
except AttributeError as err_msg:
    print("alchemy.create_water(): AttributeError -", err_msg)
for func_name in ("create_earth", "create_air"):
    try:
        func = getattr(alchemy, func_name)
        print(f"alchemy.{func_name}():", func())
    except AttributeError:
        print(f"alchemy.{func_name}(): AttributeError - not exposed")

print("\nPackage metadata:")
print("Version:", alchemy.__version__)
print("Author:", alchemy.__author__)
