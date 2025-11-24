import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================
# FUNGSI HELPER
# ==============================================================
@st.cache_data
def load_data(path="database/dataset_properti_surabaya.csv"):
    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error(f"File tidak ditemukan di path: {path}")
        return pd.DataFrame()

def reset_hasil():
    if 'hasil_saw_topsis' in st.session_state:
        st.session_state['hasil_saw_topsis'] = None

if 'hasil_saw_topsis' not in st.session_state:
    st.session_state['hasil_saw_topsis'] = None

# ==============================================================
# UI HALAMAN SPK
# ==============================================================

st.title("Pengaturan Awal")
st.info("Anda bisa navigasi kembali ke Halaman Utama menggunakan Navigation Bar")

data_global = load_data()

if data_global.empty:
    st.stop()

data = data_global.copy()

# BAGIAN 1: FILTER DATA
st.header("Opsi Pengaturan Data")

opsi_sertifikat = [
    'SHM - Sertifikat Hak Milik', 'HGB - Hak Guna Bangunan', 
    'HP - Hak Pakai', 'Lainnya (PPJB,Girik,Adat,dll)'
]

if 'Sertifikat' in data.columns:
    pilihan_sertifikat = st.multiselect(
        "Filter berdasarkan Sertifikat:",
        options=opsi_sertifikat,
        default=opsi_sertifikat,
        on_change=reset_hasil
    )
    
    if pilihan_sertifikat:
        data = data[data['Sertifikat'].isin(pilihan_sertifikat)]
        st.success(f"{len(pilihan_sertifikat)} sertifikat dipilih.")
    else:
        st.warning("Pilih minimal satu tipe sertifikat.")
        data = data.head(0)
else:
    st.error("Kolom 'Sertifikat' tidak ditemukan!")

if data.empty:
    st.warning("Data kosong setelah difilter.")
    st.stop()

st.divider()

# BAGIAN 2: PILIH KRITERIA
st.header("Pilih Kriteria")

opsi_kriteria = [
    "Price_Sudah", "Kamar Tidur", "Kamar Mandi", "Luas Tanah", "Luas Bangunan",
    "Daya Listrik", "Ruang Tamu", "Jumlah Lantai", "Terjangkau Internet", "Kondisi Properti"
]

pilihan_kriteria = st.multiselect(
    "Pilih kriteria yang dihitung:",
    options=opsi_kriteria,
    default=opsi_kriteria,
    on_change=reset_hasil
)

tersedia = [k for k in pilihan_kriteria if k in data.columns]

if not tersedia:
    st.warning("Pilih minimal satu kriteria.")
    st.stop()
else:
    st.success(f"{len(tersedia)} kriteria dipilih.")

st.divider()

# BAGIAN 3: JUMLAH DATA
st.header("Jumlah Data")
total_rows = len(data)

mode_jumlah = st.radio(
    "Mode Jumlah Data:",
    ["Semua Data (Recommended)", "Input Manual"],
    on_change=reset_hasil
)

if mode_jumlah == "Semua Data (Recommended)":
    n_data = total_rows
    st.info(f"Menggunakan total **{total_rows}** baris.")
else:
    n_data = st.number_input("Jumlah baris:", 1, total_rows, min(50, total_rows), on_change=reset_hasil)
    st.info(f"Menggunakan **{n_data}** baris teratas.")

data = data.head(n_data)

st.divider()

# BAGIAN 4: BOBOT
st.subheader("Pengaturan Bobot")
tipe_kriteria = {
    "Price_Sudah": "Cost", "Kamar Tidur": "Benefit", "Kamar Mandi": "Benefit",
    "Luas Tanah": "Benefit", "Luas Bangunan": "Benefit", "Daya Listrik": "Benefit",
    "Ruang Tamu": "Benefit", "Jumlah Lantai": "Benefit", 
    "Terjangkau Internet": "Benefit", "Kondisi Properti": "Benefit"
}

cols = st.columns(2)
raw_weights = {}
for idx, k in enumerate(tersedia):
    with cols[idx % 2]:
        raw_weights[k] = st.slider(f"Bobot {k} (%)", 0, 100, int(100/len(tersedia)), format="%d%%")

# Normalisasi bobot
w_arr = np.array(list(raw_weights.values()))
w_norm = w_arr / w_arr.sum() if not np.isclose(w_arr.sum(), 0.0) else np.ones_like(w_arr) / len(w_arr)
bobot_normal = dict(zip(tersedia, np.round(w_norm, 4)))

st.write("Bobot Ter-normalisasi:")
st.table(pd.DataFrame({
    "Kriteria": list(bobot_normal.keys()),
    "Bobot": list(bobot_normal.values()),
    "Tipe": [tipe_kriteria[k] for k in bobot_normal.keys()]
}).set_index("Kriteria"))

st.divider()

st.write("**Langkah-langkah**: SAW digunakan untuk normalisasi, sedangkan TOPSIS digunakan untuk pembobotan, solusi ideal, dan perankingan.")

