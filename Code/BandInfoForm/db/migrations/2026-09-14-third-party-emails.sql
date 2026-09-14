-- Brian, 2026-09-14: a 3rd-party booking sends the band nothing (welcome,
-- reminders, day-before, thank-you) unless staff opt it in. Idempotent.
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS band_emails BOOLEAN NOT NULL DEFAULT false;
