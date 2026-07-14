# 3CDC SOP & Document Design Standards

This file documents the design language, formatting rules, tone standards, and component specs established across all 3CDC SOP and production documents. Load this into any project to ensure consistency.

---

## Brand Colors

| Role | Name | Hex |
|---|---|---|
| Primary accent | 3CDC Red | `#C8202E` |
| Secondary accent | Yellow-Green | `#A8B400` |
| Tertiary accent | Sky Blue | `#5BA4CF` |
| Quaternary accent | Light Grey | `#B0B3B5` |
| Body text / dark elements | Dark Grey | `#444444` |
| Page background / tile bg | Off White | `#F7F7F7` |
| Danger background | Light Red | `#FFF0F0` |
| Warning background | Light Amber | `#FFF8E8` |
| Success background | Light Blue | `#F0F7FF` |
| Warning border | Amber | `#E07800` |
| Danger border | Red | `#C8202E` |

The four brand colors always appear in order: **Red → Yellow-Green → Sky Blue → Light Grey**. This order is used in the color bar, the 3CDC logo, and any multi-color decorative elements.

---

## The 3CDC Logo (Styled Text)

The 3CDC logo is always rendered as styled text using `Helvetica-Bold`, not as an image file. Each character gets its brand color:

| Character | Color |
|---|---|
| 3 | `#C8202E` (Red) |
| C | `#A8B400` (Yellow-Green) |
| D | `#5BA4CF` (Sky Blue) |
| C | `#B0B3B5` (Light Grey) |

The full organization name "Cincinnati Center City Development Corporation" appears below the logo in a smaller muted typeface.

---

## Color Bar

A four-segment color bar appears at the **top and bottom** of every PDF document. Each segment is one of the four brand colors in order. The leftmost segment has rounded left corners, the rightmost has rounded right corners; middle segments are rectangular with no rounding.

Bar height: `6pt` for footers, up to `22pt` for prominent header bars.

---

## Typography

All PDFs use the **Helvetica family** exclusively. No mixing of font families within a document.

| Use | Font | Size |
|---|---|---|
| Document title | Helvetica-Bold | 18pt |
| Section headers | Helvetica-Bold | 12pt |
| Step numbers | Helvetica-Bold | 11pt |
| Body text | Helvetica | 10pt |
| Captions | Helvetica-Oblique | 9pt |
| Small labels / tags | Helvetica-Bold | 7.5–8pt |
| Footer | Helvetica | 8pt |

Line height for body text is `15pt`. Step descriptions use `14–15pt` leading.

---

## Page Layout

- **Page size:** US Letter (8.5 × 11 inches)
- **Orientation:** Portrait unless explicitly specified otherwise
- **Margins:** 0.75" left/right, 0.5" top, 0.75" bottom
- **Content width:** `pw = letter[0] - 1.5"` (approximately 7 inches)
- All content is built with ReportLab `SimpleDocTemplate` using `Platypus` flowables
- `KeepTogether` is used on every step row + its screenshot to prevent page breaks splitting content

---

## Document Structure (Standard Order)

Every SOP PDF follows this section order:

1. **Top color bar** — four-segment brand bar
2. **Header** — 3CDC logo (left) + document title + subtitle (right), side by side in a table
3. **Horizontal rule** — `0.5pt`, Light Grey
4. **Overview section** — info table with task name, purpose, who performs it, contact
5. **Body sections** — varies by document (procedure steps, equipment reference, etc.)
6. **Quick Reference table** — condensed one-line summary of key info
7. **Contact section** — always `Blloyd@3cdc.org` unless otherwise specified
8. **Horizontal rule** — `0.5pt`, Light Grey
9. **Footer line** — "3CDC · [Document Name] · Last Revised: [Month Year]"
10. **Bottom color bar** — same as top

---

## Section Header Blocks

Section headers are full-width colored bands with white bold text. Default color is `#C8202E` (Red). Alternative colors used by context:

- **Red** — primary procedure sections, overview, contact
- **Sky Blue** — informational/reference sections, access/navigation
- **Yellow-Green** — input/action sections (e.g. "How to Add a Message")
- **Dark Grey** — notes, tips, quick reference, "things to keep in mind"
- **Navy / Dark** — phase headers within multi-phase SOPs

