import csv
import os
import re
import argparse
import sys
from collections import defaultdict

def build_tree(csv_file_path, visited=None, tree=None, depth=0, folder_recursion=False):
    if visited is None:
        visited = set()
    if tree is None:
        tree = defaultdict(list)

    # Depth stop
    if depth == 0:
        return tree

    # Add to visited list
    if csv_file_path in visited:
        return tree
    visited.add(csv_file_path)

    hashes = []

    # Truncate Hash
    hash_pattern = re.compile(r"0x([0-9a-fA-F]+)\.\d+")

    # Read Csv
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                for cell in row:
                    match = hash_pattern.search(cell)
                    if match:
                        # Steal hash 
                        hashes.append(match.group(1))
    except UnicodeDecodeError:
        # FallbackBecauseItHatesMeTM 
        try:
            with open(csv_file_path, mode='r', newline='', encoding='ISO-8859-1') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    for cell in row:
                        match = hash_pattern.search(cell)
                        if match:
                            hashes.append(match.group(1))
        except Exception as e:
            print(f"Error reading file '{csv_file_path}' with fallback encoding: {e}")
            return tree
    except Exception as e:
        print(f"Error reading file '{csv_file_path}': {e}")
        return tree

    #Find file with hash
    base_directory = os.path.dirname(csv_file_path)
    for hash_value in hashes:
        if folder_recursion:
            # Subd
            for root, _, files in os.walk(base_directory):
                for file_name in files:
                    if file_name.endswith(f"{hash_value}.csv"):
                        target_file_path = os.path.join(root, file_name)
                        if os.path.isfile(target_file_path):
                            tree[os.path.basename(csv_file_path)].append(os.path.basename(target_file_path))
                            # Recurse
                            build_tree(target_file_path, visited, tree, depth - 1, folder_recursion)
        else:
            # No subd
            for file_name in os.listdir(base_directory):
                if file_name.endswith(f"{hash_value}.csv"):
                    target_file_path = os.path.join(base_directory, file_name)
                    if os.path.isfile(target_file_path):
                        tree[os.path.basename(csv_file_path)].append(os.path.basename(target_file_path))

                        build_tree(target_file_path, visited, tree, depth - 1, folder_recursion)

    return tree

def print_tree(tree, root, indent=0, displayed=None):
    if displayed is None:
        displayed = set()

    if root in displayed:
        return
    displayed.add(root)

    print(" " * indent + root)
    for child in tree[root]:
        print_tree(tree, child, indent + 4, displayed)

# InputMessage
parser = argparse.ArgumentParser(description="Build a filesys structure from a CSV file.")
parser.add_argument("-i", help="Path to the input CSV file.")
parser.add_argument("-f", type=int, choices=[0, 1], default=0,help="Enable folder recursion IT IS SLOWER ")
parser.add_argument("-d", type=int, default=10, help="Max recursion depth, Default: 10")

args = parser.parse_args()

try:
    if not args.i:
        print("No input file provided. Use the following arguments:")
        parser.print_help()
        sys.exit(1)

    csv_file_path = args.i
    folder_recursion = bool(args.f)
    max_depth = args.d


    if os.path.isfile(csv_file_path):
        tree = build_tree(csv_file_path, depth=max_depth, folder_recursion=folder_recursion)
        root_file = os.path.basename(csv_file_path)
        print_tree(tree, root_file)
    else:
        print(f"Error: The file '{csv_file_path}' does not exist. Please check the file path.")
except Exception as e:
    print(f"An error occurred: {e}")

# Keep the console open
input("\nPress Enter to exit...")