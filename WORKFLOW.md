# Daily Workflow — langkah pipeline harian (dipakai cron)

Target audiens dan semua parameter dibaca dari `config.yaml`.
Jangan membuat posting parsial: bila satu langkah gagal total, berhenti dan laporkan.

## 0. Generate stock (opsional — bila `stock.enabled: true` di config)

Sebelum pipeline harian berjalan, timbun video dulu dengan cron terpisah:
- Tiap `interval_minutes` (default 6), generate `batch_size` video
  (default 6, maksimal 6 per run).
- Prompt tiap video dibuat unik secara kombinatorial
  (adegan × cahaya × cuaca × elemen gerak); tiap kombinasi yang dipakai dicatat
  di `manifest.jsonl` supaya tidak ada video kembar.
- Tiap batch memakai lock file: bila batch sebelumnya masih jalan, tunggu
  1 menit → cek lagi → masih jalan, tunggu 1 menit lagi → masih juga, skip
  siklus ini (jangan menumpuk batch).
- `state.json` (`count`, `next_index`, `target`) diupdate setiap 1 video
  selesai diupload, supaya crash tidak mengulang atau menghilangkan index.
- Video diupload ke folder Drive "Stock" (`stock.folder_id`), file lokal
  dihapus setelah upload.
- Bila `count >= target`, cron menghapus dirinya sendiri dan berhenti.
- Pipeline harian kemudian mengambil video dari Stock (index terkecil dulu),
  bukan generate baru.

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

- Konvensi: nama folder media **mengikuti username sosmed** (mis. `@volumarc`
  → folder `volumarc`).
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

## 4. Pindahkan ke folder /uploaded (wajib sebelum Buffer)

Sebelum dijadwalkan ke Buffer, PINDAHKAN dulu file video ke folder `uploaded`
(id folder dari `config.yaml`). Ini menandai video sudah "diklaim" sehingga
tidak dijadwalkan dua kali (anti-duplikat) dan Buffer selalu menunjuk alamat
yang benar.

```bash
hatch_gws_cli drive files update --params '{"fileId":"<id>","addParents":"<uploaded_folder_id>","removeParents":"<media_folder_id>"}'
```

Catatan: file ID Drive TIDAK berubah saat dipindah, jadi URL publik
`https://drive.google.com/uc?export=download&id=<fileId>` tetap valid.
Verifikasi ulang URL dengan `curl -sL` (harus HTTP 200 video/mp4) setelah pindah.

## 5. Caption

Tulis caption segar sesuai `config.yaml` (default: Inggris, menarik,
3 hashtag), beda dari hari-hari sebelumnya. Satu caption per slot.

## 6. Schedule via Buffer

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

## 7. Catat & laporkan

- Append satu baris ke log harian: tanggal, file video, ID posting.
- Laporan akhir: video yang dibuat, posting terjadwal + jamnya, caption yang dipakai,
  dan kegagalan bila ada. Kirim juga ke kanal laporan sesuai `config.yaml`.
