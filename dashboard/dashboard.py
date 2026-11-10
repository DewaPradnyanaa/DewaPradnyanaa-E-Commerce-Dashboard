import os
import tempfile
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur temporary directory untuk cache matplotlib
os.environ['MPLCONFIGDIR'] = os.path.join(tempfile.gettempdir(), 'matplotlib_cache')
warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# KONFIGURASI TEMA DAN PALET WARNA (Sesuai Notebook)
# ---------------------------------------------------------
sns.set_theme(style='whitegrid')
plt.rcParams['font.size'] = 10

COLOR_MAIN = '#4A90E2'      # Biru: Nilai utama / pembeli
COLOR_ACCENT = '#E63946'    # Merah: Risiko / perhatian
COLOR_GOOD = '#2A9D8F'      # Hijau toska: Performa tinggi / kepuasan
COLOR_NEUTRAL = '#B8C0CC'   # Abu-abu: Netral

# ---------------------------------------------------------
# FUNGSI MEMUAT DATASET DENGAN CACHE
# ---------------------------------------------------------
@st.cache_data
def load_data():
    csv_paths = [
        'main_data.csv',
        'dashboard/main_data.csv',
        'submission/dashboard/main_data.csv',
        os.path.join(os.path.dirname(__file__), 'main_data.csv'),
        'main_data.csv.gz',
        'dashboard/main_data.csv.gz',
        os.path.join(os.path.dirname(__file__), 'main_data.csv.gz')
    ]
    for p in csv_paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
            return df

    st.error('Berkas data utama (main_data.csv) tidak ditemukan.')
    return None

df_raw = load_data()
if df_raw is None:
    st.stop()

# ---------------------------------------------------------
# KONFIGURASI HALAMAN STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title='E-Commerce Public Analytics Dashboard',
    page_icon='🛍️',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ---------------------------------------------------------
# SIDEBAR: PROFIL DAN FILTER INTERAKTIF
# ---------------------------------------------------------
with st.sidebar:
    st.image('https://raw.githubusercontent.com/dicodingacademy/assets/main/logo.png', width=180)
    st.markdown('### 👨‍💻 Data Analyst')
    st.markdown('''
    * **Nama:** Dewa Bagus Pradnyana Cahyadi Putra  
    * **Email:** pradnyana08@gmail.com  
    * **Dicoding ID:** `ds014b6y0434`
    ''')
    st.markdown('---')
    st.subheader('⚙️ Filter Interaktif')

    # Filter 1: Rentang Tanggal Pemesanan
    min_date = df_raw['order_purchase_timestamp'].min().date()
    max_date = df_raw['order_purchase_timestamp'].max().date()

    st.markdown('**📅 Rentang Tanggal Pemesanan**')
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input('Mulai', min_value=min_date, max_value=max_date, value=min_date)
    with col_d2:
        end_date = st.date_input('Selesai', min_value=min_date, max_value=max_date, value=max_date)

    if start_date > end_date:
        st.error('Tanggal awal tidak boleh melebihi tanggal akhir!')
        start_date = min_date
        end_date = max_date

    # Filter 2: Segmen Pelanggan RFM
    all_segments = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'At-Risk / Need Attention', 'Lost Customers']
    selected_segments = st.multiselect(
        '👥 Segmen Pelanggan (RFM):',
        options=all_segments,
        default=[],
        placeholder='Semua Segmen (Default)'
    )

    # Filter 3: Metode Pembayaran
    all_payments = sorted(df_raw['primary_payment_type'].dropna().unique().tolist())
    selected_payments = st.multiselect(
        '💳 Metode Pembayaran:',
        options=all_payments,
        format_func=lambda x: str(x).replace('_', ' ').title(),
        default=[],
        placeholder='Semua Metode (Default)'
    )

    st.markdown('---')
    st.caption('💡 Filter yang dikosongkan akan menampilkan seluruh data secara default.')

