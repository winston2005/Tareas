-- Migration: Add foto_perfil column to usuarios table
-- Date: 2026-01-03
-- Description: Adds profile photo support to user accounts

-- Add foto_perfil column if it doesn't exist
ALTER TABLE usuarios ADD COLUMN foto_perfil TEXT DEFAULT NULL;

-- Optional: Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_usuarios_foto_perfil ON usuarios(foto_perfil);
