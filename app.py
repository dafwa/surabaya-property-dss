import streamlit as st
import pandas as pd
import numpy as np

# Fungsi-fungsi Halaman didefinisikan terlebih dahulu

# ==============================================================
# FUNGSI GLOBAL & LOAD DATA
# ==============================================================
@st.cache_data
def load_data(path="dataset_properti_surabaya.csv"):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

data_global = load_data()

# Fungsi helper reset hasil
def reset_hasil():
    if 'hasil_saw_topsis' in st.session_state:
        st.session_state['hasil_saw_topsis'] = None

# Inisialisasi state untuk hasil perhitungan
if 'hasil_saw_topsis' not in st.session_state:
    st.session_state['hasil_saw_topsis'] = None

# ==============================================================
# HALAMAN 1: LANDING PAGE
# ==============================================================
def homepage():
    st.title("Sistem Pendukung Keputusan Properti Surabaya")
    st.subheader("Metode SAW (Simple Additive Weighting) & TOPSIS")
    
    st.markdown("---")
    
    st.info("### Tentang Aplikasi")
    st.write("""
    Aplikasi ini dirancang untuk membantu calon pembeli properti dalam memilih hunian terbaik 
    di kota Surabaya. Sistem ini menggunakan kombinasi dua metode pengambilan keputusan yang kuat:
    
    1. **SAW (Simple Additive Weighting):** Digunakan pada tahap awal untuk normalisasi data.
    2. **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution):** Digunakan untuk pembobotan, penentuan solusi ideal, dan perankingan akhir.
    """)
    
    st.warning("### Tentang Dataset")
    st.write(f"""
    Dataset yang digunakan berasal dari data properti real di Surabaya (`dataset_properti_surabaya.csv`).
    
    - **Total Data Awal:** {len(data_global)} baris data.
    - **Sumber:** [Surabaya Housing Dataset](https://www.kaggle.com/datasets/hanselds/surabaya-housing-dataset)
    - **Fitur:** Mencakup harga, luas tanah, fasilitas, dan kondisi bangunan.
    """)

    st.success("### Kriteria Penilaian")
    st.write("""
    Terdapat 2 Tipe Kriteria yaitu:
    - **Cost:** Harga, Semakin sedikit semakin baik. 
    - **Benefit:** Keuntungan, Semakin banyak semakin baik.
             
    Sistem ini menilai properti berdasarkan kriteria berikut:
    """)
    
    kriteria_data = {
        "Kriteria": [
            "Price_Sudah (Harga)", "Kamar Tidur", "Kamar Mandi", "Luas Tanah", 
            "Luas Bangunan", "Daya Listrik", "Ruang Tamu", "Jumlah Lantai", 
            "Terjangkau Internet", "Kondisi Properti"
        ],
        "Tipe": [
            "Cost", "Benefit", "Benefit", "Benefit", "Benefit", 
            "Benefit", "Benefit", "Benefit", "Benefit", "Benefit"
        ],
        "Satuan/Skala": [
            "Rupiah (÷1000000)", "Jumlah", "Jumlah", "m²", "m²", "VA", "Ada/Tidak",
            "Jumlah", "Ya/Tidak", "Skala 1-4"
        ],
        "Deskripsi": [
            "Semakin rendah harga, semakin baik bagi calon pembeli.",
            "Semakin banyak kamar tidur, semakin nyaman untuk penghuni.",
            "Semakin banyak kamar mandi, semakin tinggi kenyamanan bagi penghuni.",
            "Semakin luas lahan, semakin besar potensi ruang dan nilai properti.",
            "Semakin luas bangunan, semakin fungsional dan fleksibel ruang yang tersedia.",
            "Semakin besar daya listrik, semakin mampu rumah mendukung untuk peralatan rumah.",
            "Semakin tersedia ruang tamu, semakin baik fungsi sosial dan kenyamanan keluarga.",
            "Semakin banyak lantai, semakin besar kapasitas ruang yang dapat dimanfaatkan.",
            "Semakin tersedia internet, semakin mendukung kebutuhan penghuni.",
            "Semakin tinggi tingkat kondisi, semakin baik kondisi fisik properti."
        ]
    }
    
    df_kriteria = pd.DataFrame(kriteria_data)
    st.dataframe(
        df_kriteria, 
        hide_index=True, 
        width="stretch"
    )

    st.markdown("---")
    st.write("### Siap untuk memulai?")
    st.write("Klik tombol di bawah ini untuk masuk ke sistem perhitungan utama, mengatur bobot, dan melihat hasil rekomendasi.")
    
    # Tombol Navigasi
    if st.button("Mulai Sistem SPK", type="primary", use_container_width=True):
        st.switch_page(app_page)

