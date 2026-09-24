-- 2026-09-24 research #(b) — the two field-gap questions Brian picked out of
-- the 2026-09-16 audit's section (b) table. Both are promoted columns, mirroring
-- the vehicle_count / large_vehicle_count pattern right above them in
-- db/schema.sql: queried and dropped into the doc, so they don't live in `data`
-- JSONB alone.
--
-- trailer — the FSQ garage clears 6 ft 8 in and the welcome email says so, but
-- the form only ever asked for a COUNT of vehicles. A van towing a trailer is
-- ONE vehicle in that count, so nobody downstream learned it can't go in the
-- garage until it showed up. BOOLEAN, same shape as merch/own_iems (the form
-- posts "Yes"/"No", advance_db.to_bool promotes it).
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS trailer BOOLEAN;

-- crew_count — additive to performers, NOT a subset of it. performers keeps its
-- exact meaning and every downstream use (the day sheet's drink tix is still
-- performers x 2); crew is what parking validations, the stage escort and the
-- day sheet's headcount need on top of it.
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS crew_count INTEGER;

-- The FSQ parking digest that goes to Mtully is a stored snapshot, not a live
-- join (see advance_db.queue_fsq_parking) — the trailer flag has to be captured
-- with the counts or the digest can't show it.
ALTER TABLE fsq_parking_queue ADD COLUMN IF NOT EXISTS trailer BOOLEAN;