Padding: `5pt` top/bottom, `10pt` left/right. Font: Helvetica-Bold 12pt, white.

---

## Step Rows

Numbered steps use a two-column table:

- **Left cell:** colored circle with step number, centered, `0.38"` wide. Background matches the section accent color.
- **Right cell:** bold title on line 1, description text on line 2. Background `#F7F7F7`.
- Row border: `0.5pt` `#DDDDDD`. Bottom rule between rows: `0.5pt` `#DDDDDD`.
- Padding: `7–8pt` top/bottom, `10pt` left on text cell.
- Step number style: Helvetica-Bold 11pt, white, `TA_CENTER`.

Step number color coding by context:
- **Sky Blue** — general navigation/action steps
- **Mood Media Red (`#DC1E1E`)** — steps performed within the Mood Media portal
- **Red (`#C8202E`)** — critical/safety steps
- **Yellow-Green** — review/check steps
- **Amber (`#8B4500`)** — wind/evacuation protocol steps
- **Light Grey** — final/completion steps

---

## Info Tables

Two-column key/value tables used for overview blocks and quick reference:

- Left column (key): `1.8"` wide, background `#EFEFEF`, bold text
- Right column (value): remaining width, white background, regular text
- Row dividers: `0.5pt` `#DDDDDD`
- Outer border: `0.5pt` `#CCCCCC`
- Padding: `5–6pt` all sides, `8pt` left/right
- Vertical alignment: TOP

---

## Warning and Note Boxes

**Danger box (red):**
- Background: `#FFF0F0`
- Border: `1.5pt` solid `#C8202E`
- Text: Helvetica-Bold 10pt, red
- Prefix: `"WARNING:  "`
- Used for safety-critical instructions (e.g. power off before opening cabinet)

**Note/warning box (amber):**
- Background: `#FFF8E8`
- Border: `1.5pt` solid `#E07800`
- Text: Helvetica-Bold 9pt, dark amber `#664400`
- Prefix: `"NOTE:  "`
- Used for important but non-critical caveats (e.g. update delay, timing notes)

All warning/note boxes are wrapped in `KeepTogether`.

---

## Screenshots and Reference Photos

**Hard rule: never use AI-generated or placeholder UI mockups.** All screenshots must be actual captures from the real application or device being documented.

- Screenshots are always wrapped in a `1pt #DDDDDD` border box
- Captions appear below each image in 9pt Helvetica-Oblique, centered
- Caption format: `"Fig. N — [description of what is shown and what to do]"`
- Images are scaled to fit within page width (`pw`) with a max height cap (typically `2.4–2.6"` for landscape screenshots, `3.0–3.2"` for portrait)
- Portrait screenshots (e.g. phone screens) are displayed at reduced width, centered
- Landscape screenshots are displayed full page width
- Side-by-side photo pairs use a two-column table with `(pw-8)/2` per column and `4pt` padding
- All images are wrapped in `KeepTogether` with their caption to prevent orphaned captions

---

## Flowcharts

Flowcharts are delivered as **HTML files** (not PDFs) for web/browser rendering, with a print-safe CSS `@media print` block so they can be saved as PDF directly from the browser.

### Flowchart Structure

- **Header** — same dark background, 3CDC logo in brand colors, title, subtitle. Bottom 5px gradient bar in brand colors.
- **Legend** — colored dots identifying node types, centered below header
- **Chart** — max-width 780px, centered, `flex-direction: column`, `align-items: center`
- **Footer** — "3CDC · [Title] · Questions? Blloyd@3cdc.org · Last Revised: [Month Year]"

### Node Types

| Type | Background | Left border / accent | Used for |
|---|---|---|---|
| Start / End pill | Dark `#2A2A2A` / Red `#C8202E` | none (pill shape, `border-radius: 999px`) | First and last nodes |
| Action node | White | 5px Sky Blue | Standard navigation/action steps |
| Decision diamond | Red `#C8202E` | clip-path diamond | Yes/No branch points |
| Check node | White | 5px Yellow-Green | Review or verification steps |
| Danger/warning node | `#FFF0F0` | 5px Red | Safety-critical steps |
| Success node | `#F0F7FF` | 5px Sky Blue | Confirmation/completion steps |
| Wait node | White | 5px Light Grey | Delay or system-wait steps |
| Safety box | `#FFF0F0` | `2px solid Red` full border | Pre-step safety warnings (not numbered) |
| Note box | Dark `#2A2A2A` | none | End-of-flow informational notes, dark bg with yellow accent text |

