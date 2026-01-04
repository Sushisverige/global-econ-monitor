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
    
    with st.sidebar:
        st.header("🔧 接続診断")
        if not api_key:
            st.error("❌ APIキー未設定")
        else:
            st.success("✅ APIキー認識OK")

    st.info("データソース: World Bank Open Data (via wbgapi) | AIエンジン: Google Gemini")

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
            # 【最終解決策】wb.data.fetchを使って、生の辞書リストとして取得する
            # これならフォーマットの崩れようがない
            raw_data = list(wb.data.fetch(list(indicators.keys()), 
                                          economy=countries, 
                                          time=range(start_year, end_year + 1)))
            
            # 生データをDataFrame化
            df = pd.DataFrame(raw_data)
            
            if df.empty:
                return pd.DataFrame()

            # データ整形: 'YR2000' -> 2000
            df['time'] = df['time'].astype(str).str.replace('YR', '').astype(int)
            
            # ピボットテーブル操作（行:国・年, 列:指標, 値:数値）
            # これで必ず狙った形になる
            df_pivot = df.pivot(index=['economy', 'time'], columns='series', values='value').reset_index()
            
            # カラム名の修正
            df_pivot = df_pivot.rename(columns={'economy': 'country', 'time': 'year'})
            df_pivot = df_pivot.rename(columns=indicators)
            
            return df_pivot
        except Exception as e:
            st.error(f"データ処理エラー: {e}")
            return pd.DataFrame()

    df = load_data()

    if not df.empty:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📊 インフレ率の推移")
            target_col = indicators['FP.CPI.TOTL.ZG']
            # データがあるか確認
            if target_col in df.columns:
                fig = px.line(df, x="year", y=target_col, color="country", markers=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("インフレ率データがありませんでした。")

        with col2:
            st.subheader("🤖 AIエコノミスト")
            st.write("ボタンを押すと分析を開始します。")
            if st.button("AI解説を生成する"):
                if not api_key:
                    st.error("Secrets未設定")
                else:
                    with st.spinner("AIが分析中..."):
                        try:
                            latest_year = df['year'].max()
                            latest_data = df[df['year'] == latest_year].to_string()
                            prompt = f"""
                            あなたはプロの経済アナリストです。以下のデータ（JPN, SWE, USA）に基づき、
                            なぜ日本だけ特殊な動きをしているのか辛口に解説してください。
                            データ: {latest_data}
                            """
                            try:
                                model = genai.GenerativeModel('gemini-1.5-flash')
                                response = model.generate_content(prompt)
                            except:
                                model = genai.GenerativeModel('gemini-pro')
                                response = model.generate_content(prompt)
                            
                            st.success("分析完了！")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"AIエラー: {e}")
        st.divider()
        st.caption("Compliance: Data from World Bank API. Analysis by Google Gemini.")
    else:
        st.warning("⚠️ データが取得できませんでした。")

if __name__ == "__main__":
    main()
