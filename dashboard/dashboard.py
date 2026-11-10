import os
import tempfile
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur temporary directory untuk cache matplotlib agar bebas warning perizinan
os.environ['MPLCONFIGDIR'] = os.path.join(tempfile.gettempdir(), 'matplotlib_cache')
warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# KONFIGURASI TEMA DAN PALET WARNA (Persis Sesuai Notebook)
# ---------------------------------------------------------
sns.set_theme(style='whitegrid')
plt.rcParams['font.size'] = 10

COLOR_MAIN = '#4A90E2'      # Biru: Nilai utama / pembeli
COLOR_ACCENT = '#E63946'    # Merah: Perhatian / risiko / penjual
COLOR_GOOD = '#2A9D8F'      # Hijau: Kondisi baik / performa tinggi
COLOR_NEUTRAL = '#B8C0CC'   # Abu-abu: Pembanding netral

# Koordinat centroid negara bagian di Brasil untuk peta interaktif
BRAZIL_STATES_COORDS = {
    'AC': {'lat': -9.0238, 'lon': -70.8120, 'name': 'Acre'},
    'AL': {'lat': -9.5713, 'lon': -36.7820, 'name': 'Alagoas'},
    'AM': {'lat': -3.4168, 'lon': -65.8561, 'name': 'Amazonas'},
    'AP': {'lat': 1.4140, 'lon': -51.7730, 'name': 'Amapá'},
    'BA': {'lat': -12.9718, 'lon': -38.5011, 'name': 'Bahia'},
    'CE': {'lat': -5.4984, 'lon': -39.3206, 'name': 'Ceará'},
    'DF': {'lat': -15.7998, 'lon': -47.8645, 'name': 'Distrito Federal'},
    'ES': {'lat': -19.1834, 'lon': -40.3089, 'name': 'Espírito Santo'},
    'GO': {'lat': -15.8270, 'lon': -49.8362, 'name': 'Goiás'},
    'MA': {'lat': -5.4194, 'lon': -45.3168, 'name': 'Maranhão'},
    'MG': {'lat': -18.5122, 'lon': -44.5550, 'name': 'Minas Gerais'},
    'MS': {'lat': -20.7722, 'lon': -54.7852, 'name': 'Mato Grosso do Sul'},
    'MT': {'lat': -12.6819, 'lon': -56.9211, 'name': 'Mato Grosso'},
    'PA': {'lat': -3.6582, 'lon': -52.6074, 'name': 'Pará'},
    'PB': {'lat': -7.2399, 'lon': -36.7820, 'name': 'Paraíba'},
    'PE': {'lat': -8.8137, 'lon': -36.9541, 'name': 'Pernambuco'},
    'PI': {'lat': -7.7183, 'lon': -42.7289, 'name': 'Piauí'},
    'PR': {'lat': -24.8948, 'lon': -51.5542, 'name': 'Paraná'},
    'RJ': {'lat': -22.9068, 'lon': -43.1729, 'name': 'Rio de Janeiro'},
    'RN': {'lat': -5.7945, 'lon': -36.5614, 'name': 'Rio Grande do Norte'},
    'RO': {'lat': -11.5057, 'lon': -63.5806, 'name': 'Rondônia'},
    'RR': {'lat': 2.7376, 'lon': -62.0751, 'name': 'Roraima'},
    'RS': {'lat': -30.0346, 'lon': -51.2177, 'name': 'Rio Grande do Sul'},
    'SC': {'lat': -27.2423, 'lon': -50.2189, 'name': 'Santa Catarina'},
    'SE': {'lat': -10.5741, 'lon': -37.3857, 'name': 'Sergipe'},
    'SP': {'lat': -23.5505, 'lon': -46.6333, 'name': 'São Paulo'},
    'TO': {'lat': -10.1753, 'lon': -48.2982, 'name': 'Tocantins'}
}

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

    st.error("Berkas data utama (main_data.csv) tidak ditemukan.")
    return None

df_raw = load_data()
if df_raw is None:
    st.stop()

