import streamlit as st
import pandas as pd
import wbgapi as wb
import plotly.express as px
from datetime import datetime
import google.generativeai as genai
import os

st.set_page_config(page_title="Global Econ Monitor", layout="wide")

# APIキー設定
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def main():
    st.title("🌏 Global Econ Monitor: AI Analysis")
    st.markdown("### 日本 vs スウェーデン vs 米国：AIによる経済構造分析")
    
    # 【強化版】サイドバーで接続とモデルを事前チェック
    with st.sidebar:
        st.header("🔧 接続診断")
        if not api_key:
            st.error("❌ APIキー未設定")
        else:
            try:
                # 実際にAPIを叩いて、使えるモデル一覧を取得する
                # これが成功すれば、接続は100%確実
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                if available_models:
                    st.success(f"✅ 接続OK (利用可能モデル数: {len(available_models)})")
                    # デバッグ用にモデル名を表示（小さく）
                    st.caption(f"Default: {available_models[0]}")
                else:
                    st.error("⚠️ 接続はできたけど、使えるモデルがありません。")
            except Exception as e:
                st.error(f"❌ API接続エラー: {e}")
                available_models = []

    st.info("データソース: World Bank Open Data (via wbgapi) | AIエンジン: Google Gemini (Auto-Select)")

    indicators = {
        'FP.CPI.TOTL.ZG': 'インフレ率 (Inflation)',
        'NY.GDP.MKTP.KD.ZG': 'GDP成長率 (GDP Growth)',
        'SL.UEM.TOTL.ZS': '失業率 (Unemployment)'
    }
    
    countries = ['JPN', 'SWE', 'USA']
    start_year = 2000
    end_year = datetime.now().year

    @st.cache_data
    def load_data():
        try:
            raw_data = list(wb.data.fetch(list(indicators.keys()), 
                                          economy=countries, 
                                          time=range(start_year, end_year + 1)))
            df = pd.DataFrame(raw_data)
            if df.empty: return pd.DataFrame()

            df['time'] = df['time'].astype(str).str.replace('YR', '').astype(int)
            df_pivot = df.pivot(index=['economy', 'time'], columns='series', values='value').reset_index()
            df_pivot = df_pivot.rename(columns={'economy': 'country', 'time': 'year'})
            df_pivot = df_pivot.rename(columns=indicators)
            return df_pivot
        except Exception:
            return pd.DataFrame()

    df = load_data()

    if not df.empty:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📊 インフレ率の推移")
            target_col = indicators['FP.CPI.TOTL.ZG']
            if target_col in df.columns:
                fig = px.line(df, x="year", y=target_col, color="country", markers=True)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🤖 AIエコノミスト")
            st.write("ボタンを押すと分析を開始します。")
            if st.button("AI解説を生成する"):
                if not api_key:
                    st.error("Secrets未設定")
                elif not available_models:
                    st.error("利用可能なAIモデルが見つかりません。")
                else:
                    with st.spinner("AIモデルを選定して分析中..."):
                        try:
                            # 1. 優先順位を決めてモデルを選ぶ (Flash > Pro > その他)
                            target_model = None
                            for m in available_models:
                                if 'flash' in m:
                                    target_model = m
                                    break
                            
                            if not target_model:
                                for m in available_models:
                                    if 'pro' in m:
                                        target_model = m
                                        break
                            
                            # 2. それでもなければリストの先頭を使う（絶対に存在する名前）
                            if not target_model:
                                target_model = available_models[0]

                            st.caption(f"使用モデル: {target_model}") # どのモデルが選ばれたか表示

                            latest_year = df['year'].max()
                            latest_data = df[df['year'] == latest_year].to_string()
                            prompt = f"""
                            あなたはプロの経済アナリストです。以下のデータ（JPN, SWE, USA）に基づき、
                            なぜ日本だけ特殊な動きをしているのか辛口に解説してください。
                            データ: {latest_data}
                            """
                            
                            model = genai.GenerativeModel(target_model)
                            response = model.generate_content(prompt)
                            
                            st.success("分析完了！")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"エラー詳細: {e}")
        st.divider()
        st.caption("Compliance: Data from World Bank API. Analysis by Google Gemini.")
    else:
        st.warning("データ取得中...")

if __name__ == "__main__":
    main()
