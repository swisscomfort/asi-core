#!/usr/bin/env python3
"""
Einfacher Debug-Test für ASI Core
"""


def debug_test():
    """Einfache Funktion zum Testen des Debuggers"""
    print("🔧 Debug-Test gestartet...")

    # Setzen Sie hier einen Breakpoint!
    test_var = "ASI Core Debug Test"
    numbers = [1, 2, 3, 4, 5]

    print(f"Test Variable: {test_var}")

    for i, num in enumerate(numbers):
        result = num * 2
        print(f"Schritt {i+1}: {num} * 2 = {result}")

    print("✅ Debug-Test abgeschlossen!")
    return test_var, numbers


if __name__ == "__main__":
    debug_test()
