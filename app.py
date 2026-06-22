import os
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="BIST Analiz", layout="wide", page_icon="📊")
st.title("📊 BIST Analiz Sistemi")

# AI yorum için kullanılacak model — daha ucuz/hızlı istersen "claude-haiku-4-5-20251001" yap
AI_MODEL = "claude-sonnet-4-6"

# Hisse tarama için kullanılan liste. Ücretsiz bir API'den "tüm BIST hisseleri"
# çekilemediği için bu liste elle hazırlanmıştır — istediğin kodu ekleyip
# çıkarabilirsin (yalnızca ".IS" olmadan, kod normalize_ticker ile otomatik ekler).
TARAMA_LISTESI = [
    "THYAO", "GARAN", "AKBNK", "ISCTR", "YKBNK", "VAKBN", "HALKB",
    "ASELS", "SISE", "KCHOL", "SAHOL", "BIMAS", "MGROS", "ULKER",
    "EREGL", "TUPRS", "PETKM", "SASA", "ARCLK", "FROTO", "TOASO",
    "TTKOM", "TCELL", "PGSUS", "ENJSA", "AEFES", "KOZAL", "KOZAA",
    "GUBRF", "ENKAI",
]


# ------------------------------------------------------------
# ORTAK YARDIMCI FONKSİYONLAR
# ------------------------------------------------------------
def normalize_ticker(t: str) -> str:
    t = t.strip().upper()
    if t and "." not in t:
        t += ".IS"
    return t


@st.cache_data(ttl=300, show_spinner=False)
def veri_cek(ticker: str) -> pd.DataFrame:
    df = yf.download(ticker, period="6mo", interval="1d",
                      auto_adjust=True, progress=False)
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def temel_veri_cek(ticker: str) -> dict:
    """Yahoo Finance'ten temel veri çeker. BIST hisselerinde bu alanlar
    genellikle eksik/kısmi gelir — bu Yahoo'nun veri kaynağı kısıtı, kodun değil."""
    try:
        info = yf.Ticker(ticker).info
    except Exception:
        return {}
    if not info:
        return {}
    return {
        "Şirket": info.get("longName"),
        "Sektör": info.get("sector"),
        "F/K": info.get("trailingPE"),
        "PD/DD": info.get("priceToBook"),
        "Piyasa Değeri": info.get("marketCap"),
        "Temettü Verimi": info.get("dividendYield"),
        "52H Yüksek": info.get("fiftyTwoWeekHigh"),
        "52H Düşük": info.get("fiftyTwoWeekLow"),
    }


def deger_formatla(anahtar: str, deger) -> str:
    if deger is None:
        return "Veri yok"
    if anahtar == "Piyasa Değeri" and isinstance(deger, (int, float)):
        return f"{deger:,.0f}"
    if anahtar == "Temettü Verimi" and isinstance(deger, (int, float)):
        return f"%{deger * 100:.2f}"
    if isinstance(deger, float):
        return f"{deger:.2f}"
    return str(deger)


