import os
import re
import requests
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from bs4 import BeautifulSoup

# ------------------------------------------------------------
# SAYFA AYARLARI & ÖZEL STİL (CSS)
# ------------------------------------------------------------
st.set_page_config(page_title="BIST Terminal & AI Analiz", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    /* Kart Yapıları */
    div[data-testid="stMetric"] {
        background-color: #1E222D;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2A2E39;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetric"] label {
        color: #787B86 !important;
        font-size: 0.85rem !important;
        font-weight: 600;
    }
    /* Konteyner Kenarlıkları */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #131722;
        border-radius: 12px;
        border: 1px solid #2A2E39 !important;
        padding: 15px;
    }
    /* Başlık Stili */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #2962FF, #00E676);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📈 BIST Akıllı Analiz & KAP Terminali</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 1. TÜM BIST HİSSE LİSTESİ
# ------------------------------------------------------------
@st.cache_data(ttl=86400, show_spinner=False)
def tum_bist_hisselerini_getir() -> list:
    try:
        url = "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/default.aspx"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            select = soup.find("select", {"id": "ddlAddCompare"})
            if select:
                hisseler = [option['value'].strip().upper() for option in select.find_all('option') if option.get('value')]
                if len(hisseler) > 50:
                    return sorted(list(set(hisseler)))
    except Exception:
        pass

    return sorted([
        "A1CAP", "AAV", "ACSEL", "ADEL", "ADESE", "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT",
        "AHGAZ", "AKBNK", "AKCNS", "AKFGY", "AKFYE", "AKGRT", "AKMGY", "AKSA", "AKSEN", "AKSGY",
        "ALARK", "ALBRK", "ALCAR", "ALCTL", "ALFAS", "ALGYO", "ALKA", "ALKIM", "ALMAD", "ALTNY",
        "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARASE", "ARCLK", "ARDYZ", "ARENA", "ARSAN", "ARTMS",
        "ASELS", "ASTOR", "ATAKP", "ATEKS", "ATSYH", "AVOD", "AVPGY", "AYCES", "AYDEM", "AYGAZ",
        "AZTEK", "BAGFS", "BAKAB", "BALAT", "BANVT", "BARMA", "BASGZ", "BAYRK", "BEGYO", "BERA",
        "BEYAZ", "BFREN", "BIENP", "BIGCHEFS", "BIMAS", "BINHO", "BIOEN", "BIZIM", "BJKAS", "BLCYT",
        "BNTAS", "BOBET", "BORSE", "BORSK", "BOSSA", "BRISA", "BRKO", "BRKSN", "BRKVY", "BRLSM",
        "BRMEN", "BRSAN", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "BURCE", "BURVA", "BVSAN", "BYDNR",
        "CAHIT", "CANTE", "CASA", "CCOLA", "CELHA", "CEMAS", "CEMTS", "CMBTN", "CMENT", "CONSE",
        "COSMO", "CRDFA", "CRFSA", "CUSAN", "CVKMD", "CWENE", "DAGI", "DAPGM", "DARDL", "DGATE",
        "DGGYO", "DITAS", "DMRGD", "DMSAS", "DNISI", "DOAS", "DOCO", "DOGUB", "DOHOL", "DOKTA",
        "DURDO", "DYOBY", "EDATA", "EDIP", "EGEEN", "EGGUB", "EGPRO", "EGSER", "EKGYO", "EKLUM",
        "EKOS", "EKSUN", "ELITE", "EMKEL", "ENJSA", "ENKAI", "ENSRI", "EPLAS", "ERCB", "EREGL",
        "ERPR", "ESEN", "ETILR", "EUPWR", "EUREK", "EUHOL", "EUKYO", "EYGYO", "FADE", "FENER",
        "FLAP", "FMIZP", "FONET", "FORMT", "FORTE", "FRIGO", "FROTO", "FZLGY", "GARAN", "GARFA",
        "GEDIK", "GEDZA", "GENIL", "GENKE", "GENTP", "GEREL", "GESAN", "GIPTA", "GLBMD", "GLYHO",
        "GMTAS", "GOKNR", "GOLTS", "GOODY", "GOZDE", "GRSEL", "GRTRK", "GSDHO", "GSRAY", "GUBRF",
        "GWIND", "GYHOL", "HALKB", "HATSN", "HEDEF", "HEKTS", "HKTM", "HLGYO", "HTTBT", "HUBVC",
        "HUNER", "HURGZ", "ICBCT", "IEYHO", "IHAAS", "IHEVA", "IHGZT", "IHLAS", "IHLGM", "IMASM",
        "INDES", "INFO", "INGRM", "INVES", "IPEKE", "ISCTR", "ISDMR", "ISFIN", "ISGSY", "ISGYO",
        "ISKPL", "ISMEN", "ISSEN", "IZENR", "IZINV", "IZMDC", "JANTS", "KAFEIN", "KAPLM", "KAREL",
        "KARSN", "KARTN", "KATMR", "KCAER", "KCHOL", "KENT", "KIMMR", "KLGYO", "KLMSN", "KLSER",
        "KNFRT", "KOCMT", "KONTR", "KONYA", "KORDS", "KOZAA", "KOZAL", "KRDMD", "KRTEK", "KRVGD",
        "KTLEV", "LIDER", "LKMNH", "LMKDC", "LOGIN", "LOGO", "LUKSK", "MAALT", "MACKO", "MAKIM",
        "MAKTK", "MANAS", "MARKA", "MAVI", "MEDTR", "MEGAP", "MEGMT", "MEPET", "MERCN", "MERIT",
        "MGROS", "MHRGY", "MIATK", "MIPAZ", "MPARK", "MRGYO", "MTRKS", "MTRYO", "MZHLD", "NATEN",
        "NETAS", "NIBAS", "NTGAZ", "NTHOL", "NUGYO", "NUHCM", "OBAMS", "OBASE", "ODAS", "OFSYM",
        "ONCSM", "ORCA", "ORGE", "ORMA", "OTKAR", "OTTO", "OYAKC", "OYLUM", "OYYAT", "OZKGY",
        "OZSUB", "PAGYO", "PAMEL", "PAPIL", "PARSN", "PASEU", "PCILT", "PEKGY", "PENGD", "PENTAS",
        "PETKM", "PGSUS", "PINAR", "PKART", "PKENT", "PLTUR", "PNLSN", "POLHO", "POLTK", "PRDGS",
        "PRDGY", "PRKAB", "PRKME", "PSA", "QUAGR", "RALYH", "RAYSG", "REEDR", "RGYAS", "RNPOL",
        "RODRG", "RUBNS", "RYGYO", "RYSAS", "SAHOL", "SAMAT", "SANEL", "SANFM", "SANKO", "SARKY",
        "SASA", "SAYAS", "SDTTR", "SELEC", "SELVA", "SEYKM", "SILVR", "SISE", "SKBNK", "SKTAS",
        "SMART", "SMRTG", "SNAAM", "SOKM", "SONME", "SOPR", "SRVGY", "SUMAS", "SUNTK", "SUWEN",
        "TATEN", "TATGD", "TAVHL", "TCELL", "TCKRC", "THYAO", "TKFEN", "TKNSA", "TOASO", "TRGYO",
        "TRILC", "TSKB", "TUKAS", "TUPRS", "TURSG", "TWORK", "ULKER", "UNLU", "VAKBN", "VAKKO",
        "VESBE", "VESTL", "VKGYO", "YAPRK", "YATAS", "YGGYO", "YKBNK", "YOTAS", "YYLGD", "ZOREN"
    ])

