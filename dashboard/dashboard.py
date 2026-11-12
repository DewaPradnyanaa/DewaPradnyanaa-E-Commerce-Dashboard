from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.ticker import FuncFormatter

# ---------------------------------------------------------------------------
# Konfigurasi halaman dan konstanta
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Dashboard Analisis E-Commerce", page_icon=":bar_chart:", layout="wide")

BLUE_BASE, BLUE_DARK = "#A9C8EE", "#1F4E8C"
RED_BASE, RED_DARK = "#F2B5B5", "#C1121F"

SEGMENT_ORDER = ["Champions", "Recent Mid-High Spenders", "Potential Loyalists",
                 "At-Risk / Need Attention", "Lost Customers"]
SPEED_ORDER = ["Fast (<=7 hari)", "Normal (8-14 hari)", "Slow (15-21 hari)", "Very Slow (>21 hari)"]
INSTALLMENT_ORDER = ["1x (Tanpa Cicilan)", "2-3x", "4-6x", "7-10x", ">10x"]
PAYMENT_LABELS = {"credit_card": "Credit Card", "boleto": "Boleto",
                  "voucher": "Voucher", "debit_card": "Debit Card"}


# ---------------------------------------------------------------------------
# Fungsi bantu format angka (pemisah ribuan titik, desimal koma)
# ---------------------------------------------------------------------------
def fmt_int(x):
    return f"{x:,.0f}".replace(",", ".")


def fmt_dec(x, digits=2):
    return f"{x:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(x, digits=1):
    return fmt_dec(x, digits) + "%"


def highlight_colors(n, idx, base, highlight):
    """Semua bar berwarna dasar, hanya bar ke-idx yang disorot."""
    return [highlight if i == idx else base for i in range(n)]


# ---------------------------------------------------------------------------
# Memuat dan menyaring data
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Memuat data...")
def load_data():
    data_path = Path(__file__).parent / "main_data.csv"
    return pd.read_csv(data_path, parse_dates=["order_purchase_timestamp"])


def sidebar_filters(df):
    """Filter global di sidebar: berlaku untuk SEMUA bagian dashboard."""
    st.sidebar.markdown("**Nama:** Dewa Bagus Pradnyana Cahyadi Putra")
    st.sidebar.markdown("**Email:** pradnyana08@gmail.com")
    st.sidebar.markdown("**ID Dicoding:** `dewa_bagus_pradnjv3s`")
    st.sidebar.markdown("---")
    st.sidebar.header("Filter Data")
    st.sidebar.caption("Filter ini berlaku untuk seluruh visualisasi di dashboard.")

    states = sorted(df["customer_state"].dropna().unique())
    selected_states = st.sidebar.multiselect(
        "Negara bagian pembeli", options=states, default=[], placeholder="Semua negara bagian"
    )
    if selected_states:
        return df[df["customer_state"].isin(selected_states)].copy()
    return df.copy()