# ---------------------------------------------------------
# KONFIGURASI HALAMAN STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Public Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# SIDEBAR: PROFIL DAN FILTER INTERAKTIF
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://raw.githubusercontent.com/dicodingacademy/assets/main/logo.png", width=180)
    st.markdown("### 👨‍💻 Data Analyst")
    st.markdown("""
    * **Nama:** Dewa Bagus Pradnyana Cahyadi Putra  
    * **Email:** pradnyana08@gmail.com  
    * **Dicoding ID:** `ds014b6y0434`
    """)
    st.markdown("---")
    st.subheader("⚙️ Filter Interaktif")

    # Filter 1: Rentang Tanggal Pemesanan
    min_date = df_raw['order_purchase_timestamp'].min().date()
    max_date = df_raw['order_purchase_timestamp'].max().date()

    st.markdown("**📅 Rentang Tanggal Pemesanan**")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("Mulai", min_value=min_date, max_value=max_date, value=min_date)
    with col_d2:
        end_date = st.date_input("Selesai", min_value=min_date, max_value=max_date, value=max_date)

    if start_date > end_date:
        st.error("Tanggal awal tidak boleh melebihi tanggal akhir!")
        start_date = min_date
        end_date = max_date

    # Filter 2: Negara Bagian Pembeli (Customer State)
    # Default KOSONG agar tidak otomatis memblokir filter, kosong = semua negara bagian
    all_states = sorted(df_raw['customer_state'].dropna().unique().tolist())
    selected_states = st.multiselect(
        "📍 Negara Bagian Pembeli (State):",
        options=all_states,
        default=[],
        placeholder="Semua Negara Bagian (Default)"
    )

    # Filter 3: Segmen Pelanggan RFM
    # Default KOSONG agar tidak otomatis memblokir filter, kosong = semua segmen
    all_segments = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'At Risk', 'Lost Customers']
    selected_segments = st.multiselect(
        "👥 Segmen Pelanggan (RFM):",
        options=all_segments,
        default=[],
        placeholder="Semua Segmen (Default)"
    )

    st.markdown("---")
    st.caption("💡 Jika filter negara bagian atau segmen dikosongkan, dashboard akan menampilkan seluruh data secara default.")

# ---------------------------------------------------------
# APLIKASI FILTER KE DATASET
# ---------------------------------------------------------
filtered_df = df_raw[
    (df_raw['order_purchase_timestamp'].dt.date >= start_date) &
    (df_raw['order_purchase_timestamp'].dt.date <= end_date)
]

# Terapkan filter hanya jika dipilih oleh pengguna
if len(selected_states) > 0:
    filtered_df = filtered_df[filtered_df['customer_state'].isin(selected_states)]

if len(selected_segments) > 0:
    filtered_df = filtered_df[filtered_df['customer_segment'].isin(selected_segments)]

# Dataset level pesanan unik untuk kalkulasi metrik pesanan
order_level_df = filtered_df.drop_duplicates('order_id')

# ---------------------------------------------------------
# HEADER & SCORECARD METRIK UTAMA (KPI)
# ---------------------------------------------------------
st.title("🛍️ E-Commerce Public Analytics Dashboard")
st.markdown("""
Dashboard interaktif untuk eksplorasi dan visualisasi mendalam **E-Commerce Public Dataset** (Olist, Brasil), 
fokus pada transaksi pesanan berstatus *delivered*.
""")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

total_orders = order_level_df['order_id'].nunique()
total_revenue = filtered_df['price'].sum()
unique_customers = filtered_df['customer_unique_id'].nunique()
avg_rating = order_level_df['review_score'].mean() if not order_level_df.empty else 0.0
avg_delivery = order_level_df['delivery_days'].mean() if not order_level_df.empty else 0.0

with kpi1:
    st.metric("Total Pesanan", f"{total_orders:,}")
with kpi2:
    st.metric("Total Revenue", f"R$ {total_revenue:,.0f}")
with kpi3:
    st.metric("Pelanggan Unik", f"{unique_customers:,}")
with kpi4:
    st.metric("Rata-rata Rating", f"{avg_rating:.2f} ★")
with kpi5:
    st.metric("Rata-rata Pengiriman", f"{avg_delivery:.1f} Hari")

st.markdown("---")

# ---------------------------------------------------------
# TAB VISUALISASI PERTANYAAN BISNIS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👥 Pertanyaan 1: Segmentasi RFM",
    "🗺️ Pertanyaan 2: Geospasial Pasar",
    "🚚 Pertanyaan 3: Durasi Pengiriman",
    "📦 Pertanyaan 4: Kinerja Kategori Produk",
    "💳 Pertanyaan 5: Metode Pembayaran",
    "📑 Kesimpulan & Rekomendasi"
])

