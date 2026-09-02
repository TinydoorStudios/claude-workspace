#!/usr/bin/env python3
"""Graft the generated status sheet into the live advance-list workbook as a tab.

Runs on the Mac (openpyxl only, no database). It loads Brian's real
advance-list.xlsx, drops any old "Status" tab, and copies the freshly-built
advance-status.xlsx (values + styling + column widths) in as a second sheet —
right after "Advance List". His input tab is never touched.

  python3 merge_status.py --list advance-list.xlsx --status advance-status.xlsx
"""
import argparse
from copy import copy
from pathlib import Path

from openpyxl import load_workbook

SHEET = "Status"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True, type=Path, help="the live advance-list.xlsx")
    ap.add_argument("--status", required=True, type=Path, help="generated advance-status.xlsx")
    ap.add_argument("--sheet", default=SHEET)
    args = ap.parse_args()

    if not args.list.exists():
        raise SystemExit(f"no such workbook: {args.list}")
    if not args.status.exists():
        raise SystemExit(f"no status workbook to merge: {args.status}")

    wb = load_workbook(args.list)
    src = load_workbook(args.status).active

    if args.sheet in wb.sheetnames:
        del wb[args.sheet]
    # place the Status tab right after the input tab
    idx = 1 if len(wb.sheetnames) >= 1 else 0
    ws = wb.create_sheet(args.sheet, index=idx)

    for col, dim in src.column_dimensions.items():
        if dim.width:
            ws.column_dimensions[col].width = dim.width
    for r, dim in src.row_dimensions.items():
        if dim.height:
            ws.row_dimensions[r].height = dim.height
    ws.freeze_panes = src.freeze_panes

    for row in src.iter_rows():
        for cell in row:
            dst = ws.cell(row=cell.row, column=cell.column, value=cell.value)
            if cell.has_style:
                dst.font = copy(cell.font)
                dst.fill = copy(cell.fill)
                dst.border = copy(cell.border)
                dst.alignment = copy(cell.alignment)
                dst.number_format = cell.number_format

    wb.save(args.list)
    print(f"Merged '{args.sheet}' tab into {args.list.name} "
          f"({src.max_row - 1} advance row(s)).")


if __name__ == "__main__":
    main()