# ---------------------------------------------------------------------------
# Bagian 1: Segmentasi pelanggan (RFM)
# ---------------------------------------------------------------------------
def section_rfm(df):
    st.subheader("Segmentasi Pelanggan Berdasarkan RFM")
    st.caption(
        "Segmen RFM dihitung di notebook pada seluruh pelanggan (tanggal acuan 30 Agustus 2018). "
        "Grafik ini menampilkan pelanggan dari negara bagian yang dipilih."
    )

    customers = df.drop_duplicates("customer_unique_id")
    summary = customers.groupby("customer_segment").agg(
        total_customers=("customer_unique_id", "count"),
        avg_recency=("recency", "mean"),
        avg_monetary=("monetary", "mean"),
        repeat_buyers=("frequency", lambda x: (x > 1).sum()),
        total_revenue=("monetary", "sum"),
    ).reindex(SEGMENT_ORDER).fillna(0)
    summary["pct_customers"] = summary["total_customers"] / summary["total_customers"].sum() * 100
    summary["pct_revenue"] = summary["total_revenue"] / summary["total_revenue"].sum() * 100
    summary["pct_repeat"] = np.where(
        summary["total_customers"] > 0, summary["repeat_buyers"] / summary["total_customers"].replace(0, np.nan) * 100, 0
    )
    summary = summary.fillna(0)

    risk = summary.loc[["At-Risk / Need Attention", "Lost Customers"]]
    repeat_pct = (customers["frequency"] > 1).mean() * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Pelanggan Segmen Berisiko", fmt_pct(risk["pct_customers"].sum()),
                help="Persentase pelanggan pada segmen At-Risk / Need Attention dan Lost Customers")
    col2.metric("Revenue Segmen Berisiko", fmt_pct(risk["pct_revenue"].sum()),
                help="Persentase revenue dari pelanggan pada segmen At-Risk / Need Attention dan Lost Customers")
    col3.metric("Pelanggan Pernah Membeli Ulang", fmt_pct(repeat_pct))

    fig, ax = plt.subplots(1, 2, figsize=(15, 5.5))
    segments = summary.index
    counts = summary["total_customers"].values
    ax[0].bar(segments, counts, color=highlight_colors(len(counts), counts.argmax(), BLUE_BASE, BLUE_DARK))
    ax[0].set_title("Jumlah Pelanggan per Segmen RFM", fontsize=12, fontweight="bold")
    ax[0].set_xlabel("Segmen Pelanggan")
    ax[0].set_ylabel("Jumlah Pelanggan Unik")
    for i, (val, pct) in enumerate(zip(counts, summary["pct_customers"])):
        ax[0].text(i, val + counts.max() * 0.02, f"{fmt_int(val)}\n({fmt_pct(pct)})", ha="center", fontsize=8.5, fontweight="bold")
    ax[0].set_ylim(0, counts.max() * 1.2 if counts.max() > 0 else 1)

    revenue = summary["total_revenue"].values
    ax[1].bar(segments, revenue, color=highlight_colors(len(revenue), revenue.argmax(), BLUE_BASE, BLUE_DARK))
    ax[1].set_title("Kontribusi Revenue per Segmen RFM", fontsize=12, fontweight="bold")
    ax[1].set_xlabel("Segmen Pelanggan")
    ax[1].set_ylabel("Total Revenue (R$)")
    for i, (val, pct) in enumerate(zip(revenue, summary["pct_revenue"])):
        ax[1].text(i, val + revenue.max() * 0.02, f"R$ {fmt_int(val)}\n({fmt_pct(pct)})", ha="center", fontsize=8.5, fontweight="bold")
    ax[1].set_ylim(0, revenue.max() * 1.2 if revenue.max() > 0 else 1)

    for a in ax:
        a.tick_params(axis="x", rotation=20)
        a.grid(axis="x", visible=False)
        a.yaxis.set_major_formatter(FuncFormatter(lambda value, pos: fmt_int(value)))
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        f"Segmen berisiko mencakup {fmt_pct(risk['pct_customers'].sum())} pelanggan dan "
        f"{fmt_pct(risk['pct_revenue'].sum())} revenue. Hanya {fmt_pct(repeat_pct)} pelanggan yang pernah membeli ulang."
    )

    with st.expander("Lihat tabel ringkasan segmen"):
        table = pd.DataFrame({
            "Segmen": summary.index,
            "Jumlah Pelanggan": summary["total_customers"].map(fmt_int).values,
            "% Pelanggan": summary["pct_customers"].map(fmt_pct).values,
            "Rata-rata Hari sejak Pembelian Terakhir": summary["avg_recency"].map(lambda x: fmt_dec(x, 0)).values,
            "Rata-rata Belanja (R$)": summary["avg_monetary"].map(fmt_dec).values,
            "% Pembeli Berulang": summary["pct_repeat"].map(fmt_pct).values,
            "% Revenue": summary["pct_revenue"].map(fmt_pct).values,
        })
        st.dataframe(table, hide_index=True)


