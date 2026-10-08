# Volumarc Pipeline

Paket alur kerja siap pakai untuk menjalankan akun konten reels AI: **generate video → watermark → hosting GitHub → penjadwalan Buffer** ke Facebook, Instagram, dan TikTok.

## Cara pakai di instance Muse yang baru

1. Berikan repo ini ke Muse (paste link repo atau clone).
2. Muse membaca `SETUP-CHECKLIST.md` dan memandu setup langkah demi langkah:
   dialog aman untuk API key Buffer & token GitHub → verifikasi → pertanyaan intake.
3. Setelah setup selesai, Muse membuat jadwal harian otomatis sesuai `WORKFLOW.md`.

## Isi repo

- `SKILL.md` — definisi skill pipeline
- `SETUP-CHECKLIST.md` — daftar dialog kredensial & pertanyaan intake (dibaca Muse saat setup)
- `WORKFLOW.md` — langkah pipeline harian (dipakai cron)
- `config.example.yaml` — template konfigurasi (salin jadi `config.yaml`)
- `bin/buffer.py` — CLI Buffer GraphQL API (account, channels, create-post)
- `bin/gh.py` — CLI GitHub REST API (user, create-repo, upload)

## Prasyarat

- Akun Buffer dengan channel **Facebook Page, Instagram Business, TikTok** yang sudah
  dihubungkan manual di publish.buffer.com (tidak bisa via API).
- Buffer API key (publish.buffer.com → Settings → API).
- GitHub Personal Access Token (classic, scope `repo`).
- Instance Muse dengan tool `credentials.request_api_access` untuk dialog aman.
  Jangan pernah meminta key/token lewat chat.
