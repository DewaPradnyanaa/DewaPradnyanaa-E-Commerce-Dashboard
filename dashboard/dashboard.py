import os
import tempfile
import warnings

# Direktori cache matplotlib harus diatur SEBELUM matplotlib diimpor
os.environ.setdefault('MPLCONFIGDIR', os.path.join(tempfile.gettempdir(), 'matplotlib_cache'))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# KONFIGURASI TEMA & PALET WARNA (identik dengan notebook)
# ---------------------------------------------------------
sns.set_theme(style='whitegrid')
plt.rcParams['font.size'] = 10

COLOR_MAIN = '#4A90E2'      # Biru: nilai utama / pembeli
COLOR_ACCENT = '#E63946'    # Merah: risiko / perhatian
COLOR_GOOD = '#2A9D8F'      # Hijau toska: performa tinggi / kepuasan
COLOR_NEUTRAL = '#B8C0CC'   # Abu-abu: netral

SEGMENT_ORDER = ['Champions', 'Loyal Customers', 'Potential Loyalists',
                 'At-Risk / Need Attention', 'Lost Customers']
SEGMENT_COLORS = dict(zip(SEGMENT_ORDER, [COLOR_GOOD, '#52B788', COLOR_MAIN, '#F4A261', COLOR_ACCENT]))

SPEED_ORDER = ['Fast (<=7 hari)', 'Normal (8-14 hari)', 'Slow (15-21 hari)', 'Very Slow (>21 hari)']
SPEED_COLORS = dict(zip(SPEED_ORDER, [COLOR_GOOD, '#52B788', '#F4A261', COLOR_ACCENT]))

LATE_LABELS = {False: 'Tepat Waktu / Lebih Awal', True: 'Terlambat vs Estimasi'}
LATE_COLORS = {False: COLOR_GOOD, True: COLOR_ACCENT}

INST_ORDER = ['1x (Bayar Penuh)', '2-3x', '4-6x', '7-10x', '>10x']


# ---------------------------------------------------------
# UTILITAS
# ---------------------------------------------------------
def idn(x, d=1):
    """Format angka gaya Indonesia: 1.234,5"""
    return f'{x:,.{d}f}'.replace(',', '_').replace('.', ',').replace('_', '.')


@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base, 'main_data.csv'),
        os.path.join(base, 'main_data.csv.gz'),
        'main_data.csv',
        'dashboard/main_data.csv',
        'submission/dashboard/main_data.csv',
    ]
    for p in candidates:
        if os.path.exists(p):
            df = pd.read_csv(p)
            df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
            return df
    return None


# ---------------------------------------------------------
# AGREGASI (logika sama dengan sel EDA di notebook)
# ---------------------------------------------------------
def summarize_rfm(df):
    cust = df.drop_duplicates('customer_unique_id')
    s = cust.groupby('customer_segment').agg(
        total_customers=('customer_unique_id', 'count'),
        avg_recency=('recency', 'mean'),
        repeat_buyers=('frequency', lambda x: (x > 1).sum()),
        total_revenue=('monetary', 'sum')
    )
    s = s.loc[[seg for seg in SEGMENT_ORDER if seg in s.index]].reset_index()
    s['pct_customers'] = s['total_customers'] / s['total_customers'].sum() * 100
    s['pct_revenue'] = s['total_revenue'] / s['total_revenue'].sum() * 100
    return s


def categorize_delivery_speed(d):
    if d <= 7:
        return 'Fast (<=7 hari)'
    elif d <= 14:
        return 'Normal (8-14 hari)'
    elif d <= 21:
        return 'Slow (15-21 hari)'
    return 'Very Slow (>21 hari)'


def summarize_delivery(df):
    v = df[df['review_score'].notna()].copy()
    v['speed_category'] = v['delivery_days'].apply(categorize_delivery_speed)

    speed = v.groupby('speed_category').agg(
        total_orders=('order_id', 'count'),
        avg_review=('review_score', 'mean'),
        pct_positive=('review_score', lambda s: (s >= 4).mean() * 100)
    )
    speed = speed.loc[[c for c in SPEED_ORDER if c in speed.index]].reset_index()

    late = v.groupby('is_late_vs_estimate').agg(
        total_orders=('order_id', 'count'),
        avg_review=('review_score', 'mean'),
        pct_positive=('review_score', lambda s: (s >= 4).mean() * 100)
    ).reset_index()
    late['status_label'] = late['is_late_vs_estimate'].map(LATE_LABELS)
    return speed, late