# ------------------------------------------------------------
# GÖSTERGE FONKSİYONLARI
# ------------------------------------------------------------
def rsi_hesapla(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.where(avg_loss != 0, 100.0)


def vwap_hesapla(df: pd.DataFrame, window: int = 20) -> pd.Series:
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    pv = tp * df["Volume"]
    return pv.rolling(window).sum() / df["Volume"].rolling(window).sum()


def stoch_rsi_hesapla(rsi: pd.Series, period: int = 14, k_smooth: int = 3, d_smooth: int = 3):
    min_rsi = rsi.rolling(period).min()
    max_rsi = rsi.rolling(period).max()
    denom = (max_rsi - min_rsi).replace(0, np.nan)
    stoch = (rsi - min_rsi) / denom * 100
    k = stoch.rolling(k_smooth).mean()
    d = k.rolling(d_smooth).mean()
    return k, d


def cci_hesapla(df: pd.DataFrame, period: int = 20) -> pd.Series:
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    sma_tp = tp.rolling(period).mean()
    mean_dev = tp.rolling(period).apply(lambda x: (x - x.mean()).abs().mean(), raw=False)
    mean_dev = mean_dev.replace(0, np.nan)
    return (tp - sma_tp) / (0.015 * mean_dev)


def gostergeleri_hesapla(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["EMA20"] = out["Close"].ewm(span=20, adjust=False).mean()
    out["EMA50"] = out["Close"].ewm(span=50, adjust=False).mean()
    out["RSI"] = rsi_hesapla(out["Close"], 14)
    out["VWAP"] = vwap_hesapla(out, 20)
    out["StochK"], out["StochD"] = stoch_rsi_hesapla(out["RSI"], 14, 3, 3)
    out["CCI"] = cci_hesapla(out, 20)
    return out


def sinyal_hesapla(rsi, ema20, ema50, cci, stochk):
    """RSI + EMA trend + CCI + Stokastik RSI'yi birleştirip kısa bir
    AL/SAT/NÖTR sinyali üretir. Bu kesin bir tavsiye değil, göstergelerin
    birlikte hangi yöne işaret ettiğinin basit bir özetidir."""
    skor = 0
    if pd.notna(rsi):
        if rsi < 30:
            skor += 1
        elif rsi > 70:
            skor -= 1
    if pd.notna(ema20) and pd.notna(ema50):
        if ema20 > ema50:
            skor += 1
        else:
            skor -= 1
    if pd.notna(cci):
        if cci < -100:
            skor += 1
        elif cci > 100:
            skor -= 1
    if pd.notna(stochk):
        if stochk < 20:
            skor += 0.5
        elif stochk > 80:
            skor -= 0.5

    if skor >= 1.5:
        return "AL", skor
    elif skor <= -1.5:
        return "SAT", skor
    else:
        return "NÖTR", skor


# ------------------------------------------------------------
# AI YORUM (opsiyonel — Anthropic API anahtarı gerektirir)
# ------------------------------------------------------------
def api_key_al():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def ai_yorum_uret(ticker: str, ozet_metin: str):
    """Hesaplanmış gösterge değerlerini Claude'a gönderip kısa Türkçe yorum üretir.
    API anahtarı yoksa veya kütüphane kurulu değilse None döner, çökmez."""
    api_key = api_key_al()
    if not api_key:
        return None, "anahtar_yok"
    try:
        import anthropic
    except ImportError:
        return None, "kutuphane_yok"
    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = (
            f"{ticker} hissesi için hesaplanmış teknik gösterge değerleri aşağıda. "
            f"Bunları sentezleyip 3-4 cümlelik, net, Türkçe bir teknik yorum yaz. "
            f"Kesin 'al' veya 'sat' emri verme, sadece göstergelerin birlikte ne "
            f"söylediğini özetle ve yatırım tavsiyesi olmadığını belirt.\n\n{ozet_metin}"
        )
        response = client.messages.create(
            model=AI_MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in response.content if hasattr(b, "text"))
        return text, None
    except Exception as e:
        return None, f"hata: {e}"


# ============================================================
# SEKMELER
# ============================================================
tab1, tab2, tab3 = st.tabs(["🔍 Tekli Analiz", "📋 Watchlist / Karşılaştırma", "🔎 Hisse Tarama"])

# ------------------------------------------------------------
# TAB 1 — TEKLİ ANALİZ
# ------------------------------------------------------------
with tab1:
    hisse_input = st.text_input("Hisse kodu girin (örn: THYAO, GENKM)", key="tekli_input")

    if not hisse_input:
        st.info("Analiz için bir hisse kodu girin.")
    else:
        ticker = normalize_ticker(hisse_input)

        with st.spinner(f"{ticker} için veri çekiliyor..."):
            try:
                raw = veri_cek(ticker)
            except Exception as e:
                st.error(f"Veri çekilirken hata oluştu: {e}")
                raw = pd.DataFrame()

        if raw.empty:
            st.error(f"'{ticker}' için veri bulunamadı. Hisse kodunu kontrol edin.")
        elif not {"Open", "High", "Low", "Close", "Volume"}.issubset(raw.columns):
            st.error("Veri eksik geldi. Lütfen tekrar deneyin.")
        else:
            data = gostergeleri_hesapla(raw)

            if len(data) < 50:
                st.warning(
                    f"Bu hissenin işlem geçmişi 50 günden kısa ({len(data)} gün). "
                    f"EMA50 gibi göstergeler bu nedenle güvenilir olmayabilir "
                    f"(yeni halka arzlarda normaldir)."
                )

            son = data.iloc[-1]
            onceki = data.iloc[-2] if len(data) > 1 else son
            degisim = son["Close"] - onceki["Close"]
            degisim_pct = (degisim / onceki["Close"] * 100) if onceki["Close"] else 0

            st.subheader("💰 Fiyat Bilgisi")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Son Kapanış", f"{son['Close']:.2f}", f"{degisim:+.2f} ({degisim_pct:+.2f}%)")
            c2.metric("Açılış", f"{son['Open']:.2f}")
            c3.metric("Yüksek", f"{son['High']:.2f}")
            c4.metric("Düşük", f"{son['Low']:.2f}")
            c5.metric("Hacim", f"{son['Volume']:,.0f}")

            st.divider()
            st.subheader("📈 Fiyat, Hareketli Ortalamalar ve VWAP")
            st.line_chart(data[["Close", "EMA20", "EMA50", "VWAP"]])
            st.caption("VWAP burada 20 günlük hacim ağırlıklı ortalama fiyatı temsil eder.")

            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("📊 RSI (14)")
                st.line_chart(data["RSI"])
            with col_b:
                st.subheader("📊 Stokastik RSI")
                st.line_chart(data[["StochK", "StochD"]])

            st.subheader("📊 CCI (20)")
            st.line_chart(data["CCI"])

            st.divider()
            st.subheader("🧠 Teknik Analiz")

            rsi_son, stochk_son, stochd_son = son["RSI"], son["StochK"], son["StochD"]
            cci_son, vwap_son = son["CCI"], son["VWAP"]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**RSI**")
                if pd.notna(rsi_son):
                    st.metric("Değer", f"{rsi_son:.1f}")
                    if rsi_son < 30:
                        st.success("Aşırı satım")
                    elif rsi_son > 70:
                        st.warning("Aşırı alım")
                    else:
                        st.info("Nötr")
                st.markdown("**EMA Trend**")
                if son["EMA20"] > son["EMA50"]:
                    st.success("Yükseliş eğilimi")
                else:
                    st.error("Düşüş eğilimi")
            with col2:
                st.markdown("**Stokastik RSI**")
                if pd.notna(stochk_son):
                    st.metric("%K / %D", f"{stochk_son:.1f} / {stochd_son:.1f}")
                    if stochk_son < 20:
                        st.success("Aşırı satım")
                    elif stochk_son > 80:
                        st.warning("Aşırı alım")
                    else:
                        st.info("Nötr")
                st.markdown("**VWAP Konumu**")
                if pd.notna(vwap_son):
                    if son["Close"] > vwap_son:
                        st.success(f"Fiyat VWAP üzerinde")
                    else:
                        st.error(f"Fiyat VWAP altında")
            with col3:
                st.markdown("**CCI**")
                if pd.notna(cci_son):
                    st.metric("Değer", f"{cci_son:.1f}")
                    if cci_son > 100:
                        st.warning("Aşırı alım momentumu")
                    elif cci_son < -100:
                        st.success("Aşırı satım momentumu")
                    else:
                        st.info("Nötr")

            st.divider()
            st.subheader("🏢 Temel Veriler")
            temel = temel_veri_cek(ticker)
            if not temel or not any(temel.values()):
                st.info(
                    "Bu hisse için Yahoo Finance'te temel veri bulunamadı. "
                    "BIST hisselerinde bu veriler genellikle eksiktir (Yahoo'nun "
                    "kaynak kısıtı) — özellikle yeni IPO'larda hiç olmayabilir."
                )
            else:
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("F/K", deger_formatla("F/K", temel.get("F/K")))
                f2.metric("PD/DD", deger_formatla("PD/DD", temel.get("PD/DD")))
                f3.metric("Piyasa Değeri", deger_formatla("Piyasa Değeri", temel.get("Piyasa Değeri")))
                f4.metric("Temettü Verimi", deger_formatla("Temettü Verimi", temel.get("Temettü Verimi")))
                st.caption(
                    f"Şirket: {temel.get('Şirket') or 'Veri yok'}  |  "
                    f"Sektör: {temel.get('Sektör') or 'Veri yok'}  |  "
                    f"52H Aralık: {deger_formatla('52H Düşük', temel.get('52H Düşük'))} - "
                    f"{deger_formatla('52H Yüksek', temel.get('52H Yüksek'))}"
                )

            st.divider()
            st.subheader("🤖 AI Yorumu")
            ozet_metin = (
                f"Son kapanış: {son['Close']:.2f} ({degisim_pct:+.2f}% günlük)\n"
                f"RSI(14): {rsi_son:.1f}\n"
                f"EMA20: {son['EMA20']:.2f}, EMA50: {son['EMA50']:.2f}\n"
                f"Stokastik RSI %K: {stochk_son:.1f}, %D: {stochd_son:.1f}\n"
                f"CCI(20): {cci_son:.1f}\n"
                f"VWAP(20): {vwap_son:.2f}\n"
            )
            yorum, hata = ai_yorum_uret(ticker, ozet_metin)
            if yorum:
                st.info(yorum)
            elif hata == "anahtar_yok":
                st.caption(
                    "💡 AI yorumu için Anthropic API anahtarı tanımlı değil. "
                    "Aktif etmek için: `.streamlit/secrets.toml` dosyasına "
                    '`ANTHROPIC_API_KEY = "sk-ant-..."` ekle veya ortam değişkeni olarak tanımla.'
                )
            elif hata == "kutuphane_yok":
                st.caption("💡 AI yorumu için `pip install anthropic` gerekiyor.")
            else:
                st.caption(f"AI yorumu alınamadı ({hata}).")

            st.caption(
                "⚠️ Bu analiz teknik göstergelere dayanır; düzenleyici kısıtlamalar, "
                "halka açıklık oranı veya gerçek zamanlı emir derinliği/kurumsal akış "
                "verisini içermez (bu veriler ücretsiz kaynaklarda mevcut değildir). "
                "Yatırım tavsiyesi değildir."
            )

# ------------------------------------------------------------
# TAB 2 — WATCHLIST
# ------------------------------------------------------------
with tab2:
    st.subheader("📋 Çoklu Hisse Karşılaştırma")
    liste_input = st.text_input(
        "Hisse kodlarını virgülle ayırarak girin",
        value="THYAO, GARAN, ASELS, SISE",
        key="watchlist_input",
    )
    kodlar = [normalize_ticker(t) for t in liste_input.split(",") if t.strip()]

    if kodlar:
        satirlar = []
        with st.spinner("Hisseler taranıyor..."):
            for kod in kodlar:
                try:
                    raw = veri_cek(kod)
                    if raw.empty or len(raw) < 2:
                        satirlar.append({"Hisse": kod, "Son Fiyat": None, "Günlük %": None,
                                          "RSI": None, "Trend": "Veri yok", "Sinyal": "—", "Skor": None})
                        continue
                    data = gostergeleri_hesapla(raw)
                    s, o = data.iloc[-1], data.iloc[-2]
                    pct = (s["Close"] - o["Close"]) / o["Close"] * 100 if o["Close"] else 0
                    trend = "Yükseliş" if s["EMA20"] > s["EMA50"] else "Düşüş"
                    sinyal, skor = sinyal_hesapla(s["RSI"], s["EMA20"], s["EMA50"], s["CCI"], s["StochK"])
                    satirlar.append({
                        "Hisse": kod,
                        "Son Fiyat": round(float(s["Close"]), 2),
                        "Günlük %": round(float(pct), 2),
                        "RSI": round(float(s["RSI"]), 1) if pd.notna(s["RSI"]) else None,
                        "Trend": trend,
                        "Sinyal": sinyal,
                        "Skor": skor,
                    })
                except Exception:
                    satirlar.append({"Hisse": kod, "Son Fiyat": None, "Günlük %": None,
                                      "RSI": None, "Trend": "Hata", "Sinyal": "—", "Skor": None})

        sonuc_df = pd.DataFrame(satirlar).sort_values("Skor", ascending=False, na_position="last")
        st.dataframe(
            sonuc_df.style.map(
                lambda v: "color: green; font-weight: bold" if v == "AL"
                else ("color: red; font-weight: bold" if v == "SAT" else ""),
                subset=["Sinyal"],
            ),
            use_container_width=True, hide_index=True,
        )
        st.caption(
            "Sinyal = RSI + EMA trend + CCI + Stokastik RSI'nin birleşik skoru. "
            "Skor ≥ 1.5 → AL, ≤ -1.5 → SAT, arası → NÖTR. Yatırım tavsiyesi değildir."
        )

# ------------------------------------------------------------
# TAB 3 — HİSSE TARAMA
# ------------------------------------------------------------
with tab3:
    st.subheader("🔎 Hisse Tarama")
    st.caption(
        f"Aşağıdaki {len(TARAMA_LISTESI)} hisse taranır (listeyi kodun en üstündeki "
        f"`TARAMA_LISTESI` değişkeninden düzenleyebilirsin). Tüm BIST hisselerini "
        f"ücretsiz bir API'den tek seferde çekmek mümkün değil, bu yüzden liste elle "
        f"hazırlanmıştır."
    )

    filtre = st.radio(
        "Sinyal filtresi", ["Tümü", "Sadece AL", "Sadece SAT", "Sadece NÖTR"],
        horizontal=True, key="tarama_filtre",
    )

    if st.button("🔍 Taramayı Başlat", key="tarama_buton"):
        sonuclar = []
        ilerleme = st.progress(0, text="Taranıyor...")
        for i, kod_kisa in enumerate(TARAMA_LISTESI):
            kod = normalize_ticker(kod_kisa)
            try:
                raw = veri_cek(kod)
                if raw.empty or len(raw) < 2:
                    sonuclar.append({"Hisse": kod_kisa, "Son Fiyat": None, "Günlük %": None,
                                      "RSI": None, "Sinyal": "—", "Skor": None})
                else:
                    data = gostergeleri_hesapla(raw)
                    s, o = data.iloc[-1], data.iloc[-2]
                    pct = (s["Close"] - o["Close"]) / o["Close"] * 100 if o["Close"] else 0
                    sinyal, skor = sinyal_hesapla(s["RSI"], s["EMA20"], s["EMA50"], s["CCI"], s["StochK"])
                    sonuclar.append({
                        "Hisse": kod_kisa,
                        "Son Fiyat": round(float(s["Close"]), 2),
                        "Günlük %": round(float(pct), 2),
                        "RSI": round(float(s["RSI"]), 1) if pd.notna(s["RSI"]) else None,
                        "Sinyal": sinyal,
                        "Skor": skor,
                    })
            except Exception:
                sonuclar.append({"Hisse": kod_kisa, "Son Fiyat": None, "Günlük %": None,
                                  "RSI": None, "Sinyal": "Hata", "Skor": None})
            ilerleme.progress((i + 1) / len(TARAMA_LISTESI), text=f"Taranıyor... {kod_kisa}")
        ilerleme.empty()

        tarama_df = pd.DataFrame(sonuclar)
        if filtre == "Sadece AL":
            tarama_df = tarama_df[tarama_df["Sinyal"] == "AL"]
        elif filtre == "Sadece SAT":
            tarama_df = tarama_df[tarama_df["Sinyal"] == "SAT"]
        elif filtre == "Sadece NÖTR":
            tarama_df = tarama_df[tarama_df["Sinyal"] == "NÖTR"]

        tarama_df = tarama_df.sort_values("Skor", ascending=False, na_position="last")

        if tarama_df.empty:
            st.info("Seçilen filtreye uyan hisse bulunamadı.")
        else:
            st.dataframe(
                tarama_df.style.map(
                    lambda v: "color: green; font-weight: bold" if v == "AL"
                    else ("color: red; font-weight: bold" if v == "SAT" else ""),
                    subset=["Sinyal"],
                ),
                use_container_width=True, hide_index=True,
            )
        st.caption(
            "Sinyal = RSI + EMA trend + CCI + Stokastik RSI'nin birleşik skoru. "
            "Skor ≥ 1.5 → AL, ≤ -1.5 → SAT, arası → NÖTR. Yatırım tavsiyesi değildir."
        )
    else:
        st.info("Taramayı başlatmak için yukarıdaki butona bas.")