-- 2026-09-15 — a booking edited in the app has to reach advance-list.xlsx.
--
-- seed_bookings/append_bookings only ever APPENDED new bookings. An edit
-- updated the bookings table and stopped there, so the next pipeline run —
-- which rebuilds events/acts from the SHEET — quietly reinstated the old
-- values. That was cosmetic staleness until 2026-09-15; now the sheet's Start
-- column also decides who is Artist 1/2/3, so a stale row reorders the bill.
-- Caught live: Brian's own Cincy Steel correction (9/20) and Rob Keenan (9/23)
-- were both reverted by the next run.
--
-- Flag rather than a blanket reconcile: only a row somebody actually edited is
-- pushed back, so a value Brian typed straight into the sheet on an untouched
-- booking is never overwritten by the database.
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS sheet_dirty BOOLEAN NOT NULL DEFAULT false;
CREATE INDEX IF NOT EXISTS idx_bookings_sheet_dirty ON bookings (sheet_dirty)
    WHERE sheet_dirty;
