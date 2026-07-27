#!/usr/bin/env python3
"""
gen_aliases.py — build mic_aliases.txt (alias<TAB>slug) so the photo importer can
resolve friendly filenames like "57", "B58", "421", "v7x" to the right mic page.

Sources: curated shorthands (below) win; then auto-derived from mic_data.json
(slug, and slug minus the brand prefix). Ambiguous auto aliases are dropped.
Run after adding mics:  python3 gen_aliases.py
"""
import json, os, re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "mic_data.json")
OUT = os.path.join(HERE, "mic_aliases.txt")

# Curated — Brian's spoken/written shorthands. These always win.
CURATED = {
    "421": "sennheiser-md421", "md421": "sennheiser-md421", "421-u": "sennheiser-md421",
    "52": "shure-beta-52a", "b52": "shure-beta-52a", "beta52": "shure-beta-52a", "52a": "shure-beta-52a",
    "57": "shure-sm57", "sm57": "shure-sm57",
    "58": "shure-sm58", "sm58": "shure-sm58",
    "b58": "shure-beta-58a", "b58a": "shure-beta-58a", "beta58": "shure-beta-58a",
    "58a": "shure-beta-58a", "beta58a": "shure-beta-58a",
    "604": "sennheiser-e604", "e604": "sennheiser-e604",
    "609": "sennheiser-e609", "e609": "sennheiser-e609",
    "v7x": "se-v7-x", "v7-x": "se-v7-x", "v7": "se-v7-x",
    "vbeat": "se-v-beat", "vkick": "se-v-kick",
    "i5": "audix-i5", "d2": "audix-d2", "d4": "audix-d4", "d6": "audix-d6",
    "pro6l": "audio-technica-pro-6l", "pro-6l": "audio-technica-pro-6l",
    "nd408": "electro-voice-nd408", "n-d408": "electro-voice-nd408",
    "nd-408": "electro-voice-nd408", "ev408": "electro-voice-nd408",
    "ev-408": "electro-voice-nd408",  # bare "408" left unmapped — ambiguous with the Lauten LS-408
    "s3": "deity-s3", "s-mic-3": "deity-s3", "smic3": "deity-s3", "s2": "deity-s2",
    "121l": "royer-r-121", "r121l": "royer-r-121", "r-121l": "royer-r-121",
    "trp2": "aea-trp2", "trp": "aea-trp2", "aeatrp2": "aea-trp2",
    "m60": "telefunken-m60",
    "27": "shure-beta-27", "b27": "shure-beta-27", "beta27": "shure-beta-27",
    "4099": "dpa-4099", "dpa4099": "dpa-4099",
    "81": "shure-sm81", "sm81": "shure-sm81",
    "91": "shure-beta-91a", "91a": "shure-beta-91a", "beta91": "shure-beta-91a", "beta-91a": "shure-beta-91a",
    "98": "shure-beta-98hc", "98hc": "shure-beta-98hc", "b98": "shure-beta-98hc", "beta98": "shure-beta-98hc",
    "at-pro-35": "audio-technica-pro35", "pro35": "audio-technica-pro35", "pro-35": "audio-technica-pro35", "atpro35": "audio-technica-pro35",
    "mkh-40": "sennheiser-mkh40", "mkh40": "sennheiser-mkh40", "mkh": "sennheiser-mkh40",
    "sr20": "earthworks-sr20sp", "sr20sp": "earthworks-sr20sp", "sr20sp-gen-2": "earthworks-sr20sp", "earthworks-sr20sp-gen-2": "earthworks-sr20sp",
    "sr25": "earthworks-sr25", "dm6": "earthworks-dm6", "dm17": "earthworks-dm17",
    "mk4": "schoeps-cmc6-mk4", "mk5": "schoeps-cmc6-mk5", "mk41": "schoeps-cmc6-mk41",
    "kms105": "neumann-kms-105", "105": "neumann-kms-105", "tlm102": "neumann-tlm-102", "102": "neumann-tlm-102",
    "c414": "akg-c414", "414": "akg-c414", "c422": "akg-c422", "422": "akg-c422",
    "87": "warm-audio-wa-87", "u87": "warm-audio-wa-87", "wa87": "warm-audio-wa-87", "wa-87": "warm-audio-wa-87",
    "87jr": "warm-audio-wa-87", "u87jr": "warm-audio-wa-87", "87-jr": "warm-audio-wa-87", "u87-jr": "warm-audio-wa-87",
    "ls408": "lauten-ls-408", "ls-408": "lauten-ls-408",
    "j48": "radial-j48", "rndi": "neve-rndi", "imp": "whirlwind-imp",
    "ar133": "bss-ar133", "ar-133": "bss-ar133", "bss-ar-133": "bss-ar133", "bss-audio-ar-133": "bss-ar133",
    "98hc": "shure-beta-98hc", "98h:c": "shure-beta-98hc", "98h-c": "shure-beta-98hc", "shure-beta-98h:c": "shure-beta-98hc", "beta98hc": "shure-beta-98hc",
    "warm-87jr": "warm-audio-wa-87", "87-jr": "warm-audio-wa-87", "warm87jr": "warm-audio-wa-87",
    "r10": "royer-r-10", "r-10": "royer-r-10", "r121": "royer-r-121", "r-121": "royer-r-121", "r88": "aea-r88",
    "om1": "line-audio-om1", "cm4": "line-audio-cm4", "se8": "se-se8", "b3": "countryman-b3",
}

BRANDS = {"shure", "audix", "sennheiser", "se", "audio", "technica", "dpa",
          "neumann", "akg", "royer", "aea", "radial", "neve", "warm", "line",
          "deity", "earthworks", "schoeps", "countryman", "telefunken", "lauten",
          "bss", "whirlwind"}

def norm(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def main():
    data = json.load(open(DATA))
    mics = data["mics"] if isinstance(data, dict) else data
    slugs = {m["slug"] for m in mics}
    auto = defaultdict(set)  # alias -> set(slug)
    for m in mics:
        slug = m["slug"]
        auto[slug].add(slug)
        parts = slug.split("-")
        # slug minus leading brand tokens
        i = 0
        while i < len(parts) - 1 and parts[i] in BRANDS:
            i += 1
        brandless = "-".join(parts[i:])
        if brandless:
            auto[brandless].add(slug)
    # curated wins; auto only if unambiguous and not overriding curated
    final = {}
    for a, s in CURATED.items():
        if s in slugs:
            final[a] = s
    for a, sset in auto.items():
        if a in final:
            continue
        if len(sset) == 1:
            final[a] = next(iter(sset))
    with open(OUT, "w") as f:
        for a in sorted(final):
            f.write(f"{a}\t{final[a]}\n")
    print(f"wrote {len(final)} aliases -> {OUT}")

if __name__ == "__main__":
    main()
