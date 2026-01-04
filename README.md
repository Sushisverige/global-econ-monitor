# 🌏 Global Econ Monitor: AI Analysis

世界銀行のオープンデータをリアルタイムで取得し、生成AI (Google Gemini) が経済指標を分析するダッシュボードアプリです。
日本、スウェーデン、米国のインフレ率・GDP成長率・失業率を比較し、AIが「なぜ日本経済が特殊な動きをしているのか」を辛口に解説します。

## 🚀 デモアプリ (Live Demo)
**[👉 ここをクリックしてアプリを開く (Click Here)](https://global-econ-monitor-vnheasvzdqefoi6mqhssvj.streamlit.app/)**

## 🛠 使用技術 (Tech Stack)
- **Frontend:** Streamlit
- **Data Source:** World Bank Open Data (via wbgapi)
- **AI Engine:** Google Gemini 1.5 Flash (via Google AI Studio)
- **Visualization:** Plotly Express
- **Deploy:** Streamlit Cloud

## ✨ 主な機能
1. **リアルタイムデータ取得:** APIを通じて最新の経済指標を自動取得
2. **インタラクティブなグラフ:** Plotlyによる動的なデータ可視化
3. **AIアナリスト:** Gemini APIを使用し、データに基づいた経済分析レポートを自動生成
4. **堅牢な設計:** API接続エラー時の自動ハンドリング機能搭載
