import streamlit as st
import pandas as pd
import wbgapi as wb  # 新しいライブラリ
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
    
    # 接続診断
    with st.sidebar:
        st.header("🔧 接続診断")
        if not api_key:
            st.error("❌ APIキー未設定")
        else:
            st.success("✅ APIキー認識OK")

    st.info("データソース: World Bank Open Data (via wbgapi) | AIエンジン: Google Gemini")

    # 1. データ取得設定
    # キー: インフレ率, GDP成長率, 失業率
    indicators = {
        'FP.CPI.TOTL.ZG': 'インフレ率 (Inflation)',
        'NY.GDP.MKTP.KD.ZG': 'GDP成長率 (GDP Growth)',
        'SL.UEM.TOTL.ZS': '失業率 (Unemployment)'
    }
    countries = ['JP', 'SE', 'US']
    start_year = 2000
    end_year = datetime.now().year

    @st.cache_data
    def load_data():
        try:
            # wbgapiを使用してデータを取得（ここを刷新）
            # numericTime=Trueで年を数値化、indexをリセットして扱いやすくする
            data = wb.data.DataFrame(list(indicators.keys()), 
                                     economy=countries, 
                                     time=range(start_year, end_year + 1), 
                                     numericTime=True)
            
            # データの整形
            data = data.reset_index()
            # wbgapiは 'economy', 'time' というカラム名で返すのでリネーム
            data = data.rename(columns={'economy': 'country', 'time': 'year'})
            
            # 指標コードをわかりやすい名前に変更
            data = data.rename(columns=indicators)
            return data
        except Exception as e:
            st.error(f"データ取得エラー: {e}")
            return pd.DataFrame()

    df = load_data()

    if not df.empty:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📊 インフレ率の推移")
            # データが存在するカラム名を取得
            target_col = indicators['FP.CPI.TOTL.ZG']
            
            # データフレームに該当カラムがあるか確認
            if target_col in df.columns:
                fig = px.line(df, x="year", y=target_col, color="country", markers=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("インフレ率データの取得に失敗しました")

        with col2:
            st.subheader("🤖 AIエコノミスト")
            st.write("直近のデータを基に分析します。")
            
            if st.button("AI解説を生成する"):
                if not api_key:
                    st.error("APIキーがありません。Secretsを設定してください。")
                else:
                    with st.spinner("AIが分析中..."):
                        try:
                            latest_year = df['year'].max()
                            latest_data = df[df['year'] == latest_year].to_string()
                            prompt = f"""
                            あなたはプロの経済アナリストです。以下のデータ（JP, SE, US）に基づき、
                            なぜ日本だけ特殊な動きをしているのか辛口に解説してください。
                            データ: {latest_data}
                            """
                            
                            # モデル自動切り替え
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
        st.warning("データが取得できませんでした。しばらく待ってからリロードしてください。")

if __name__ == "__main__":
    main()
