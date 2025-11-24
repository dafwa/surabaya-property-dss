import streamlit as st
import pandas as pd

# ==============================================================
# FUNGSI LOAD DATA (Untuk Statistik di Beranda)
# ==============================================================
@st.cache_data
def load_data(path="database/dataset_properti_surabaya.csv"):
    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        return pd.DataFrame()

data_global = load_data()

# ==============================================================
# HALAMAN BERANDA (LANDING PAGE)
# ==============================================================
def halaman_landing():
    st.title("Sistem Pendukung Keputusan Properti Surabaya")
    st.subheader("Menggunakan Metode SAW & TOPSIS")
    
    st.divider()
    
    st.info("### Tentang Aplikasi")
    st.write("""
    Aplikasi ini dirancang untuk membantu calon pembeli properti dalam memilih hunian terbaik 
    di kota Surabaya. Sistem ini menggunakan kombinasi dua metode pengambilan keputusan yang kuat:
    
    1. **SAW (Simple Additive Weighting):** Digunakan pada tahap awal untuk normalisasi data.
    2. **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution):** Digunakan untuk pembobotan, penentuan solusi ideal, dan perankingan akhir.
    """)

    st.info("### Alur Kerja Sistem")
    st.markdown("""
    **Tahapan Proses dalam Aplikasi:**
    1. **Load Data**: Sistem memuat dataset properti yang tersedia.
    2. **Filtering Awal**: Pengguna memfilter data berdasarkan jenis sertifikat (SHM, HGB, dll).
    3. **Pemilihan Kriteria**: Pengguna memilih kriteria apa saja yang ingin dihitung (Harga, Luas, Fasilitas, dll).
    4. **Pembatasan Data**: Menentukan jumlah data yang akan diproses untuk efisiensi.
    5. **Pembobotan**: Pengguna mengatur tingkat kepentingan (bobot) untuk setiap kriteria dalam persentase.
    6. **Perhitungan & Perankingan**: Sistem menghitung skor menggunakan metode SAW & TOPSIS untuk menghasilkan rekomendasi terbaik.
    """)
    
    if not data_global.empty:
        st.warning("### Tentang Dataset")
        st.write(f"""
        Dataset yang digunakan berasal dari data properti real di Surabaya (`dataset_properti_surabaya.csv`).
        - **Total Data Awal:** {len(data_global)} baris data.
        - **Sumber:** [Surabaya Housing Dataset](https://www.kaggle.com/datasets/hanselds/surabaya-housing-dataset)
        - **Fitur:** Mencakup harga, luas tanah, fasilitas, dan kondisi bangunan.
        """)
    else:
        st.error("File dataset tidak ditemukan di folder 'database/'.")

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
            "Belum Renovasi / Standar / Sudah Renovasi / Baru"
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
# SETUP NAVIGASI
# ==============================================================

# 1. Halaman Beranda 
landing_page = st.Page(halaman_landing, title="Beranda")

# 2. Halaman SPK
app_page = st.Page("pages/spk.py", title="Sistem SPK")

# Setup Navigation
pg = st.navigation([landing_page, app_page], position="top")

# Konfigurasi Global
st.set_page_config(page_title="SPK - SAW & TOPSIS", layout="wide")

# Jalankan
pg.run()