# =========================================================
# TAB 1: PERTANYAAN 1 - SEGMENTASI PELANGGAN BERBASIS RFM
# =========================================================
with tab1:
    st.header("👥 Segmentasi Pelanggan Berbasis Analisis RFM (Recency, Frequency, Monetary)")
    st.markdown("""
    **Pertanyaan SMART:** *Bagaimana sebaran segmentasi pelanggan berdasarkan analisis RFM (Recency, Frequency, Monetary) per 30 Agustus 2018, berapa porsi pelanggan pada segmen berisiko (At-Risk / Lost), dan berapa kontribusi revenue dari masing-masing segmen?*
    """)

    rfm_cust_df = filtered_df[['customer_unique_id', 'customer_segment', 'recency', 'frequency', 'monetary']].drop_duplicates('customer_unique_id')

    if rfm_cust_df.empty:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
    else:
        segment_order = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'At Risk', 'Lost Customers']
        palette_rfm = [COLOR_GOOD, '#52B788', COLOR_MAIN, '#F4A261', COLOR_ACCENT]

        rfm_summary = rfm_cust_df.groupby('customer_segment').agg(
            total_customers=('customer_unique_id', 'count'),
            total_revenue=('monetary', 'sum'),
            avg_recency=('recency', 'mean'),
            repeat_buyers=('frequency', lambda x: (x > 1).sum())
        ).reindex(segment_order).dropna(subset=['total_customers']).reset_index()

        tot_cust = rfm_summary['total_customers'].sum()
        tot_rev = rfm_summary['total_revenue'].sum()
        rfm_summary['pct_customers'] = (rfm_summary['total_customers'] / max(tot_cust, 1)) * 100
        rfm_summary['pct_revenue'] = (rfm_summary['total_revenue'] / max(tot_rev, 1)) * 100

        # --- GRAFIK 1: DUAL BAR CHART (PERSIS SESUAI NOTEBOOK CELL 17) ---
        fig1, ax1 = plt.subplots(1, 2, figsize=(16, 6))

        # Panel 1: Jumlah Pelanggan per Segmen (5 Bar)
        sns.barplot(
            data=rfm_summary, x='customer_segment', y='total_customers',
            order=rfm_summary['customer_segment'], palette=palette_rfm[:len(rfm_summary)], ax=ax1[0]
        )
        ax1[0].set_title('Distribusi Jumlah Pelanggan per Segmen RFM', fontsize=12, fontweight='bold', pad=10)
        ax1[0].set_xlabel('Segmen Pelanggan', fontsize=10)
        ax1[0].set_ylabel('Jumlah Pelanggan', fontsize=10)
        max_cust = rfm_summary['total_customers'].max()
        for i, (val, pct) in enumerate(zip(rfm_summary['total_customers'], rfm_summary['pct_customers'])):
            ax1[0].text(i, val + (max_cust * 0.02), f"{val:,}\n({pct:.1f}%)", ha='center', fontsize=9)
        ax1[0].set_ylim(0, max_cust * 1.18)
        ax1[0].tick_params(axis='x', rotation=15)

        # Panel 2: Total Revenue per Segmen (5 Bar)
        sns.barplot(
            data=rfm_summary, x='customer_segment', y='total_revenue',
            order=rfm_summary['customer_segment'], palette=palette_rfm[:len(rfm_summary)], ax=ax1[1]
        )
        ax1[1].set_title('Kontribusi Revenue per Segmen RFM (BRL)', fontsize=12, fontweight='bold', pad=10)
        ax1[1].set_xlabel('Segmen Pelanggan', fontsize=10)
        ax1[1].set_ylabel('Total Revenue (R$)', fontsize=10)
        max_rev = rfm_summary['total_revenue'].max()
        for i, (val, pct) in enumerate(zip(rfm_summary['total_revenue'], rfm_summary['pct_revenue'])):
            ax1[1].text(i, val + (max_rev * 0.02), f"R$ {val:,.0f}\n({pct:.1f}%)", ha='center', fontsize=9)
        ax1[1].set_ylim(0, max_rev * 1.18)
        ax1[1].tick_params(axis='x', rotation=15)

        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

        # Tabel Rincian Metrik Segmen
        st.subheader("📋 Ringkasan Metrik Segmen RFM")
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

        with st.expander("💡 **Insight Kunci Segmentasi RFM** (klik untuk membuka)", expanded=True):
            st.markdown("""
- **Dominasi Segmen Berisiko (At Risk & Lost Customers):** Segmen *Lost Customers* (54.412 pelanggan, 58,3%) dan *At Risk* (996 pelanggan, 1,1%) secara kumulatif mencakup lebih dari **59%** basis pelanggan dan menyumbang lebih dari **58%** pendapatan historis (R$ 7,66 juta).
- **Segmen Champions & Loyal:** Mencakup ~1,9% pelanggan, merupakan pembeli setia dengan transaksi belanja berulang dan skor moneter tertinggi.
- **Tantangan Repeat Order:** Sebanyak **97%** pelanggan platform hanya pernah bertransaksi satu kali (*one-time buyer*). Program *retention marketing* seperti kupon diskon pesanan kedua (*second-order voucher*) menjadi kunci menjaga kelangsungan pendapatan.
            """)

