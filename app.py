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
st.set_page_config(page_title="BIST SMC & Likidite Terminali", layout="wide", page_icon="📈")

st.markdown("""
    <style>
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
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #131722;
        border-radius: 12px;
        border: 1px solid #2A2E39 !important;
        padding: 15px;
    }
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

st.markdown('<div class="main-title">📈 BIST Akıllı Analiz & Likidite Terminali</div>', unsafe_allow_html=True)

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
# 3. PRICE ACTION & LİKİDİTE HESAPLAMA MOTORU
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

def swing_noktalari_hesapla(df: pd.DataFrame, window: int = 5):
    """Solunda ve sağında N mum olan lokal en yüksek (Swing High) ve en düşükleri (Swing Low) bulur."""
    out = df.copy()
    out["Swing_High"] = np.nan
    out["Swing_Low"] = np.nan

    for i in range(window, len(df) - window):
        high_range = df["High"].iloc[i - window : i + window + 1]
        low_range = df["Low"].iloc[i - window : i + window + 1]

        if df["High"].iloc[i] == high_range.max():
            out.iloc[i, out.columns.get_loc("Swing_High")] = df["High"].iloc[i]

        if df["Low"].iloc[i] == low_range.min():
            out.iloc[i, out.columns.get_loc("Swing_Low")] = df["Low"].iloc[i]

    return out

def likidite_ve_seviyeleri_analiz_et(df: pd.DataFrame):
    """En yakın Destek/Direnç ve Buy-side / Sell-side Likidite havuzlarını tespit eder."""
    df_swing = swing_noktalari_hesapla(df)
    son_fiyat = df["Close"].iloc[-1]

    # Son tespit edilen Swing seviyeleri
    swing_highs = df_swing["Swing_High"].dropna().tolist()
    swing_lows = df_swing["Swing_Low"].dropna().tolist()

    # En yakın dirençler (Fiyatın üzerindeki tepe noktaları)
    direncler = [h for h in swing_highs if h > son_fiyat]
    # En yakın destekler (Fiyatın altındaki dip noktaları)
    destekler = [l for l in swing_lows if l < son_fiyat]

    en_yakin_direnc = min(direncler) if direncler else df["High"].max()
    en_yakin_destek = max(destekler) if destekler else df["Low"].min()

    # Likidite Havuzları (BSL & SSL)
    # Buy-side Liquidity (BSL): Son tepe noktasının hemen üzeri (Stop-loss havuzu)
    bsl = en_yakin_direnc * 1.005 
    # Sell-side Liquidity (SSL): Son dip noktasının hemen altı (Stop-loss havuzu)
    ssl = en_yakin_destek * 0.995 

    direnc_mesafe = ((en_yakin_direnc - son_fiyat) / son_fiyat) * 100
    destek_mesafe = ((son_fiyat - en_yakin_destek) / son_fiyat) * 100

    return {
        "son_fiyat": son_fiyat,
        "destek": en_yakin_destek,
        "direnc": en_yakin_direnc,
        "bsl": bsl,
        "ssl": ssl,
        "destek_mesafe": destek_mesafe,
        "direnc_mesafe": direnc_mesafe,
        "df_swing": df_swing
    }

# ============================================================
# ARAYÜZ VE SEKMELER
# ============================================================
tum_hisseler = tum_bist_hisselerini_getir()
tab1, tab2 = st.tabs(["📊 Price Action & Likidite Terminali", "🔎 Destek/Direnç Tarama"])

# ------------------------------------------------------------
# TAB 1 — PRICE ACTION & LİKİDİTE TERMINALI
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
        with st.spinner(f"**{ticker}** Price Action & Likidite Haritası çıkarılıyor..."):
            raw = veri_cek(ticker)
            haberler = haberleri_cek(ticker)

        if raw.empty:
            st.error("⚠️ Hisse verisi çekilemedi. Kodun doğruluğunu kontrol edin.")
        else:
            pa_data = likidite_ve_seviyeleri_analiz_et(raw)
            son = raw.iloc[-1]
            onceki = raw.iloc[-2] if len(raw) > 1 else son
            degisim_pct = ((son["Close"] - onceki["Close"]) / onceki["Close"] * 100) if onceki["Close"] else 0

            # Şık Metrik Kartları (SMC Odaklı)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Son Fiyat", f"{pa_data['son_fiyat']:.2f} TL", f"{degisim_pct:+.2f}%")
            c2.metric("En Yakın Destek (Swing Low)", f"{pa_data['destek']:.2f} TL", f"-%{pa_data['destek_mesafe']:.1f} Uzaklık")
            c3.metric("En Yakın Direnç (Swing High)", f"{pa_data['direnc']:.2f} TL", f"+%{pa_data['direnc_mesafe']:.1f} Uzaklık")
            c4.metric("Üst Likidite (BSL - Buy Side)", f"{pa_data['bsl']:.2f} TL", "Stop-Loss Havuzu")

            # Fiyat Grafiği ve Swing Seviyeleri
            st.write("")
            st.subheader("🎯 Swing High/Low ve Destek/Direnç Seviyeleri")
            
            # Grafik İçin Veri Hazırlığı
            chart_df = pa_data["df_swing"][["Close"]].copy()
            chart_df["Direnç (Swing High)"] = pa_data["direnc"]
            chart_df["Destek (Swing Low)"] = pa_data["destek"]
            
            st.line_chart(chart_df, height=340)

            # Analiz ve Likidite Yorum Alanı
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
                    st.subheader("🧠 SMC & Likidite Analiz Özeti")
                    st.divider()
                    
                    # Konum Değerlendirmesi
                    if pa_data['destek_mesafe'] < 2.0:
                        st.warning(f"⚠️ **Destek Bölgesine Çok Yakın!** Fiyat desteğe yalnızca %{pa_data['destek_mesafe']:.1f} mesafede. Altındaki Sell-side Liquidity (SSL: {pa_data['ssl']:.2f} TL) süpürülebilir.")
                    elif pa_data['direnc_mesafe'] < 2.0:
                        st.info(f"🚀 **Direnç Bölgesine Yakın!** Fiyat dirence %{pa_data['direnc_mesafe']:.1f} mesafede. Üstündeki Buy-side Liquidity (BSL: {pa_data['bsl']:.2f} TL) hedeflenebilir.")
                    else:
                        st.success(f"⚖️ **Kanal Ortasında:** Fiyat destek ve direnç arasında dengeli bir bölgede bulunuyor.")

                    st.write("")
                    st.markdown(f"• **Buy-Side Liquidity (BSL):** `{pa_data['bsl']:.2f} TL` (Satıcı stop emri havuzu)")
                    st.markdown(f"• **Sell-Side Liquidity (SSL):** `{pa_data['ssl']:.2f} TL` (Alıcı stop emri havuzu)")

                    nlp_sonuc = kural_tabanli_haber_analizi(haberler)
                    st.write("---")
                    st.markdown(f"**Haber Sentiment Sinyali:** `{nlp_sonuc['durum']}`")

# ------------------------------------------------------------
# TAB 2 — DESTEK / DİRENÇ TARAMA PANELİ
# ------------------------------------------------------------
with tab2:
    st.subheader(f"🔎 Destek ve Direncine Yaklaşan Hisseler ({len(tum_hisseler)} Hisse)")
    st.caption("Fiyatı kırılım veya tepki alma ihtimali yüksek olan destek/direncine yakın BIST hisselerini tarayın.")

    if st.button("🚀 SMC Taramasını Başlat", type="primary"):
        sonuclar = []
        bar = st.progress(0, text="Hisseler taranıyor...")

        for i, h_kodu in enumerate(tum_hisseler):
            t_kod = normalize_ticker(h_kodu)
            try:
                df_raw = veri_cek(t_kod)
                if not df_raw.empty and len(df_raw) > 15:
                    pa = likidite_ve_seviyeleri_analiz_et(df_raw)
                    son = df_raw.iloc[-1]
                    onceki = df_raw.iloc[-2] if len(df_raw) > 1 else son
                    pct = ((son["Close"] - onceki["Close"]) / onceki["Close"] * 100) if onceki["Close"] else 0

                    konum = "Nötr"
                    if pa['destek_mesafe'] <= 2.5:
                        konum = "🟢 Desteğe Yakın (Tepki Bölgesi)"
                    elif pa['direnc_mesafe'] <= 2.5:
                        konum = "🔴 Dirence Yakın (Test Bölgesi)"

                    sonuclar.append({
                        "Hisse": h_kodu,
                        "Fiyat (TL)": round(float(pa['son_fiyat']), 2),
                        "Günlük %": round(float(pct), 2),
                        "Destek (TL)": round(float(pa['destek']), 2),
                        "Direnç (TL)": round(float(pa['direnc']), 2),
                        "Destek Mesafe (%)": round(float(pa['destek_mesafe']), 1),
                        "Direnç Mesafe (%)": round(float(pa['direnc_mesafe']), 1),
                        "Konum": konum
                    })
            except Exception:
                pass

            bar.progress((i + 1) / len(tum_hisseler), text=f"Taranıyor... {h_kodu}")

        bar.empty()
        
        df_res = pd.DataFrame(sonuclar)
        st.dataframe(
            df_res.style.map(
                lambda v: "color: #00E676; font-weight: bold" if "Desteğe Yakın" in str(v)
                else ("color: #FF5252; font-weight: bold" if "Dirence Yakın" in str(v) else ""),
                subset=["Konum"]
            ),
            use_container_width=True, hide_index=True
        )
