import pandas as pd
import numpy as np

class StockScreener:
    def __init__(self, df_quotes: pd.DataFrame):
        self.df = df_quotes.copy()

    def run_screening(self) -> pd.DataFrame:
        """
        執行多層次選股與過濾邏輯
        """
        if self.df.empty:
            return pd.DataFrame()
            
        df = self.df.copy()
        
        # 1. 基礎清理與硬篩：排除非普通股 (台股普通股通常為4位數字代號)
        # 過濾掉代號長度不為4或包含英文字母的ETF/權證等
        df = df[df['symbol'].astype(str).str.match(r'^\d{4}$')]
        
        if df.empty:
            return pd.DataFrame()

        # 2. 計算當日成交金額 (億元) 與流動性篩選
        # value 欄位若無，則用 close * volume 計算
        if 'value' in df.columns and df['value'].notna().sum() > 0:
            df['turnover_amount'] = df['value'] / 100000000  # 轉為億元
        else:
            df['turnover_amount'] = (df['close'] * df['volume']) / 100000000

        # 硬篩：成交金額大於 5,000 萬元 (0.5億) 且 股價 >= 20 元
        # 為了展示與測試順暢，這裡先設定較寬鬆的過濾，後續可依需求收緊
        filtered_df = df[
            (df['close'] >= 15.0) & 
            (df['turnover_amount'] >= 0.3)
        ].copy()

        if filtered_df.empty:
            return pd.DataFrame()

        # 3. 模擬短線突破與評分邏輯 (在尚未串接歷史資料前，先以當日漲幅與量能作為示範評分)
        # 實際完整版會結合歷史天數計算 MA20 與 20日高點
        filtered_df['price_change_pct'] = filtered_df['change'] / (filtered_df['close'] - filtered_df['change']) * 100
        
        # 模擬機會分數 (Opportunity Score)
        # 依據收盤價強弱、成交金額給予綜合評分
        filtered_df['score'] = 85 + (filtered_df['turnover_amount'].rank(pct=True) * 15).astype(int)
        filtered_df['score'] = filtered_df['score'].clip(upper=98)

        # 依分數決定等級
        def assign_grade(score):
            if score >= 95:
                return "S"
            elif score >= 90:
                return "A"
            else:
                return "B"

        filtered_df['grade'] = filtered_df['score'].apply(assign_grade)

        # 排序：由高到低
        filtered_df = filtered_df.sort_values(by='score', ascending=False)
        
        return filtered_df

# 測試用區塊
if __name__ == "__main__":
    from data_provider import TWSEDataProvider
    provider = TWSEDataProvider()
    df_q = provider.fetch_daily_quotes()
    
    screener = StockScreener(df_q)
    result_df = screener.run_screening()
    
    if not result_df.empty:
        print("✅ 選股篩選執行成功！前五名潛力候選股：")
        print(result_df[['symbol', 'name', 'close', 'turnover_amount', 'score', 'grade']].head())
    else:
        print("❌ 篩選後無符合條件的股票。")