def group_installments(x):
    if x == 1:
        return '1x (Bayar Penuh)'
    elif x <= 3:
        return '2-3x'
    elif x <= 6:
        return '4-6x'
    elif x <= 10:
        return '7-10x'
    return '>10x'


def summarize_payment(df):
    p = df[df['primary_payment_type'].notna()].copy()

    pay = p.groupby('primary_payment_type').agg(
        total_orders=('order_id', 'count'),
        total_payment_value=('total_payment_value', 'sum'),
        avg_order_value=('total_payment_value', 'mean')
    ).sort_values('total_orders', ascending=False).reset_index()
    pay['order_share_pct'] = pay['total_orders'] / pay['total_orders'].sum() * 100
    pay['value_share_pct'] = pay['total_payment_value'] / pay['total_payment_value'].sum() * 100

    cc = p[(p['primary_payment_type'] == 'credit_card') & (p['max_installments'] >= 1)].copy()
    cc['installment_group'] = cc['max_installments'].apply(group_installments)
    inst = cc.groupby('installment_group').agg(
        total_orders=('order_id', 'count'),
        total_value=('total_payment_value', 'sum'),
        avg_order_value=('total_payment_value', 'mean')
    )
    inst = inst.loc[[g for g in INST_ORDER if g in inst.index]].reset_index()
    return pay, inst


# ---------------------------------------------------------
# GRAFIK (kode plotting disalin dari sel visualisasi notebook)
# ---------------------------------------------------------
def plot_rfm(rfm_summary):
    fig, ax = plt.subplots(1, 2, figsize=(16, 6))
    order = rfm_summary['customer_segment']
    palette_rfm = [SEGMENT_COLORS[s] for s in order]

    # Panel 1: Jumlah Pelanggan per Segmen
    sns.barplot(data=rfm_summary, x='customer_segment', y='total_customers',
                hue='customer_segment', order=order, palette=palette_rfm,
                legend=False, ax=ax[0])
    ax[0].set_title('Distribusi Jumlah Pelanggan per Segmen RFM', fontsize=13, fontweight='bold', pad=12)
    ax[0].set_xlabel('Segmen Pelanggan', fontsize=11)
    ax[0].set_ylabel('Jumlah Pelanggan', fontsize=11)
    max_c = rfm_summary['total_customers'].max()
    for i, (val, pct) in enumerate(zip(rfm_summary['total_customers'], rfm_summary['pct_customers'])):
        ax[0].text(i, val + (max_c * 0.02), f"{val:,}\n({pct:.1f}%)", ha='center', fontsize=9.5, fontweight='bold')
    ax[0].set_ylim(0, max_c * 1.18)
    ax[0].tick_params(axis='x', rotation=15)

    # Panel 2: Total Revenue per Segmen
    sns.barplot(data=rfm_summary, x='customer_segment', y='total_revenue',
                hue='customer_segment', order=order, palette=palette_rfm,
                legend=False, ax=ax[1])
    ax[1].set_title('Kontribusi Pendapatan per Segmen RFM (BRL)', fontsize=13, fontweight='bold', pad=12)
    ax[1].set_xlabel('Segmen Pelanggan', fontsize=11)
    ax[1].set_ylabel('Total Revenue (R$)', fontsize=11)
    max_r = rfm_summary['total_revenue'].max()
    for i, (val, pct) in enumerate(zip(rfm_summary['total_revenue'], rfm_summary['pct_revenue'])):
        ax[1].text(i, val + (max_r * 0.02), f"R$ {val:,.0f}\n({pct:.1f}%)", ha='center', fontsize=9.5, fontweight='bold')
    ax[1].set_ylim(0, max_r * 1.18)
    ax[1].tick_params(axis='x', rotation=15)

    plt.tight_layout()
    return fig