# ---------------------------------------------------------
# APLIKASI FILTER KE DATASET
# ---------------------------------------------------------
filtered_df = df_raw[
    (df_raw['order_purchase_timestamp'].dt.date >= start_date) &
    (df_raw['order_purchase_timestamp'].dt.date <= end_date)
]

if len(selected_segments) > 0:
    filtered_df = filtered_df[filtered_df['customer_segment'].isin(selected_segments)]

if len(selected_payments) > 0:
    filtered_df = filtered_df[filtered_df['primary_payment_type'].isin(selected_payments)]

# Dataset level pesanan unik
order_level_df = filtered_df.drop_duplicates('order_id')

# ---------------------------------------------------------
# HEADER & SCORECARD METRIK UTAMA (KPI)
# ---------------------------------------------------------
st.title('🛍️ E-Commerce Public Analytics Dashboard')
st.markdown('''
Dashboard interaktif untuk eksplorasi dan visualisasi analitik **E-Commerce Public Dataset** (Olist, Brasil), 
fokus pada 3 pertanyaan bisnis utama berstandar SMART: **Segmentasi RFM**, **Durasi Pengiriman & Kepuasan**, serta **Metode Pembayaran & Cicilan**.
''')

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

total_orders = order_level_df['order_id'].nunique()
total_revenue = filtered_df['price'].sum() if 'price' in filtered_df.columns else filtered_df['total_items_price'].sum()
unique_customers = filtered_df['customer_unique_id'].nunique()
avg_rating = order_level_df['review_score'].mean() if not order_level_df.empty else 0.0
avg_delivery = order_level_df['delivery_days'].mean() if not order_level_df.empty else 0.0

with kpi1:
    st.metric('Total Pesanan', f'{total_orders:,}')
with kpi2:
    st.metric('Total Revenue', f'R$ {total_revenue:,.0f}')
with kpi3:
    st.metric('Pelanggan Unik', f'{unique_customers:,}')
with kpi4:
    st.metric('Rata-rata Rating', f'{avg_rating:.2f} ★')
with kpi5:
    st.metric('Rata-rata Pengiriman', f'{avg_delivery:.1f} Hari')

st.markdown('---')

# ---------------------------------------------------------
# TAB VISUALISASI 3 PERTANYAAN BISNIS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    '👥 Pertanyaan 1: Segmentasi RFM',
    '🚚 Pertanyaan 2: Durasi Pengiriman & Kepuasan',
    '💳 Pertanyaan 3: Metode Pembayaran & Cicilan',
    '📑 Kesimpulan & Rekomendasi Bisnis'
])