# =========================================================
# TAB 2: PERTANYAAN 2 - DISTRIBUSI GEOSPASIAL PASAR
# =========================================================
with tab2:
    st.header("🗺️ Distribusi Geospasial Pasar: Pembeli vs Penjual")
    st.markdown("""
    **Pertanyaan SMART:** *Negara bagian (state) mana yang mencatatkan jumlah pesanan dan revenue tertinggi, bagaimana perbandingannya dengan jumlah penjual (seller) lokal, dan bagaimana ketimpangan pasokan antarwilayah di Brasil?*
    """)

    # Agregasi Pembeli
    geo_buyer = order_level_df.groupby('customer_state').agg(
        total_orders=('order_id', 'nunique')
    ).reset_index().rename(columns={'customer_state': 'state'})

    geo_rev = filtered_df.groupby('customer_state')['price'].sum().reset_index().rename(
        columns={'customer_state': 'state', 'price': 'total_revenue'}
    )
    geo_buyer = geo_buyer.merge(geo_rev, on='state', how='left')

    # Agregasi Penjual
    geo_seller = filtered_df.drop_duplicates('seller_id').groupby('seller_state')['seller_id'].count().reset_index().rename(
        columns={'seller_state': 'state', 'seller_id': 'total_sellers'}
    )

    geo_balance = geo_buyer.merge(geo_seller, on='state', how='left').fillna({'total_sellers': 0})
    tot_orders_sum = geo_balance['total_orders'].sum()
    tot_sellers_sum = geo_balance['total_sellers'].sum()

    geo_balance['order_share_pct'] = (geo_balance['total_orders'] / max(tot_orders_sum, 1)) * 100
    geo_balance['seller_share_pct'] = (geo_balance['total_sellers'] / max(tot_sellers_sum, 1)) * 100

    # Mengambil state dengan >= 1000 pesanan (persis 12 state sesuai notebook Cell 20)
    top_states = geo_balance[geo_balance['total_orders'] >= 1000].sort_values('total_orders', ascending=False).reset_index(drop=True)
    if top_states.empty:
        top_states = geo_balance.sort_values('total_orders', ascending=False).head(12).reset_index(drop=True)

    # --- GRAFIK 2: DUAL SUBPLOT (PERSIS SESUAI NOTEBOOK CELL 20 - 12 BAR) ---
    fig2, ax2 = plt.subplots(1, 2, figsize=(16, 6))

    # Panel 1: Jumlah Pesanan Pembeli per State (12 Bar Horizontal)
    sns.barplot(data=top_states, x='total_orders', y='state', color=COLOR_MAIN, ax=ax2[0])
    ax2[0].set_title('Top State Berdasarkan Jumlah Pesanan Pembeli', fontsize=12, fontweight='bold', pad=10)
    ax2[0].set_xlabel('Jumlah Pesanan', fontsize=10)
    ax2[0].set_ylabel('Negara Bagian (State)', fontsize=10)
    max_to = top_states['total_orders'].max()
    for i, val in enumerate(top_states['total_orders']):
        ax2[0].text(val + (max_to * 0.02), i, f"{val:,}", va='center', fontsize=9)
    ax2[0].set_xlim(0, max_to * 1.18)

    # Panel 2: Porsi Pesanan Pembeli vs Porsi Penjual Aktif (Grouped Bar Chart - 12 Pasang Bar)
    x = np.arange(len(top_states))
    width = 0.38
    b1 = ax2[1].barh(x - width/2, top_states['order_share_pct'], width, label='% Pesanan Pembeli', color=COLOR_MAIN)
    b2 = ax2[1].barh(x + width/2, top_states['seller_share_pct'], width, label='% Penjual Aktif', color=COLOR_ACCENT)
    ax2[1].set_yticks(x)
    ax2[1].set_yticklabels(top_states['state'])
    ax2[1].invert_yaxis()
    ax2[1].set_xlabel('Persentase terhadap Total Nasional (%)', fontsize=10)
    ax2[1].set_title('Perbandingan Pangsa Pesanan Pembeli vs Penjual Aktif', fontsize=12, fontweight='bold', pad=10)
    ax2[1].legend(loc='lower right')

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    # --- PETA INTERAKTIF SEBARAN GEOSPASIAL ---
    st.subheader("📍 Peta Interaktif Sebaran Permintaan Negara Bagian di Brasil")
    map_data_list = []
    for _, row in geo_balance.iterrows():
        st_code = row['state']
        if st_code in BRAZIL_STATES_COORDS:
            coords = BRAZIL_STATES_COORDS[st_code]
            map_data_list.append({
                'state': st_code,
                'name': coords['name'],
                'lat': coords['lat'],
                'lon': coords['lon'],
                'total_orders': row['total_orders'],
                'total_sellers': row['total_sellers']
            })

    if map_data_list:
        map_df = pd.DataFrame(map_data_list)
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            st.map(map_df, latitude='lat', longitude='lon', size='total_orders', color='#4A90E2')
        with col_m2:
            st.markdown("##### 📌 Negara Bagian Teratas")
            display_map = map_df[['state', 'name', 'total_orders', 'total_sellers']].sort_values('total_orders', ascending=False).head(10).copy()
            display_map.columns = ['State', 'Nama', 'Pesanan', 'Penjual']
            st.dataframe(display_map, use_container_width=True)

    with st.expander("💡 **Insight Geospasial (Pembeli vs Penjual)** (klik untuk membuka)", expanded=True):
        st.markdown("""
- **Sentralisasi di São Paulo (SP):** São Paulo (SP) menjadi pusat perniagaan e-commerce terbesar di Brasil dengan menguasai **40.494 pesanan (42,0%)** dan menampung hampir **60% penjual aktif** (1.769 penjual).
- **Defisit Pasokan Penjual Lokal:** Wilayah seperti Rio de Janeiro (RJ: 12,8% pesanan vs 5,5% penjual) dan Minas Gerais (MG: 11,8% pesanan vs 7,9% penjual) mengalami defisit penjual lokal yang tinggi, sehingga sangat bergantung pada pengiriman lintas wilayah (*inter-state*).
        """)

