#!/bin/zsh
# Export each named .docx in $PAGES_DIR (default /private/tmp/memo-pages) to PDF via Word; print page counts.
D=${PAGES_DIR:-/private/tmp/memo-pages}; mkdir -p "$D"
for f in "$@"; do
  rm -f "$D/$f.pdf"
  osascript -e "with timeout of 150 seconds
tell application \"Microsoft Word\"
  set d to open file name \"$D/$f.docx\"
  delay 2
  save as d file name \"$D/$f.pdf\" file format format PDF
  close d saving no
end tell
end timeout" >/dev/null 2>&1
  python3 -c "import fitz;d=fitz.open('$D/$f.pdf');print('$f',len(d),'pages', repr(d[-1].get_text()[:80]) if len(d)>1 else '');d[0].get_pixmap(dpi=90).save('$D/$f.png')"
done
