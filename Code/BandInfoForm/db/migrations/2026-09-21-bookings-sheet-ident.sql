-- 2026-09-21 sweep (IDENT-3): the identity (artist_name, venue, event_date)
-- a booking's advance-list.xlsx row was last WRITTEN under — stamped by
-- mark_bookings_seeded / mark_bookings_synced from the run's own snapshot.
--
-- edited_bookings used to rebuild that identity from booking_edits history
-- (earliest 'old' since synced_at). A second rename merged into a still-unsent
-- notice row (A->B synced, then B->C => {A->C}) or an edit-and-revert lost
-- the row the sheet actually had (B), so the sync couldn't find it, the
-- reconcile appended a second row, and the stale one re-minted a show that
-- got welcomed again.
--
-- Idempotent (re-run on every deploy). The backfill only fills rows whose
-- sheet row is known to match the booking right now (seeded, not dirty);
-- dirty rows keep the old reconstruction until their next sync stamps one.
-- Runs after 2026-09-15-sheet-writeback and 2026-09-16-sheet-removals, which
-- add sheet_dirty and synced_at.
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS sheet_ident JSONB;

UPDATE bookings
   SET sheet_ident = jsonb_build_object('artist_name', artist_name,
                                        'venue', venue,
                                        'event_date', to_char(event_date, 'YYYY-MM-DD'))
 WHERE sheet_ident IS NULL AND seeded_at IS NOT NULL AND NOT sheet_dirty;
