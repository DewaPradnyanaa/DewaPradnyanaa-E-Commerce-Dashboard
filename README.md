# Proyek Analisis Data: E-Commerce Public Dataset

- **Nama:** Dewa Bagus Pradnyana Cahyadi Putra
- **Email:** pradnyana08@gmail.com
- **ID Dicoding:** dewa_bagus_pradnjv3s

Proyek ini menganalisis *E-Commerce Public Dataset* (transaksi marketplace di Brasil) pada pesanan berstatus *delivered* periode 15 September 2016 - 29 Agustus 2018 (96.470 pesanan dan 93.350 pelanggan unik). Hasil analisis disajikan dalam notebook dan dashboard Streamlit interaktif. Seluruh nilai uang dalam Brazilian Real (R$).

## Pertanyaan Bisnis

1. **Segmentasi RFM:** bagaimana sebaran pelanggan pada lima segmen RFM (acuan 30 Agustus 2018), berapa persen pelanggan dan revenue pada segmen berisiko, serta berapa persen pelanggan yang pernah membeli ulang?
2. **Durasi pengiriman dan skor ulasan:** berapa rata-rata skor ulasan pada empat kelompok durasi pengiriman, dan berapa selisih skornya antara pesanan yang tepat waktu dan yang melewati tanggal estimasi?
3. **Metode pembayaran dan cicilan:** metode pembayaran apa yang memiliki porsi pesanan dan nilai transaksi terbesar, dan berapa rata-rata nilai pesanan (AOV) kartu kredit pada lima kelompok cicilan?

## Ringkasan Temuan

- **Segmentasi RFM:** segmen terbesar adalah *Recent Mid-High Spenders* (33.087 pelanggan; 35,44%) dengan kontribusi revenue 50,94%. Segmen berisiko (*At-Risk / Need Attention* dan *Lost Customers*) mencakup 37.340 pelanggan (40,00%) dan 40,24% revenue. Hanya 2.801 pelanggan (3,00%) yang pernah membeli lebih dari sekali.
- **Durasi pengiriman dan ulasan:** rata-rata skor ulasan turun dari 4,41 (≤ 7 hari) menjadi 4,29 (8-14 hari), 4,10 (15-21 hari), dan 3,01 (> 21 hari). Pesanan yang melewati tanggal estimasi berskor 2,27, dibanding 4,29 pada pesanan yang tepat waktu atau lebih awal (selisih 2,02 poin).
- **Metode pembayaran dan cicilan:** kartu kredit menguasai 75,48% pesanan dan 78,47% nilai transaksi. AOV kartu kredit naik dari R$ 100,62 (tanpa cicilan) menjadi R$ 333,47 (cicilan 7-10x). Hasil ini menunjukkan hubungan, bukan bukti sebab-akibat.

## Struktur Folder

```
submission
├── dashboard
│   ├── dashboard.py
│   └── main_data.csv
├── data
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

- `data/` berisi dataset asli. Notebook hanya membaca lima berkas: `orders`, `customers`, `order_items`, `order_reviews`, dan `order_payments`. Empat berkas lainnya (`geolocation`, `products`, `product_category_name_translation`, `sellers`) tidak dibutuhkan oleh ketiga pertanyaan bisnis.
- `dashboard/main_data.csv` (96.470 baris, 17 kolom, satu baris per pesanan) dihasilkan oleh sel terakhir `notebook.ipynb` dan hanya memuat kolom yang dibutuhkan dashboard.
- `url.txt` berisi tautan dashboard yang sudah di-deploy.

## Menjalankan Notebook

1. Pastikan dataset berada di folder `data/` dan library pada `requirements.txt` sudah terpasang (lihat langkah 1 pada bagian dashboard di bawah). Untuk menjalankan notebook di lokal, pasang juga Jupyter: `pip install jupyter`.
2. Buka `notebook.ipynb` (Jupyter, VS Code, atau Google Colab), lalu jalankan seluruh sel dari atas ke bawah. Jika memakai Google Colab, unggah folder `data/` terlebih dahulu.
3. Sel terakhir membuat ulang `dashboard/main_data.csv`.

## Menjalankan Dashboard Streamlit di Lokal

1. Siapkan lingkungan (proyek ini diuji pada Python 3.13) dan pasang library:

   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # macOS / Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```

   Jika memakai Anaconda: `conda create --name main-ds python=3.11`, `conda activate main-ds`, lalu `pip install -r requirements.txt`.

2. Jalankan dashboard dari folder utama proyek (folder yang berisi `requirements.txt`):

   ```bash
   streamlit run dashboard/dashboard.py
   ```

   Dashboard membaca `main_data.csv` relatif terhadap lokasi `dashboard.py`, sehingga tetap berjalan jika dipanggil dari folder lain, misalnya `streamlit run path/ke/submission/dashboard/dashboard.py`.

3. Buka alamat yang tampil di terminal (biasanya `http://localhost:8501`).

## Fitur Dashboard

- **Ringkasan:** total pesanan, pelanggan unik, total revenue (harga barang), dan rata-rata skor ulasan.
- **Filter negara bagian pembeli (sidebar):** berlaku untuk seluruh visualisasi di dashboard.
- **Tab Segmentasi Pelanggan (RFM):** persentase pelanggan dan revenue segmen berisiko, persentase pelanggan yang pernah membeli ulang, jumlah pelanggan dan kontribusi revenue per segmen, serta tabel ringkasan.
- **Tab Durasi Pengiriman & Ulasan:** rata-rata skor ulasan per kelompok durasi dan per status ketepatan terhadap estimasi, serta selisih skornya.
- **Tab Metode Pembayaran & Cicilan:** porsi pesanan dan nilai transaksi per metode, serta AOV kartu kredit per kelompok cicilan. Filter metode pembayaran berada di dalam tab ini karena hanya memengaruhi grafik porsi dan tabel di tab tersebut. Grafik AOV per kelompok cicilan tidak dipengaruhi filter metode pembayaran ini (tetap menampilkan seluruh pesanan kartu kredit pada negara bagian yang dipilih).
- **Format angka:** metrik, tabel, dan keterangan memakai dua desimal seperti output notebook. Label di dalam grafik memakai satu desimal untuk persen dan bilangan bulat untuk nilai R$, seperti pada grafik di notebook.

## Deploy ke Streamlit Community Cloud (Opsional)

1. Unggah folder proyek ke repositori GitHub, termasuk `requirements.txt` dan `dashboard/main_data.csv`.
2. Masuk ke [Streamlit Community Cloud](https://streamlit.io/cloud), pilih **New app**, lalu pilih repositori dan cabang yang sesuai.
3. Isi **Main file path** dengan `dashboard/dashboard.py`, lalu deploy.
4. Salin tautan aplikasi ke `url.txt`.
