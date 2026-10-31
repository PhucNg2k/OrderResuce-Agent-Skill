import { cpSync, mkdirSync } from 'node:fs';
mkdirSync('dist', { recursive: true });
cpSync('public', 'dist/public', { recursive: true });
cpSync('fixtures', 'dist/fixtures', { recursive: true });
