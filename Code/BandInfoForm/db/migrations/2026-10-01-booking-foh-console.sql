-- FSQ FOH console pick (Brian, 2026-10-01): DiGiCo Quantum 225 (default) or iPad.
-- Chosen on /booking, read by daysheet._consoles_text into the Consoles row's dropdown.
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS foh_console TEXT;
