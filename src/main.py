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
    
    # 【修正点】国コードを2文字(JP)から3文字(JPN)に変更
    countries = ['JPN', 'SWE', 'USA']
    
    start_year = 2000
    end_year = datetime.now().year

    @st.cache_data
    def load_data():
        try:
            # データ取得
            data = wb.data.DataFrame(list(indicators.keys()), 
                                     economy=countries, 
                                     time=range(start_year, end_year + 1), 
                                     numericTime=True)
            
            if data is None or data.empty:
                return pd.DataFrame()

            data = data.reset_index()
            data = data.rename(columns={'economy': 'country', 'time': 'year'})
            data = data.rename(columns=indicators)
            return data
        except Exception as e:
            # エラー内容を画面に出す（デバッグ用）
            st.error(f"データ取得エラー詳細: {e}")
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
            else:
                st.warning("インフレ率データが見つかりませんでした。")

        with col2:
            st.subheader("🤖 AIエコノミスト")
            st.write("ボタンを押すと分析を開始します。")
            if st.button("AI解説を生成する"):
                if not api_key:
                    st.error("Secretsが未設定です。")
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
        st.caption("Compliance: Data from World Bank API (wbgapi). Analysis by Google Gemini.")
    else:
        # データが取れなかった場合
        st.warning("⚠️ データが取得できませんでした。")
        st.write("考えられる原因：World BankのAPIが一時的に混雑しているか、国コードの設定ミスです。")

if __name__ == "__main__":
    main()