# =========================================================
# TAB 3: PERTANYAAN 3 - DURASI PENGIRIMAN & REVIEW SCORE
# =========================================================
with tab3:
    st.header("🚚 Hubungan Durasi Pengiriman dengan Kepuasan Pelanggan (Review Score)")
    st.markdown("""
    **Pertanyaan SMART:** *Bagaimana pengaruh durasi pengiriman terhadap skor ulasan pelanggan (review score), dan seberapa drastis kepuasan pelanggan turun ketika pengiriman terlambat dari estimasi (late vs estimate)?*
    """)

    deliv_df = order_level_df.dropna(subset=['delivery_days', 'review_score']).copy()
    deliv_df = deliv_df[deliv_df['delivery_days'] >= 0]

    if deliv_df.empty:
        st.warning("Data durasi pengiriman dan ulasan tidak tersedia pada filter saat ini.")
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

        # --- GRAFIK 3: DUAL SUBPLOT (PERSIS SESUAI NOTEBOOK CELL 23) ---
        fig3, ax3 = plt.subplots(1, 2, figsize=(16, 5))

        # Panel 1: Rata-rata Skor Ulasan berdasarkan Kategori Kecepatan (4 Bar)
        colors_speed = [COLOR_GOOD, '#52B788', '#F4A261', COLOR_ACCENT][:len(speed_summary)]
        bars1 = ax3[0].bar(speed_summary['speed_category'], speed_summary['avg_review'], color=colors_speed)
        ax3[0].set_title('Rata-rata Rating berdasarkan Kecepatan Pengiriman', fontsize=12, fontweight='bold', pad=10)
        ax3[0].set_ylabel('Rata-rata Skor Ulasan (Skala 1-5)', fontsize=10)
        ax3[0].set_ylim(0, 5.2)
        for i, (val, n) in enumerate(zip(speed_summary['avg_review'], speed_summary['total_orders'])):
            ax3[0].text(i, val + 0.12, f"{val:.2f} ★\n({n:,} pesanan)", ha='center', fontsize=9)
        ax3[0].tick_params(axis='x', rotation=10)

        # Panel 2: Dampak Keterlambatan Pengiriman (2 Bar)
        late_labels = ['Tepat Waktu / Lebih Awal', 'Terlambat vs Estimasi']
        colors_late = [COLOR_GOOD, COLOR_ACCENT][:len(late_summary)]
        bars2 = ax3[1].bar(late_labels[:len(late_summary)], late_summary['avg_review'], color=colors_late, width=0.5)
        ax3[1].set_title('Pengaruh Keterlambatan Pengiriman terhadap Kepuasan', fontsize=12, fontweight='bold', pad=10)
        ax3[1].set_ylabel('Rata-rata Skor Ulasan (Skala 1-5)', fontsize=10)
        ax3[1].set_ylim(0, 5.2)
        for i, (val, n, pct) in enumerate(zip(
            late_summary['avg_review'], late_summary['total_orders'], late_summary['pct_positive']
        )):
            ax3[1].text(i, val + 0.12, f"{val:.2f} ★\n{pct:.1f}% ulasan positif\n({n:,} pesanan)", ha='center', fontsize=9)

        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

        with st.expander("💡 **Insight Hubungan Pengiriman & Kepuasan** (klik untuk membuka)", expanded=True):
            st.markdown("""
- **Penalti Keterlambatan Estimasi:** Pesanan yang datang tepat waktu mendapatkan skor rating tinggi **4,29 ★** dengan **82,3% ulasan positif** (88.644 pesanan). Sebaliknya, pesanan yang terlambat melewati estimasi mengalami penurunan kepuasan drastis ke **2,57 ★** dengan hanya **33,8% ulasan positif** (7.826 pesanan).
- **Batas Kritis Durasi:** Rata-rata kepuasan tetap sangat baik pada durasi *Fast* (<=7 hari: 4,42 ★) dan *Normal* (8-14 hari: 4,31 ★). Kepuasan mulai anjlok tajam saat pengiriman memakan waktu *Very Slow* (>21 hari: 3,12 ★).
            """)

