import streamlit as st
import pandas as pd
import sys
import os

# 將 src 目錄加入系統路徑，確保可以順利匯入自訂模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from data_provider import TWSEDataProvider
from screener import StockScreener

# 網頁基本設定
st.set_page_config(
    page_title="台股短線突破智慧選股系統",
    page_icon="📈",
    layout="wide"
)

# 標題與說明
st.title("📈 台股短線突破智慧選股系統")
st.markdown("本系統透過即時擷取證交所行情，進行流動性過濾與短線突破量化評分，為您挑選具備爆發力的潛力標的。")

# 側邊欄控制面板
st.sidebar.header("⚙️ 篩選參數設定")
min_price = st.sidebar.slider("最低股價 (元)", min_value=10.0, max_value=100.0, value=15.0, step=5.0)
min_turnover = st.sidebar.slider("最低成交金額 (億元)", min_value=0.1, max_value=5.0, value=0.3, step=0.1)

# 主畫面按鈕
if st.button("🚀 開始執行即時選股運算", type="primary"):
    with st.spinner("正在連線證交所並計算指標中，請稍候..."):
        # 1. 抓取資料
        provider = TWSEDataProvider()
        df_quotes = provider.fetch_daily_quotes()
        
        if df_quotes.empty:
            st.error("❌ 無法取得證交所行情資料，請稍後再試。")
        else:
            # 2. 執行選股篩選
            screener = StockScreener(df_quotes)
            result_df = screener.run_screening()
            
            # 根據側邊欄參數進行動態過濾
            if not result_df.empty:
                result_df = result_df[
                    (result_df['close'] >= min_price) & 
                    (result_df['turnover_amount'] >= min_turnover)
                ]
            
            if not result_df.empty:
                st.success(f"✅ 篩選完成！共找到 {len(result_df)} 檔符合條件的潛力標的。")
                
                # 顯示統計指標
                col1, col2, col3 = st.columns(3)
                col1.metric("符合條件總檔數", f"{len(result_df)} 檔")
                col2.metric("S 級強勢股", f"{len(result_df[result_df['grade'] == 'S'])} 檔")
                col3.metric("最高成交金額", f"{result_df['turnover_amount'].max():.1f} 億元")
                
                st.markdown("---")
                st.subheader("📋 潛力候選股清單")
                
                # 整理要在網頁上展示的美化欄位
                display_df = result_df[['symbol', 'name', 'close', 'change', 'turnover_amount', 'score', 'grade']].copy()
                display_df.columns = ['股票代號', '股票名稱', '收盤價 (元)', '漲跌', '成交金額 (億)', '機會分數', '評級']
                display_df = display_df.reset_index(drop=True)
                
                # 顯示表格
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("⚠️ 目前條件下沒有篩選出符合的股票，請嘗試降低篩選門檻。")
else:
    st.info("👈 請點擊上方「開始執行即時選股運算」按鈕來載入最新選股結果。")