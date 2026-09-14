"""
buildpkg.py — Mac: build a show from a *.spec.json package made on the Proxmox
instance. The package is the approved spec; this honors it as-is.

    python3 -m backend.buildpkg ~/Downloads/Some_Show.spec.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backend.knowledge import Knowledge          # noqa: E402
from backend.spec import ShowSpec                # noqa: E402
from backend import build as buildmod            # noqa: E402
from backend.harvest import harvest_show         # noqa: E402


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("usage: python3 -m backend.buildpkg <package.spec.json>")
        return 2
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    if not cfg.get("audio_root"):
        print("ERROR: this config has no audio_root — run on the Mac.")
        return 2
    kn = Knowledge(cfg)
    spec = ShowSpec.load(argv[0])
    print(f"Building '{spec.show_name}' ({spec.venue}) from {argv[0]} …\n")
    result = buildmod.build_all(kn, spec, write_ses=True)
    harvest_show(kn, spec, result)
    print(f"\nFolder: {result['folder']}")
    print(f".ses verified: {result['ses_ok']}  {result.get('readback','')}")
    for w in result["warnings"]:
        print("  ! " + w)
    print("\nFiles:")
    for k, v in result["files"].items():
        print(f"  {k:8s} {Path(v).name}")
    print("\nLoad the .ses on the console, confirm, then push to the wiki.")
    return 0 if result.get("ses_ok") in (True, None) else 1


if __name__ == "__main__":
    sys.exit(main())
