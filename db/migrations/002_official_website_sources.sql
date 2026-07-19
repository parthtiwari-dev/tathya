-- Adds official website source support for existing Supabase projects.
-- Run before seeding `pmindia-news-updates`.

alter type source_type add value if not exists 'official_website';