# =========================================================
# TAB 1: PERTANYAAN 1 - SEGMENTASI RFM
# =========================================================
with tab1:
    st.header('👥 Segmentasi Pelanggan Berbasis Analisis RFM (Recency, Frequency, Monetary)')
    st.markdown('''
    **Pertanyaan SMART:** *Bagaimana sebaran segmentasi pelanggan berdasarkan analisis RFM per 30 Agustus 2018, berapa proporsi pelanggan pada segmen berisiko (At-Risk / Lost), dan berapa kontribusi revenue dari masing-masing segmen?*
    ''')

    rfm_cust_df = filtered_df[['customer_unique_id', 'customer_segment', 'recency', 'frequency', 'monetary']].drop_duplicates('customer_unique_id')

    if rfm_cust_df.empty:
        st.warning('Tidak ada data yang sesuai dengan filter yang dipilih.')
    else:
        segment_order_full = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'At-Risk / Need Attention', 'Lost Customers']
        palette_rfm = [COLOR_GOOD, '#52B788', COLOR_MAIN, '#F4A261', COLOR_ACCENT]

        rfm_summary = rfm_cust_df.groupby('customer_segment').agg(
            total_customers=('customer_unique_id', 'count'),
            total_revenue=('monetary', 'sum'),
            avg_recency=('recency', 'mean'),
            repeat_buyers=('frequency', lambda x: (x > 1).sum())
        ).reindex(segment_order_full).dropna(subset=['total_customers']).reset_index()

        tot_cust = rfm_summary['total_customers'].sum()
        tot_rev = rfm_summary['total_revenue'].sum()
        rfm_summary['pct_customers'] = (rfm_summary['total_customers'] / max(tot_cust, 1)) * 100
        rfm_summary['pct_revenue'] = (rfm_summary['total_revenue'] / max(tot_rev, 1)) * 100

        # --- GRAFIK 1: DUAL BAR CHART (PERSIS SESUAI NOTEBOOK) ---
        fig1, ax1 = plt.subplots(1, 2, figsize=(16, 6))

        # Panel 1: Jumlah Pelanggan per Segmen
        sns.barplot(
            data=rfm_summary, x='customer_segment', y='total_customers',
            order=rfm_summary['customer_segment'], palette=palette_rfm[:len(rfm_summary)], ax=ax1[0]
        )
        ax1[0].set_title('Distribusi Jumlah Pelanggan per Segmen RFM', fontsize=13, fontweight='bold', pad=12)
        ax1[0].set_xlabel('Segmen Pelanggan', fontsize=11)
        ax1[0].set_ylabel('Jumlah Pelanggan', fontsize=11)
        max_c = rfm_summary['total_customers'].max()
        for i, (val, pct) in enumerate(zip(rfm_summary['total_customers'], rfm_summary['pct_customers'])):
            ax1[0].text(i, val + (max_c * 0.02), f"{val:,}\n({pct:.1f}%)", ha='center', fontsize=9.5, fontweight='bold')
        ax1[0].set_ylim(0, max_c * 1.18)
        ax1[0].tick_params(axis='x', rotation=15)

        # Panel 2: Total Revenue per Segmen
        sns.barplot(
            data=rfm_summary, x='customer_segment', y='total_revenue',
            order=rfm_summary['customer_segment'], palette=palette_rfm[:len(rfm_summary)], ax=ax1[1]
        )
        ax1[1].set_title('Kontribusi Pendapatan per Segmen RFM (BRL)', fontsize=13, fontweight='bold', pad=12)
        ax1[1].set_xlabel('Segmen Pelanggan', fontsize=11)
        ax1[1].set_ylabel('Total Revenue (R$)', fontsize=11)
        max_r = rfm_summary['total_revenue'].max()
        for i, (val, pct) in enumerate(zip(rfm_summary['total_revenue'], rfm_summary['pct_revenue'])):
            ax1[1].text(i, val + (max_r * 0.02), f"R$ {val:,.0f}\n({pct:.1f}%)", ha='center', fontsize=9.5, fontweight='bold')
        ax1[1].set_ylim(0, max_r * 1.18)
        ax1[1].tick_params(axis='x', rotation=15)

        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

        # Tabel Ringkasan Metrik Segmen
        st.subheader('📋 Ringkasan Metrik Segmen RFM')
        display_summary = rfm_summary.copy()
        display_summary.columns = [
            'Segmen Pelanggan', 'Total Pelanggan', 'Total Revenue (R$)',
            'Rata-rata Recency (Hari)', 'Repeat Buyers',
            'Proporsi Pelanggan (%)', 'Kontribusi Revenue (%)'
        ]
        st.dataframe(
            display_summary.style.format({
                'Total Pelanggan': '{:,.0f}',
                'Total Revenue (R$)': 'R$ {:,.2f}',
                'Rata-rata Recency (Hari)': '{:.1f}',
                'Repeat Buyers': '{:,.0f}',
                'Proporsi Pelanggan (%)': '{:.2f}%',
                'Kontribusi Revenue (%)': '{:.2f}%'
            }),
            use_container_width=True
        )

        with st.expander('💡 **Insight Kunci Segmentasi RFM** (klik untuk membuka)', expanded=True):
            st.markdown('''
- **Segmen Tulang Punggung (Loyal Customers):** Mencakup **32.278 pelanggan (34,6%)** dan menghasilkan pendapatan terbesar yakni **R$ 6,69 juta (50,5%)**. Kelompok ini memiliki aktivitas transaksi yang relatif baru dengan nominal belanja menengah ke atas.
- **Porsi Segmen Berisiko (At-Risk & Lost Customers):** Secara gabungan mencapai **37.214 pelanggan (39,9%)** dan menyumbangkan **R$ 5,30 juta (40,1%)** dari keseluruhan omset historis platform. Tingginya angka ini membuktikan bahwa risiko hilangnya pendapatan (*revenue churn*) sangat nyata jika tidak dilakukan program reaktivasi terarah.
- **Segmen Champions:** Merupakan **1,0% pelanggan terbaik (937 pelanggan)** yang memiliki frekuensi pesanan berulang dan skor moneter tertinggi secara berkelanjutan.
            ''')

