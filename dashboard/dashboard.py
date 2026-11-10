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
# KONFIGURASI TEMA DAN PALET WARNA (Sesuai dengan Notebook)
# ---------------------------------------------------------
sns.set_theme(style='whitegrid')
plt.rcParams['font.size'] = 10

COLOR_MAIN = '#4A90E2'      # Biru: Nilai utama / pembeli
COLOR_ACCENT = '#E63946'    # Merah: Perhatian / risiko / penjual
COLOR_GOOD = '#2A9D8F'      # Hijau: Kondisi baik / performa tinggi
COLOR_NEUTRAL = '#B8C0CC'   # Abu-abu: Pembanding netral

# Koordinat centroid negara bagian di Brasil untuk visualisasi peta interaktif
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
    """Memuat file main_data.csv atau main_data.csv.gz dari beberapa kemungkinan direktori relatif."""
    possible_paths = [
        'main_data.csv',
        'main_data.csv.gz',
        'dashboard/main_data.csv',
        'dashboard/main_data.csv.gz',
        'main_data (3).csv',
        'dashboard/main_data (3).csv',
        os.path.join(os.path.dirname(__file__), 'main_data.csv'),
        os.path.join(os.path.dirname(__file__), 'main_data.csv.gz'),
        os.path.join(os.path.dirname(__file__), 'main_data (3).csv'),
        '../dashboard/main_data.csv',
        'data/main_data.csv'
    ]

    file_path = None
    for p in possible_paths:
        if os.path.exists(p):
            file_path = p
            break

    if file_path is None:
        st.error("Berkas `main_data.csv` atau `main_data.csv.gz` tidak ditemukan! Pastikan file berada di folder `dashboard/` atau satu direktori dengan `dashboard.py`.")
        st.stop()

    df = pd.read_csv(file_path)

    # Konversi kolom tanggal menjadi format datetime
    if 'order_purchase_timestamp' in df.columns:
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')

    # Hitung rute pengiriman jika belum ada
    if 'shipping_route' not in df.columns and 'customer_state' in df.columns and 'seller_state' in df.columns:
        df['shipping_route'] = np.where(df['customer_state'] == df['seller_state'], 'Satu state', 'Lintas state')

    return df

# ---------------------------------------------------------
# PENGATURAN HALAMAN STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Public Data Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Memuat data
main_df = load_data()

# ---------------------------------------------------------
# SIDEBAR: IDENTITAS & FILTER INTERAKTIF
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://raw.githubusercontent.com/dicodingacademy/assets/main/logo.png", width=180)
    st.title("🛒 E-Commerce Dashboard")
    st.markdown("""
    **Proyek Analisis Data:** E-Commerce Public Dataset  
    * **Nama:** Dewa Bagus Pradnyana Cahyadi Putra  
    * **Email:** pradnyana08@gmail.com  
    * **Dicoding ID:** `ds014b6y0434`
    """)
    st.markdown("---")

    st.subheader("🔍 Filter Interaktif")

    # 1. Filter Rentang Tanggal Pembelian
    min_date = main_df['order_purchase_timestamp'].min().date()
    max_date = main_df['order_purchase_timestamp'].max().date()

    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input(
            "Mulai:",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key="start_date"
        )
    with col_date2:
        end_date = st.date_input(
            "Akhir:",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="end_date"
        )

    # Validasi rentang tanggal
    if start_date > end_date:
        st.error("⚠️ Tanggal mulai harus lebih awal atau sama dengan tanggal akhir!")
        st.stop()

    # 2. Filter Negara Bagian Pembeli (Customer State)
    all_states = sorted(main_df['customer_state'].dropna().unique().tolist())
    selected_states = st.multiselect(
        "Pilih Negara Bagian (Customer State):",
        options=all_states,
        default=[]
    )

    # 3. Filter Segmen Pelanggan (RFM Segment)
    all_segments = sorted(main_df['customer_segment'].dropna().unique().tolist())
    selected_segments = st.multiselect(
        "Pilih Segmen RFM Pelanggan:",
        options=all_segments,
        default=[]
    )

    st.markdown("---")
    st.caption("💡 *Tip:* Biarkan filter kosong untuk menampilkan keseluruhan data platform.")

# ---------------------------------------------------------
# APLIKASIKAN FILTER PADA DATASET
# ---------------------------------------------------------
filtered_df = main_df.copy()

# Filter Tanggal
filtered_df = filtered_df[
    (filtered_df['order_purchase_timestamp'].dt.date >= start_date) &
    (filtered_df['order_purchase_timestamp'].dt.date <= end_date)
]

# Filter Negara Bagian
if selected_states:
    filtered_df = filtered_df[filtered_df['customer_state'].isin(selected_states)]

# Filter Segmen Pelanggan
if selected_segments:
    filtered_df = filtered_df[filtered_df['customer_segment'].isin(selected_segments)]

# Periksa apakah data kosong setelah filter
if filtered_df.empty:
    st.warning("⚠️ Tidak ada data yang sesuai dengan kombinasi filter yang dipilih. Silakan ubah filter di sidebar.")
    st.stop()

# Pisahkan dataframe level pesanan (tanpa duplikasi order_id) untuk metrik level pesanan
order_level_df = filtered_df.drop_duplicates('order_id')

# ---------------------------------------------------------
# HEADER UTAMA & KPI SCORECARD
# ---------------------------------------------------------
st.title("📊 E-Commerce Business Intelligence & Analytics Dashboard")
st.markdown("Analisis komprehensif pesanan berstatus **delivered** dari E-Commerce Public Dataset di Brasil.")

