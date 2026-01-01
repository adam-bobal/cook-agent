"""Interactive console for the cooking agent."""
from __future__ import annotations

import os
from typing import Optional

from .model_client import GitHubModelClient
from .recipes import search_recipes, extract_ingredients


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_menu():
    print("Cooking AI Agent")
    print("1) Search recipes")
    print("2) Extract ingredients from text")
    print("3) Quit")


def run_cli():
    client = GitHubModelClient()
    configured = client.configured()
    if configured:
        print("Model client configured. Using remote model for extraction when available.")
    else:
        print("No remote model configured — running in local fallback mode.")

    while True:
        print()
        show_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            q = input("Search query (ingredient or title): ").strip()
            if not q:
                print("Empty query — try again.")
                continue
            results = search_recipes(q)
            if not results:
                print("No matching recipes in sample dataset.")
            else:
                for i, r in enumerate(results, 1):
                    print(f"{i}. {r['title']}")
                    print(f"   Ingredients: {', '.join(r['ingredients'])}")
                    print(f"   Instructions: {r['instructions']}")

        elif choice == "2":
            print("Enter the text to extract ingredients from (finish with an empty line):")
            lines = []
            while True:
                try:
                    ln = input()
                except EOFError:
                    break
                if not ln:
                    break
                lines.append(ln)
            text = "\n".join(lines)
            if not text.strip():
                print("No text provided.")
                continue
            ingredients = extract_ingredients(text, model_client=client if configured else None)
            if ingredients:
                print("Extracted ingredients:", ", ".join(ingredients))
            else:
                print("No ingredients extracted.")

        elif choice == "3" or choice.lower() in ("q", "quit", "exit"):
            print("Goodbye")
            break
        else:
            print("Unknown option — try again.")
