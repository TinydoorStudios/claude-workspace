#!/usr/bin/env python3
"""Build a Wiki.js navigation.updateTree GraphQL payload from kb-nav.json.
Emits a JSON string ready to POST to the Wiki.js GraphQL endpoint.
Wiki.js v2 nav tree = one locale ('en') with a flat list of items:
headers + links, each with a uuid. Headers group the links that follow them.
"""
import json, sys, uuid

nav = json.load(open(sys.argv[1]))
items = []
for g in nav["groups"]:
    items.append({
        "id": str(uuid.uuid4()), "kind": "header",
        "label": g["header"], "icon": "", "targetType": "", "target": "",
        "visibilityMode": "all", "visibilityGroups": []
    })
    for ln in g["links"]:
        items.append({
            "id": str(uuid.uuid4()), "kind": "link",
            "label": ln["label"], "icon": "mdi-text-box-outline",
            "targetType": "page", "target": ln["path"],
            "visibilityMode": "all", "visibilityGroups": []
        })

mutation = (
    "mutation($tree:[NavigationTreeInput]!){"
    "navigation{updateTree(tree:$tree){responseResult{succeeded message}}}}"
)
payload = {"query": mutation, "variables": {"tree": [{"locale": "en", "items": items}]}}
print(json.dumps(payload))