# Tampilan Key Performance Indicators (KPI) menggunakan st.metric bawaan Streamlit
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

total_orders = order_level_df['order_id'].nunique()
total_revenue = filtered_df['price'].sum()
total_customers = filtered_df['customer_unique_id'].nunique()

avg_rating = order_level_df['review_score'].mean()
rating_display = f"{avg_rating:.2f} / 5" if pd.notna(avg_rating) else "N/A"

avg_delivery = order_level_df['delivery_days'].mean()
delivery_display = f"{avg_delivery:.1f} Hari" if pd.notna(avg_delivery) else "N/A"

kpi1.metric(label="📋 Total Pesanan", value=f"{total_orders:,}")
kpi2.metric(label="💰 Total Revenue", value=f"R$ {total_revenue:,.0f}")
kpi3.metric(label="👤 Pelanggan Unik", value=f"{total_customers:,}")
kpi4.metric(label="⭐ Rata-rata Rating", value=rating_display)
kpi5.metric(label="🚚 Rata-rata Pengiriman", value=delivery_display)

st.markdown("---")

# ---------------------------------------------------------
# TAB NAVIGASI UTAMA (MENCAKUP SELURUH GRAFIK DARI NOTEBOOK)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👥 Pertanyaan 1: Segmentasi RFM",
    "🗺️ Pertanyaan 2: Analisis Geospasial",
    "🚚 Pertanyaan 3: Durasi Pengiriman & Rating",
    "📦 Pertanyaan 4: Kinerja Kategori Produk",
    "💳 Pertanyaan 5: Metode Pembayaran & Cicilan",
    "📝 Rangkuman & Rekomendasi Bisnis"
])

# =========================================================
# TAB 1: PERTANYAAN 1 - SEGMENTASI RFM
# =========================================================
with tab1:
    st.header("👥 Segmentasi Pelanggan Berbasis Analisis RFM (Recency, Frequency, Monetary)")
    st.markdown("""
    **Pertanyaan SMART:** *Bagaimana profil segmentasi pelanggan berdasarkan analisis RFM, seberapa besar kelompok pelanggan yang berisiko hilang (At-Risk / Lost), dan berapa porsi pendapatan yang mereka sumbangkan?*
    """)

    # Agregasi data pelanggan unik untuk RFM
    rfm_cust_df = filtered_df[['customer_unique_id', 'customer_segment', 'recency', 'frequency', 'monetary']].drop_duplicates('customer_unique_id')

    if rfm_cust_df.empty:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
    else:
        segment_order = ['Recent Mid-High Spenders', 'Potential Loyalists', 'At-Risk / Need Attention', 'Lost Customers', 'Champions']
        segment_colors = {
            'Champions': COLOR_GOOD,
            'Recent Mid-High Spenders': COLOR_MAIN,
            'Potential Loyalists': COLOR_MAIN,
            'At-Risk / Need Attention': COLOR_ACCENT,
            'Lost Customers': COLOR_ACCENT
        }

        segment_summary = rfm_cust_df.groupby('customer_segment').agg(
            total_customers=('customer_unique_id', 'count'),
            avg_recency_days=('recency', 'mean'),
            avg_monetary=('monetary', 'mean'),
            repeat_buyers_pct=('frequency', lambda x: (x > 1).mean() * 100),
            total_revenue=('monetary', 'sum')
        ).reset_index()

        total_rfm_cust = len(rfm_cust_df)
        total_rfm_rev = segment_summary['total_revenue'].sum()
        segment_summary['customer_share_pct'] = segment_summary['total_customers'] / max(total_rfm_cust, 1) * 100
        segment_summary['revenue_share_pct'] = segment_summary['total_revenue'] / max(total_rfm_rev, 1) * 100

        # Urutkan sesuai segment_order (hanya segmen yang tersedia)
        available_segments = [s for s in segment_order if s in segment_summary['customer_segment'].values]
        plot_df = segment_summary.set_index('customer_segment').reindex(available_segments).reset_index()

        if not plot_df.empty:
            # --- GRAFIK 1: HORIZONTAL BAR CHART SESUAI CELL 29 ---
            fig1, ax1 = plt.subplots(figsize=(12, 5.5))
            bar_palette = [segment_colors.get(s, COLOR_NEUTRAL) for s in plot_df['customer_segment']]
            sns.barplot(
                data=plot_df,
                x='total_customers',
                y='customer_segment',
                palette=bar_palette,
                ax=ax1
            )

            max_cust = plot_df['total_customers'].max()
            for index, row in plot_df.iterrows():
                ax1.text(
                    row['total_customers'] + max(max_cust * 0.015, 5),
                    index,
                    f"{row['total_customers']:,.0f} ({row['customer_share_pct']:.1f}%) | rata-rata {row['avg_recency_days']:.0f} hari",
                    va='center', fontsize=9.5, fontweight='bold', color='#333333'
                )

            ax1.set_title('Distribusi Segmen Pelanggan Berdasarkan RFM Analysis', fontsize=13, fontweight='bold', pad=15)
            ax1.set_xlabel('Jumlah Pelanggan Unik', fontsize=11, labelpad=8)
            ax1.set_ylabel('Segmen Pelanggan', fontsize=11)
            ax1.set_xlim(0, max(max_cust * 1.55, 10))
            ax1.grid(axis='x', linestyle='--', alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig1)
            plt.close(fig1)

            # Tabel Rincian Metrik Segmen
            st.subheader("📋 Ringkasan Metrik Segmen RFM")
            display_summary = plot_df.copy()
            display_summary.columns = [
                'Segmen Pelanggan', 'Total Pelanggan', 'Rata-rata Recency (Hari)',
                'Rata-rata Belanja (R$)', 'Repeat Buyers (%)', 'Total Revenue (R$)',
                'Proporsi Pelanggan (%)', 'Kontribusi Revenue (%)'
            ]
            st.dataframe(
                display_summary.style.format({
                    'Total Pelanggan': '{:,.0f}',
                    'Rata-rata Recency (Hari)': '{:.1f}',
                    'Rata-rata Belanja (R$)': 'R$ {:,.2f}',
                    'Repeat Buyers (%)': '{:.2f}%',
                    'Total Revenue (R$)': 'R$ {:,.2f}',
                    'Proporsi Pelanggan (%)': '{:.2f}%',
                    'Kontribusi Revenue (%)': '{:.2f}%'
                }),
                use_container_width=True
            )

        # Insight Box
        with st.expander("💡 **Insight Kunci Segmentasi RFM** (klik untuk membuka)", expanded=True):
            st.markdown("""
- **Recent Mid-High Spenders** adalah tulang punggung pendapatan bisnis: mencakup **35,4%** pelanggan dan menyumbang **50,9%** revenue (rata-rata belanja R$ 203,54).
- **Segmen Berisiko (At-Risk & Lost):** Mencakup total **40,0%** pelanggan dan menyumbang **40,2%** total revenue, dengan rata-rata 316 dan 473 hari tidak bertransaksi.
- **Champions:** Hanya **1,0%** pelanggan (932 orang), seluruhnya merupakan pembeli berulang (repeat rate 100%) dengan nilai transaksi tertinggi (rata-rata R$ 327,10).
- **Tantangan Retensi:** Sebanyak **97,0%** basis pelanggan hanya bertransaksi satu kali. Segmen berisiko mayoritas bukanlah pelanggan setia yang hilang, melainkan pembeli pertama kali yang belum pernah kembali.
            """)

