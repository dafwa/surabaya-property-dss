import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SPK - SAW & TOPSIS", layout="wide")
st.title("Sistem Pendukung Keputusan: Metode SAW dan TOPSIS")

# ==============================================================
# Fungsi: Memuat Dataset
# ==============================================================

@st.cache_data
def load_data(path="dataset_properti_surabaya.csv"):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

data = load_data()

# ==============================================================
# BAGIAN 1 : OPSI PENGATURAN DATA
# ==============================================================

st.header("Opsi Pengaturan Data")

opsi_sertifikat = [
    'SHM - Sertifikat Hak Milik',
    'HGB - Hak Guna Bangunan',
    'HP - Hak Pakai',
    'Lainnya (PPJB,Girik,Adat,dll)'
]

if 'Sertifikat' in data.columns:
    pilihan_sertifikat = st.multiselect(
        "Filter berdasarkan Sertifikat:",
        options=opsi_sertifikat,
        default=opsi_sertifikat,
        help="Pilih satu atau lebih tipe sertifikat untuk dimasukkan dalam perhitungan."
    )

    if pilihan_sertifikat:
        data = data[data['Sertifikat'].isin(pilihan_sertifikat)]
    else:
        st.warning("Pilih minimal satu tipe sertifikat untuk melanjutkan.")
        data = data.head(0)
else:
    st.error("Kolom 'Sertifikat' tidak ditemukan dalam dataset!")

if data.empty:
    st.warning("Tidak ada data yang cocok dengan filter Anda. Perhitungan tidak dapat dilanjutkan.")
    st.stop()

st.divider()

# ==============================================================
# BAGIAN 2 : PILIHAN KRITERIA
# ==============================================================

st.header("Pilih Kriteria yang Dipertimbangkan")

opsi_kriteria = [
    "Price_Sudah", "Kamar Tidur", "Kamar Mandi", "Luas Tanah", "Luas Bangunan",
    "Daya Listrik", "Ruang Tamu", "Jumlah Lantai", "Terjangkau Internet", "Kondisi Properti"
]

pilihan_kriteria = st.multiselect(
    "Pilih kriteria yang ingin dipertimbangkan:",
    options=opsi_kriteria,
    default=opsi_kriteria,
    help="Kriteria yang tidak dipilih tidak akan digunakan dalam proses perhitungan."
)

tersedia = [k for k in pilihan_kriteria if k in data.columns]

if not tersedia:
    st.warning("Anda belum memilih kriteria apapun. Silakan pilih minimal satu kriteria untuk melanjutkan.")
    st.stop()
else:
    st.success(f"{len(tersedia)} kriteria dipilih untuk perhitungan: {', '.join(tersedia)}")

st.divider()

# ==============================================================
# BAGIAN 3 : PEMBATASAN JUMLAH DATA
# ==============================================================

st.header("Jumlah Data yang Akan Dihitung")

total_rows = len(data)
options_dict = {
    '50': 50,
    '100': 100,
    '200': 200,
    f'Semua ({total_rows})': total_rows
}

valid_options = [key for key, val in options_dict.items() if val < total_rows]
valid_options.append(f'Semua ({total_rows})')

if total_rows <= 50:
    valid_options = [f'Semua ({total_rows})']
    default_index = 0
else:
    default_index = len(valid_options) - 1

pilihan_jumlah = st.radio(
    "Pilih jumlah data (baris) yang akan dihitung:",
    options=valid_options,
    index=default_index,
    help=f"Dataset ini memiliki total {total_rows} baris data."
)

if pilihan_jumlah == f'Semua ({total_rows})':
    n_data = total_rows
else:
    n_data = int(pilihan_jumlah)

data = data.head(n_data)
st.info(f"Perhitungan akan dilakukan pada {len(data)} baris data teratas.")

st.divider()

# ==============================================================
# BAGIAN 4 : PENGATURAN BOBOT KRITERIA
# ==============================================================

st.subheader("Pengaturan Bobot Kriteria")

tipe_kriteria = {
    "Price_Sudah": "Cost",
    "Kamar Tidur": "Benefit",
    "Kamar Mandi": "Benefit",
    "Luas Tanah": "Benefit",
    "Luas Bangunan": "Benefit",
    "Daya Listrik": "Benefit",
    "Ruang Tamu": "Benefit",
    "Jumlah Lantai": "Benefit",
    "Terjangkau Internet": "Benefit",
    "Kondisi Properti": "Benefit"
}

cols = st.columns(2)
raw_weights = {}

for idx, k in enumerate(tersedia):
    with cols[idx % 2]:
        raw_weights[k] = st.slider(
            f"Bobot {k}",
            min_value=0.0, max_value=1.0,
            value=round(1.0 / len(tersedia), 3),
            step=0.01
        )

# Normalisasi bobot
w_arr = np.array(list(raw_weights.values()))
w_norm = w_arr / w_arr.sum() if not np.isclose(w_arr.sum(), 0.0) else np.ones_like(w_arr) / len(w_arr)
bobot_normal = dict(zip(tersedia, np.round(w_norm, 4)))

df_bobot = pd.DataFrame({
    "Kriteria": list(bobot_normal.keys()),
    "Bobot": list(bobot_normal.values()),
    "Tipe": [tipe_kriteria[k] for k in bobot_normal.keys()]
}).set_index("Kriteria")

st.write("Bobot Ter-normalisasi (Jumlah = 1)")
st.table(df_bobot)