# ------------------------------------------------------------
# 2. HABER VE KAP AKIŞI ÇEKME
# ------------------------------------------------------------
@st.cache_data(ttl=900, show_spinner=False)
def haberleri_cek(ticker: str) -> list:
    haberler = []
    clean_code = ticker.replace(".IS", "")
    try:
        rss_url = f"https://news.google.com/rss/search?q={clean_code}+hisse+OR+KAP+OR+borsa&hl=tr&gl=TR&ceid=TR:tr"
        res = requests.get(rss_url, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "xml")
            items = soup.find_all("item")[:6]
            for item in items:
                title = item.title.text if item.title else ""
                link = item.link.text if item.link else ""
                source = item.source.text if item.source else "Haber Kaynağı"
                if title:
                    haberler.append({"baslik": title, "kaynak": source, "link": link})
    except Exception:
        pass
    return haberler

# ------------------------------------------------------------
# 3. YEREL & ÜCRETSİZ NLP HABER ANALİZİ
# ------------------------------------------------------------
def kural_tabanli_haber_analizi(haberler: list) -> dict:
    if not haberler:
        return {"skor": 0, "durum": "⚪ Nötr / Veri Yok", "detay": "Analiz edilecek aktif haber akışı bulunamadı."}

    pozitif_kelimeler = ["anlaşma", "sözleşme", "rekor", "yükseliş", "kâr", "artış", "temettü", "onay", "büyüme", "ihale", "alım", "ortaklık"]
    negatif_kelimeler = ["zarar", "düşüş", "ceza", "iptal", "dava", "soruşturma", "sıkıntı", "istifa", "zararda", "geriledi", "satış", "fesih"]

    p_skor = sum(1 for h in haberler for p in pozitif_kelimeler if p in h["baslik"].lower())
    n_skor = sum(1 for h in haberler for n in negatif_kelimeler if n in h["baslik"].lower())

    if p_skor + n_skor == 0:
        return {"skor": 0, "durum": "⚪ Nötr / Dengeli", "detay": "Haber başlıklarında belirgin pozitif veya negatif finansal anahtar kelime algılanmadı."}
    
    if p_skor > n_skor:
        return {"skor": p_skor, "durum": "🟢 Pozitif Akış", "detay": f"Haber başlıklarında **{p_skor} adet** olumlu finansal kelime tespit edildi (sözleşme, kâr, ihale vb.)."}
    elif n_skor > p_skor:
        return {"skor": -n_skor, "durum": "🔴 Riskli / Negatif Akış", "detay": f"Haber başlıklarında **{n_skor} adet** risk unsuru içeren kelime tespit edildi (düşüş, zarar vb.)."}
    else:
        return {"skor": 0, "durum": "⚪ Nötr", "detay": "Dengeli haber akışı: Olumlu ve olumsuz sinyaller eşit ağırlıkta."}