def plot_delivery(speed_summary, late_summary):
    fig, ax = plt.subplots(1, 2, figsize=(16, 5))

    # Panel 1: Rata-rata Skor Ulasan berdasarkan Kategori Kecepatan
    colors_speed = [SPEED_COLORS[c] for c in speed_summary['speed_category']]
    ax[0].bar(speed_summary['speed_category'], speed_summary['avg_review'], color=colors_speed)
    ax[0].set_title('Rata-rata Rating berdasarkan Kecepatan Pengiriman', fontsize=13, fontweight='bold', pad=12)
    ax[0].set_ylabel('Rata-rata Skor Ulasan (Skala 1 - 5)', fontsize=11)
    ax[0].set_ylim(0, 5.2)
    for i, (val, n) in enumerate(zip(speed_summary['avg_review'], speed_summary['total_orders'])):
        ax[0].text(i, val + 0.12, f"{val:.2f} ★\n({n:,} pesanan)", ha='center', fontsize=9.5, fontweight='bold')
    ax[0].tick_params(axis='x', rotation=10)

    # Panel 2: Dampak Keterlambatan Pengiriman vs Estimasi
    colors_late = [LATE_COLORS[b] for b in late_summary['is_late_vs_estimate']]
    ax[1].bar(late_summary['status_label'], late_summary['avg_review'], color=colors_late, width=0.5)
    ax[1].set_title('Pengaruh Keterlambatan Estimasi terhadap Kepuasan', fontsize=13, fontweight='bold', pad=12)
    ax[1].set_ylabel('Rata-rata Skor Ulasan (Skala 1 - 5)', fontsize=11)
    ax[1].set_ylim(0, 5.2)
    for i, (val, n, pct) in enumerate(zip(late_summary['avg_review'], late_summary['total_orders'],
                                          late_summary['pct_positive'])):
        ax[1].text(i, val + 0.12, f"{val:.2f} ★\n{pct:.1f}% ulasan positif\n({n:,} pesanan)",
                   ha='center', fontsize=9.5, fontweight='bold')

    plt.tight_layout()
    return fig


def plot_payment(payment_summary, installment_summary):
    fig, ax = plt.subplots(1, 2, figsize=(16, 6))

    # Panel 1: Pangsa Pesanan vs Pangsa Nilai Transaksi per Metode
    labels_pay = payment_summary['primary_payment_type'].str.replace('_', ' ').str.title()
    x_pos = np.arange(len(payment_summary))
    width = 0.38
    b1 = ax[0].bar(x_pos - width / 2, payment_summary['order_share_pct'], width,
                   label='% Jumlah Pesanan', color=COLOR_MAIN)
    b2 = ax[0].bar(x_pos + width / 2, payment_summary['value_share_pct'], width,
                   label='% Nilai Transaksi', color=COLOR_GOOD)
    ax[0].set_xticks(x_pos)
    ax[0].set_xticklabels(labels_pay)
    ax[0].set_ylabel('Persentase terhadap Total (%)', fontsize=11)
    ax[0].set_title('Porsi Pesanan vs Nilai Transaksi per Metode Pembayaran', fontsize=13, fontweight='bold', pad=12)
    ax[0].bar_label(b1, fmt='%.1f%%', padding=3, fontsize=9.5, fontweight='bold')
    ax[0].bar_label(b2, fmt='%.1f%%', padding=3, fontsize=9.5, fontweight='bold')
    y_top = max(payment_summary['order_share_pct'].max(), payment_summary['value_share_pct'].max())
    ax[0].set_ylim(0, max(88, y_top * 1.11))   # 88 = nilai pada notebook
    ax[0].legend()

    # Panel 2: AOV berdasarkan Kelompok Tenor Cicilan
    ax[1].bar(installment_summary['installment_group'], installment_summary['avg_order_value'], color=COLOR_MAIN)
    ax[1].set_title('Rata-rata Nilai Belanja (AOV) berdasarkan Tenor Cicilan', fontsize=13, fontweight='bold', pad=12)
    ax[1].set_xlabel('Kelompok Tenor Cicilan Kartu Kredit', fontsize=11)
    ax[1].set_ylabel('Average Order Value (R$)', fontsize=11)
    if not installment_summary.empty:
        max_aov = installment_summary['avg_order_value'].max()
        for i, (aov, n) in enumerate(zip(installment_summary['avg_order_value'],
                                         installment_summary['total_orders'])):
            ax[1].text(i, aov + (max_aov * 0.02), f"R$ {aov:,.0f}\n({n:,})",
                       ha='center', fontsize=9.5, fontweight='bold')
        ax[1].set_ylim(0, max_aov * 1.22)

    plt.tight_layout()
    return fig


# ---------------------------------------------------------
# TEKS INSIGHT DINAMIS (angka selalu sama dengan grafik)
# ---------------------------------------------------------
def seg_value(summary, seg, col):
    row = summary.loc[summary['customer_segment'] == seg, col]
    return float(row.iloc[0]) if not row.empty else 0.0


