import os
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv
from models import run_all, ModelResult

load_dotenv()

st.set_page_config(
    page_title="AI Model Comparator",
    page_icon="⚡",
    layout="wide",
)

# ---------------------------------------------------------------------------
# CSS Section
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
    }

    .stApp, section.main, .block-container {
        background-color: #ffffff !important;
    }
    #MainMenu, footer { visibility: hidden; }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a73e8, #0f9d58);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .hero-sub {
        font-size: 1rem;
        color: #6b7280;
        margin-top: 4px;
        margin-bottom: 1.5rem;
    }

    .model-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 24px;
        height: 100%;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .model-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
    }
    .model-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-gemini { background: #e8f0fe; color: #1a73e8; }
    .badge-groq   { background: #f0fdf4; color: #16a34a; }

    .model-name {
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0;
        color: #111827;
    }
    .model-id {
        font-size: 11px;
        color: #9ca3af;
        font-family: monospace;
    }

    .output-box {
        background: #f9fafb;
        border: 1px solid #f3f4f6;
        border-radius: 10px;
        padding: 16px;
        min-height: 220px;
        font-size: 14px;
        line-height: 1.75;
        color: #1f2937;
        white-space: pre-wrap;
        word-break: break-word;
    }
    .output-box-error {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #dc2626;
    }

    .metric-row {
        display: flex;
        gap: 10px;
        margin-top: 16px;
    }
    .metric-pill {
        flex: 1;
        background: #f3f4f6;
        border-radius: 10px;
        padding: 10px 8px;
        text-align: center;
    }
    .metric-pill-label {
        font-size: 11px;
        color: #6b7280;
        margin-bottom: 2px;
    }
    .metric-pill-value {
        font-size: 15px;
        font-weight: 700;
        color: #111827;
    }

    .winner-tag {
        display: inline-block;
        background: #fef9c3;
        color: #854d0e;
        border: 1px solid #fde68a;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        margin-left: 6px;
    }

    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #374151;
        margin: 2rem 0 1rem;
    }

    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        height: 46px !important;
        font-size: 15px !important;
    }
    
    .stTextArea textarea {
        background-color: #f9fafb !important;
        color: #1f2937 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
    }
    .stTextArea textarea::placeholder {
        color: #9ca3af !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Greeting Section
# ---------------------------------------------------------------------------
st.markdown("""
<div style="
    background: linear-gradient(135deg, #f0f7ff 0%, #fafffe 100%);
    border: 1px solid #e0eeff;
    border-left: 4px solid #1a73e8;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 28px;
">
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
        <span style="font-size:2rem;">👋</span>
        <div>
            <p style="margin:0; font-size:1.25rem; font-weight:700; color:#111827;">
                Halo! Aku Gabriella
            </p>
            <p style="margin:0; font-size:0.85rem; color:#6b7280;">AI Engineer in Progress · Portfolio Project</p>
        </div>
    </div>
    <p style="margin:0 0 14px; font-size:0.97rem; color:#374151; line-height:1.7;">
        Di sini aku sedang membangun portofoliku sebagai <strong>AI Engineer</strong>. 
        Pada project ini aku melakukan komparasi antara dua model AI, yaitu 
        <strong style="color:#1a73e8;">Gemini 2.5 Flash</strong> dan 
        <strong style="color:#16a34a;">LLaMA 3.1 via Groq</strong>
        untuk satu prompt yang sama secara <em>real-time</em>.
    </p>
    <p style="margin:0 0 10px; font-size:0.9rem; font-weight:600; color:#111827;">🎯 Objektif Proyek:</p>
    <ul style="margin:0; padding-left:20px; font-size:0.9rem; color:#374151; line-height:1.9;">
        <li>Memahami perbedaan <strong>kualitas output</strong> antar model AI untuk prompt yang sama</li>
        <li>Mengukur dan membandingkan <strong>latency (kecepatan respons)</strong> masing-masing model</li>
        <li>Menganalisis <strong>efisiensi token</strong>, seberapa banyak token yang dipakai untuk menghasilkan jawaban</li>
        <li>Mengevaluasi model mana yang paling cocok untuk <strong>use case tertentu</strong> (ringkas vs detail, cepat vs dalam)</li>
        <li>Membangun fondasi <strong>tooling perbandingan model</strong> yang bisa dikembangkan lebih lanjut</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header Section
# ---------------------------------------------------------------------------
st.markdown('<p class="hero-title">⚡ AI Model Comparator</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Bandingkan <strong>Gemini 2.5 Flash</strong> vs <strong>LLaMA 3.1 (Groq)</strong> '
    '— output, latency, dan token dalam satu tampilan.</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Cek API keys
# ---------------------------------------------------------------------------
missing = []
for key, label in [("GEMINI_API_KEY", "Google Gemini"), ("GROQ_API_KEY", "Groq")]:
    if not os.environ.get(key):
        missing.append(label)

if missing:
    st.warning(f"⚠️ API key belum diset: **{', '.join(missing)}**. Isi file `.env` dulu ya.", icon="🔑")

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------
prompt = st.text_area(
    "✏️ Prompt",
    placeholder="Contoh: Jelaskan perbedaan machine learning dan deep learning dalam bahasa sederhana.",
    height=130,
    label_visibility="collapsed",
)

left, _, right = st.columns([3, 1, 1])
with left:
    max_tokens = st.slider("Maks token output", 128, 2048, 512, step=128)
with right:
    run_btn = st.button("▶ Bandingkan", type="primary", use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if run_btn:
    if not prompt.strip():
        st.error("Prompt tidak boleh kosong.")
        st.stop()

    with st.spinner("Mengirim ke Gemini dan Groq secara paralel..."):
        all_results: list[ModelResult] = run_all(prompt.strip(), max_tokens)

    # Ambil hanya Gemini dan Groq (skip Claude)
    results = [r for r in all_results if r.label in ("Gemini 2.5 Flash", "LLaMA 3.1 (Groq)")]

    valid = [r for r in results if not r.error and r.latency_ms > 0]
    fastest    = min(valid, key=lambda r: r.latency_ms).label    if valid else None
    most_tokens = max(valid, key=lambda r: r.output_tokens).label if valid else None

    # -----------------------------------------------------------------------
    # Kartu hasil
    # -----------------------------------------------------------------------
    col_left, col_right = st.columns(2)
    card_configs = [
        ("gemini", "badge-gemini", "🔵", col_left),
        ("groq",   "badge-groq",   "🟢", col_right),
    ]

    for r, (key, badge_cls, dot, col) in zip(results, card_configs):
        with col:
            winner_html = ""
            if r.label == fastest:
                winner_html += '<span class="winner-tag">⚡ Tercepat</span>'
            if r.label == most_tokens:
                winner_html += '<span class="winner-tag">📝 Terpanjang</span>'

            output_cls = "output-box-error" if r.error else ""
            output_text = r.error if r.error else r.output

            st.markdown(f"""
            <div class="model-card">
                <div class="model-header">
                    <span style="font-size:1.4rem">{dot}</span>
                    <div>
                        <p class="model-name">{r.label} {winner_html}</p>
                        <span class="model-id">{r.model_id}</span>
                    </div>
                    <span class="model-badge {badge_cls}" style="margin-left:auto">
                        {"Gemini" if key == "gemini" else "Groq"}
                    </span>
                </div>
                <div class="output-box {output_cls}">{output_text}</div>
                <div class="metric-row">
                    <div class="metric-pill">
                        <div class="metric-pill-label">⏱ Latency</div>
                        <div class="metric-pill-value">{f"{r.latency_ms:.0f} ms" if not r.error else "—"}</div>
                    </div>
                    <div class="metric-pill">
                        <div class="metric-pill-label">🔢 Output token</div>
                        <div class="metric-pill-value">{r.output_tokens if not r.error else "—"}</div>
                    </div>
                    <div class="metric-pill">
                        <div class="metric-pill-label">💰 Biaya</div>
                        <div class="metric-pill-value">{"Gratis" if not r.error else "—"}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Chart & Ringkasan
    # -----------------------------------------------------------------------
    if valid:
        st.markdown("---")
        st.markdown('<p class="section-title">📊 Perbandingan Metrik</p>', unsafe_allow_html=True)

        labels = [r.label for r in valid]
        colors = ["#1a73e8", "#16a34a"]
        c1, c2 = st.columns(2)

        with c1:
            fig = go.Figure(go.Bar(
                x=labels, y=[r.latency_ms for r in valid],
                marker_color=colors,
                text=[f"{r.latency_ms:.0f} ms" for r in valid],
                textposition="outside", width=0.4,
            ))
            fig.update_layout(
                title="Latency — lebih rendah lebih baik",
                yaxis_title="ms", plot_bgcolor="white", paper_bgcolor="white",
                showlegend=False, height=300,
                margin=dict(t=40, b=20, l=20, r=20),
                font=dict(family="Inter, sans-serif"),
            )
            fig.update_yaxes(gridcolor="#f3f4f6")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig2 = go.Figure(go.Bar(
                x=labels, y=[r.output_tokens for r in valid],
                marker_color=colors,
                text=[f"{r.output_tokens} tok" for r in valid],
                textposition="outside", width=0.4,
            ))
            fig2.update_layout(
                title="Output tokens — panjang respons",
                yaxis_title="tokens", plot_bgcolor="white", paper_bgcolor="white",
                showlegend=False, height=300,
                margin=dict(t=40, b=20, l=20, r=20),
                font=dict(family="Inter, sans-serif"),
            )
            fig2.update_yaxes(gridcolor="#f3f4f6")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<p class="section-title">📋 Ringkasan</p>', unsafe_allow_html=True)
        rows = []
        for r in results:
            rows.append({
                "Model": r.label,
                "Latency (ms)": f"{r.latency_ms:.0f}" if not r.error else "—",
                "Input tokens": r.input_tokens if not r.error else "—",
                "Output tokens": r.output_tokens if not r.error else "—",
                "Biaya": "Gratis" if not r.error else "Error",
                "Status": "✅ OK" if not r.error else f"❌ {r.error[:50]}",
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#9ca3af;font-size:13px">'
    'Fase 1 · AI Model Comparator · Gemini Flash &amp; Groq (Gratis)'
    '</p>',
    unsafe_allow_html=True,
)