### Node Number Badges

- `32px × 32px` circle, `border-radius: 50%`
- Font: DM Mono 13px bold, white
- Color matches the node's accent color

### Branch Rows (Decision splits)

- Two-column flex layout, `gap: 16px`
- Left branch label: green pill (`#E8F4E8` bg, `#2E7D32` text) for "Yes" paths
- Right branch label: red pill (`#FDECEA` bg, Red text) for "No" paths
- Branch node cards: `border-radius: 10px`, left accent border `4px`, white background

### Connectors

- Vertical line: `2px` wide, Light Grey `#B0B3B5`, `opacity: 0.5`
- Arrowhead: triangle pointing down, same grey

### Animation

- Nodes fade up on load: `opacity: 0 → 1`, `translateY(18px → 0)`, `0.45s forwards`
- Staggered delays: `0.05s` increments per child element
- All animations disabled in `@media print`

### Page Break Rules (print CSS)

All node types, connectors, branch rows, and note boxes have:
```css
page-break-inside: avoid;
break-inside: avoid;
```
Connectors immediately following a node also have `page-break-before: avoid` to prevent orphaned arrows.

---

## Tone & Voice Standards

These apply to all 3CDC internal SOPs and staff-facing documents.

- **Collegial, not corporate.** Write like a knowledgeable colleague, not a policy document or a help desk.
- **Direct and clear.** No filler phrases, no over-explaining basics to people who already know their jobs.
- **Warm but not excessive.** A small number of friendly phrases is fine. Avoid exclamation points except sparingly. Never use more than one per paragraph.
- **No content guidance.** Don't tell staff how to do their creative jobs (e.g. don't say "keep messages on brand" in a messaging SOP — they know).
- **No customer-service tone.** Phrases like "We're happy to help!" or "You're all set!" are too much. Use plain language: "Reach out to Blloyd@3cdc.org with questions."
- **Assume competence.** Don't explain what a venue is to venue staff. Don't explain what the LED board displays to marketing staff.
- **Safety language is an exception.** Safety warnings can and should be direct and firm: "Do not skip this step."

---

## Credentials & Passes (Vehicle Pass / Badges)

- **Background:** White — clean credential style
- **Outer border:** `2.5pt` Dark Grey, `border-radius: 14`
- **Top and bottom color bars:** four-segment brand bar
- **3CDC logo:** large styled text, centered, at top
- **Main banner:** full-width dark grey rounded rectangle, white bold text, all caps
- **Name:** large bold, centered, with a red accent rule underneath
- **Venue tiles:** five equal-width tiles in a row, each with its own brand color accent strip at top, venue name in bold inside
- **Vertical centering:** all content is mathematically centered on the page using total content height calculation

---

## Training / Passport Documents

- Two-column layout for checklist sections (fits more on one page)
- Section headers include a numbered pill badge and colored left accent stripe
- Each checklist item has alternating row tint (`#F7F7F7`)
- Trainer sign-off box: `0.16"` square, rounded corners, Light Grey border, right-aligned per row
- Completion sign-off block at the bottom: Employee Signature, Date Completed, Trainer Signature
- Fields use a simple underline style (no boxes)

---

## Default Contact

Unless otherwise specified, all documents use:

```
Brian Lloyd
Blloyd@3cdc.org
(315) 404-5648
Events & Production | 3CDC
```

---

## File Naming Convention

| Document type | Filename pattern |
|---|---|
| SOP PDF | `[Venue_or_System]_SOP.pdf` |
| Flowchart HTML | `[Venue_or_System]_Flowchart.html` |
| Vehicle / credential pass | `3CDC_[Type]_Pass.pdf` |
| Training passport | `3CDC_[Team]_Passport.pdf` |

---

## Tools & Libraries

All PDFs are generated with **Python + ReportLab** using the Platypus framework.
All flowcharts are HTML with vanilla CSS and the **DM Sans + DM Mono** Google Fonts.
Screenshots are processed with **Pillow (PIL)** for resizing and annotation.

---

*Last updated: June 2026*