# =========================================================
# TAB 4: PERTANYAAN 4 - KINERJA KATEGORI PRODUK
# =========================================================
with tab4:
    st.header("📦 Kinerja Kategori Produk (Revenue & Volume Pesanan)")
    st.markdown("""
    **Pertanyaan SMART:** *Kategori produk apa saja yang menjadi penyumbang revenue dan volume pesanan terbesar di platform, serta kategori mana yang kinerjanya paling rendah (bottom categories)?*
    """)

    prod_perf = filtered_df.dropna(subset=['product_category_name_english']).groupby('product_category_name_english').agg(
        total_orders=('order_id', 'nunique'),
        total_items=('order_id', 'count'),
        total_revenue=('price', 'sum')
    ).reset_index().rename(columns={'product_category_name_english': 'product_category'})

    if prod_perf.empty:
        st.warning("Data kategori produk tidak tersedia pada filter saat ini.")
    else:
        prod_perf['product_category'] = prod_perf['product_category'].str.replace('_', ' ').str.title()
        top_revenue = prod_perf.sort_values('total_revenue', ascending=False).head(10)
        top_volume = prod_perf.sort_values('total_orders', ascending=False).head(10)
        bottom_revenue = prod_perf.sort_values('total_revenue', ascending=True).head(10)

        # --- GRAFIK 4A: TOP 10 REVENUE & ORDER VOLUME (PERSIS SESUAI NOTEBOOK CELL 26) ---
        fig4a, ax4a = plt.subplots(1, 2, figsize=(16, 6))

        # Panel Kiri: Top 10 Revenue (10 Bar)
        sns.barplot(data=top_revenue, x='total_revenue', y='product_category', color=COLOR_MAIN, ax=ax4a[0])
        ax4a[0].set_title('Top 10 Kategori Berdasarkan Revenue (BRL)', fontsize=12, fontweight='bold', pad=10)
        ax4a[0].set_xlabel('Total Revenue (R$)', fontsize=10)
        ax4a[0].set_ylabel('Kategori Produk', fontsize=10)
        max_rev = top_revenue['total_revenue'].max()
        for i, val in enumerate(top_revenue['total_revenue']):
            ax4a[0].text(val + (max_rev * 0.02), i, f"R$ {val:,.0f}", va='center', fontsize=9)
        ax4a[0].set_xlim(0, max_rev * 1.3)
        ax4a[0].ticklabel_format(style='plain', axis='x')

        # Panel Kanan: Top 10 Volume Pesanan (10 Bar)
        sns.barplot(data=top_volume, x='total_orders', y='product_category', color=COLOR_GOOD, ax=ax4a[1])
        ax4a[1].set_title('Top 10 Kategori Berdasarkan Volume Pesanan', fontsize=12, fontweight='bold', pad=10)
        ax4a[1].set_xlabel('Jumlah Pesanan', fontsize=10)
        ax4a[1].set_ylabel('')
        max_vol = top_volume['total_orders'].max()
        for i, val in enumerate(top_volume['total_orders']):
            ax4a[1].text(val + (max_vol * 0.02), i, f"{val:,}", va='center', fontsize=9)
        ax4a[1].set_xlim(0, max_vol * 1.25)

        plt.tight_layout()
        st.pyplot(fig4a)
        plt.close(fig4a)

        # --- GRAFIK 4B: BOTTOM 10 REVENUE (PERSIS SESUAI NOTEBOOK CELL 26 - 10 BAR) ---
        st.subheader("⚠️ Bottom 10 Kategori Berdasarkan Revenue Terendah")
        fig4b, ax4b = plt.subplots(figsize=(11, 4.5))
        sns.barplot(data=bottom_revenue, x='total_revenue', y='product_category', color=COLOR_ACCENT, ax=ax4b)
        ax4b.set_title('Bottom 10 Kategori Berdasarkan Revenue', fontsize=12, fontweight='bold', pad=10)
        ax4b.set_xlabel('Total Revenue (R$)', fontsize=10)
        ax4b.set_ylabel('Kategori Produk', fontsize=10)
        max_bot = bottom_revenue['total_revenue'].max()
        for i, (val, ords) in enumerate(zip(bottom_revenue['total_revenue'], bottom_revenue['total_orders'])):
            ax4b.text(val + (max_bot * 0.02), i, f"R$ {val:,.0f} ({ords} pesanan)", va='center', fontsize=8.5)
        ax4b.set_xlim(0, max_bot * 1.35)

        plt.tight_layout()
        st.pyplot(fig4b)
        plt.close(fig4b)

        with st.expander("💡 **Insight Kinerja Kategori Produk** (klik untuk membuka)", expanded=True):
            st.markdown("""
- **Top 3 Kontributor Omset:** *Health Beauty* (R$ 1.233.132), *Watches Gifts* (R$ 1.165.899), dan *Bed Bath Table* (R$ 1.023.435) menjadi tiga kategori utama yang masing-masing melampaui R$ 1 juta.
- **Nilai per Pesanan Tinggi:** Kategori *Watches Gifts* berada pada posisi ke-7 dalam volume pesanan (5.493 pesanan) namun berada di peringkat ke-2 dalam perolehan revenue karena nilai rata-rata belanja yang tinggi per item.
- **Bottom 10 Kategori:** Kategori seperti *Security And Services* (R$ 283; 2 pesanan) dan *Fashion Childrens Clothes* (R$ 520; 7 pesanan) menyumbangkan porsi revenue yang sangat kecil (< 0,1%).
            """)

