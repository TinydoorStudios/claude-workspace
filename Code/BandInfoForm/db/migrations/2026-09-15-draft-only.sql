-- 2026-09-15 — "Draft the advance email, don't send it" (Brian).
-- A safety net for the nights where something still needs checking before the
-- band hears from us: the welcome is created as a real Outlook draft in
-- Production@3cdc.org instead of being sent, and Brian sends it by hand.
-- Distinct from skip_welcome_email ("Manual band advance"), which means no
-- welcome exists at all because the band already emailed their details in.
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS draft_only BOOLEAN NOT NULL DEFAULT false;

-- Stamped when the welcome was put in the drafts folder rather than sent, so
-- the lifecycle doesn't redraft it every morning and Brian can see which shows
-- are waiting on him. Sending is still a human action in Outlook; nothing here
-- claims the band has been contacted.
ALTER TABLE shows ADD COLUMN IF NOT EXISTS advance_held_draft_at TIMESTAMPTZ;