st.divider()

# ==============================================================
# BAGIAN 5 : PERHITUNGAN SAW + TOPSIS
# ==============================================================

if st.button("Lakukan Perhitungan SAW + TOPSIS"):

    # 1. Normalisasi (SAW)
    st.subheader("1. Normalisasi (Metode SAW) - Matriks R")
    R = pd.DataFrame(index=data.index)
    for k in tersedia:
        if tipe_kriteria[k] == "Benefit":
            R[k] = data[k] / data[k].max()
        else:
            R[k] = data[k].min() / data[k]
    st.dataframe(R.round(4))

    # 2. Normalisasi Terbobot (TOPSIS)
    st.subheader("2. Normalisasi Terbobot (Metode TOPSIS) - Matriks Y")
    Y = R * np.array(list(bobot_normal.values()))
    st.dataframe(Y.round(4))

    # 3. Solusi Ideal Positif dan Negatif
    st.subheader("3. Solusi Ideal Positif dan Negatif")
    ideal_plus, ideal_minus = {}, {}
    for k in tersedia:
        if tipe_kriteria[k] == "Benefit":
            ideal_plus[k], ideal_minus[k] = Y[k].max(), Y[k].min()
        else:
            ideal_plus[k], ideal_minus[k] = Y[k].min(), Y[k].max()

    st.write("Solusi Ideal Positif (+)")
    st.json(ideal_plus)
    st.write("Solusi Ideal Negatif (-)")
    st.json(ideal_minus)

    # 4. Jarak terhadap Solusi Ideal
    st.subheader("4. Jarak terhadap Solusi Ideal (D+ dan D-)")
    D_plus = np.sqrt(((Y - pd.Series(ideal_plus)) ** 2).sum(axis=1))
    D_minus = np.sqrt(((Y - pd.Series(ideal_minus)) ** 2).sum(axis=1))
    df_jarak = pd.DataFrame({"D+": D_plus.round(4), "D-": D_minus.round(4)})
    st.dataframe(df_jarak)

    # 5. Nilai Preferensi
    st.subheader("5. Nilai Preferensi (V) = D- / (D+ + D-)")
    V = D_minus / (D_plus + D_minus)
    data["Nilai_V"] = V.round(4)
    st.dataframe(data[["Kode Properti", "Nilai_V"]].sort_values(by="Nilai_V", ascending=False))

    # 6. Peringkat Akhir
    st.subheader("6. Peringkat Akhir")
    ranking = data[["Kode Properti", "Nilai_V"]].sort_values(by="Nilai_V", ascending=False).reset_index(drop=True)
    ranking.index += 1
    st.dataframe(ranking)

    # 7. Detail Hasil Peringkat
    st.subheader("7. Detail Hasil Peringkat (Data Lengkap)")
    data_lengkap_ranked = data.sort_values(by="Nilai_V", ascending=False).reset_index(drop=True)
    data_lengkap_ranked.index += 1

    cols = list(data_lengkap_ranked.columns)
    if 'Nilai_V' in cols:
        cols.insert(0, cols.pop(cols.index('Nilai_V')))
        if 'Kode Properti' in cols:
            cols.insert(1, cols.pop(cols.index('Kode Properti')))
        data_lengkap_ranked = data_lengkap_ranked[cols]

    # ==============================================================
    # KONVERSI NILAI KE BENTUK ASLI
    # ==============================================================

    data_lengkap_asli = data_lengkap_ranked.copy()

    internet_map = {1: 'Ya', 0: 'Tidak'}
    kondisi_map = {1: 'Butuh Renovasi', 2: 'Standar', 3: 'Bagus', 4: 'Baru'}

    if 'Terjangkau Internet' in data_lengkap_asli.columns:
        data_lengkap_asli['Terjangkau Internet'] = data_lengkap_asli['Terjangkau Internet'].map(internet_map).fillna('-')

    if 'Kondisi Properti' in data_lengkap_asli.columns:
        data_lengkap_asli['Kondisi Properti'] = data_lengkap_asli['Kondisi Properti'].map(kondisi_map).fillna('-')

    kolom_tampil = [
        "Kode Properti", "Kecamatan", "Price", "Kamar Tidur", "Kamar Mandi",
        "Luas Tanah", "Luas Bangunan", "Sertifikat", "Daya Listrik",
        "Ruang Tamu", "Jumlah Lantai", "Terjangkau Internet", "Kondisi Properti", "Nilai_V"
    ]

    kolom_tersedia = [k for k in kolom_tampil if k in data_lengkap_asli.columns]
    tabel_tampil = data_lengkap_asli[kolom_tersedia]

    st.subheader("Tabel Hasil Akhir (Nilai Asli Ditampilkan)")
    st.dataframe(tabel_tampil)

    # ==============================================================
    # UNDUH HASIL
    # ==============================================================

    st.subheader("Unduh Hasil Perankingan")

    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=True).encode('utf-8')

    csv_data = convert_df_to_csv(data_lengkap_ranked)

    st.download_button(
        label="Unduh Hasil (CSV)",
        data=csv_data,
        file_name=f"hasil_perankingan_topsis_{len(ranking)}_data.csv",
        mime="text/csv"
    )

st.write("---")
st.caption("Langkah-langkah: SAW digunakan untuk normalisasi, sedangkan TOPSIS digunakan untuk pembobotan, solusi ideal, dan perankingan.")