def risk_totals(summary):
    risk = summary[summary['customer_segment'].isin(['At-Risk / Need Attention', 'Lost Customers'])]
    return (int(risk['total_customers'].sum()), risk['pct_customers'].sum(),
            risk['total_revenue'].sum(), risk['pct_revenue'].sum())


def late_pair(late_summary):
    on = late_summary[late_summary['is_late_vs_estimate'] == False]
    lt = late_summary[late_summary['is_late_vs_estimate'] == True]
    return (on.iloc[0] if not on.empty else None), (lt.iloc[0] if not lt.empty else None)


def speed_rating(speed_summary, cat):
    row = speed_summary.loc[speed_summary['speed_category'] == cat, 'avg_review']
    return float(row.iloc[0]) if not row.empty else None


def insight_rfm(s):
    n_loyal, p_loyal = int(seg_value(s, 'Loyal Customers', 'total_customers')), seg_value(s, 'Loyal Customers', 'pct_customers')
    r_loyal, pr_loyal = seg_value(s, 'Loyal Customers', 'total_revenue'), seg_value(s, 'Loyal Customers', 'pct_revenue')
    n_ch, p_ch = int(seg_value(s, 'Champions', 'total_customers')), seg_value(s, 'Champions', 'pct_customers')
    n_rk, p_rk, r_rk, pr_rk = risk_totals(s)
    return f'''
- **Segmen Tulang Punggung (Loyal Customers):** **{idn(n_loyal, 0)} pelanggan ({idn(p_loyal)}%)** dengan pendapatan **R$ {idn(r_loyal / 1e6, 2)} juta ({idn(pr_loyal)}%)**.
- **Segmen Berisiko (At-Risk & Lost Customers):** gabungan **{idn(n_rk, 0)} pelanggan ({idn(p_rk)}%)** menyumbang **R$ {idn(r_rk / 1e6, 2)} juta ({idn(pr_rk)}%)** dari omset historis, sehingga risiko *revenue churn* nyata bila tidak ada program reaktivasi.
- **Segmen Champions:** **{idn(p_ch)}% pelanggan ({idn(n_ch, 0)} pelanggan)** dengan frekuensi dan nilai belanja tertinggi.
'''


def insight_delivery(speed, late):
    on, lt = late_pair(late)
    fast, normal = speed_rating(speed, 'Fast (<=7 hari)'), speed_rating(speed, 'Normal (8-14 hari)')
    lines = []
    if on is not None and lt is not None:
        lines.append(
            f"- **Penalti Keterlambatan yang Tajam:** pesanan tepat waktu/lebih awal meraih **{idn(on['avg_review'], 2)} ★** "
            f"({idn(on['pct_positive'])}% ulasan positif), sedangkan pesanan terlambat turun ke **{idn(lt['avg_review'], 2)} ★** "
            f"({idn(lt['pct_positive'])}% positif), selisih **{idn(on['avg_review'] - lt['avg_review'], 2)} bintang**.")
    elif on is not None:
        lines.append(f"- Pada filter ini seluruh pesanan tepat waktu/lebih awal dengan rating **{idn(on['avg_review'], 2)} ★**.")
    elif lt is not None:
        lines.append(f"- Pada filter ini seluruh pesanan terlambat dengan rating **{idn(lt['avg_review'], 2)} ★**.")
    if fast is not None and normal is not None:
        lines.append(
            f"- **Ambang Toleransi 14 Hari:** pengiriman ≤7 hari menghasilkan **{idn(fast, 2)} ★** dan 8-14 hari **{idn(normal, 2)} ★**; "
            f"rating menurun pada kategori yang lebih lambat.")
    return '\n'.join(lines)


def insight_payment(pay, inst):
    top = pay.iloc[0]
    lines = [
        f"- **Metode Dominan:** **{str(top['primary_payment_type']).replace('_', ' ').title()}** menguasai "
        f"**{idn(top['order_share_pct'])}% pesanan** ({idn(top['total_orders'], 0)} transaksi) dan "
        f"**{idn(top['value_share_pct'])}% nilai transaksi** (R$ {idn(top['total_payment_value'] / 1e6, 2)} juta)."
    ]
    if len(inst) >= 2:
        first, last = inst.iloc[0], inst.iloc[-1]
        lines.append(
            f"- **Efek Cicilan terhadap AOV:** AOV tenor **{first['installment_group']}** sebesar **R$ {idn(first['avg_order_value'], 0)}**, "
            f"sedangkan tenor **{last['installment_group']}** mencapai **R$ {idn(last['avg_order_value'], 0)}** "
            f"({idn(last['avg_order_value'] / first['avg_order_value'], 1)}x lipat).")
    return '\n'.join(lines)