# BAGIAN 5: PERHITUNGAN
if st.button("Lakukan Perhitungan SAW + TOPSIS"):
    # 1. SAW Normalisasi
    R = pd.DataFrame(index=data.index)
    for k in tersedia:
        if tipe_kriteria[k] == "Benefit":
            R[k] = data[k] / data[k].max()
        else:
            R[k] = data[k].min() / data[k]

    # 2. TOPSIS Terbobot
    Y = R * np.array(list(bobot_normal.values()))

    # 3. Solusi Ideal
    ideal_plus, ideal_minus = {}, {}
    for k in tersedia:
        if tipe_kriteria[k] == "Benefit":
            ideal_plus[k], ideal_minus[k] = Y[k].max(), Y[k].min()
        else:
            ideal_plus[k], ideal_minus[k] = Y[k].min(), Y[k].max()

    # 4. Jarak
    D_plus = np.sqrt(((Y - pd.Series(ideal_plus)) ** 2).sum(axis=1))
    D_minus = np.sqrt(((Y - pd.Series(ideal_minus)) ** 2).sum(axis=1))
    df_jarak = pd.DataFrame({"D+": D_plus.round(4), "D-": D_minus.round(4)})

    # 5. Preferensi V
    V = D_minus / (D_plus + D_minus)
    data["Nilai_V"] = V.round(4)
    
    # 6. Ranking
    ranking = data[["Kode Properti", "Nilai_V"]].sort_values("Nilai_V", ascending=False).reset_index(drop=True)
    ranking.index += 1

    # 7. Data Lengkap
    data_lengkap = data.sort_values("Nilai_V", ascending=False).reset_index(drop=True)
    data_lengkap.index += 1
    
    # Rapikan kolom (Pindahkan Nilai_V ke depan)
    cols_list = list(data_lengkap.columns)
    if 'Nilai_V' in cols_list: cols_list.insert(0, cols_list.pop(cols_list.index('Nilai_V')))
    if 'Kode Properti' in cols_list: cols_list.insert(1, cols_list.pop(cols_list.index('Kode Properti')))
    data_lengkap = data_lengkap[cols_list]

    # Konversi ke nilai asli
    data_lengkap_asli = data_lengkap.copy()
    tamu_map = {1: 'Ada', 0: 'Tidak'}
    internet_map = {1: 'Ya', 0: 'Tidak'}
    kondisi_map = {1: 'Butuh Renovasi', 2: 'Standar', 3: 'Sudah Renovasi', 4: 'Baru'}
    if 'Ruang Tamu' in data_lengkap_asli.columns:
        data_lengkap_asli['Ruang Tamu'] = data_lengkap_asli['Ruang Tamu'].map(tamu_map).fillna('-')
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
    tabel_akhir_siap = data_lengkap_asli[kolom_tersedia]

    # Simpan ke session state
    st.session_state['hasil_saw_topsis'] = {
        'R': R, 'Y': Y, 'ideal_plus': ideal_plus, 'ideal_minus': ideal_minus,
        'df_jarak': df_jarak, 'ranking': ranking, 'tabel_akhir_siap': tabel_akhir_siap, 
        'data_lengkap': data_lengkap
    }
    st.success("Perhitungan Selesai! Scroll ke bawah.")

# TAMPILAN HASIL
if st.session_state['hasil_saw_topsis']:
    res = st.session_state['hasil_saw_topsis']
    
    with st.expander("Rincian Perhitungan (Langkah 1-6) - Klik untuk melihat"):
        st.write("Berikut adalah detail langkah perhitungan SAW dan TOPSIS:")
        st.subheader("1. Normalisasi SAW")
        st.dataframe(res['R'].round(4))
        
        st.subheader("2. Normalisasi Terbobot TOPSIS")
        st.dataframe(res['Y'].round(4))
        
        st.subheader("3. Solusi Ideal")
        st.write("Positif (+):", res['ideal_plus'])
        st.write("Negatif (-):", res['ideal_minus'])
        
        st.subheader("4. Jarak Solusi Ideal")
        st.dataframe(res['df_jarak'])
        
        st.subheader("5 & 6. Nilai Preferensi & Peringkat")
        st.dataframe(res['ranking'])
    
    st.divider()
    st.subheader("7. Hasil Akhir Lengkap")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        tampil_semua = st.checkbox("Tampilkan Semua", False)
        limit = len(res['tabel_akhir_siap']) if tampil_semua else st.number_input("Tampilkan Top-N:", 1, len(res['tabel_akhir_siap']), 10)
    
    view_df = res['tabel_akhir_siap'].head(limit)
    st.dataframe(view_df)
    
    st.subheader("Unduh Hasil")
    @st.cache_data
    def to_csv(df): return df.to_csv(index=True).encode('utf-8')
    
    st.download_button(
        f"Unduh CSV ({len(view_df)} Data)",
        to_csv(view_df),
        "hasil_spk.csv",
        "text/csv"
    )

st.divider()

if st.button("Restart Sistem", type="secondary"):
    st.session_state.clear()
    st.rerun()