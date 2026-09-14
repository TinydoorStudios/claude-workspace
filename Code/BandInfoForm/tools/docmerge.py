#!/usr/bin/env python3
"""Filed advance docs are never overwritten (2026-09-13 audit, items 1 + 2).

A show's advance doc is created ONCE, from the universal template. After
that, every pipeline pass (a booking, a band submission, "Run again")
builds what the doc WOULD say from scratch in memory, then walks the filed
doc cell by cell:

  - the pipeline has nothing for a cell (fresh == blank template)  -> skip
  - the filed doc already says the same thing                       -> skip
  - the filed doc's cell is still blank (== the blank template)     -> fill it
  - the filed doc says something different                          -> leave
    it alone and record a notice (emailed to Brian as a diff)

"Blank" means the cell still matches the pristine universal template
exactly — "FOH – " with no name, a checkbox group with nothing ticked.
Multi-paragraph cells (Engineer's FOH/Mon lines, Event Type's two checkbox
lines, the EVENT INFORMATION header's Date/Event/Venue/Location lines) are
compared paragraph by paragraph when their shape still matches the
template, so filling the Mon line never touches a hand-typed FOH line.

Per-cell provenance (review 2026-09-14, H2 — Brian's call): `filed_docs.cells`
records what the pipeline last wrote into each cell. A cell that still reads
exactly what the pipeline wrote is the pipeline's to update (a returning
band's prior-show pre-fill, a corrected monitor count, a cancelled act);
a cell that reads anything else was typed by a person and is never touched —
a differing value becomes a notice instead. "Blank" cells (still the
template) are filled as before. Whole-file sha256 is still recorded so a
hand-edited doc is flagged in the notice.
A doc that Word/Dropbox shows as open (a "~$" owner file beside it) is not
touched at all that run; the next run picks it up. Writes are atomic
(temp file + os.replace) and re-check the hash right before replacing, so a
save that lands mid-run is never clobbered.

The filename follows fieldspec.event_display_name (series/event + headliner).
When that name changes, the SAME file is renamed in place — never a second
copy. Lookups go through `filed_docs` by venue + date + event key, not by
filename sort order. Past shows are never touched.
"""
import copy
import datetime as dt
import filecmp
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _c in (HERE.parent, HERE.parent / "app"):
    if (_c / "advance_db.py").exists():
        sys.path.insert(0, str(_c))
        break
sys.path.insert(0, str(HERE))
import advance_db as db
import daysheet
import fieldspec as fs

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml.ns import qn

SLOT_COL_NAMES = {1: "Opener", 2: "Direct Support", 3: "Headliner"}


# ── small XML helpers ───────────────────────────────────────────────────────

