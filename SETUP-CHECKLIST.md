# Setup Checklist — dibaca Muse saat setup di instance baru

Jalankan bagian A → B → C → D berurutan. Jangan meminta key/token lewat chat.

## A. Kredensial & koneksi

1. **Buffer API key** (via dialog aman) — user membuatnya di publish.buffer.com → Settings → API.
   Panggil `credentials.request_api_access` dengan:
   provider `buffer`, api_hosts `["api.buffer.com"]`, auth_scheme `api_key`,
   placement `bearer_header`.
2. **Google Drive** (via konektor, bukan dialog) — jalankan `hatch_gws_cli drive status`.
   Bila belum terhubung dan ada `connect_url`, tampilkan sebagai
   `[Connect Google Drive](<connect_url>)` lalu berhenti dan tunggu user mengetuknya.
   Jangan mengarang URL sendiri.

## B. Verifikasi otomatis (setelah A selesai)

1. Buffer: `bin/buffer.py account` → key valid bila mengembalikan email & organizations.
   `bin/buffer.py channels --org <orgId>` → catat channel ID untuk
   Facebook Page, Instagram, dan TikTok; pastikan `isDisconnected` false.
2. Drive: `hatch_gws_cli drive status` → pastikan terhubung.
   Buat folder media (atau pakai yang sudah ada):
   `drive files create --params '{"ignoreDefaultVisibility":true}' --json '{"name":"<nama-folder>","mimeType":"application/vnd.google-apps.folder","parents":["root"]}'`
   Upload 1 file tes ke folder itu, lalu bagikan publik:
   `drive permissions create --params '{"fileId":"<id>"}' --json '{"type":"anyone","role":"reader"}'`
   URL langsung: `https://drive.google.com/uc?export=download&id=<fileId>` —
   verifikasi dengan curl harus HTTP 200 dan bertipe video.

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
12. Folder Google Drive untuk media? (buat baru / pakai yang sudah ada)

## D. Finalisasi

1. Salin `config.example.yaml` → `config.yaml`, isi dari jawaban user.
2. Buat cron harian berisi langkah `WORKFLOW.md` (goal-owned bila ada goal).
3. Jalankan 1x manual sebagai uji coba; verifikasi semua posting berstatus `scheduled`.