# ==============================================================
# HALAMAN 2: SISTEM UTAMA
# ==============================================================
def startpage():
    st.title("Sistem Pendukung Keputusan")
    
    data = data_global.copy()

    # BAGIAN 1 : OPSI PENGATURAN DATA
    st.header("Opsi Pengaturan Data")

    opsi_sertifikat = [
        'SHM - Sertifikat Hak Milik',
        'HGB - Hak Guna Bangunan',
        'HP - Hak Pakai',
        'Lainnya (PPJB,Girik,Adat,dll)'
    ]

    if 'Sertifikat' in data.columns:
        pilihan_sertifikat = st.multiselect(
            "Filter berdasarkan Sertifikat yang Anda inginkan:",
            options=opsi_sertifikat,
            default=opsi_sertifikat,
            help="Pilih satu atau lebih tipe sertifikat untuk dimasukkan dalam perhitungan.",
            on_change=reset_hasil
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
        return 

    st.divider()

    # BAGIAN 2 : PILIHAN KRITERIA
    st.header("Pilih Kriteria yang Dipertimbangkan")

    opsi_kriteria = [
        "Price_Sudah", "Kamar Tidur", "Kamar Mandi", "Luas Tanah", "Luas Bangunan",
        "Daya Listrik", "Ruang Tamu", "Jumlah Lantai", "Terjangkau Internet", "Kondisi Properti"
    ]

    pilihan_kriteria = st.multiselect(
        "Pilih kriteria yang ingin dipertimbangkan:",
        options=opsi_kriteria,
        default=opsi_kriteria,
        help="Kriteria yang tidak dipilih tidak akan digunakan dalam proses perhitungan.",
        on_change=reset_hasil
    )

    tersedia = [k for k in pilihan_kriteria if k in data.columns]

    if not tersedia:
        st.warning("Anda belum memilih kriteria apapun. Silakan pilih minimal satu kriteria untuk melanjutkan.")
        return
    else:
        st.success(f"{len(tersedia)} kriteria dipilih untuk perhitungan: {', '.join(tersedia)}")

    st.divider()

    # BAGIAN 3 : PEMBATASAN JUMLAH DATA
    st.header("Jumlah Data yang Akan Dihitung")

    total_rows = len(data)
    
    mode_jumlah = st.radio(
        "Mode Penentuan Jumlah Data:",
        ["Gunakan Semua Data", "Input Manual Jumlah Data"],
        help="Pilih 'Input Manual' jika ingin membatasi perhitungan pada jumlah baris tertentu.",
        on_change=reset_hasil
    )

    if mode_jumlah == "Gunakan Semua Data":
        n_data = total_rows
        st.info(f"Menggunakan seluruh data yang tersedia: **{total_rows}** baris.")
    else:
        n_data = st.number_input(
            f"Masukkan jumlah data yang ingin dihitung (Maks: {total_rows}):",
            min_value=1,
            max_value=total_rows,
            value=min(50, total_rows),
            step=10,
            on_change=reset_hasil
        )
        st.info(f"Menggunakan **{n_data}** baris data teratas.")

    data = data.head(n_data)

    st.divider()

    # BAGIAN 4 : PENGATURAN BOBOT KRITERIA
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
                f"Bobot {k} (%)",
                min_value=0, 
                max_value=100,
                value=int(100 / len(tersedia)), 
                step=1,
                format="%d%%"
            )

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

    # BAGIAN 5 : PERHITUNGAN SAW + TOPSIS
    if st.button("Lakukan Perhitungan SAW + TOPSIS"):
        
        # 1. Normalisasi SAW
        R = pd.DataFrame(index=data.index)
        for k in tersedia:
            if tipe_kriteria[k] == "Benefit":
                R[k] = data[k] / data[k].max()
            else:
                R[k] = data[k].min() / data[k]

        # 2. Normalisasi Terbobot TOPSIS
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

        # 5. Nilai Preferensi V
        V = D_minus / (D_plus + D_minus)
        data["Nilai_V"] = V.round(4)
        
        # 6. Peringkat
        ranking = data[["Kode Properti", "Nilai_V"]].sort_values(by="Nilai_V", ascending=False).reset_index(drop=True)
        ranking.index += 1

        # 7. Data Lengkap
        data_lengkap_ranked = data.sort_values(by="Nilai_V", ascending=False).reset_index(drop=True)
        data_lengkap_ranked.index += 1
        
        cols = list(data_lengkap_ranked.columns)
        if 'Nilai_V' in cols:
            cols.insert(0, cols.pop(cols.index('Nilai_V')))
            if 'Kode Properti' in cols:
                cols.insert(1, cols.pop(cols.index('Kode Properti')))
            data_lengkap_ranked = data_lengkap_ranked[cols]
        
        # Konversi ke nilai asli
        data_lengkap_asli = data_lengkap_ranked.copy()
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

        # Simpan Hasil
        st.session_state['hasil_saw_topsis'] = {
            'R': R,
            'Y': Y,
            'ideal_plus': ideal_plus,
            'ideal_minus': ideal_minus,
            'df_jarak': df_jarak,
            'data_V': data[["Kode Properti", "Nilai_V"]].sort_values(by="Nilai_V", ascending=False),
            'ranking': ranking,
            'data_lengkap_ranked': data_lengkap_ranked,
            'tabel_akhir_siap': tabel_akhir_siap
        }
        
        st.success("Perhitungan Selesai! Scroll ke bawah untuk melihat hasilnya.")

    # BAGIAN TAMPILAN
    if st.session_state['hasil_saw_topsis'] is not None:
        hasil = st.session_state['hasil_saw_topsis']
        
        st.subheader("1. Normalisasi (Metode SAW) - Matriks R")
        st.dataframe(hasil['R'].round(4))

        st.subheader("2. Normalisasi Terbobot (Metode TOPSIS) - Matriks Y")
        st.dataframe(hasil['Y'].round(4))

        st.subheader("3. Solusi Ideal Positif dan Negatif")
        st.write("Solusi Ideal Positif (+)")
        st.json(hasil['ideal_plus'])
        st.write("Solusi Ideal Negatif (-)")
        st.json(hasil['ideal_minus'])

        st.subheader("4. Jarak terhadap Solusi Ideal (D+ dan D-)")
        st.dataframe(hasil['df_jarak'])

        st.subheader("5. Nilai Preferensi (V)")
        st.dataframe(hasil['data_V'])

        st.subheader("6. Peringkat Akhir")
        st.dataframe(hasil['ranking'])

        # Langkah 7
        st.subheader("7. Tabel Hasil Akhir (Nilai Asli Ditampilkan)")
        
        tabel_full = hasil['tabel_akhir_siap']
        
        col_filter1, col_filter2 = st.columns([1, 2])
        with col_filter1:
            tampil_semua = st.checkbox("Tampilkan Semua Data", value=False)
            
            if not tampil_semua:
                jml_tampil = st.number_input(
                    "Tampilkan berapa data teratas?", 
                    min_value=1, 
                    max_value=len(tabel_full), 
                    value=min(10, len(tabel_full)), 
                    step=1
                )
            else:
                jml_tampil = len(tabel_full)
        
        if tampil_semua:
            df_final_view = tabel_full
        else:
            df_final_view = tabel_full.head(jml_tampil)
            
        st.dataframe(df_final_view)

        # Unduh Hasil
        st.subheader("Unduh Hasil Perankingan")
        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=True).encode('utf-8')

        csv_data = convert_df_to_csv(df_final_view)
        
        st.download_button(
            label=f"Unduh Hasil ({len(df_final_view)} Data)", 
            data=csv_data,
            file_name=f"hasil_perankingan_{len(df_final_view)}_data.csv",
            mime="text/csv",
            help="Mengunduh data sesuai dengan yang ditampilkan di tabel di atas."
        )

    st.write("---")
    
    # Tombol Restart
    if st.button("Restart Sistem", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.caption("Langkah-langkah: SAW digunakan untuk normalisasi, sedangkan TOPSIS digunakan untuk pembobotan, solusi ideal, dan perankingan.")


# ==============================================================
# SETUP NAVIGASI ST.PAGE (NATIVE)
# ==============================================================

# Definisikan Halaman
landing_page = st.Page(homepage, title="Beranda")
app_page = st.Page(startpage, title="SPK")

# Setup Navigasi
pg = st.navigation([landing_page, app_page], position="top")

# Konfigurasi Global
st.set_page_config(page_title="SPK - SAW & TOPSIS", layout="wide")

# Jalankan Navigasi
pg.run()