# =========================================================
# TAB 2: PERTANYAAN 2 - DURASI PENGIRIMAN & KEPUASAN
# =========================================================
with tab2:
    st.header('🚚 Hubungan Durasi Pengiriman dengan Kepuasan Pelanggan (Review Score)')
    st.markdown('''
    **Pertanyaan SMART:** *Bagaimana pengaruh durasi pengiriman terhadap skor ulasan pelanggan (review score), dan seberapa drastis kepuasan pelanggan turun ketika pengiriman terlambat dari estimasi (late vs estimate)?*
    ''')

    deliv_df = order_level_df.dropna(subset=['delivery_days', 'review_score']).copy()
    deliv_df = deliv_df[deliv_df['delivery_days'] >= 0]

    if deliv_df.empty:
        st.warning('Data durasi pengiriman dan ulasan tidak tersedia pada filter saat ini.')
    else:
        def categorize_delivery_speed(d):
            if d <= 7:
                return 'Fast (<=7 hari)'
            elif d <= 14:
                return 'Normal (8-14 hari)'
            elif d <= 21:
                return 'Slow (15-21 hari)'
            else:
                return 'Very Slow (>21 hari)'

        deliv_df['speed_category'] = deliv_df['delivery_days'].apply(categorize_delivery_speed)
        speed_order = ['Fast (<=7 hari)', 'Normal (8-14 hari)', 'Slow (15-21 hari)', 'Very Slow (>21 hari)']

        speed_summary = deliv_df.groupby('speed_category').agg(
            total_orders=('order_id', 'count'),
            avg_review=('review_score', 'mean'),
            pct_positive=('review_score', lambda s: (s >= 4).mean() * 100)
        ).reindex(speed_order).dropna(subset=['total_orders']).reset_index()

        late_summary = deliv_df.groupby('is_late_vs_estimate').agg(
            total_orders=('order_id', 'count'),
            avg_review=('review_score', 'mean'),
            pct_positive=('review_score', lambda s: (s >= 4).mean() * 100)
        ).reset_index()
        late_summary['status_label'] = late_summary['is_late_vs_estimate'].map({
            False: 'Tepat Waktu / Lebih Awal', 
            True: 'Terlambat vs Estimasi'
        })

        # --- GRAFIK 2: DUAL SUBPLOT (PERSIS SESUAI NOTEBOOK) ---
        fig2, ax2 = plt.subplots(1, 2, figsize=(16, 5))

        # Panel 1: Rata-rata Skor Ulasan berdasarkan Kategori Kecepatan
        colors_speed = [COLOR_GOOD, '#52B788', '#F4A261', COLOR_ACCENT][:len(speed_summary)]
        bars1 = ax2[0].bar(speed_summary['speed_category'], speed_summary['avg_review'], color=colors_speed)
        ax2[0].set_title('Rata-rata Rating berdasarkan Kecepatan Pengiriman', fontsize=13, fontweight='bold', pad=12)
        ax2[0].set_ylabel('Rata-rata Skor Ulasan (Skala 1 - 5)', fontsize=11)
        ax2[0].set_ylim(0, 5.2)
        for i, (val, n) in enumerate(zip(speed_summary['avg_review'], speed_summary['total_orders'])):
            ax2[0].text(i, val + 0.12, f'{val:.2f} ★\n({n:,} pesanan)', ha='center', fontsize=9.5, fontweight='bold')
        ax2[0].tick_params(axis='x', rotation=10)

        # Panel 2: Dampak Keterlambatan Pengiriman vs Estimasi
        colors_late = [COLOR_GOOD, COLOR_ACCENT][:len(late_summary)]
        bars2 = ax2[1].bar(late_summary['status_label'], late_summary['avg_review'], color=colors_late, width=0.5)
        ax2[1].set_title('Pengaruh Keterlambatan Estimasi terhadap Kepuasan', fontsize=13, fontweight='bold', pad=12)
        ax2[1].set_ylabel('Rata-rata Skor Ulasan (Skala 1 - 5)', fontsize=11)
        ax2[1].set_ylim(0, 5.2)
        for i, (val, n, pct) in enumerate(zip(
            late_summary['avg_review'], late_summary['total_orders'], late_summary['pct_positive']
        )):
            ax2[1].text(i, val + 0.12, f'{val:.2f} ★\n{pct:.1f}% ulasan positif\n({n:,} pesanan)', ha='center', fontsize=9.5, fontweight='bold')

        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

        with st.expander('💡 **Insight Hubungan Pengiriman & Kepuasan** (klik untuk membuka)', expanded=True):
            st.markdown('''
- **Penalti Keterlambatan yang Tajam:** Pelanggan yang menerima paket tepat waktu memberikan penilaian sangat positif (**4,29 ★** dan 82,3% ulasan positif). Namun, ketika paket meleset melewati tanggal estimasi, skor kepuasan terjun bebas ke **2,57 ★** (hanya 33,8% ulasan positif). Keterlambatan estimasi terbukti menjadi pemicu komplain dan rating buruk nomor satu.
- **Dua Minggu Emas Logistik:** Pengiriman dalam rentang 1–14 hari mampu mempertahankan skor ulasan di atas 4,3 bintang. Efisiensi kurir dan gudang pada 14 hari pertama pengiriman merupakan pilar utama penjaga reputasi toko dan loyalitas pelanggan.
            ''')

