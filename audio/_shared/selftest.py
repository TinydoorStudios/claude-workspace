#!/usr/bin/env python3
"""
selftest.py — the one regression test the show pipeline needs.

The .ses patcher writes 40 MB binaries that get recalled on a console, so a
silent regression there is the expensive kind. This test:

  1. lints the calibration MD (0 errors),
  2. patches it against BOTH venue templates into a temp dir and requires the
     engine's own PASS lines, then compares the output md5 to the golden in
     `goldens.json` (a template drop or an intentional engine change updates
     the goldens with --update-goldens),
  3. runs build_packet.py on `selftest_fixture.spec.json` and requires every
     packet file to land and the written .md to pass lint.

    python3 selftest.py            # run
    python3 selftest.py --update-goldens
    python3 selftest.py --quick    # skip the packet build (PDF render)

Wired into audio/_skills/git-hooks/pre-commit for commits that touch the
engine, the patchers, the templates or the packet builder. Exit 0 = all PASS.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile

AUDIO = os.path.expanduser("~/Documents/Claude/audio")
HERE = os.path.dirname(os.path.abspath(__file__))
GOLDENS = os.path.join(HERE, "goldens.json")
CAL_MD = os.path.join(AUDIO, "Fountain Square", "Q225 SES Patcher SOP",
                      "CALIBRATION_TEST - FOH Channel Processing.md")
VENUES = {
    "fsq":  ("Fountain Square/Q225 SES Patcher SOP/apply_show_TEMPLATE_FSQ.py",
             "Fountain Square/_TEMPLATE/brian fsq start.ses"),
    "memo": ("Memorial Hall/Q225 SES Patcher SOP/apply_show_TEMPLATE.py",
             "Memorial Hall/_TEMPLATE/brian memo june 2026.ses"),
}
BUILD_PACKET = os.path.join(AUDIO, "_skills", "show-deep-build", "scripts", "build_packet.py")
FIXTURE = os.path.join(HERE, "selftest_fixture.spec.json")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--update-goldens", action="store_true")
    ap.add_argument("--quick", action="store_true", help="skip the packet build")
    a = ap.parse_args()
    fails = []
    goldens = json.load(open(GOLDENS)) if os.path.exists(GOLDENS) else {}
    tmp = tempfile.mkdtemp(prefix="selftest-")

    # 1. lint
    sys.path.insert(0, HERE)
    import md_lint
    errs, _ = md_lint.lint(CAL_MD)
    print(f"[lint] calibration MD: {'PASS' if not errs else 'FAIL ' + '; '.join(errs)}")
    if errs:
        fails.append("lint")

    # 2. patchers
    for venue, (patcher, template) in VENUES.items():
        dest = os.path.join(tmp, f"{venue}.ses")
        rc, out = run([sys.executable, os.path.join(AUDIO, patcher),
                       "--src", os.path.join(AUDIO, template), "--dest", dest, "--md", CAL_MD])
        needed = ("bytes changed outside mic'd blocks: 0 PASS",
                  "do-not-write tags modified: 0 PASS", "readback: PASS")
        flat = " ".join(out.split())
        missing = [n for n in needed if n not in flat]
        ok = rc == 0 and not missing and "!!" not in out
        digest = md5(dest) if os.path.exists(dest) else None
        if a.update_goldens and digest:
            goldens[venue] = {"md5": digest, "template": os.path.basename(template),
                              "template_bytes": os.path.getsize(os.path.join(AUDIO, template))}
        elif digest and venue in goldens and goldens[venue]["md5"] != digest:
            ok = False
            missing.append(f"md5 {digest} != golden {goldens[venue]['md5']}")
        elif venue not in goldens:
            missing.append("no golden yet — run --update-goldens")
        print(f"[patch] {venue}: {'PASS' if ok else 'FAIL'}"
              + (f"  ({'; '.join(missing)})" if missing else "") + f"  md5 {digest}")
        if not ok:
            fails.append(f"patch-{venue}")
            print(out[-1500:])

    # 3. packet build
    if not a.quick:
        out_dir = os.path.join(tmp, "packet")
        os.makedirs(out_dir)
        spec = os.path.join(out_dir, "Selftest.spec.json")
        shutil.copy(FIXTURE, spec)
        rc, out = run([sys.executable, BUILD_PACKET, "--spec", spec, "--out", out_dir])
        want = ["Selftest - FOH Channel Processing.md", "Selftest - Input List.xlsx",
                "Selftest - Show Packet.pdf", "Selftest - FOH EQ Reasoning.pdf",
                "Selftest - MASTER.pdf", "show.status.json"]
        absent = [w for w in want if not os.path.exists(os.path.join(out_dir, w))]
        ok = rc == 0 and not absent and "md_lint PASS" in out
        print(f"[packet] build: {'PASS' if ok else 'FAIL'}"
              + (f"  (missing {absent})" if absent else ""))
        if not ok:
            fails.append("packet")
            print(out[-2000:])
        else:
            st = json.load(open(os.path.join(out_dir, "show.status.json")))
            if not st.get("md_md5"):
                fails.append("packet-stamp"); print("[packet] status file has no md_md5 stamp")

    if a.update_goldens:
        json.dump(goldens, open(GOLDENS, "w"), indent=2)
        print(f"goldens written -> {GOLDENS}")
    shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST", "PASS" if not fails else f"FAIL {fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
