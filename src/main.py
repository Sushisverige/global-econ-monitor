import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="Global Econ Monitor", layout="wide")
    
    st.title("🌏 Global Econ Monitor vs Japan")
    st.markdown("### 世界銀行オープンデータを活用した経済指標ダッシュボード")
    
    st.info("システムステータス: 正常 (Dockerコンテナ上で動作中)")

    st.write("ここにデータが表示されます...")

if __name__ == "__main__":
    main()