# =========================================================
# TAB 5: PERTANYAAN 5 - METODE PEMBAYARAN & CICILAN
# =========================================================
with tab5:
    st.header("💳 Metode Pembayaran, Nilai Transaksi, dan Cicilan")
    st.markdown("""
    **Pertanyaan SMART:** *Metode pembayaran apa yang paling dominan digunakan pelanggan, dan bagaimana pemilihan jumlah cicilan kartu kredit memengaruhi nilai rata-rata pesanan (Average Order Value / AOV)?*
    """)

    pay_df = order_level_df.dropna(subset=['primary_payment_type']).copy()

    if pay_df.empty:
        st.warning("Data pembayaran tidak tersedia pada filter saat ini.")
    else:
        pay_summary = pay_df.groupby('primary_payment_type').agg(
            total_orders=('order_id', 'count'),
            total_payment_value=('total_payment_value', 'sum')
        ).sort_values('total_orders', ascending=False).reset_index()

        tot_pay_orders = pay_summary['total_orders'].sum()
        tot_pay_val = pay_summary['total_payment_value'].sum()
        pay_summary['order_share_pct'] = (pay_summary['total_orders'] / max(tot_pay_orders, 1)) * 100
        pay_summary['value_share_pct'] = (pay_summary['total_payment_value'] / max(tot_pay_val, 1)) * 100

        # Data Cicilan Kartu Kredit
        credit_card_df = pay_df[(pay_df['primary_payment_type'] == 'credit_card') & (pay_df['max_installments'] >= 1)].copy()

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

        inst_order = ['1x (Bayar Penuh)', '2-3x', '4-6x', '7-10x', '>10x']
        credit_card_df['installment_group'] = credit_card_df['max_installments'].apply(group_installments)
        installment_summary = credit_card_df.groupby('installment_group').agg(
            total_orders=('order_id', 'count'),
            avg_order_value=('total_payment_value', 'mean')
        ).reindex(inst_order).dropna(subset=['total_orders']).reset_index()

        # --- GRAFIK 5: DUAL SUBPLOT (PERSIS SESUAI NOTEBOOK CELL 29) ---
        fig5, ax5 = plt.subplots(1, 2, figsize=(16, 6))

        # Panel 1: Porsi Pesanan vs Porsi Nilai Transaksi per Metode (4 Pasang Bar)
        labels = pay_summary['primary_payment_type'].str.replace('_', ' ').str.title()
        x = np.arange(len(pay_summary))
        width = 0.38
        b1 = ax5[0].bar(x - width/2, pay_summary['order_share_pct'], width, label='% Jumlah Pesanan', color=COLOR_MAIN)
        b2 = ax5[0].bar(x + width/2, pay_summary['value_share_pct'], width, label='% Nilai Transaksi', color=COLOR_GOOD)
        ax5[0].set_xticks(x)
        ax5[0].set_xticklabels(labels)
        ax5[0].set_ylabel('Persentase (%)', fontsize=10)
        ax5[0].set_title('Porsi Pesanan vs Nilai Transaksi per Metode Pembayaran', fontsize=12, fontweight='bold', pad=10)
        ax5[0].bar_label(b1, fmt='%.1f%%', padding=3, fontsize=9)
        ax5[0].bar_label(b2, fmt='%.1f%%', padding=3, fontsize=9)
        ax5[0].set_ylim(0, 88)
        ax5[0].legend()

        # Panel 2: AOV Berdasarkan Kelompok Tenor Cicilan (5 Bar)
        bars_inst = ax5[1].bar(installment_summary['installment_group'].astype(str), installment_summary['avg_order_value'], color=COLOR_MAIN)
        ax5[1].set_title('Rata-rata Nilai Belanja (AOV) berdasarkan Tenor Cicilan', fontsize=12, fontweight='bold', pad=10)
        ax5[1].set_xlabel('Kelompok Tenor Cicilan', fontsize=10)
        ax5[1].set_ylabel('Average Order Value (R$)', fontsize=10)
        max_aov = installment_summary['avg_order_value'].max()
        for i, (aov, n) in enumerate(zip(installment_summary['avg_order_value'], installment_summary['total_orders'])):
            ax5[1].text(i, aov + (max_aov * 0.02), f"R$ {aov:,.0f}\n({n:,})", ha='center', fontsize=9)
        ax5[1].set_ylim(0, max_aov * 1.22)

        plt.tight_layout()
        st.pyplot(fig5)
        plt.close(fig5)

        with st.expander("💡 **Insight Metode Pembayaran & Cicilan** (klik untuk membuka)", expanded=True):
            st.markdown("""
- **Dominasi Kartu Kredit:** Kartu kredit menjadi instrumen utama pada **72.818 pesanan (75,5%)** dan menyerap **78,5% total nilai pembayaran** (R$ 12,10 juta).
- **Efek Pendorong Cicilan (Installment Uplift):** Terdapat korelasi positif yang nyata antara panjang tenor cicilan dengan nilai transaksi. Pembeli dengan cicilan >10x mencatatkan AOV sebesar **R$ 361**, meningkat 3,6 kali lipat dibandingkan transaksi 1x bayar penuh (R$ 101).
            """)