# =========================================================
# TAB 3: PERTANYAAN 3 - METODE PEMBAYARAN & CICILAN
# =========================================================
with tab3:
    st.header('💳 Metode Pembayaran, Nilai Transaksi, dan Cicilan')
    st.markdown('''
    **Pertanyaan SMART:** *Metode pembayaran apa yang paling dominan digunakan pelanggan, dan bagaimana pemilihan jumlah cicilan kartu kredit memengaruhi nilai rata-rata pesanan (Average Order Value / AOV)?*
    ''')

    pay_df = order_level_df.dropna(subset=['primary_payment_type']).copy()

    if pay_df.empty:
        st.warning('Data pembayaran tidak tersedia pada filter saat ini.')
    else:
        payment_summary = pay_df.groupby('primary_payment_type').agg(
            total_orders=('order_id', 'count'),
            total_payment_value=('total_payment_value', 'sum'),
            avg_order_value=('total_payment_value', 'mean')
        ).sort_values('total_orders', ascending=False).reset_index()

        tot_p_orders = payment_summary['total_orders'].sum()
        tot_p_val = payment_summary['total_payment_value'].sum()
        payment_summary['order_share_pct'] = (payment_summary['total_orders'] / max(tot_p_orders, 1)) * 100
        payment_summary['value_share_pct'] = (payment_summary['total_payment_value'] / max(tot_p_val, 1)) * 100

        # Cicilan Kartu Kredit
        cc_df = pay_df[(pay_df['primary_payment_type'] == 'credit_card') & (pay_df['max_installments'] >= 1)].copy()

        def group_installments(x):
            if x == 1:
                return '1x (Bayar Penuh)'
            elif x <= 3:
                return '2-3x'
            elif x <= 6:
                return '4-6x'
            elif x <= 10:
                return '7-10x'
            else:
                return '>10x'

        cc_df['installment_group'] = cc_df['max_installments'].apply(group_installments)
        inst_order = ['1x (Bayar Penuh)', '2-3x', '4-6x', '7-10x', '>10x']

        installment_summary = cc_df.groupby('installment_group').agg(
            total_orders=('order_id', 'count'),
            total_value=('total_payment_value', 'sum'),
            avg_order_value=('total_payment_value', 'mean')
        ).reindex(inst_order).dropna(subset=['total_orders']).reset_index()

        # --- GRAFIK 3: DUAL SUBPLOT (PERSIS SESUAI NOTEBOOK) ---
        fig3, ax3 = plt.subplots(1, 2, figsize=(16, 6))

        # Panel 1: Pangsa Pesanan vs Nilai Transaksi per Metode
        labels_pay = payment_summary['primary_payment_type'].str.replace('_', ' ').str.title()
        x_pos = np.arange(len(payment_summary))
        width = 0.38
        b1 = ax3[0].bar(x_pos - width/2, payment_summary['order_share_pct'], width, label='% Jumlah Pesanan', color=COLOR_MAIN)
        b2 = ax3[0].bar(x_pos + width/2, payment_summary['value_share_pct'], width, label='% Nilai Transaksi', color=COLOR_GOOD)
        ax3[0].set_xticks(x_pos)
        ax3[0].set_xticklabels(labels_pay)
        ax3[0].set_ylabel('Persentase terhadap Total (%)', fontsize=11)
        ax3[0].set_title('Porsi Pesanan vs Nilai Transaksi per Metode Pembayaran', fontsize=13, fontweight='bold', pad=12)
        ax3[0].bar_label(b1, fmt='%.1f%%', padding=3, fontsize=9.5, fontweight='bold')
        ax3[0].bar_label(b2, fmt='%.1f%%', padding=3, fontsize=9.5, fontweight='bold')
        ax3[0].set_ylim(0, 88)
        ax3[0].legend()

        # Panel 2: AOV berdasarkan Kelompok Tenor Cicilan
        bars_inst = ax3[1].bar(installment_summary['installment_group'], installment_summary['avg_order_value'], color=COLOR_MAIN)
        ax3[1].set_title('Rata-rata Nilai Belanja (AOV) berdasarkan Tenor Cicilan', fontsize=13, fontweight='bold', pad=12)
        ax3[1].set_xlabel('Kelompok Tenor Cicilan Kartu Kredit', fontsize=11)
        ax3[1].set_ylabel('Average Order Value (R$)', fontsize=11)
        max_aov = installment_summary['avg_order_value'].max()
        for i, (aov, n) in enumerate(zip(installment_summary['avg_order_value'], installment_summary['total_orders'])):
            ax3[1].text(i, aov + (max_aov * 0.02), f"R$ {aov:,.0f}\n({n:,})", ha='center', fontsize=9.5, fontweight='bold')
        ax3[1].set_ylim(0, max_aov * 1.22)

        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

        with st.expander('💡 **Insight Metode Pembayaran & Cicilan** (klik untuk membuka)', expanded=True):
            st.markdown('''
- **Dominasi Kartu Kredit:** Kartu kredit menjadi penggerak utama 3 dari 4 pesanan di platform (**75,5% pesanan dan 78,5% nilai uang**). Ketersediaan fitur cicilan menjadi faktor penentu preferensi pembeli dibandingkan metode tunai seperti boleto.
- **Daya Dorong Keranjang Belanja (*Basket Size Uplift*):** Fasilitas cicilan terbukti secara empiris meningkatkan kesediaan konsumen membeli barang dengan harga lebih mahal. Pembeli dengan skema cicilan 7-10x membelanjakan rata-rata **R$ 319**, sedangkan cicilan >10x mencapai **R$ 384**, melipatgandakan nilai transaksi dibandingkan pembeli tunai 1x (R$ 101).
            ''')