# ------------------------------------------------------------
# 4. TEKNİK GÖSTERGELER
# ------------------------------------------------------------
def normalize_ticker(t: str) -> str:
    t = t.strip().upper()
    if t and "." not in t:
        t += ".IS"
    return t

@st.cache_data(ttl=300, show_spinner=False)
def veri_cek(ticker: str) -> pd.DataFrame:
    df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True, progress=False)
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def rsi_hesapla(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.where(avg_loss != 0, 100.0)

def gostergeleri_hesapla(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["EMA20"] = out["Close"].ewm(span=20, adjust=False).mean()
    out["EMA50"] = out["Close"].ewm(span=50, adjust=False).mean()
    out["RSI"] = rsi_hesapla(out["Close"], 14)
    return out

# ============================================================
# ARAYÜZ VE SEKMELER
# ============================================================
tum_hisseler = tum_bist_hisselerini_getir()
tab1, tab2 = st.tabs(["📊 Hisse & KAP Terminali", "🔎 Tüm BIST Tarama Panel"])

# ------------------------------------------------------------
# TAB 1 — MODERN HİSSE TERMINALİ
# ------------------------------------------------------------
with tab1:
    with st.container(border=True):
        col_sel, col_txt = st.columns([3, 1])
        with col_sel:
            secilen = st.selectbox(f"BIST Hisse Seçimi ({len(tum_hisseler)} Hisse)", tum_hisseler, index=0)
        with col_txt:
            manuel = st.text_input("Hızlı Kod Arama", placeholder="Örn: EREGL")

    hisse_kodu = manuel if manuel else secilen
    ticker = normalize_ticker(hisse_kodu)

    if ticker:
        with st.spinner(f"**{ticker}** piyasa verileri ve KAP haberleri getiriliyor..."):
            raw = veri_cek(ticker)
            haberler = haberleri_cek(ticker)

        if raw.empty:
            st.error("⚠️ Hisse verisi çekilemedi. Kodun doğruluğunu kontrol edin.")
        else:
            data = gostergeleri_hesapla(raw)
            son = data.iloc[-1]
            onceki = data.iloc[-2] if len(data) > 1 else son
            degisim_pct = ((son["Close"] - onceki["Close"]) / onceki["Close"] * 100) if onceki["Close"] else 0

            # Şık Metrik Kartları
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Son Fiyat", f"{son['Close']:.2f} TL", f"{degisim_pct:+.2f}%")
            
            rsi_val = son['RSI']
            rsi_text = f"{rsi_val:.1f}" if pd.notna(rsi_val) else "—"
            c2.metric("RSI (14)", rsi_text, "Aşırı Alım" if rsi_val > 70 else ("Aşırı Satım" if rsi_val < 30 else "Nötr"))
            
            c3.metric("EMA (20)", f"{son['EMA20']:.2f} TL")
            c4.metric("EMA (50)", f"{son['EMA50']:.2f} TL")

            # Fiyat Grafiği
            st.write("")
            st.subheader("📈 Fiyat & Hareketli Ortalamalar (EMA)")
            st.line_chart(data[["Close", "EMA20", "EMA50"]], height=320)

            # Analiz ve Haber Bölümü
            col_news, col_analysis = st.columns([1, 1])

            with col_news:
                with st.container(border=True):
                    st.subheader("📰 Anlık KAP & BIST Haber Akışı")
                    st.divider()
                    if haberler:
                        for h in haberler:
                            st.markdown(f"🔹 **[{h['baslik']}]({h['link']})**  \n*Kaynağı: {h['kaynak']}*")
                            st.write("---")
                    else:
                        st.info("Bu hisse için yakın zamanda haber akışı bulunamadı.")

            with col_analysis:
                with st.container(border=True):
                    st.subheader("🧠 Akıllı Haber & Trend Sentezi")
                    st.divider()
                    
                    nlp_sonuc = kural_tabanli_haber_analizi(haberler)
                    
                    st.markdown(f"**Haber Sentiment Sinyali:** `{nlp_sonuc['durum']}`")
                    st.caption(nlp_sonuc["detay"])
                    st.write("")

                    st.markdown("**Teknik Trend Eğilimi:**")
                    if son["EMA20"] > son["EMA50"]:
                        st.success("🟢 **Boğa Trendi (Yükseliş)** — EMA20 ortalaması EMA50'nin üzerinde seyrediyor.")
                    else:
                        st.error("🔴 **Ayı Trendi (Düşüş)** — EMA20 ortalaması EMA50'nin altında seyrediyor.")

# ------------------------------------------------------------
# TAB 2 — TÜM BIST TARAMA PANELİ
# ------------------------------------------------------------
with tab2:
    st.subheader(f"🔎 BIST Tüm Hisseler Taraması ({len(tum_hisseler)} Hisse)")
    st.caption("Tüm BIST hisselerinin anlık fiyat, RSI ve EMA trend durumlarını listeleyin.")

    if st.button("🚀 Taramayı Başlat", type="primary"):
        sonuclar = []
        bar = st.progress(0, text="Hisseler taranıyor...")

        for i, h_kodu in enumerate(tum_hisseler):
            t_kod = normalize_ticker(h_kodu)
            try:
                df_raw = veri_cek(t_kod)
                if not df_raw.empty and len(df_raw) > 2:
                    df_g = gostergeleri_hesapla(df_raw)
                    s = df_g.iloc[-1]
                    o = df_g.iloc[-2]
                    pct = ((s["Close"] - o["Close"]) / o["Close"] * 100) if o["Close"] else 0

                    sonuclar.append({
                        "Hisse": h_kodu,
                        "Fiyat (TL)": round(float(s["Close"]), 2),
                        "Günlük %": round(float(pct), 2),
                        "RSI (14)": round(float(s["RSI"]), 1) if pd.notna(s["RSI"]) else None,
                        "Trend": "🟢 Yükseliş" if s["EMA20"] > s["EMA50"] else "🔴 Düşüş"
                    })
            except Exception:
                pass

            bar.progress((i + 1) / len(tum_hisseler), text=f"Taranıyor... {h_kodu}")

        bar.empty()
        
        df_res = pd.DataFrame(sonuclar)
        st.dataframe(
            df_res.style.map(
                lambda v: "color: #00E676; font-weight: bold" if "Yükseliş" in str(v)
                else ("color: #FF5252; font-weight: bold" if "Düşüş" in str(v) else ""),
                subset=["Trend"]
            ),
            use_container_width=True, hide_index=True
        )
