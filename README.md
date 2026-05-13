# ⚡ AI Model Comparator

Hi, aku gabby!
Disini aku sedang membangun protofolio untuk AI Engineer
Aku akan membandingkan **· Gemini 1.5 Flash · LLaMA 3 (Groq)** untuk prompt yang sama, lengkap dengan latency, jumlah token, dan estimasi biaya — secara real-time.

## Cara pakai

### 1. Clone & install dependensi

```bash
git clone <repo-url>
cd P1-ai-comparator
pip install -r requirements.txt
```

### 2. Buat file `.env`

```bash
cp .env.example .env
```

Isi `.env` dengan API key kamu:

| Provider | Daftar di | Harga |
|----------|-----------|-------|
| Google Gemini | https://aistudio.google.com/app/apikey | **Gratis** (15 req/menit) |
| Groq | https://console.groq.com/keys | **Gratis** (rate limited) |

### 3. Jalankan

```bash
streamlit run app.py
```

Buka browser di `http://localhost:8501`

## Struktur proyek

```
ai-comparator/
├── app.py           # UI Streamlit
├── models.py        # Pemanggil API + dispatcher paralel
├── requirements.txt
├── .env.example     # Template API keys
└── README.md
```

## Deploy ke Streamlit Cloud (gratis)

1. Push ke GitHub (pastikan `.env` ada di `.gitignore`)
2. Buka https://share.streamlit.io → New app
3. Pilih repo → `app.py` sebagai entry point
4. Tambahkan API key di **Settings → Secrets** dengan format sama seperti `.env`
