-- ONE-TIME data fix, already applied to live 2026-09-14 with the review-pass
-- deploy. NOT a migration: deploy_app.command and tools/staging/setup.sh
-- never run db/oneoff/. Do not re-run. (Moved out of
-- db/migrations/2026-09-14-review.sql in the 2026-09-21 sweep — deploy
-- re-ran it on every deploy in UTC and pre-skipped live reminder tiers.)
SET timezone = 'America/New_York';
-- record fix: tier-7 pre-skips written before the `sent` column existed
UPDATE advance_reminders r SET sent = false
  FROM shows s WHERE s.id = r.show_id AND r.days_before = 7
   AND s.advance_draft_created_at IS NOT NULL
   AND (s.show_date - s.advance_draft_created_at::date) <= 7 AND r.sent;
-- M1 applied to in-flight shows: pre-skip any tier that would fire within
-- 48h of a welcome sent in the last 2 days (Amador Sisters tier 3 on 9/14)
INSERT INTO advance_reminders (show_id, days_before, sent)
SELECT s.id, t.tier, false
  FROM shows s CROSS JOIN (VALUES (7),(3),(1)) AS t(tier)
 WHERE s.advance_draft_created_at > now() - interval '2 days'
   AND s.responded_at IS NULL AND s.cancelled_at IS NULL
   AND t.tier > (s.show_date - s.advance_draft_created_at::date) - 2
ON CONFLICT (show_id, days_before) DO NOTHING;
