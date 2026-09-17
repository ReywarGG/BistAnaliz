import os
import re
import requests
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from bs4 import BeautifulSoup

st.set_page_config(page_title="BIST Analiz & Haber Akışı", layout="wide", page_icon="📊")
st.title("📊 BIST Analiz & Ücretsiz Haber Sentez Sistemi")

# ------------------------------------------------------------
# 1. TÜM BIST HİSSE LİSTESİ (KAPSAMLI YEDEK LİSTE İLE)
# ------------------------------------------------------------
@st.cache_data(ttl=86400, show_spinner=False)
def tum_bist_hisselerini_getir() -> list:
    """
    İş Yatırım web kaynağından BIST hisselerini dinamik çeker.
    Çekemezse kapsayıcı BIST yedek listesini kullanır.
    """
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

    # Web kazıma başarısız olursa kullanılacak tam BIST hisse listesi
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
    
    # Google News RSS üzerinden BIST / KAP haber araması
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
# 3. YEREL & ÜCRETSİZ NLP HABER ANALİZİ (API'SİZ)
# ------------------------------------------------------------
def kural_tabanli_haber_analizi(haberler: list) -> dict:
    if not haberler:
        return {"skor": 0, "durum": "⚪ Nötr / Veri Yok", "detay": "Analiz edilecek haber bulunamadı."}

    pozitif_kelimeler = ["anlaşma", "sözleşme", "rekor", "yükseliş", "kâr", "artış", "temettü", "onay", "büyüme", "ihale", "alım", "ortaklık"]
    negatif_kelimeler = ["zarar", "düşüş", "ceza", "iptal", "dava", "soruşturma", "sıkıntı", "istifa", "zararda", "geriledi", "satış", "fesih"]

    p_skor = 0
    n_skor = 0

    for h in haberler:
        baslik = h["baslik"].lower()
        for p in pozitif_kelimeler:
            if p in baslik:
                p_skor += 1
        for n in negatif_kelimeler:
            if n in baslik:
                n_skor += 1

    toplam = p_skor + n_skor
    if toplam == 0:
        return {"skor": 0, "durum": "⚪ Nötr / Dengeli", "detay": "Haber başlıklarında belirgin pozitif veya negatif finansal anahtar kelime bulunamadı."}
    
    if p_skor > n_skor:
        return {"skor": p_skor, "durum": "🟢 Olumlu (Pozitif Akış)", "detay": f"Haberlerde {p_skor} adet olumlu finansal anahtar kelime öne çıkıyor (sözleşme, kâr, ihale vb.)."}
    elif n_skor > p_skor:
        return {"skor": -n_skor, "durum": "🔴 Olumsuz (Riskli Akış)", "detay": f"Haberlerde {n_skor} adet olumsuz finansal kelime tespit edildi (düşüş, zarar, dava vb.)."}
    else:
        return {"skor": 0, "durum": "⚪ Nötr", "detay": "Olumlu ve olumsuz haber başlıkları eşit ağırlıkta."}

# ------------------------------------------------------------
# 4. TEKNİK GÖSTERGELER VE VERİ
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
# SEKMELER VE ARAYÜZ
# ============================================================
tum_hisseler = tum_bist_hisselerini_getir()
tab1, tab2 = st.tabs(["🔍 Hisse & Haber Analizi", "🔎 Tüm BIST Tarama"])

# ------------------------------------------------------------
# TAB 1 — TEKLİ ANALİZ VE HABER SENTEZİ
# ------------------------------------------------------------
with tab1:
    col_sel, col_txt = st.columns([2, 1])
    with col_sel:
        secilen = st.selectbox(f"Tüm BIST Hisselerinden Seçin ({len(tum_hisseler)} Hisse)", tum_hisseler, index=0)
    with col_txt:
        manuel = st.text_input("Veya Hisse Kodu Yazın", placeholder="Örn: EREGL")

    hisse_kodu = manuel if manuel else secilen
    ticker = normalize_ticker(hisse_kodu)

    if ticker:
        with st.spinner(f"{ticker} verileri ve haberleri çekiliyor..."):
            raw = veri_cek(ticker)
            haberler = haberleri_cek(ticker)

        if raw.empty:
            st.error("Veri çekilemedi. Kodun doğruluğunu kontrol edin.")
        else:
            data = gostergeleri_hesapla(raw)
            son = data.iloc[-1]
            onceki = data.iloc[-2] if len(data) > 1 else son
            degisim_pct = ((son["Close"] - onceki["Close"]) / onceki["Close"] * 100) if onceki["Close"] else 0

            # Fiyat Paneli
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Son Fiyat", f"{son['Close']:.2f} TL", f"{degisim_pct:+.2f}%")
            c2.metric("RSI (14)", f"{son['RSI']:.1f}" if pd.notna(son['RSI']) else "—")
            c3.metric("EMA20", f"{son['EMA20']:.2f}")
            c4.metric("EMA50", f"{son['EMA50']:.2f}")

            st.line_chart(data[["Close", "EMA20", "EMA50"]])

            col_news, col_analysis = st.columns([1, 1])

            with col_news:
                st.subheader("📰 Güncel KAP & BIST Haber Akışı")
                if haberler:
                    for h in haberler:
                        st.markdown(f"• **[{h['baslik']}]({h['link']})**\n*{h['kaynak']}*")
                else:
                    st.info("Bu hisse için yakın zamanda haber akışı bulunamadı.")

            with col_analysis:
                st.subheader("🧠 Haber & Sinyal Analizi (API'siz)")
                nlp_sonuc = kural_tabanli_haber_analizi(haberler)
                
                st.info(f"**Haber Duygu Durumu:** {nlp_sonuc['durum']}")
                st.write(nlp_sonuc["detay"])
                
                # Teknik Özet
                st.markdown("**Teknik Eğilim:**")
                if son["EMA20"] > son["EMA50"]:
                    st.success("🟢 Yükseliş Eğilimi (EMA20, EMA50'nin üzerinde)")
                else:
                    st.error("🔴 Düşüş Eğilimi (EMA20, EMA50'nin altında)")

# ------------------------------------------------------------
# TAB 2 — TÜM BIST TARAMA
# ------------------------------------------------------------
with tab2:
    st.subheader(f"🔎 BIST Tüm Hisseler Taraması ({len(tum_hisseler)} Hisse)")

    if st.button("🚀 Taramayı Başlat"):
        sonuclar = []
        bar = st.progress(0, text="Taranıyor...")

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
                        "Fiyat": round(float(s["Close"]), 2),
                        "Günlük %": round(float(pct), 2),
                        "RSI": round(float(s["RSI"]), 1) if pd.notna(s["RSI"]) else None,
                        "Trend": "Yükseliş" if s["EMA20"] > s["EMA50"] else "Düşüş"
                    })
            except Exception:
                pass

            bar.progress((i + 1) / len(tum_hisseler), text=f"Taranıyor... {h_kodu}")

        bar.empty()
        st.dataframe(pd.DataFrame(sonuclar), use_container_width=True)
