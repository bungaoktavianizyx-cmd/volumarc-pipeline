# Setup Checklist — dibaca Muse saat setup di instance baru

Jalankan bagian A → B → C → D berurutan. Jangan meminta key/token lewat chat.

## A. Dialog kredensial (WAJIB via dialog aman)

1. **Buffer API key** — user membuatnya di publish.buffer.com → Settings → API.
   Panggil `credentials.request_api_access` dengan:
   provider `buffer`, api_hosts `["api.buffer.com"]`, auth_scheme `api_key`,
   placement `bearer_header`.
2. **GitHub token** — Personal Access Token (classic) di github.com/settings/tokens,
   scope `repo`.
   Panggil `credentials.request_api_access` dengan:
   provider `github`, api_hosts `["api.github.com"]`, auth_scheme `api_key`,
   placement `bearer_header`.

## B. Verifikasi otomatis (setelah dialog diisi)

1. Buffer: `bin/buffer.py account` → key valid bila mengembalikan email & organizations.
   `bin/buffer.py channels --org <orgId>` → catat channel ID untuk
   Facebook Page, Instagram, dan TikTok; pastikan `isDisconnected` false.
2. GitHub: `bin/gh.py user` → catat username.
3. Buat repo media (`bin/gh.py create-repo --name <nama>`), upload 1 file,
   verifikasi URL publik `https://raw.githubusercontent.com/<owner>/<repo>/main/<path>`
   mengembalikan HTTP 200.

## C. Pertanyaan intake (tanyakan ke user, satu per satu bila perlu)

1. Berapa posting per hari? (default: 2)
2. Jam posting & zona waktu target? (default: 08:00 & 19:00 US Eastern)
3. Style/prompt video, atau kirim video referensi? (default: dreamy sky — lihat WORKFLOW.md)
4. Bahasa & gaya caption, jumlah hashtag? (default: Inggris, menarik, 3 hashtag)
5. Watermark? teks, posisi, ukuran, transparansi? (default: kecil transparan tengah bawah)
6. Preferensi audio? (default: ambient calming/nostalgic, tanpa suara orang)
7. Channel & akun target apa saja? (harus sudah dihubungkan manual di Buffer)
8. Target audiens? (default: US)
9. Beri label AI-generated di platform? (default: ya, untuk kepatuhan)
10. Laporan harian dikirim ke mana? (default: chat; Telegram bila tersedia)
11. Jadwalkan pipeline otomatis? Jam berapa pipeline berjalan?
    (default: tiap hari 05:00 waktu zona target)
12. Repo GitHub untuk hosting media? (buat baru / pakai yang sudah ada)

## D. Finalisasi

1. Salin `config.example.yaml` → `config.yaml`, isi dari jawaban user.
2. Buat cron harian berisi langkah `WORKFLOW.md` (goal-owned bila ada goal).
3. Jalankan 1x manual sebagai uji coba; verifikasi semua posting berstatus `scheduled`.
