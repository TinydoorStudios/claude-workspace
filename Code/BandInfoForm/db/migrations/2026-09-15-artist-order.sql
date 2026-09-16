-- 2026-09-15 — Artist 1 / Artist 2 / Artist 3 replaces opener / direct support /
-- headliner (Brian). An act's position on the bill is no longer declared by
-- staff; it is DERIVED from its set start time — earliest is Artist 1, latest is
-- Artist 3 — so a band added later with an earlier start renumbers the bill by
-- itself, with nothing to copy and nothing to migrate.
--
-- Nothing is dropped. `slot` and `slot_order` stay as history on rows already
-- written; nothing writes them from here on, and no read path consults them.

-- Each act carries its own schedule now. These used to live on the EVENT as
-- "first non-empty value across the group's rows", which silently printed one
-- band's load-in/start/end against another band's rows on any multi-act bill.
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS set_start  TEXT;
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS set_end    TEXT;
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS load_in    TEXT;
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS soundcheck TEXT;

-- The act is identified by its artist, not by a slot name it no longer has.
ALTER TABLE event_acts ALTER COLUMN slot       DROP NOT NULL;
ALTER TABLE event_acts ALTER COLUMN slot_order DROP NOT NULL;
DROP INDEX IF EXISTS uq_event_acts_slot;
CREATE UNIQUE INDEX IF NOT EXISTS uq_event_acts_artist
    ON event_acts (event_id, artist_id);

-- Backfill each act's schedule from the booking row that created it: same
-- venue + date + series (series guards against a 3rd-party event sharing a
-- venue/date with an internal bill), artist matched on the same normalization
-- artists.match_key uses.
UPDATE event_acts ea
   SET set_start  = b.event_start,
       set_end    = b.event_end,
       load_in    = b.load_in,
       soundcheck = b.soundcheck
  FROM events e, artists a, bookings b
 WHERE ea.event_id = e.id
   AND a.id = ea.artist_id
   AND b.venue = e.venue
   AND b.event_date = e.event_date
   AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key
   AND lower(btrim(COALESCE(b.series, ''))) = lower(btrim(COALESCE(e.series, '')))
   AND ea.set_start IS NULL;
