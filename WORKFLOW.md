# Daily Workflow — langkah pipeline harian (dipakai cron)

Target audiens dan semua parameter dibaca dari `config.yaml`.
Jangan membuat posting parsial: bila satu langkah gagal total, berhenti dan laporkan.

## 1. Generate video

`media.generate_video`, 9:16 vertikal ±10 detik. Pertahankan DNA gaya,
variasikan scene tiap hari (formasi awan, warna dedaunan, dawn vs golden-hour light).

Prompt default:

> Vertical 9:16 video, dreamy AI digital art style: low-angle upward view of a
> dramatic deep-blue sky filled with volumetric white and golden clouds, sun
> peeking through tree branches with a warm lens flare, natural frame of tree
> canopy at the edges, hyper-saturated colors, high contrast, golden-hour glow,
> serene surreal fantasy mood. Camera is completely still and static with no
> movement and no zoom; only the clouds drift slowly and naturally. Audio:
> calming nostalgic ambient soundscape, soft and dreamy, no human voices, no
> speech, no singing. No text, no watermark

## 2. Watermark

Kecil, transparan, tengah bawah (sesuaikan dari `config.yaml`):

```bash
ffmpeg -y -i INPUT -vf "drawtext=fontfile=/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf:text='@volumarc':fontsize=20:fontcolor=white@0.4:x=(w-text_w)/2:y=h-80" -c:v libx264 -preset medium -crf 20 -c:a copy OUTPUT.mp4
```

## 3. Upload ke Google Drive & publikasikan

- Upload file watermark ke folder media (id folder dari `config.yaml`):
  `hatch_gws_cli drive +upload ...` (lihat `drive +upload --help`; path lokal
  harus absolut dan di dalam home directory).
- Jadikan publik ("anyone with the link"):
  `hatch_gws_cli drive permissions create --params '{"fileId":"<id>"}' --json '{"type":"anyone","role":"reader"}'`
- URL publik untuk Buffer: `https://drive.google.com/uc?export=download&id=<fileId>`
- Verifikasi: `curl -s -o /dev/null -w "%{http_code} %{content_type}\n" "<url>"`
  harus HTTP 200 dan bertipe video. Bila Drive menampilkan halaman konfirmasi,
  coba ulang atau gunakan file lebih kecil.
- Nama file: `sky-reel-<N>.mp4`, N berurutan (cek isi folder dulu supaya tidak duplikat).

## 4. Caption

Tulis caption segar sesuai `config.yaml` (default: Inggris, menarik,
3 hashtag), beda dari hari-hari sebelumnya. Satu caption per slot.

## 5. Schedule via Buffer

Untuk "hari ini" dalam zona waktu target. Slot default: 12:00 UTC (=08:00 ET)
dan 23:00 UTC (=19:00 ET). Bila slot sudah lewat saat dijalankan, geser ke
besok — jangan pernah menjadwalkan di masa lalu.

Untuk SETIAP slot, buat satu posting per channel:

```bash
python3 bin/buffer.py create-post --service <facebook|instagram|tiktok> \
  --channel <channel-id> --text "<caption>" --video-url <url> --due-at <ISO-8601 UTC>
```

- facebook → metadata otomatis `{facebook: {type: "reel"}}`
- instagram → metadata otomatis `{instagram: {type: "reel", shouldShareToFeed: true, isAiGenerated: true}}`
- tiktok → metadata otomatis `{tiktok: {isAiGenerated: true}}`

Setiap posting harus mengembalikan `PostActionSuccess` berstatus `scheduled`.
Gagal → coba sekali lagi dengan input dikoreksi; masih gagal → laporkan dan lanjutkan sisanya.

## 6. Catat & laporkan

- Append satu baris ke log harian: tanggal, file video, ID posting.
- Laporan akhir: video yang dibuat, posting terjadwal + jamnya, caption yang dipakai,
  dan kegagalan bila ada. Kirim juga ke kanal laporan sesuai `config.yaml`.
