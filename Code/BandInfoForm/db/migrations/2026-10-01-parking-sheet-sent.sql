-- Washington Park garage parking sheet (Brian, 2026-10-01): stamped when the
-- sheet goes to the band, on the welcome or from the "Parking sheet not sent"
-- dashboard item, so it is never sent twice.
ALTER TABLE shows ADD COLUMN IF NOT EXISTS parking_sheet_sent_at TIMESTAMPTZ;