# ---------------------------------------------------------------------------
# Bagian 2: Durasi pengiriman dan skor ulasan
# ---------------------------------------------------------------------------
def section_delivery(df):
    st.subheader("Durasi Pengiriman dan Skor Ulasan")
    reviewed = df[df["review_score"].notna()]
    if reviewed.empty:
        st.warning("Tidak ada pesanan berulasan pada filter yang dipilih.")
        return

    speed = reviewed.groupby("speed_category").agg(
        total_orders=("order_id", "count"),
        avg_review=("review_score", "mean"),
        pct_positive=("review_score", lambda s: (s >= 4).mean() * 100),
    ).reindex(SPEED_ORDER)
    late = reviewed.groupby("is_late_vs_estimate").agg(
        total_orders=("order_id", "count"),
        avg_review=("review_score", "mean"),
        pct_positive=("review_score", lambda s: (s >= 4).mean() * 100),
    ).reindex([0, 1])
    late.index = ["Tepat Waktu / Lebih Awal", "Terlambat vs Estimasi"]

    on_time_score, late_score = late["avg_review"].iloc[0], late["avg_review"].iloc[1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Pesanan Berulasan", fmt_int(len(reviewed)))
    col2.metric("Ulasan Positif (skor >= 4)", fmt_pct((reviewed["review_score"] >= 4).mean() * 100))
    if pd.notna(on_time_score) and pd.notna(late_score):
        col3.metric("Selisih Skor (Tepat Waktu - Terlambat)", fmt_dec(on_time_score - late_score),
                    help="Selisih rata-rata skor antara pesanan yang tiba tepat waktu dan yang melewati estimasi")
    else:
        col3.metric("Selisih Skor (Tepat Waktu - Terlambat)", "-")

    fig, ax = plt.subplots(1, 2, figsize=(15, 5.5))
    speed_vals = speed["avg_review"].fillna(0).values
    ax[0].bar(speed.index, speed_vals,
              color=highlight_colors(len(speed_vals), int(np.argmin(np.where(speed_vals > 0, speed_vals, np.inf))), RED_BASE, RED_DARK))
    ax[0].set_title("Rata-rata Skor Ulasan per Kelompok Durasi Pengiriman", fontsize=12, fontweight="bold")
    ax[0].set_xlabel("Kelompok Durasi Pengiriman")
    ax[0].set_ylabel("Rata-rata Skor Ulasan (Skala 1-5)")
    ax[0].set_ylim(0, 5.3)
    for i, (val, n) in enumerate(zip(speed_vals, speed["total_orders"].fillna(0))):
        if n > 0:
            ax[0].text(i, val + 0.12, f"{fmt_dec(val)}\n({fmt_int(n)} pesanan)", ha="center", fontsize=8.5, fontweight="bold")
    ax[0].tick_params(axis="x", rotation=10)

    late_vals = late["avg_review"].fillna(0).values
    ax[1].bar(late.index, late_vals, width=0.5,
              color=highlight_colors(len(late_vals), int(np.argmin(np.where(late_vals > 0, late_vals, np.inf))), RED_BASE, RED_DARK))
    ax[1].set_title("Rata-rata Skor Ulasan: Tepat Waktu vs Terlambat dari Estimasi", fontsize=12, fontweight="bold")
    ax[1].set_xlabel("Status Pengiriman terhadap Tanggal Estimasi")
    ax[1].set_ylabel("Rata-rata Skor Ulasan (Skala 1-5)")
    ax[1].set_ylim(0, 5.3)
    for i, (val, n, pct) in enumerate(zip(late_vals, late["total_orders"].fillna(0), late["pct_positive"].fillna(0))):
        if n > 0:
            ax[1].text(i, val + 0.12, f"{fmt_dec(val)}\n{fmt_pct(pct)} ulasan positif\n({fmt_int(n)} pesanan)",
                       ha="center", fontsize=8.5, fontweight="bold")
    for a in ax:
        a.grid(axis="x", visible=False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    if pd.notna(on_time_score) and pd.notna(late_score):
        st.caption(
            f"Pesanan yang melewati tanggal estimasi berskor {fmt_dec(late_score)}, dibanding {fmt_dec(on_time_score)} "
            f"pada pesanan yang tepat waktu. Hasil ini menunjukkan hubungan, bukan bukti sebab-akibat."
        )

    with st.expander("Lihat tabel ringkasan"):
        table = pd.DataFrame({
            "Kelompok Durasi": speed.index,
            "Jumlah Pesanan": speed["total_orders"].fillna(0).map(fmt_int).values,
            "Rata-rata Skor": speed["avg_review"].map(lambda x: "-" if pd.isna(x) else fmt_dec(x)).values,
            "% Ulasan Positif (skor >= 4)": speed["pct_positive"].map(lambda x: "-" if pd.isna(x) else fmt_pct(x)).values,
        })
        st.dataframe(table, hide_index=True)


# ---------------------------------------------------------------------------
# Bagian 3: Metode pembayaran dan cicilan
# ---------------------------------------------------------------------------
def section_payment(df):
    st.subheader("Metode Pembayaran dan Cicilan")
    pay = df[df["primary_payment_type"].notna()]
    if pay.empty:
        st.warning("Tidak ada pesanan dengan data pembayaran pada filter yang dipilih.")
        return

    summary = pay.groupby("primary_payment_type").agg(
        total_orders=("order_id", "count"),
        total_value=("total_payment_value", "sum"),
        avg_order_value=("total_payment_value", "mean"),
    ).sort_values("total_orders", ascending=False)
    summary["order_share_pct"] = summary["total_orders"] / summary["total_orders"].sum() * 100
    summary["value_share_pct"] = summary["total_value"] / summary["total_value"].sum() * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Pesanan dengan Data Pembayaran", fmt_int(len(pay)))
    col2.metric("Total Nilai Transaksi", f"R$ {fmt_int(pay['total_payment_value'].sum())}")
    col3.metric("Rata-rata Nilai Pesanan (AOV)", f"R$ {fmt_dec(pay['total_payment_value'].mean())}")

    # Filter metode pembayaran: hanya memengaruhi grafik kiri dan tabel di bagian ini
    selected_methods = st.multiselect(
        "Metode pembayaran yang ditampilkan (hanya memengaruhi grafik porsi pesanan dan tabel)",
        options=list(summary.index), default=list(summary.index),
        format_func=lambda m: PAYMENT_LABELS.get(m, m),
    )
    shown = summary.loc[summary.index.isin(selected_methods)]

    cc = pay[pay["installment_group"].notna()]
    installment = cc.groupby("installment_group").agg(
        total_orders=("order_id", "count"),
        avg_order_value=("total_payment_value", "mean"),
    ).reindex(INSTALLMENT_ORDER)

    fig, ax = plt.subplots(1, 2, figsize=(15, 5.5))
    if shown.empty:
        ax[0].text(0.5, 0.5, "Pilih minimal satu metode pembayaran", ha="center", va="center")
        ax[0].set_axis_off()
    else:
        labels = [PAYMENT_LABELS.get(m, m) for m in shown.index]
        x_pos = np.arange(len(shown))
        width = 0.38
        b1 = ax[0].bar(x_pos - width / 2, shown["order_share_pct"], width, label="% Jumlah Pesanan", color=BLUE_BASE)
        b2 = ax[0].bar(x_pos + width / 2, shown["value_share_pct"], width, label="% Nilai Transaksi", color=BLUE_DARK)
        ax[0].set_xticks(x_pos)
        ax[0].set_xticklabels(labels)
        ax[0].set_xlabel("Metode Pembayaran Utama")
        ax[0].set_ylabel("Persentase terhadap Seluruh Pesanan / Nilai (%)")
        ax[0].set_title("Porsi Pesanan vs Porsi Nilai Transaksi per Metode", fontsize=12, fontweight="bold")
        ax[0].bar_label(b1, labels=[fmt_pct(v) for v in shown["order_share_pct"]], padding=3, fontsize=8.5, fontweight="bold")
        ax[0].bar_label(b2, labels=[fmt_pct(v) for v in shown["value_share_pct"]], padding=3, fontsize=8.5, fontweight="bold")
        ax[0].set_ylim(0, max(shown["order_share_pct"].max(), shown["value_share_pct"].max()) * 1.18)
        ax[0].legend()

    aov = installment["avg_order_value"].fillna(0).values
    if cc.empty:
        ax[1].text(0.5, 0.5, "Tidak ada pesanan kartu kredit pada filter ini", ha="center", va="center")
        ax[1].set_axis_off()
    else:
        ax[1].bar(installment.index, aov, color=highlight_colors(len(aov), int(aov.argmax()), BLUE_BASE, BLUE_DARK))
        ax[1].set_title("AOV Kartu Kredit per Kelompok Cicilan", fontsize=12, fontweight="bold")
        ax[1].set_xlabel("Kelompok Cicilan Kartu Kredit")
        ax[1].set_ylabel("Average Order Value (R$)")
        for i, (val, n) in enumerate(zip(aov, installment["total_orders"].fillna(0))):
            if n > 0:
                ax[1].text(i, val + aov.max() * 0.02, f"R$ {fmt_int(val)}\n({fmt_int(n)} pesanan)", ha="center", fontsize=8.5, fontweight="bold")
        ax[1].set_ylim(0, aov.max() * 1.25 if aov.max() > 0 else 1)
    for a in ax:
        a.grid(axis="x", visible=False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Grafik kanan selalu menampilkan seluruh pesanan kartu kredit dan tidak dipengaruhi filter metode pembayaran di atas.")

    top = summary.iloc[0]
    st.caption(
        f"{PAYMENT_LABELS.get(summary.index[0], summary.index[0])} memiliki porsi terbesar: {fmt_pct(top['order_share_pct'])} pesanan "
        f"dan {fmt_pct(top['value_share_pct'])} nilai transaksi. AOV yang lebih tinggi pada cicilan panjang menunjukkan hubungan, "
        f"bukan bukti bahwa cicilan menaikkan nilai belanja."
    )

    with st.expander("Lihat tabel ringkasan"):
        table = pd.DataFrame({
            "Metode Pembayaran": [PAYMENT_LABELS.get(m, m) for m in shown.index],
            "Jumlah Pesanan": shown["total_orders"].map(fmt_int).values,
            "% Pesanan": shown["order_share_pct"].map(fmt_pct).values,
            "% Nilai Transaksi": shown["value_share_pct"].map(fmt_pct).values,
            "AOV (R$)": shown["avg_order_value"].map(fmt_dec).values,
        })
        st.dataframe(table, hide_index=True)


# ---------------------------------------------------------------------------
# Halaman utama
# ---------------------------------------------------------------------------
def main():
    st.title("Dashboard Analisis E-Commerce")
    st.caption("Pesanan berstatus delivered, 15 September 2016 - 29 Agustus 2018. Nilai uang dalam Brazilian Real (R$).")

    df = load_data()
    filtered = sidebar_filters(df)
    if filtered.empty:
        st.warning("Tidak ada data pada filter yang dipilih. Ubah pilihan negara bagian.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Pesanan", fmt_int(filtered["order_id"].nunique()))
    col2.metric("Pelanggan Unik", fmt_int(filtered["customer_unique_id"].nunique()))
    col3.metric("Total Revenue (harga barang)", f"R$ {fmt_int(filtered['total_items_price'].sum())}")
    col4.metric("Rata-rata Skor Ulasan", fmt_dec(filtered["review_score"].mean()))

    tab_rfm, tab_delivery, tab_payment = st.tabs(
        ["Segmentasi Pelanggan (RFM)", "Durasi Pengiriman & Ulasan", "Metode Pembayaran & Cicilan"]
    )
    with tab_rfm:
        section_rfm(filtered)
    with tab_delivery:
        section_delivery(filtered)
    with tab_payment:
        section_payment(filtered)


main()