# ---------------------------------------------------------
# APLIKASI STREAMLIT
# ---------------------------------------------------------
def main():
    st.set_page_config(
        page_title='E-Commerce Public Analytics Dashboard',
        page_icon='🛍️',
        layout='wide',
        initial_sidebar_state='expanded'
    )

    df_raw = load_data()
    if df_raw is None:
        st.error('Berkas data utama (main_data.csv) tidak ditemukan.')
        st.stop()

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown('### 👨‍💻 Data Analyst')
        st.markdown('''
        * **Nama:** Dewa Bagus Pradnyana Cahyadi Putra  
        * **Email:** pradnyana08@gmail.com  
        * **Dicoding ID:** `dewa_bagus_pradnjv3s`
        ''')
        st.markdown('---')
        st.subheader('⚙️ Filter Interaktif')

        min_date = df_raw['order_purchase_timestamp'].min().date()
        max_date = df_raw['order_purchase_timestamp'].max().date()

        st.markdown('**📅 Rentang Tanggal Pemesanan**')
        c1, c2 = st.columns(2)
        with c1:
            start_date = st.date_input('Mulai', min_value=min_date, max_value=max_date, value=min_date)
        with c2:
            end_date = st.date_input('Selesai', min_value=min_date, max_value=max_date, value=max_date)

        if start_date > end_date:
            st.error('Tanggal awal tidak boleh melebihi tanggal akhir!')
            start_date, end_date = min_date, max_date

        selected_segments = st.multiselect(
            '👥 Segmen Pelanggan (RFM):', options=SEGMENT_ORDER, default=[],
            placeholder='Semua Segmen (Default)')

        all_payments = sorted(df_raw['primary_payment_type'].dropna().unique().tolist())
        selected_payments = st.multiselect(
            '💳 Metode Pembayaran:', options=all_payments,
            format_func=lambda x: str(x).replace('_', ' ').title(),
            default=[], placeholder='Semua Metode (Default)')

        st.markdown('---')
        st.caption('💡 Filter yang dikosongkan akan menampilkan seluruh data secara default.')

    # ---------------- FILTER DATA ----------------
    # main_data.csv = 1 baris per pesanan
    order_df = df_raw[
        (df_raw['order_purchase_timestamp'].dt.date >= start_date) &
        (df_raw['order_purchase_timestamp'].dt.date <= end_date)
    ]
    if selected_segments:
        order_df = order_df[order_df['customer_segment'].isin(selected_segments)]
    if selected_payments:
        order_df = order_df[order_df['primary_payment_type'].isin(selected_payments)]

    # ---------------- HEADER & KPI ----------------
    st.title('🛍️ E-Commerce Public Analytics Dashboard')
    st.markdown('''
    Dashboard interaktif untuk eksplorasi **E-Commerce Public Dataset** (Olist, Brasil) dengan fokus pada 3 pertanyaan bisnis SMART:
    **Segmentasi RFM**, **Durasi Pengiriman & Kepuasan**, serta **Metode Pembayaran & Cicilan**.
    ''')

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric('Total Pesanan', f'{order_df["order_id"].nunique():,}')
    k2.metric('Total Revenue', f'R$ {order_df["total_items_price"].sum():,.0f}')
    k3.metric('Pelanggan Unik', f'{order_df["customer_unique_id"].nunique():,}')
    k4.metric('Rata-rata Rating', f'{order_df["review_score"].mean():.2f} ★' if not order_df.empty else '-')
    k5.metric('Rata-rata Pengiriman', f'{order_df["delivery_days"].mean():.1f} Hari' if not order_df.empty else '-')
    st.markdown('---')

    tab1, tab2, tab3, tab4 = st.tabs([
        '👥 Pertanyaan 1: Segmentasi RFM',
        '🚚 Pertanyaan 2: Durasi Pengiriman & Kepuasan',
        '💳 Pertanyaan 3: Metode Pembayaran & Cicilan',
        '📑 Kesimpulan & Rekomendasi Bisnis'
    ])

    # ===== TAB 1 =====
    with tab1:
        st.header('👥 Segmentasi Pelanggan Berbasis Analisis RFM')
        st.markdown('**Pertanyaan SMART:** *Bagaimana sebaran segmentasi pelanggan berdasarkan analisis RFM per 30 Agustus 2018, '
                    'berapa proporsi pelanggan pada segmen berisiko (At-Risk / Lost), dan berapa kontribusi revenue dari masing-masing segmen?*')
        if order_df.empty:
            st.warning('Tidak ada data yang sesuai dengan filter yang dipilih.')
        else:
            rfm_summary = summarize_rfm(order_df)
            fig = plot_rfm(rfm_summary)
            st.pyplot(fig)
            plt.close(fig)

            st.subheader('📋 Ringkasan Metrik Segmen RFM')
            disp = rfm_summary[['customer_segment', 'total_customers', 'total_revenue', 'avg_recency',
                                'repeat_buyers', 'pct_customers', 'pct_revenue']].copy()
            disp.columns = ['Segmen Pelanggan', 'Total Pelanggan', 'Total Revenue (R$)',
                            'Rata-rata Recency (Hari)', 'Repeat Buyers',
                            'Proporsi Pelanggan (%)', 'Kontribusi Revenue (%)']
            st.dataframe(disp.style.format({
                'Total Pelanggan': '{:,.0f}', 'Total Revenue (R$)': 'R$ {:,.2f}',
                'Rata-rata Recency (Hari)': '{:.1f}', 'Repeat Buyers': '{:,.0f}',
                'Proporsi Pelanggan (%)': '{:.2f}%', 'Kontribusi Revenue (%)': '{:.2f}%'
            }), hide_index=True)

            with st.expander('💡 **Insight Kunci Segmentasi RFM**', expanded=True):
                st.markdown(insight_rfm(rfm_summary))

    # ===== TAB 2 =====
    with tab2:
        st.header('🚚 Hubungan Durasi Pengiriman dengan Kepuasan Pelanggan')
        st.markdown('**Pertanyaan SMART:** *Bagaimana pengaruh durasi pengiriman terhadap skor ulasan pelanggan (review score), '
                    'dan seberapa drastis kepuasan pelanggan turun ketika pengiriman terlambat dari estimasi (late vs estimate)?*')
        if order_df['review_score'].notna().sum() == 0:
            st.warning('Data durasi pengiriman dan ulasan tidak tersedia pada filter saat ini.')
        else:
            speed_summary, late_summary = summarize_delivery(order_df)
            fig = plot_delivery(speed_summary, late_summary)
            st.pyplot(fig)
            plt.close(fig)
            with st.expander('💡 **Insight Hubungan Pengiriman & Kepuasan**', expanded=True):
                st.markdown(insight_delivery(speed_summary, late_summary))

    # ===== TAB 3 =====
    with tab3:
        st.header('💳 Metode Pembayaran, Nilai Transaksi, dan Cicilan')
        st.markdown('**Pertanyaan SMART:** *Metode pembayaran apa yang paling dominan digunakan pelanggan, dan bagaimana pemilihan '
                    'jumlah cicilan kartu kredit memengaruhi nilai rata-rata pesanan (Average Order Value / AOV)?*')
        if order_df['primary_payment_type'].notna().sum() == 0:
            st.warning('Data pembayaran tidak tersedia pada filter saat ini.')
        else:
            payment_summary, installment_summary = summarize_payment(order_df)
            fig = plot_payment(payment_summary, installment_summary)
            st.pyplot(fig)
            plt.close(fig)
            with st.expander('💡 **Insight Metode Pembayaran & Cicilan**', expanded=True):
                st.markdown(insight_payment(payment_summary, installment_summary))

    # ===== TAB 4 (selalu memakai SELURUH data, sesuai notebook) =====
    with tab4:
        st.header('📑 Kesimpulan Eksekutif & Rekomendasi Bisnis')
        st.caption('Kesimpulan dihitung dari seluruh data (tidak terpengaruh filter sidebar).')
        st.markdown('---')

        g_rfm = summarize_rfm(df_raw)
        g_speed, g_late = summarize_delivery(df_raw)
        g_pay, g_inst = summarize_payment(df_raw)

        n_rk, p_rk, r_rk, pr_rk = risk_totals(g_rfm)
        loyal_p = seg_value(g_rfm, 'Loyal Customers', 'pct_customers')
        pot_p = seg_value(g_rfm, 'Potential Loyalists', 'pct_customers')
        loyal_pr = seg_value(g_rfm, 'Loyal Customers', 'pct_revenue')
        loyal_r = seg_value(g_rfm, 'Loyal Customers', 'total_revenue')
        lost_p = seg_value(g_rfm, 'Lost Customers', 'pct_customers')
        atrisk_p = seg_value(g_rfm, 'At-Risk / Need Attention', 'pct_customers')
        ch_p = seg_value(g_rfm, 'Champions', 'pct_customers')
        ch_n = int(seg_value(g_rfm, 'Champions', 'total_customers'))

        cust = df_raw.drop_duplicates('customer_unique_id')
        repeat_rate = (cust['frequency'] > 1).mean() * 100

        on, lt = late_pair(g_late)
        fast, normal = speed_rating(g_speed, 'Fast (<=7 hari)'), speed_rating(g_speed, 'Normal (8-14 hari)')
        top = g_pay.iloc[0]
        inst_first, inst_last = g_inst.iloc[0], g_inst.iloc[-1]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader('📌 Kesimpulan Berdasarkan 3 Pertanyaan SMART')
            st.markdown(f'''
1. **Segmentasi Pelanggan (RFM):**
   * **Loyal Customers ({idn(loyal_p)}%)** dan **Potential Loyalists ({idn(pot_p)}%)** membentuk **{idn(loyal_p + pot_p)}%** basis pelanggan.
   * *Loyal Customers* menopang omset utama: **{idn(loyal_pr)}% (R$ {idn(loyal_r / 1e6, 2)} juta)**.
   * Segmen berisiko (*Lost* {idn(lost_p)}% + *At-Risk* {idn(atrisk_p)}%) menyumbang **{idn(pr_rk)}% pendapatan historis (R$ {idn(r_rk / 1e6, 2)} juta)**.
   * *Champions* hanya **{idn(ch_p)}% ({idn(ch_n, 0)} pelanggan)**.

2. **Durasi Pengiriman & Rating Kepuasan:**
   * Pesanan tepat waktu meraih **{idn(on['avg_review'], 2)} ★ ({idn(on['pct_positive'])}% positif)**, sedangkan pesanan terlambat turun ke **{idn(lt['avg_review'], 2)} ★ ({idn(lt['pct_positive'])}% positif)**.
   * Pengiriman ≤14 hari menjaga rating di atas 4,3 bintang (**{idn(fast, 2)} ★** untuk ≤7 hari, **{idn(normal, 2)} ★** untuk 8-14 hari).

3. **Metode Pembayaran & Cicilan:**
   * **{str(top['primary_payment_type']).replace('_', ' ').title()}** mendominasi **{idn(top['order_share_pct'])}%** pesanan dan **{idn(top['value_share_pct'])}%** nilai transaksi.
   * AOV naik seiring tenor: **R$ {idn(inst_first['avg_order_value'], 0)}** (tenor {inst_first['installment_group']}) menjadi **R$ {idn(inst_last['avg_order_value'], 0)}** (tenor {inst_last['installment_group']}).
            ''')

        with col2:
            st.subheader('🎯 Rekomendasi Aksi Nyata (Actionable Insights)')
            st.markdown(f'''
1. **Program Win-Back & Retensi Awal:**
   - Berikan kupon diskon pesanan kedua dalam 7-14 hari setelah paket *delivered* untuk menaikkan *repeat purchase rate* dari **{idn(repeat_rate)}%**.
   - Jalankan kampanye reaktivasi bagi **{idn(n_rk, 0)} pelanggan** segmen *At-Risk* dan *Lost* untuk mengamankan **{idn(pr_rk, 0)}%** potensi pendapatan.

2. **Penyempurnaan Estimasi Tiba (SLA Safety Buffer):**
   - Tambahkan *buffer* 2-3 hari pada estimasi rute jarak jauh agar rating tidak jatuh ke level **{idn(lt['avg_review'], 2)} ★**.
   - Tetapkan target SLA maksimal 14 hari bagi mitra logistik.

3. **Kemitraan Promosi Cicilan 0%:**
   - Gandeng bank rekanan untuk cicilan 0% tenor 6-12 bulan pada produk bernilai menengah-tinggi guna mendongkrak AOV.
            ''')

        st.markdown('---')
        st.caption('Dicoding Submission: Proyek Analisis Data | Dewa Bagus Pradnyana Cahyadi Putra | E-Commerce Public Dataset')


if __name__ == '__main__':
    main()