# =========================================================
# TAB 2: PERTANYAAN 2 - ANALISIS GEOSPASIAL
# =========================================================
with tab2:
    st.header("🗺️ Analisis Geospasial: Permintaan Pembeli vs Pasokan Penjual")
    st.markdown("""
    **Pertanyaan SMART:** *Negara bagian (state) mana yang menjadi pusat pesanan dan revenue tertinggi, bagaimana keseimbangannya dengan jumlah penjual aktif lokal, serta seberapa jauh efisiensi pengiriman antarwilayah?*
    """)

    # 1. Agregasi Pembeli
    geo_cust = order_level_df.groupby('customer_state').agg(
        total_orders=('order_id', 'nunique')
    ).reset_index().rename(columns={'customer_state': 'state'})

    geo_rev = filtered_df.groupby('customer_state')['price'].sum().reset_index().rename(
        columns={'customer_state': 'state', 'price': 'total_revenue'}
    )
    geo_cust = geo_cust.merge(geo_rev, on='state', how='left')

    # 2. Agregasi Penjual
    geo_sell = filtered_df.groupby('seller_state')['seller_id'].nunique().reset_index().rename(
        columns={'seller_state': 'state', 'seller_id': 'total_sellers'}
    )

    # 3. Gabungkan Data State
    geo_analysis = geo_cust.merge(geo_sell, on='state', how='left')
    geo_analysis['total_sellers'] = geo_analysis['total_sellers'].fillna(0).astype(int)

    tot_orders_sum = geo_analysis['total_orders'].sum()
    tot_rev_sum = geo_analysis['total_revenue'].sum()
    geo_analysis['order_share_pct'] = geo_analysis['total_orders'] / max(tot_orders_sum, 1) * 100
    geo_analysis['revenue_share_pct'] = geo_analysis['total_revenue'] / max(tot_rev_sum, 1) * 100
    geo_analysis['orders_per_seller'] = np.where(
        geo_analysis['total_sellers'] > 0,
        geo_analysis['total_orders'] / geo_analysis['total_sellers'],
        np.nan
    )
    geo_analysis = geo_analysis.sort_values('total_orders', ascending=False).reset_index(drop=True)

    # Filter state dengan pesanan signifikan (>= 1.000 pesanan sesuai notebook atau top 10)
    top_states = geo_analysis[geo_analysis['total_orders'] >= 1000].copy()
    if top_states.empty:
        top_states = geo_analysis.head(10).copy()

    # --- GRAFIK 2A: DUAL BAR CHART SESUAI CELL 32 ---
    st.subheader("📊 Permintaan Pembeli vs Pasokan Penjual (Top Negara Bagian)")
    fig2, ax2 = plt.subplots(1, 2, figsize=(15, 6.5), sharey=True)

    max_top_orders = max(top_states['total_orders'].max(), 1)
    ax2[0].barh(top_states['state'], top_states['total_orders'], color=COLOR_MAIN)
    ax2[0].set_title('Jumlah Pesanan Pembeli', fontsize=12, fontweight='bold', pad=10)
    ax2[0].set_xlabel('Jumlah Pesanan', fontsize=10)
    ax2[0].set_ylabel('Negara Bagian (State)', fontsize=10)
    ax2[0].invert_yaxis()
    for i, (orders, rev) in enumerate(zip(top_states['total_orders'], top_states['revenue_share_pct'])):
        ax2[0].text(orders + (max_top_orders * 0.02), i, f"{orders:,.0f} ({rev:.1f}%)", va='center', fontsize=8.5)
    ax2[0].set_xlim(0, max_top_orders * 1.35)

    # Panel Kanan: Rasio Pesanan per Penjual
    ops_values = top_states['orders_per_seller'].fillna(0)
    max_ops = max(ops_values.max(), 1)
    ratio_colors = [COLOR_ACCENT if r > 100 else COLOR_NEUTRAL for r in ops_values]
    ax2[1].barh(top_states['state'], ops_values, color=ratio_colors)
    ax2[1].set_title('Pesanan per Penjual (Merah: > 100)', fontsize=12, fontweight='bold', pad=10)
    ax2[1].set_xlabel('Pesanan per Penjual', fontsize=10)
    for i, (ratio, sellers) in enumerate(zip(ops_values, top_states['total_sellers'])):
        ax2[1].text(ratio + (max_ops * 0.02), i, f"{ratio:.0f} ({sellers:,} penjual)", va='center', fontsize=8.5)
    ax2[1].set_xlim(0, max_ops * 1.35)

    fig2.suptitle('Permintaan Pembeli vs Pasokan Penjual per Negara Bagian', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    # --- PETA INTERAKTIF SEBARAN GEOSPASIAL ---
    st.subheader("📍 Peta Interaktif Sebaran Permintaan & Pasokan Negara Bagian di Brasil")
    map_data_list = []
    for _, row in geo_analysis.iterrows():
        st_code = row['state']
        if st_code in BRAZIL_STATES_COORDS:
            coords = BRAZIL_STATES_COORDS[st_code]
            map_data_list.append({
                'state': st_code,
                'name': coords['name'],
                'lat': coords['lat'],
                'lon': coords['lon'],
                'total_orders': row['total_orders'],
                'total_sellers': row['total_sellers'],
                'orders_per_seller': row['orders_per_seller'] if pd.notna(row['orders_per_seller']) else 0
            })

    if map_data_list:
        map_df = pd.DataFrame(map_data_list)
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            st.map(map_df, latitude='lat', longitude='lon', size='total_orders', color='#4A90E2')
        with col_m2:
            st.markdown("##### 📌 8 Negara Bagian Teratas")
            display_map = map_df[['state', 'name', 'total_orders', 'total_sellers', 'orders_per_seller']].sort_values('total_orders', ascending=False).head(8).copy()
            display_map.columns = ['State', 'Nama', 'Pesanan', 'Penjual', 'Rasio']
            st.dataframe(display_map, use_container_width=True)

    # Perbandingan Pengiriman Satu State vs Lintas State
    st.subheader("📦 Efisiensi Rute Logistik: Satu State vs Lintas State")
    if 'shipping_route' in filtered_df.columns:
        route_df = filtered_df.groupby('shipping_route').agg(
            total_items=('order_id', 'count'),
            avg_delivery_days=('delivery_days', 'mean'),
            avg_freight_value=('freight_value', 'mean')
        ).reset_index()
        route_items_total = route_df['total_items'].sum()
        route_df['share_pct'] = route_df['total_items'] / max(route_items_total, 1) * 100

        rcol1, rcol2 = st.columns(2)
        satu_st = route_df[route_df['shipping_route'] == 'Satu state']
        lintas_st = route_df[route_df['shipping_route'] == 'Lintas state']

        with rcol1:
            if not satu_st.empty:
                st.metric("🚚 Satu State (Intra-state)", f"{satu_st['share_pct'].values[0]:.1f}% Item")
                st.markdown(f"""
- Rata-rata Durasi: **{satu_st['avg_delivery_days'].values[0]:.1f} hari**
- Rata-rata Ongkir: **R$ {satu_st['avg_freight_value'].values[0]:.2f}**
                """)
        with rcol2:
            if not lintas_st.empty:
                st.metric("🚛 Lintas State (Inter-state)", f"{lintas_st['share_pct'].values[0]:.1f}% Item")
                st.markdown(f"""
- Rata-rata Durasi: **{lintas_st['avg_delivery_days'].values[0]:.1f} hari** (hampir 2x lipat)
- Rata-rata Ongkir: **R$ {lintas_st['avg_freight_value'].values[0]:.2f}** (+75% lebih mahal)
                """)

    with st.expander("💡 **Insight Geospasial & Pasokan Penjual** (klik untuk membuka)", expanded=True):
        st.markdown("""
- **Dominasi São Paulo (SP):** SP adalah episentrum baik pembeli (40.501 pesanan, 38,3% revenue) maupun penjual (1.769 penjual). Rasio pesanan per penjual sangat sehat (23 pesanan/penjual).
- **Ketimpangan Pasokan Tertinggi:** Negara bagian **Bahia (BA)** mencatat 181 pesanan per penjual, **Pernambuco (PE)** 177, dan **Ceará (CE)** 107. Wilayah ini memiliki permintaan tinggi namun kekurangan pasokan penjual lokal.
- **Dampak Pengiriman Lintas State:** 63,8% transaksi dikirim lintas negara bagian dengan durasi rata-rata 15,0 hari dan biaya R$ 23,63, dibandingkan hanya 7,9 hari dan R$ 13,45 jika barang dikirim dari state yang sama.
        """)

# =========================================================
# TAB 3: PERTANYAAN 3 - DURASI PENGIRIMAN & REVIEW SCORE
# =========================================================
with tab3:
    st.header("🚚 Hubungan Durasi Pengiriman dengan Kepuasan Pelanggan (Review Score)")
    st.markdown("""
    **Pertanyaan SMART:** *Bagaimana pengaruh kecepatan pengiriman (Fast, Normal, Slow) terhadap skor ulasan pembeli, dan seberapa drastis kepuasan turun saat pesanan terlambat dari tanggal estimasi?*
    """)

    deliv_df = order_level_df.dropna(subset=['delivery_days', 'review_score']).copy()
    deliv_df = deliv_df[deliv_df['delivery_days'] >= 0]

    if deliv_df.empty:
        st.warning("Data durasi pengiriman dan ulasan tidak tersedia pada filter saat ini.")
    else:
        # 1. Kategori Pengiriman
        def categorize_speed(days):
            if days < 7:
                return 'Fast (< 7 Hari)'
            elif days <= 14:
                return 'Normal (7-14 Hari)'
            else:
                return 'Slow (> 14 Hari)'

        cat_order = ['Fast (< 7 Hari)', 'Normal (7-14 Hari)', 'Slow (> 14 Hari)']
        deliv_df['delivery_cat_std'] = pd.Categorical(
            deliv_df['delivery_days'].apply(categorize_speed),
            categories=cat_order,
            ordered=True
        )
        cat_summary = deliv_df.groupby('delivery_cat_std', observed=True).agg(
            total_orders=('order_id', 'nunique'),
            avg_rating=('review_score', 'mean')
        ).reset_index()

        # 2. Fine Bins
        fine_bins = [-1, 3, 6, 10, 14, 21, 30, np.inf]
        fine_labels = ['0-3', '4-6', '7-10', '11-14', '15-21', '22-30', '> 30']
        deliv_df['fine_bin'] = pd.cut(deliv_df['delivery_days'], bins=fine_bins, labels=fine_labels)
        fine_summary = deliv_df.groupby('fine_bin', observed=True).agg(
            total_orders=('order_id', 'nunique'),
            avg_rating=('review_score', 'mean')
        ).reset_index()

        # 3. Status Terhadap Estimasi
        late_summary = deliv_df.groupby('is_late_vs_estimate').agg(
            total_orders=('order_id', 'nunique'),
            avg_rating=('review_score', 'mean')
        ).reset_index()
        late_summary['status'] = late_summary['is_late_vs_estimate'].map({0: 'Tepat waktu / lebih awal', 1: 'Melewati estimasi'})

        # --- GRAFIK 3: SUBPLOT 1x3 SESUAI CELL 35 ---
        fig3, ax3 = plt.subplots(1, 3, figsize=(16, 5))

        # Panel 1: Rating per Kategori Pengiriman
        n_cats = len(cat_summary)
        cat_colors = [COLOR_GOOD, COLOR_MAIN, COLOR_ACCENT][:n_cats]
        b1 = ax3[0].bar(cat_summary['delivery_cat_std'].astype(str), cat_summary['avg_rating'], color=cat_colors)
        ax3[0].set_title('Rating per Kategori Durasi', fontsize=11, fontweight='bold', pad=10)
        ax3[0].set_ylabel('Rata-rata Review Score (1-5)', fontsize=10)
        ax3[0].set_ylim(0, 5)
        ax3[0].bar_label(b1, fmt='%.2f', padding=3, fontsize=9.5, fontweight='bold')
        ax3[0].tick_params(axis='x', rotation=15)

        # Panel 2: Rating per Rentang Hari Pengiriman
        fine_colors = [COLOR_NEUTRAL if lbl in ['0-3', '4-6', '7-10', '11-14'] else COLOR_ACCENT for lbl in fine_summary['fine_bin'].astype(str)]
        b2 = ax3[1].bar(fine_summary['fine_bin'].astype(str), fine_summary['avg_rating'], color=fine_colors)
        ax3[1].set_title('Rating per Rentang Hari Pengiriman', fontsize=11, fontweight='bold', pad=10)
        ax3[1].set_xlabel('Durasi Pengiriman (Hari)', fontsize=10)
        ax3[1].set_ylim(0, 5)
        ax3[1].bar_label(b2, fmt='%.2f', padding=3, fontsize=9, fontweight='bold')

        # Panel 3: Status Tanggal Estimasi
        n_late = len(late_summary)
        late_colors = [COLOR_GOOD, COLOR_ACCENT][:n_late]
        b3 = ax3[2].bar(late_summary['status'], late_summary['avg_rating'], color=late_colors)
        ax3[2].set_title('Rating Berdasarkan Tanggal Estimasi', fontsize=11, fontweight='bold', pad=10)
        ax3[2].set_ylim(0, 5)
        ax3[2].bar_label(b3, fmt='%.2f', padding=3, fontsize=9.5, fontweight='bold')
        ax3[2].tick_params(axis='x', rotation=15)

        fig3.suptitle('Durasi Pengiriman dan Kepuasan Pelanggan (Review Score)', fontsize=13, fontweight='bold', y=1.03)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

        with st.expander("💡 **Insight Hubungan Pengiriman & Kepuasan** (klik untuk membuka)", expanded=True):
            st.markdown("""
- **Penurunan Skor Berdasarkan Kategori:** Rating pelanggan tinggi pada durasi **Fast (< 7 hari: 4,42)** dan **Normal (7–14 hari: 4,30)**, namun merosot tajam pada kategori **Slow (> 14 hari: 3,65)**.
- **Titik Kritis Pengiriman (> 21 Hari):** Rating bertahan di atas 4,00 hingga hari ke-21 (15–21 hari: 4,10), namun jatuh drastis ke **3,49** pada rentang 22–30 hari dan anjlok ke **2,17** ketika durasi melampaui 30 hari.
- **Dampak Keterlambatan Estimasi:** Pesanan yang **melewati tanggal estimasi** hanya memperoleh rating **2,57** (dibandingkan 4,29 pada pengiriman tepat waktu).
- **Toleransi Pelanggan:** Sebanyak **73,8%** pesanan lambat (> 14 hari) tetap tiba sebelum atau tepat pada tanggal estimasi yang dijanjikan, membuktikan bahwa menepati komitmen janji pengiriman sama pentingnya dengan kecepatan mutlak.
            """)

# =========================================================
# TAB 4: PERTANYAAN 4 - KINERJA KATEGORI PRODUK
# =========================================================
with tab4:
    st.header("📦 Kinerja Kategori Produk (Revenue & Volume Pesanan)")
    st.markdown("""
    **Pertanyaan SMART:** *Kategori produk apa saja yang menjadi penyumbang pesanan dan revenue terbesar di platform, serta kategori mana yang paling minim peminat?*
    """)

    prod_perf = filtered_df.dropna(subset=['product_category_name_english']).groupby('product_category_name_english').agg(
        total_orders=('order_id', 'nunique'),
        total_items=('order_id', 'count'),
        total_revenue=('price', 'sum')
    ).reset_index().rename(columns={'product_category_name_english': 'product_category'})

    if prod_perf.empty:
        st.warning("Data kategori produk tidak tersedia pada filter saat ini.")
    else:
        tot_platform_rev = prod_perf['total_revenue'].sum()
        prod_perf['revenue_share_pct'] = prod_perf['total_revenue'] / max(tot_platform_rev, 1) * 100
        prod_perf = prod_perf.sort_values('total_revenue', ascending=False).reset_index(drop=True)

        top_revenue = prod_perf.head(10)
        top_volume = prod_perf.sort_values('total_orders', ascending=False).head(10)
        bottom_revenue = prod_perf.sort_values('total_revenue', ascending=True).head(10)

        # --- GRAFIK 4A: TOP 10 REVENUE & ORDER VOLUME SESUAI CELL 38 ---
        st.subheader("🏆 Top 10 Kategori Produk: Revenue & Volume Pesanan")
        fig4a, ax4a = plt.subplots(1, 2, figsize=(16, 6))

        # Panel Kiri: Top 10 Revenue
        max_rev = max(top_revenue['total_revenue'].max(), 1)
        sns.barplot(data=top_revenue, x='total_revenue', y='product_category', color=COLOR_MAIN, ax=ax4a[0])
        ax4a[0].set_title('Top 10 Kategori Berdasarkan Revenue', fontsize=12, fontweight='bold', pad=10)
        ax4a[0].set_xlabel('Total Revenue (R$)', fontsize=10)
        ax4a[0].set_ylabel('Kategori Produk', fontsize=10)
        for i, val in enumerate(top_revenue['total_revenue']):
            ax4a[0].text(val + (max_rev * 0.02), i, f"R$ {val:,.0f}", va='center', fontsize=8.5)
        ax4a[0].set_xlim(0, max_rev * 1.3)
        ax4a[0].ticklabel_format(style='plain', axis='x')

        # Panel Kanan: Top 10 Volume Pesanan
        max_vol = max(top_volume['total_orders'].max(), 1)
        sns.barplot(data=top_volume, x='total_orders', y='product_category', color=COLOR_GOOD, ax=ax4a[1])
        ax4a[1].set_title('Top 10 Kategori Berdasarkan Volume Pesanan', fontsize=12, fontweight='bold', pad=10)
        ax4a[1].set_xlabel('Jumlah Pesanan', fontsize=10)
        ax4a[1].set_ylabel('')
        for i, val in enumerate(top_volume['total_orders']):
            ax4a[1].text(val + (max_vol * 0.02), i, f"{val:,.0f}", va='center', fontsize=8.5)
        ax4a[1].set_xlim(0, max_vol * 1.25)

        plt.tight_layout()
        st.pyplot(fig4a)
        plt.close(fig4a)

        # --- GRAFIK 4B: BOTTOM 10 REVENUE SESUAI CELL 38 ---
        st.subheader("⚠️ Bottom 10 Kategori Produk Berdasarkan Revenue Terendah")
        fig4b, ax4b = plt.subplots(figsize=(11, 4.5))
        max_bot_rev = max(bottom_revenue['total_revenue'].max(), 1)
        sns.barplot(data=bottom_revenue, x='total_revenue', y='product_category', color=COLOR_ACCENT, ax=ax4b)
        ax4b.set_title('Bottom 10 Kategori Berdasarkan Revenue', fontsize=12, fontweight='bold', pad=10)
        ax4b.set_xlabel('Total Revenue (R$)', fontsize=10)
        ax4b.set_ylabel('Kategori Produk', fontsize=10)
        for i, (val, orders) in enumerate(zip(bottom_revenue['total_revenue'], bottom_revenue['total_orders'])):
            ax4b.text(val + (max_bot_rev * 0.03), i, f"R$ {val:,.0f} ({orders} pesanan)", va='center', fontsize=8.5)
        ax4b.set_xlim(0, max_bot_rev * 1.45)
        plt.tight_layout()
        st.pyplot(fig4b)
        plt.close(fig4b)

        with st.expander("💡 **Insight Kinerja Kategori Produk** (klik untuk membuka)", expanded=True):
            st.markdown("""
- **Konsentrasi Pendapatan:** Tiga kategori teratas — **health_beauty** (R$ 1.233.132), **watches_gifts** (R$ 1.166.177), dan **bed_bath_table** (R$ 1.023.435) — menyumbang **25,9%** dari total seluruh revenue. 10 kategori teratas menyumbang **62,4%** revenue.
- **Pembeda Revenue vs Volume:** Kategori **bed_bath_table** adalah juara volume transaksi (9.272 pesanan), sementara **watches_gifts** unggul dalam nilai per pesanan (AOV tinggi).
- **Kategori Terbawah:** 10 kategori paling bawah — mulai dari *security_and_services* (R$ 283), *fashion_childrens_clothes* (R$ 520), hingga *cds_dvds_musicals* (R$ 730) — hanya menyumbang **0,09%** total revenue platform.
            """)

# =========================================================
# TAB 5: PERTANYAAN 5 - METODE PEMBAYARAN & CICILAN
# =========================================================
with tab5:
    st.header("💳 Preferensi Metode Pembayaran dan Peran Cicilan")
    st.markdown("""
    **Pertanyaan SMART:** *Metode pembayaran apa yang paling banyak digunakan pembeli, dan bagaimana pemilihan tenor cicilan kartu kredit memengaruhi nilai rata-rata belanja (Average Order Value/AOV)?*
    """)

    pay_summary = order_level_df.groupby('primary_payment_type').agg(
        total_orders=('order_id', 'nunique'),
        total_value=('total_payment_value', 'sum'),
        avg_order_value=('total_payment_value', 'mean')
    ).reset_index()

    if pay_summary.empty:
        st.warning("Data pembayaran tidak tersedia pada filter saat ini.")
    else:
        tot_pay_orders = pay_summary['total_orders'].sum()
        tot_pay_val = pay_summary['total_value'].sum()
        pay_summary['order_share_pct'] = pay_summary['total_orders'] / max(tot_pay_orders, 1) * 100
        pay_summary['value_share_pct'] = pay_summary['total_value'] / max(tot_pay_val, 1) * 100
        pay_summary = pay_summary.sort_values('total_orders', ascending=False).reset_index(drop=True)

        # Kelompok Cicilan Kartu Kredit
        credit_card_df = order_level_df[order_level_df['primary_payment_type'] == 'credit_card'].copy()

        if credit_card_df.empty:
            has_installment = False
            installment_summary = pd.DataFrame(columns=['installment_group', 'total_orders', 'avg_order_value'])
        else:
            has_installment = True
            credit_card_df['installment_group'] = pd.cut(
                credit_card_df['max_installments'],
                bins=[-1, 1, 4, 8, 100],
                labels=['1x (tanpa cicilan)', '2-4x', '5-8x', '> 8x']
            )
            installment_summary = credit_card_df.groupby('installment_group', observed=True).agg(
                total_orders=('order_id', 'nunique'),
                avg_order_value=('total_payment_value', 'mean')
            ).reset_index()

        # --- GRAFIK 5: DUAL SUBPLOT SESUAI CELL 41 ---
        fig5, ax5 = plt.subplots(1, 2, figsize=(15, 6))

        # Panel 1: Porsi Pesanan vs Porsi Nilai Transaksi
        method_labels = pay_summary['primary_payment_type'].str.replace('_', ' ').str.title()
        x = np.arange(len(pay_summary))
        width = 0.38
        b1 = ax5[0].bar(x - width / 2, pay_summary['order_share_pct'], width, label='Porsi Jumlah Pesanan', color=COLOR_MAIN)
        b2 = ax5[0].bar(x + width / 2, pay_summary['value_share_pct'], width, label='Porsi Nilai Transaksi', color=COLOR_GOOD)
        ax5[0].set_xticks(x)
        ax5[0].set_xticklabels(method_labels)
        ax5[0].set_ylabel('Persentase (%)', fontsize=10)
        ax5[0].set_title('Porsi Pesanan vs Porsi Nilai Transaksi per Metode', fontsize=12, fontweight='bold', pad=10)
        ax5[0].bar_label(b1, fmt='%.1f%%', padding=3, fontsize=8.5)
        ax5[0].bar_label(b2, fmt='%.1f%%', padding=3, fontsize=8.5)
        max_share = max(pay_summary['order_share_pct'].max(), pay_summary['value_share_pct'].max())
        ax5[0].set_ylim(0, max(max_share * 1.15, 10))
        ax5[0].legend(frameon=True)

        # Panel 2: AOV Berdasarkan Kelompok Cicilan
        if has_installment and not installment_summary.empty:
            b_inst = ax5[1].bar(installment_summary['installment_group'].astype(str), installment_summary['avg_order_value'], color=COLOR_MAIN)
            ax5[1].set_title('AOV Pesanan Kartu Kredit per Kelompok Cicilan', fontsize=12, fontweight='bold', pad=10)
            ax5[1].set_xlabel('Kelompok Cicilan', fontsize=10)
            ax5[1].set_ylabel('Rata-rata Nilai Pesanan / AOV (R$)', fontsize=10)
            max_aov = max(installment_summary['avg_order_value'].max(), 1)
            for i, (aov, n) in enumerate(zip(installment_summary['avg_order_value'], installment_summary['total_orders'])):
                ax5[1].text(i, aov + (max_aov * 0.02), f"R$ {aov:,.0f}\n({n:,} pesanan)", ha='center', fontsize=8.5)
            ax5[1].set_ylim(0, max_aov * 1.25)
        else:
            ax5[1].set_title('AOV Kartu Kredit per Cicilan (Tidak ada data)', fontsize=12, fontweight='bold', pad=10)
            ax5[1].text(0.5, 0.5, 'Tidak ada data kartu kredit\npada filter saat ini', ha='center', va='center', transform=ax5[1].transAxes, fontsize=12, color='gray')

        plt.tight_layout()
        st.pyplot(fig5)
        plt.close(fig5)

        with st.expander("💡 **Insight Metode Pembayaran & Cicilan** (klik untuk membuka)", expanded=True):
            st.markdown("""
- **Dominasi Kartu Kredit:** Menguasai **75,5%** volume pesanan dan **78,5%** nilai transaksi dengan AOV sebesar R$ 166,18.
- **Posisi Kuat Boleto:** Metode tiket pembayaran lokal (Boleto) menempati posisi kedua dengan **19,9%** pesanan dan **18,0%** nilai transaksi, menjadikannya kanal penting untuk menjangkau pelanggan *unbanked*.
- **Peran Kunci Cicilan Terhadap AOV:** AOV melonjak drastis seiring panjangnya tenor cicilan. AOV kartu kredit naik dari **R$ 100,62** (1x bayar langsung) menjadi **R$ 389,49** (> 8x cicilan), atau naik hampir **3,9 kali lipat**.
            """)

# =========================================================
# TAB 6: RANGKUMAN & REKOMENDASI BISNIS STRATEGIS
# =========================================================
with tab6:
    st.header("📝 Kesimpulan & Actionable Recommendation")

    st.subheader("📌 5 Kesimpulan Utama Hasil Analisis")
    st.markdown("""
1. **Segmentasi Pelanggan (RFM):** Basis pelanggan e-commerce sangat bergantung pada pembeli satu kali (hanya 3,0% yang pernah membeli ulang). Segmen *Recent Mid-High Spenders* menjadi motor pendapatan utama (50,9% revenue). Sementara segmen *At-Risk* dan *Lost* mencakup 40,0% pelanggan yang perlu diaktifkan kembali.
2. **Distribusi Geospasial Pasar:** Konsentrasi penjual terpusat di SP (1.769 penjual). Terjadi defisit pasokan penjual lokal yang masif di BA, PE, CE, dan ES. Akibatnya 63,8% pengiriman terpaksa lintas state, melipatgandakan waktu tempuh (15 hari vs 7,9 hari) dan ongkos kirim.
3. **Durasi Pengiriman & Kepuasan:** Skor ulasan turun tajam setelah pengiriman melewati 21 hari (dari 4,10 menjadi 3,49 dan 2,17). Pelanggan sangat sensitif terhadap janji estimasi: keterlambatan dari tanggal estimasi menjatuhkan skor ulasan rata-rata ke level 2,57.
4. **Kinerja Kategori Produk:** 10 kategori teratas mendominasi 62,4% pendapatan (*health_beauty*, *watches_gifts*, dan *bed_bath_table* menyumbang 25,9%). 10 kategori terbawah hanya menyumbang 0,09% revenue.
5. **Metode Pembayaran & Cicilan:** Kartu kredit (75,5%) dan Boleto (19,9%) mendominasi 95%+ transaksi. Tenor cicilan > 8x mampu mendongkrak AOV hingga 3,9 kali lipat dibanding pembayaran 1x.
    """)

    st.markdown("---")
    st.subheader("🎯 Actionable Recommendations (Rekomendasi Tindakan Bisnis)")

    rec_col1, rec_col2 = st.columns(2)

    with rec_col1:
        st.info("""
**1. Program Pembelian Kedua (Retensi Otomatis)**

Jalankan kampanye otomatis berupa voucher diskon pembelian kedua yang dikirim via email/notifikasi beberapa hari setelah pesanan pertama diterima dengan status delivered. Targetkan segmen *Recent Mid-High Spenders* dan *Potential Loyalists* untuk menaikkan repeat purchase rate di atas 3%.
        """)

        st.info("""
**2. Ekspansi Fulfillment Hub Regional**

Bangun micro-fulfillment center atau rekrut penjual lokal di kawasan dengan rasio pesanan per penjual tertinggi seperti **Bahia (BA), Pernambuco (PE), Ceará (CE)**, serta **Rio de Janeiro (RJ)** untuk memangkas ketergantungan pengiriman lintas negara bagian dari 63,8% ke bawah 50%.
        """)

        st.info("""
**3. Pengetatan SLA & Kompensasi Keterlambatan Estimasi**

Tetapkan batas Service Level Agreement (SLA) pengiriman maksimal 21 hari. Bangun sistem deteksi dini untuk pesanan yang berisiko melewati tanggal estimasi dan kirimkan voucher kompensasi otomatis untuk mencegah review rating anjlok ke bintang 1–2.
        """)

    with rec_col2:
        st.success("""
**4. Kurasi Inventaris & Promosi Unggulan**

Alokasikan slot promosi berbayar, rekomendasi algoritma homepage, dan kapasitas pergudangan prioritas untuk 3 kategori teratas: *health_beauty*, *watches_gifts*, dan *bed_bath_table*. Lakukan review efisiensi biaya penyimpanan pada 10 kategori terendah yang kinerjanya sangat minim.
        """)

        st.success("""
**5. Strategi Promo Cicilan Bunga 0%**

Bekerja sama dengan penyedia kartu kredit dan payment gateway untuk memberikan promo cicilan 0% pada tenor 2–4x (kelompok terbanyak) dan tenor panjang (> 8x) khusus untuk produk bernilai tinggi guna mengerek Average Order Value (AOV) platform lebih tinggi lagi.
        """)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.caption("Dicoding Submission: Proyek Analisis Data | Dewa Bagus Pradnyana Cahyadi Putra | E-Commerce Public Dataset")
