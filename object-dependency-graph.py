#! /usr/bin/env python3

"""
creates a graphviz '.dot' file with relation A -> B if object file B provides symbol that is required by object file A. The relation is annotated with the respective symbol names.
all object files in current or given directory (including subdirectories) are processed.
"""

import os
import subprocess
import sys
import re
from collections import defaultdict  # multimap impl


def find_object_files(rootdir):
    for root, folders, files in os.walk(rootdir):
        for file in files:
            if file.endswith(".o"):
                yield os.path.join(root, file)


def symbols(path):
    result = subprocess.run(["nm", "-C", path], stdout=subprocess.PIPE)

    CODE_POS = 17
    provided, required = list(), list()
    for item in result.stdout.decode("utf-8").split("\n"):
        if len(item) == 0:
            continue
        if item[CODE_POS] == "U":
            required.append(item[CODE_POS+2:])
        elif item[CODE_POS] == "T":
            provided.append(item[CODE_POS+2:])

    return provided, required


def create_obj_db(path):
    obj_db = list()

    for obj in find_object_files(path):
        provided, required = symbols(obj)
        obj_db.append((obj, provided, required))

    return obj_db


def find_symbol_provider(name, db):
    for obj, provided, _ in db:
        if name in provided:
            return obj


def object_relations(obj_db):
    for user, _, required in obj_db:
        m = defaultdict(set)
        for symbol in required:
            provider = find_symbol_provider(symbol, obj_db)
            if provider:
                m[provider].add(symbol)

        for provider, symbols in m.items():
            yield user, provider, symbols


def simplify(name):
    type_map = {
        "\(.*\)": "()",     # remove signature
        ".*::": "",         # remove namespace
    }

    for k, v in type_map.items():
        name = re.sub(k, v, name)

    return name


def main():
    path = "." if len(sys.argv) < 2 else sys.argv[1]

    obj_db = create_obj_db(path)

    print("digraph G {\nrankdir=\"LR\";")
    for user, provider, symbols in object_relations(obj_db):
        # shorten paths
        user = os.path.basename(user)
        provider = os.path.basename(provider)
        # shorten signatures
        label = ", ".join([simplify(s) for s in symbols])
        # label = ", ".join(symbols)
        print(
            """\t"{}" -> "{}" [label="{}"]""".format(user, provider, label))
    print("}")


if __name__ == '__main__':
    main()
