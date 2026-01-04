import streamlit as st
import pandas as pd
from pandas_datareader import wb
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
    st.title("🌏 Global Econ Monitor: AI Analysis (Debug Mode)")
    st.markdown("### 日本 vs スウェーデン vs 米国：AIによる経済構造分析")
    
    # API接続テスト（サイドバーに表示）
    with st.sidebar:
        st.header("🔧 接続診断")
        if not api_key:
            st.error("❌ APIキーが設定されていません")
        else:
            try:
                st.write("APIキー: 認識済み")
                # 利用可能なモデル一覧を取得して表示
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                st.success(f"✅ 接続OK! 利用可能モデル数: {len(models)}")
                st.code("\n".join(models))
                # 優先的に使うモデルを決める
                valid_models = [m for m in models if 'flash' in m or 'pro' in m]
                model_name = valid_models[0] if valid_models else 'models/gemini-pro'
                st.info(f"使用するモデル: {model_name}")
            except Exception as e:
                st.error(f"❌ モデル一覧取得エラー: {e}")
                model_name = None

    # データ取得ロジック
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
            data = wb.download(indicator=list(indicators.keys()), country=countries, start=start_year, end=end_year)
            data = data.reset_index()
            data['year'] = data['year'].astype(int)
            data = data.rename(columns=indicators)
            return data
        except Exception:
            return pd.DataFrame()

    df = load_data()

    if not df.empty:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📊 インフレ率の推移")
            target_col = indicators['FP.CPI.TOTL.ZG']
            fig = px.line(df, x="year", y=target_col, color="country", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🤖 AIエコノミスト")
            st.write("直近のデータを基に、日本経済の課題を分析します。")
            
            if st.button("AI解説を生成する"):
                if not api_key or not model_name:
                    st.error("API接続に問題があるため実行できません。サイドバーを確認してください。")
                else:
                    with st.spinner(f"AIが分析中... (Model: {model_name})"):
                        try:
                            latest_year = df['year'].max()
                            latest_data = df[df['year'] == latest_year].to_string()
                            prompt = f"""
                            あなたはプロの経済アナリストです。以下のデータ（JP, SE, US）に基づき、
                            なぜ日本だけ特殊な動きをしているのか辛口に解説してください。
                            データ: {latest_data}
                            """
                            
                            # 自動判別したモデル名を使用
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(prompt)
                            
                            st.success("分析完了！")
                            st.markdown(response.text)
                            
                        except Exception as e:
                            st.error(f"エラー詳細: {e}")

        st.divider()
        st.caption("Compliance: Data from World Bank API. Analysis by Google Gemini.")
    else:
        st.warning("データ取得失敗")

if __name__ == "__main__":
    main()