# =========================================================
# TAB 6: KESIMPULAN EKSEKUTIF & REKOMENDASI BISNIS
# =========================================================
with tab6:
    st.header("📑 Kesimpulan Eksekutif & Rekomendasi Bisnis")
    st.markdown("---")

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.subheader("📌 Kesimpulan Berdasarkan 5 Pertanyaan SMART")
        st.markdown("""
1. **Segmentasi Pelanggan (RFM):**
   * Pelanggan didominasi pembeli satu kali (*one-time buyers*, ~97%).
   * Segmen berisiko (*At Risk* dan *Lost Customers*) mencakup lebih dari **59%** basis pelanggan dan menyumbangkan lebih dari separuh pendapatan historis perusahaan.
2. **Distribusi Geospasial Pasar:**
   * Konsentrasi ekonomi sangat kuat di São Paulo (SP) yang menyerap **42,0%** pesanan nasional (40.494 pesanan) dan menampung hampir 60% penjual aktif.
   * Negara bagian lain (RJ, MG, RS) mengalami defisit penjual lokal yang tinggi sehingga bergantung pada pengiriman lintas wilayah.
3. **Durasi Pengiriman & Kepuasan:**
   * Ketepatan waktu terhadap estimasi adalah faktor penentu utama: pesanan tepat waktu meraih rating rata-rata **4,29 ★**, sedangkan pesanan terlambat anjlok ke **2,57 ★**.
   * Durasi pengiriman di bawah 14 hari menghasilkan kepuasan stabil di atas 4,3 bintang.
4. **Kinerja Kategori Produk:**
   * Tiga kategori penopang omset utama adalah *Health Beauty*, *Watches Gifts*, dan *Bed Bath Table*.
   * Kategori bernilai tinggi seperti *Watches Gifts* memiliki AOV tinggi meskipun volumenya moderat.
5. **Metode Pembayaran & Cicilan:**
   * Kartu kredit mendominasi 75,5% pesanan dan 78,5% nilai transaksi.
   * Fasilitas cicilan terbukti efektif melipatgandakan *basket size* belanja (AOV cicilan >10x mencapai R$ 361 dibanding R$ 101 pada pembayaran penuh).
        """)

    with col_c2:
        st.subheader("🎯 Rekomendasi Aksi Nyata (Actionable Insights)")
        st.markdown("""
1. **Automated Early-Retention Program:**
   * Kirimkan voucher diskon pembelian kedua (*second-order coupon*) secara otomatis dalam 7–14 hari setelah barang tiba untuk menaikkan repeat purchase rate dari 3%.
2. **Pengembangan Hub Logistik Regional:**
   * Bangun pusat pemenuhan (*fulfillment hub*) atau kemitraan 3PL lokal di Rio de Janeiro dan Minas Gerais untuk memangkas waktu kirim lintas state dari 14 hari ke < 7 hari.
3. **Penyempurnaan Algoritma Estimasi Tanggal Tiba (SLA Buffer):**
   * Tambahkan batas aman (*safety buffer*) 2–3 hari pada estimasi tiba di wilayah rawan keterlambatan guna menghindari penalti rating 2,5 bintang.
4. **Program Promosi Cicilan 0%:**
   * Gandeng bank penerbit kartu kredit untuk memberikan opsi cicilan 0% pada produk kategori bernilai tinggi (*Watches*, *Computers*, *Appliances*) guna mendongkrak omset.
        """)

    st.markdown("---")
    st.caption("Dicoding Submission: Proyek Analisis Data | Dewa Bagus Pradnyana Cahyadi Putra | E-Commerce Public Dataset")
