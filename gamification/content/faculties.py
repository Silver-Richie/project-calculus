"""
Data fakultas. Deskripsi dan fokus diambil dari "Peta topik" pada
2_Materi_Khusus_FT_FMIPA_Fasilkom.pdf.
"""

FACULTIES = [
    {
        "slug": "ft",
        "name": "Fakultas Teknik",
        "short_name": "FT",
        "icon": "⚙️",
        "description": "Kalkulus untuk pemodelan rekayasa: kalkulus sebagai alat pemodelan fisika dan rekayasa.",
        "focus_areas": "Laju terkait & optimasi • Usaha • Volume & luas permukaan benda putar • "
                       "Nilai rata-rata & RMS • Pusat massa • PD orde 1",
    },
    {
        "slug": "fmipa",
        "name": "Fakultas Matematika dan Ilmu Pengetahuan Alam",
        "short_name": "FMIPA",
        "icon": "🔬",
        "description": "Analisis dan ketelitian konsep: pembuktian, deret, dan teknik integrasi.",
        "focus_areas": "Limit ε–δ • Teorema Nilai Antara, Rolle, Nilai Rata-rata • Deret & uji kekonvergenan • "
                       "Taylor dengan sisa • Integral tak wajar • Integral lipat & koordinat polar",
    },
    {
        "slug": "fasilkom",
        "name": "Fakultas Ilmu Komputer",
        "short_name": "Fasilkom",
        "icon": "💻",
        "description": "Kalkulus untuk komputasi dan AI: machine learning, analisis algoritma, dan metode numerik.",
        "focus_areas": "Gradient descent • Backpropagation • Aktivasi & softmax • Notasi asimptotik • "
                       "Integrasi numerik • Newton–Raphson • Probabilitas kontinu",
    },
]