def _t(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def _p_text(p_el):
    """Visible text of a paragraph, including checkbox glyphs inside content
    controls; line breaks and tabs count as whitespace so a value written as
    'a\nb' compares equal however Word stored the break."""
    out = []
    for el in p_el.iter(qn("w:t"), qn("w:br"), qn("w:tab"), qn("w:cr")):
        out.append(el.text or "" if el.tag == qn("w:t") else " ")
    return "".join(out)


def _tc_text(tc):
    return "\n".join(_p_text(p) for p in tc.iter(qn("w:p")))


def _tc_paras(tc):
    return [c for c in tc if c.tag == qn("w:p")]


def _has_table(tc):
    return any(True for _ in tc.iter(qn("w:tbl")))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def event_key(ev):
    return re.sub(r"\s+", " ", (ev.get("name") or ev.get("series") or "").strip()).lower()


def word_lock_present(path):
    """True if Word (on any synced machine) has this doc open — Word drops
    a '~$' owner file beside it, named '~$' + the filename minus its first
    two characters for longer names."""
    path = Path(path)
    try:
        for p in path.parent.glob("~$*"):
            tail = p.name[2:]
            if tail and path.name.endswith(tail):
                return True
    except OSError:
        return False
    return False


class _Ctx:
    """Everything one merge pass needs: the three documents, a running max
    content-control id for the filed doc, the notice list, and the per-cell
    provenance map in (`prov`, what the pipeline last wrote) and out
    (`newprov`, what the pipeline owns after this pass)."""

    def __init__(self, T, F, E, prov=None):
        self.T, self.F, self.E = T, F, E
        self.changed = 0
        self.notices = []
        self.prov = dict(prov or {})
        self.newprov = {}
        ids = [int(el.get(qn("w:val"))) for el in E.element.body.iter(qn("w:id"))
               if el.getparent() is not None and el.getparent().tag == qn("w:sdtPr")
               and (el.get(qn("w:val")) or "").lstrip("-").isdigit()]
        self.next_sdt_id = (max(ids) + 1) if ids else 200000000

    def prepare_copy(self, el):
        """Deep-copy a fresh-doc element for insertion into the filed doc:
        re-home any hyperlink relationship and renumber checkbox ids."""
        new = copy.deepcopy(el)
        for link in new.iter(qn("w:hyperlink")):
            rid = link.get(qn("r:id"))
            if not rid:
                continue
            rel = self.F.part.rels.get(rid)
            if rel is None:
                continue
            new_rid = self.E.part.relate_to(rel.target_ref, RT.HYPERLINK, is_external=True)
            link.set(qn("r:id"), new_rid)
        for id_el in new.iter(qn("w:id")):
            if id_el.getparent() is not None and id_el.getparent().tag == qn("w:sdtPr"):
                id_el.set(qn("w:val"), str(self.next_sdt_id))
                self.next_sdt_id += 1
        return new

    def notice(self, section, column, doc_value, new_value):
        self.notices.append({"field": section + (f" — {column}" if column else ""),
                             "doc_value": doc_value, "new_value": new_value})


def _replace_tc_content(ctx, e_tc, f_tc):
    for child in list(e_tc):
        if child.tag != qn("w:tcPr"):
            e_tc.remove(child)
    for child in f_tc:
        if child.tag != qn("w:tcPr"):
            e_tc.append(ctx.prepare_copy(child))


def _tokens(s):
    return set(re.findall(r"[a-z0-9]+", _t(s).lower()))


def _differs_meaningfully(e_text, f_text):
    """A diff worth reporting: every word/number of the new value is NOT
    already present in what the doc says (a hand edit that extends the
    pipeline's value — '5 wedges (2 for drums)' vs '5 wedges' — is not a
    conflict; '3 wedges' vs '5 wedges' is). Whole tokens, not substrings
    (review 2026-09-14, judgment call 6: '5' inside '15' used to hide a diff)."""
    tf = _tokens(f_text)
    return bool(tf) and not tf <= _tokens(e_text)


def _compare_cell(ctx, t_tc, f_tc, e_tc, section, column):
    key = f"{section}|{column or ''}"
    tT, tF, tE = _t(_tc_text(t_tc)), _t(_tc_text(f_tc)), _t(_tc_text(e_tc))
    if tF == tT:
        # the pipeline has nothing for this cell; keep ownership only if the
        # doc still reads what we last wrote
        if key in ctx.prov and ctx.prov[key] == tE:
            ctx.newprov[key] = tE
        return
    if tE == tF:
        ctx.newprov[key] = tF
        return
    cell_owned = tE == tT or ctx.prov.get(key) == tE
    pT, pF, pE = _tc_paras(t_tc), _tc_paras(f_tc), _tc_paras(e_tc)
    if (not any(_has_table(x) for x in (t_tc, f_tc, e_tc))
            and len(pT) == len(pF) == len(pE) and len(pT) > 1):
        owned_paras = []
        for i, (a, b, c) in enumerate(zip(pT, pF, pE)):
            ta, tb, tc_ = _t(_p_text(a)), _t(_p_text(b)), _t(_p_text(c))
            pk = f"{key}|{i}"
            if tb == ta:
                if pk in ctx.prov and ctx.prov[pk] == tc_:
                    ctx.newprov[pk] = tc_
                continue
            if tc_ == tb:
                ctx.newprov[pk] = tb
                continue
            if tc_ == ta or cell_owned or ctx.prov.get(pk) == tc_:
                c.addprevious(ctx.prepare_copy(b))
                c.getparent().remove(c)
                ctx.newprov[pk] = tb
                ctx.changed += 1
            elif _differs_meaningfully(tc_, tb):
                ctx.notice(section, column, _p_text(c).strip(), _p_text(b).strip())
        return
    if cell_owned:
        _replace_tc_content(ctx, e_tc, f_tc)
        ctx.newprov[key] = tF
        ctx.changed += 1
    elif _differs_meaningfully(tE, tF):
        ctx.notice(section, column, _tc_text(e_tc).strip(), _tc_text(f_tc).strip())


def _rows_by_key(table, label_fn):
    out, counts = {}, {}
    for row in table.rows:
        lab = label_fn(row)
        n = counts.get(lab, 0)
        counts[lab] = n + 1
        out[(lab, n)] = row
    return out


def _grid_label(row):
    tcs = row._tr.tc_lst
    return daysheet.norm(_tc_text(tcs[0])) if tcs else ""


def _act_names(E_grid):
    """column index -> band name as the filed doc shows it (for notices)."""
    names = {}
    for row in E_grid.rows:
        tcs = row._tr.tc_lst
        if not tcs or _t(_tc_text(tcs[0])):
            continue
        for i, tc in enumerate(tcs[1:], start=1):
            paras = _tc_paras(tc)
            if len(paras) >= 2 and _t(_p_text(paras[1])):
                names[i] = _t(_p_text(paras[1]))
        if names:
            break
    return names


def merge(T, F, E, prov=None):
    """Update E (filed doc) from F (fresh build): blank cells and cells the
    pipeline itself last wrote (per `prov`) take the fresh value; anything a
    person typed is left alone and reported. Returns
    (changes_made, notices, new_provenance)."""
    ctx = _Ctx(T, F, E, prov=prov)

    gT, gF, gE = daysheet.find_grid(T), daysheet.find_grid(F), daysheet.find_grid(E)
    if gT is not None and gF is not None and gE is not None:
        rT, rF, rE = (_rows_by_key(g, _grid_label) for g in (gT, gF, gE))
        names = _act_names(gE)
        for key, t_row in rT.items():
            f_row, e_row = rF.get(key), rE.get(key)
            if f_row is None or e_row is None:
                continue
            tT, tF, tE = t_row._tr.tc_lst, f_row._tr.tc_lst, e_row._tr.tc_lst
            if not (len(tT) == len(tF) == len(tE)):
                continue
            section = _t(_tc_text(tT[0])).rstrip(":") or "Act names"
            for i in range(1, len(tT)):
                col = None if len(tT) == 2 else (names.get(i) or SLOT_COL_NAMES.get(i))
                _compare_cell(ctx, tT[i], tF[i], tE[i], section, col)

    lT, lF, lE = daysheet.find_lead_table(T), daysheet.find_lead_table(F), daysheet.find_lead_table(E)
    if lT is not None and lF is not None and lE is not None:
        for ri in range(min(len(lT.rows), len(lF.rows), len(lE.rows))):
            a, b, c = lT.rows[ri]._tr.tc_lst, lF.rows[ri]._tr.tc_lst, lE.rows[ri]._tr.tc_lst
            if len(a) >= 2 and len(b) >= 2 and len(c) >= 2:
                _compare_cell(ctx, a[1], b[1], c[1], _t(_tc_text(a[0])) or "Lead", None)

    sT, sF, sE = (daysheet.find_schedule_table(d) for d in (T, F, E))
    if sT is not None and sF is not None and sE is not None:
        def labels(tbl):
            return [daysheet.norm(_tc_text(r._tr.tc_lst[-1])) for r in tbl.rows if r._tr.tc_lst]
        LT, LF, LE = labels(sT), labels(sF), labels(sE)

        def all_times_blank_like_template(tbl_e):
            for re_, rt in zip(tbl_e.rows, sT.rows):
                if _t(_tc_text(re_._tr.tc_lst[0])) != _t(_tc_text(rt._tr.tc_lst[0])):
                    return False
            return True

        def times_owned(tbl_e):
            for i, re_ in enumerate(tbl_e.rows):
                v = _t(_tc_text(re_._tr.tc_lst[0]))
                if v and ctx.prov.get(f"Schedule|row{i}") != v:
                    return False
            return True

        if LF != LT and LE == LT and (all_times_blank_like_template(sE) or times_owned(sE)):
            # a locked series schedule replaces the template rows wholesale
            tbl_el = sE._tbl
            for r in list(sE.rows):
                tbl_el.remove(r._tr)
            for i, r in enumerate(sF.rows):
                tbl_el.append(ctx.prepare_copy(r._tr))
                ctx.newprov[f"Schedule|row{i}"] = _t(_tc_text(r._tr.tc_lst[0]))
            ctx.changed += 1
        elif LE == LF:
            base = sT if LF == LT else sF
            for i, (rb, rf, re_) in enumerate(zip(base.rows, sF.rows, sE.rows)):
                label = _t(_tc_text(rf._tr.tc_lst[-1]))
                t_tc = rb._tr.tc_lst[0] if LF == LT else _blank_like(rf._tr.tc_lst[0])
                _compare_cell(ctx, t_tc, rf._tr.tc_lst[0], re_._tr.tc_lst[0],
                              f"Schedule: {label}", None)
                v = _t(_tc_text(re_._tr.tc_lst[0]))
                if v and ctx.prov.get(f"Schedule|row{i}") == v:
                    ctx.newprov[f"Schedule|row{i}"] = v
    return ctx.changed, ctx.notices, ctx.newprov


def all_acts_cancelled(ev, acts):
    """Every act on this bill has its show cancelled (review 2026-09-14, M4)
    -> the filed doc is renamed with a CANCELLED marker. One cancelled band
    on a multi-band bill only blanks its own column (daysheet.build)."""
    ids = [a.get("artist_id") for a in acts if a.get("artist_id")]
    if not ids or not ev.get("event_date"):
        return False
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT artist_id FROM shows WHERE venue=%s AND show_date=%s
                       AND cancelled_at IS NOT NULL AND artist_id = ANY(%s)""",
                    (ev.get("venue"), ev.get("event_date"), ids))
        cancelled = {r["artist_id"] for r in cur.fetchall()}
    return all(i in cancelled for i in ids)


def _blank_like(tc):
    """A stand-in 'template' cell with no text, for locked-schedule rows that
    have no pristine template equivalent."""
    new = copy.deepcopy(tc)
    for t in new.iter(qn("w:t")):
        t.text = ""
    return new


# ── filing ──────────────────────────────────────────────────────────────────

def _atomic_save(doc, dest, expect_sha=None):
    """Save `doc` to `dest` via a temp file in the same folder. If
    expect_sha is given and the file on disk no longer matches it (someone
    saved it while we were working), abort — never clobber."""
    dest = Path(dest)
    tmp = dest.parent / f".~advtmp-{os.getpid()}-{dest.name}"
    doc.save(str(tmp))
    if expect_sha is not None and dest.exists() and sha256_file(dest) != expect_sha:
        tmp.unlink(missing_ok=True)
        return False
    if word_lock_present(dest):
        tmp.unlink(missing_ok=True)
        return False
    os.replace(tmp, dest)
    return True


def _rel_to_root(path):
    try:
        return str(Path(path).relative_to(fs.real_dropbox_root()))
    except ValueError:
        return str(path)


def _abs_from_reg(p):
    p = Path(p)
    return p if p.is_absolute() else fs.real_dropbox_root() / p


def locate(cur, venue, event_date, key, n_events_same_day=1):
    """The registry row for this show's doc, or None. Exact key first; if
    the event name was edited (key changed) and this venue+date has only
    one registered doc and one event, that doc is still this show's."""
    row = db.get_filed_doc(cur, venue, event_date, key)
    if row:
        return row
    rows = db.filed_docs_for(cur, venue, event_date)
    if len(rows) == 1 and n_events_same_day == 1:
        return rows[0]
    return None


def _find_moved_doc(folder, d, reg):
    """The doc a registry row points at, after someone renamed it: first a
    file with the exact recorded hash, else the single date-stamped doc in
    the folder that no other registry row claims."""
    if not folder.exists():
        return None
    cands = sorted(folder.glob(f"{d.strftime('%m%d%y')} * Prod Adv.docx"))
    if reg.get("sha256"):
        for c in cands:
            if sha256_file(c) == reg["sha256"]:
                return c
    with db.get_conn() as conn, conn.cursor() as cur:
        claimed = {(_abs_from_reg(r["path"])).name for r in db.filed_docs_for(cur, reg["venue"], d)
                   if r["id"] != reg["id"]}
    free = [c for c in cands if c.name not in claimed]
    return free[0] if len(free) == 1 else None


def file_event_doc(eid, ev, acts, stem, stageplot_names=None, today=None, dry_run=False,
                   n_events_same_day=1):
    """Create or merge-fill this event's filed doc. Returns a result dict:
    action in created|merged|unchanged|locked|past|conflict|dry-run, path,
    notices (list), hand_edited (bool), renamed_from (str|None)."""
    today = today or dt.date.today()
    d = ev.get("event_date")
    res = {"action": None, "path": None, "notices": [], "hand_edited": False,
           "renamed_from": None, "filled": 0}
    if not d:
        res["action"] = "no-date"
        return res
    if d < today:
        res["action"] = "past"
        return res
    venue = ev.get("venue")
    folder = fs.real_dropbox_root() / fs.real_venue_folder(venue) / fs.real_month_folder(venue, d)
    desired = folder / f"{stem}.docx"
    key = event_key(ev)

    with db.get_conn() as conn, conn.cursor() as cur:
        reg = locate(cur, venue, d, key, n_events_same_day)
    existing = None
    if reg and _abs_from_reg(reg["path"]).exists():
        existing = _abs_from_reg(reg["path"])
    elif desired.exists():
        existing = desired
    elif reg:
        # registered doc is gone from where we left it — most likely a person
        # renamed or moved it within the month folder. Adopt the one
        # unregistered doc for this date rather than creating a duplicate.
        existing = _find_moved_doc(folder, d, reg)
    res["path"] = str(existing or desired)

    fresh, _event, _acts, _n = daysheet.build(eid, stageplot_names=stageplot_names or {})

    if existing is None:
        res["action"] = "created"
        if dry_run:
            return res
        folder.mkdir(parents=True, exist_ok=True)
        if not _atomic_save(fresh, desired):
            res["action"] = "locked"
            return res
        # provenance of a freshly created doc: every cell that differs from
        # the template is the pipeline's (merge of the fresh doc against
        # itself records exactly those)
        _c, _n, prov = merge(T := Document(str(daysheet.UNIVERSAL_TEMPLATE)),
                             Document(str(desired)), Document(str(desired)))
        with db.get_conn() as conn, conn.cursor() as cur:
            db.upsert_filed_doc(cur, venue, d, key, _rel_to_root(desired), sha256_file(desired),
                                cells=prov)
            conn.commit()
        res["path"] = str(desired)
        return res

    if word_lock_present(existing):
        res["action"] = "locked"
        return res

    before_sha = sha256_file(existing)
    res["hand_edited"] = bool(reg and reg.get("sha256") and reg["sha256"] != before_sha)
    E = Document(str(existing))
    T = Document(str(daysheet.UNIVERSAL_TEMPLATE))
    changed, notices, newprov = merge(T, fresh, E, prov=(reg or {}).get("cells") or {})
    res["notices"] = notices
    res["filled"] = changed
    res["action"] = "merged" if changed else "unchanged"
    if dry_run:
        return res

    target = existing
    if changed:
        if not _atomic_save(E, existing, expect_sha=before_sha):
            res["action"] = "conflict"
            return res
    # rename in place when the display name changed — never a second copy
    if existing.name != desired.name and not desired.exists():
        folder.mkdir(parents=True, exist_ok=True)
        os.rename(existing, desired)
        res["renamed_from"] = existing.name
        target = desired
    res["path"] = str(target)
    with db.get_conn() as conn, conn.cursor() as cur:
        new_sha = sha256_file(target)
        # keep the recorded hash as "what the pipeline last wrote" — only
        # refresh it when the pipeline itself wrote (or first registers)
        if changed or not reg:
            db.upsert_filed_doc(cur, venue, d, key, _rel_to_root(target), new_sha,
                                seeded=not reg and not changed, reg_id=(reg or {}).get("id"),
                                cells=newprov)
        else:
            db.upsert_filed_doc(cur, venue, d, key, _rel_to_root(target), reg.get("sha256"),
                                reg_id=reg.get("id"), keep_written_at=True, cells=newprov)
        conn.commit()
    return res


def file_stage_plot(src, folder, fname, dry_run=False):
    """Copy a band's uploaded plot next to the doc. Never overwrites a
    different existing plot: a changed upload is saved alongside as
    '<stem> (updated MMDDYY-HHMM)<ext>' and reported. Returns
    (filed_name, notice_or_None)."""
    folder = Path(folder)
    dest = folder / fname
    if dry_run:
        return fname, None
    folder.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy(src, dest)
        return fname, None
    if filecmp.cmp(src, dest, shallow=False):
        return fname, None
    stem, ext = Path(fname).stem, Path(fname).suffix
    for p in folder.glob(f"{stem} (updated *){ext}"):
        if filecmp.cmp(src, p, shallow=False):
            return fname, None
    alt = f"{stem} (updated {dt.datetime.now().strftime('%m%d%y-%H%M')}){ext}"
    shutil.copy(src, folder / alt)
    return fname, {"field": "Stage plot file", "doc_value": fname,
                   "new_value": f"new upload saved as {alt}"}


def record_and_email_notices(results, send_mail=True):
    """results: [(ev, res)]. Stores each notice once (doc_notices), then
    queues ONE digest item with the notices not reported before (review
    2026-09-14, E1: these ride the 7am digest and the dashboard's "Needs
    you" panel, not their own email). Returns the number of new notices."""
    import mailer
    inserted = 0
    with db.get_conn() as conn, conn.cursor() as cur:
        for ev, res in results:
            for n in res.get("notices") or []:
                nid = db.insert_doc_notice(cur, ev.get("venue"), ev.get("event_date"),
                                           event_key(ev), "diff", n["field"],
                                           n.get("new_value") or "", n.get("doc_value") or "",
                                           detail=Path(res.get("path") or "").name
                                           + (" (hand-edited)" if res.get("hand_edited") else ""))
                if nid:
                    inserted += 1
        conn.commit()
        pending = db.unnotified_doc_notices(cur)
    if not pending or not send_mail:
        return inserted
    new = pending
    rows = []
    for n in new:
        where = (f"{mailer.esc(n['venue'])} {n['event_date'].strftime('%m/%d')} — "
                 f"{mailer.esc(n.get('detail'))}")
        edited = ""
        rows.append(
            f"<tr><td style='padding:6px 10px;vertical-align:top'>{where}{edited}</td>"
            f"<td style='padding:6px 10px;vertical-align:top'><b>{mailer.esc(n['field'])}</b></td>"
            f"<td style='padding:6px 10px;vertical-align:top;white-space:pre-wrap'>{mailer.esc(n.get('doc_value'))}</td>"
            f"<td style='padding:6px 10px;vertical-align:top;white-space:pre-wrap'>{mailer.esc(n.get('new_value'))}</td></tr>")
    html = ("<div style='font-family:-apple-system,sans-serif;font-size:13px'>"
            "<p>These filed advance docs were <b>not changed</b> — the doc already has a value, "
            "and newer info came in that's different. Update the doc by hand if the new value is right.</p>"
            "<table style='border-collapse:collapse' border='1' cellspacing='0'>"
            "<tr><th>Show / doc</th><th>Field</th><th>Doc says</th><th>New info</th></tr>"
            + "".join(rows) + "</table></div>")
    with db.get_conn() as conn, conn.cursor() as cur:
        db.queue_digest_item(cur, "doc", f"Advance doc changes to review — {len(new)} field(s)", html)
        db.mark_doc_notices_notified(cur, [n["id"] for n in new])
        conn.commit()
    return inserted