# =========================================================
# TAB 4: KESIMPULAN & REKOMENDASI BISNIS
# =========================================================
with tab4:
    st.header('📑 Kesimpulan Eksekutif & Rekomendasi Bisnis')
    st.markdown('---')

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.subheader('📌 Kesimpulan Berdasarkan 3 Pertanyaan SMART')
        st.markdown('''
1. **Segmentasi Pelanggan (RFM):**
   * Basis pelanggan didominasi oleh segmen aktif, yaitu **Loyal Customers (34,6%)** dan **Potential Loyalists (24,6%)**, yang secara akumulatif membentuk **59,2%** dari seluruh pelanggan.
   * Segmen *Loyal Customers* menjadi penopang omset utama dengan kontribusi **50,5% (R$ 6,69 juta)**.
   * Terdapat risiko *revenue churn* yang tinggi dari kelompok berisiko (*Lost Customers* 20,0% dan *At-Risk / Need Attention* 19,9%) yang menyumbang **40,1% pendapatan historis (R$ 5,30 juta)**.
   * Segmen *Champions* mencakup **1,0% pelanggan (937 orang)** dengan nilai belanja tertinggi secara konsisten.

2. **Durasi Pengiriman & Rating Kepuasan:**
   * Ketepatan waktu terhadap tanggal estimasi adalah penentu rating nomor satu: pesanan tepat waktu meraih skor rating tinggi **4,29 ★ (82,3% positif)**, sedangkan pesanan terlambat anjlok tajam ke **2,57 ★ (33,8% positif)**.
   * Durasi pengiriman di bawah 14 hari menghasilkan kepuasan stabil di atas 4,3 bintang.

3. **Metode Pembayaran & Cicilan:**
   * Kartu kredit mendominasi 75,5% volume pesanan dan 78,5% nilai transaksi.
   * Fasilitas cicilan terbukti efektif melipatgandakan ukuran keranjang belanja (AOV cicilan >10x mencapai R$ 384 dibanding R$ 101 pada pembayaran penuh).
        ''')

    with col_c2:
        st.subheader('🎯 Rekomendasi Aksi Nyata (Actionable Insights)')
        st.markdown('''
1. **Automated Early-Retention Win-Back Program:**
   - Luncurkan program otomatis pemberian kupon diskon pesanan kedua (*second-order voucher*) dalam 7–14 hari setelah paket berstatus *delivered* guna menaikkan *repeat purchase rate* dari 2,7%.
   - Jalankan kampanye re-aktivasi *Win-Back* khusus bagi 37.214 pelanggan pada segmen *At-Risk / Need Attention* dan *Lost Customers* untuk mengamankan 40% potensi pendapatan.

2. **Penyempurnaan Algoritma Estimasi Tiba (SLA Safety Buffer):**
   - Tambahkan batas toleransi pengiriman (*safety buffer*) 2–3 hari pada tanggal estimasi tiba untuk rute pengiriman jarak jauh guna mencegah jatuhnya rating kepuasan ke 2,57 bintang.
   - Tetapkan target SLA maksimal pengiriman di bawah 14 hari bagi seluruh mitra logistik.

3. **Kemitraan Promosi Cicilan 0%:**
   - Gandeng perbankan rekanan untuk menyediakan promosi cicilan bunga 0% dengan tenor 6–12 bulan pada produk bernilai menengah-tinggi untuk terus mendongkrak AOV platform.
        ''')

    st.markdown('---')
    st.caption('Dicoding Submission: Proyek Analisis Data | Dewa Bagus Pradnyana Cahyadi Putra | E-Commerce Public Dataset')
