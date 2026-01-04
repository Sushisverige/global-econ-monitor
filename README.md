# Global Econ Monitor vs Japan (G7 Comparison Dashboard)

## 📌 Project Overview
世界銀行 (World Bank) のオープンデータAPIを活用し、日本とG7諸国・スウェーデンの経済指標（インフレ率、実質賃金など）をリアルタイムで比較・可視化するダッシュボードです。

## 🛡 Compliance & Ethics (設計思想)
1. **No Scraping Policy**: World Bank Open Data API のみを使用し、規約を遵守。
2. **Privacy by Design**: 個人情報を一切保持しないステートレス設計。
3. **AI Governance**: AIの回答には必ず免責とデータ出典を明記。

## 🛠 Tech Stack
* Python 3.10, Streamlit, Docker, GitHub Actions, Gemini API

## 🚀 Quick Start
```bash
docker-compose up --build
```
