# Proyek Analisis Data: E-Commerce Public Dataset

- **Nama:** Dewa Bagus Pradnyana Cahyadi Putra
- **Email:** pradnyana08@gmail.com
- **ID Dicoding:** dewa_bagus_pradnjv3s

Proyek ini menganalisis *E-Commerce Public Dataset* (transaksi marketplace di Brasil) pada pesanan berstatus *delivered* periode 15 September 2016 - 29 Agustus 2018 (96.470 pesanan dan 93.350 pelanggan unik). Hasil analisis disajikan dalam notebook dan dashboard Streamlit interaktif.

## Pertanyaan Bisnis

1. **Segmentasi RFM:** bagaimana sebaran pelanggan pada lima segmen RFM (acuan 30 Agustus 2018), berapa persen pelanggan dan revenue pada segmen berisiko, serta berapa persen pelanggan yang pernah membeli ulang?
2. **Durasi pengiriman dan skor ulasan:** berapa rata-rata skor ulasan pada empat kelompok durasi pengiriman, dan berapa selisih skornya antara pesanan yang tepat waktu dan yang melewati tanggal estimasi?
3. **Metode pembayaran dan cicilan:** metode pembayaran apa yang memiliki porsi pesanan dan nilai transaksi terbesar, dan berapa rata-rata nilai pesanan (AOV) kartu kredit pada lima kelompok cicilan?

## Ringkasan Temuan

- Hanya 3,0% pelanggan yang pernah membeli ulang. Segmen berisiko (*At-Risk* dan *Lost*) mencakup 40,0% pelanggan dan 40,2% revenue.
- Pesanan yang melewati tanggal estimasi berskor 2,57, dibanding 4,29 pada pesanan yang tepat waktu (selisih 1,73 poin). Penurunan skor menurut durasi paling tajam setelah 21 hari.
- Kartu kredit menguasai 75,5% pesanan dan 78,5% nilai transaksi. AOV kartu kredit naik dari R$ 101 (tanpa cicilan) menjadi R$ 333 (cicilan 7-10x). Hasil ini menunjukkan hubungan, bukan bukti sebab-akibat.

## Struktur Folder

```
submission
├── dashboard
│   ├── dashboard.py
│   └── main_data.csv
├── data
│   ├── customers_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   └── orders_dataset.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

- `data/` berisi dataset mentah yang dibaca oleh notebook (cukup lima berkas di atas).
- `dashboard/main_data.csv` dihasilkan oleh sel terakhir `notebook.ipynb`.
- `url.txt` berisi tautan dashboard jika sudah di-deploy (opsional).

## Menjalankan Notebook

1. Letakkan dataset pada folder `data/` dan pastikan library pada `requirements.txt` sudah terpasang.
2. Buka `notebook.ipynb` (Jupyter, VS Code, atau Google Colab), lalu jalankan seluruh sel dari atas ke bawah.
3. Sel terakhir membuat ulang `dashboard/main_data.csv`.

## Menjalankan Dashboard Streamlit di Lokal

1. Siapkan lingkungan dan pasang library:

   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # macOS / Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```

   Jika memakai Anaconda: `conda create --name main-ds python=3.11`, `conda activate main-ds`, lalu `pip install -r requirements.txt`.

2. Jalankan dashboard dari folder utama proyek:

   ```bash
   streamlit run dashboard/dashboard.py
   ```

3. Buka alamat yang tampil di terminal (biasanya `http://localhost:8501`).

## Fitur Dashboard

- **Ringkasan:** total pesanan, pelanggan unik, total revenue, dan rata-rata skor ulasan.
- **Filter negara bagian pembeli (sidebar):** berlaku untuk seluruh visualisasi di dashboard.
- **Tab Segmentasi Pelanggan (RFM):** jumlah pelanggan dan kontribusi revenue per segmen, serta tabel ringkasan.
- **Tab Durasi Pengiriman & Ulasan:** rata-rata skor ulasan per kelompok durasi dan per status ketepatan terhadap estimasi.
- **Tab Metode Pembayaran & Cicilan:** porsi pesanan dan nilai transaksi per metode, serta AOV kartu kredit per kelompok cicilan. Filter metode pembayaran berada di dalam tab ini karena hanya memengaruhi grafik porsi dan tabel di tab tersebut.

## Deploy ke Streamlit Community Cloud (Opsional)

1. Unggah folder proyek ke repositori GitHub, termasuk `requirements.txt` dan `dashboard/main_data.csv`.
2. Masuk ke [Streamlit Community Cloud](https://streamlit.io/cloud), pilih **New app**, lalu pilih repositori dan cabang yang sesuai.
3. Isi **Main file path** dengan `dashboard/dashboard.py`, lalu deploy.
4. Salin tautan aplikasi ke `url.txt`.
