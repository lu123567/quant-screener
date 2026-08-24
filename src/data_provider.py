import requests
import pandas as pd
import time
from datetime import datetime

class TWSEDataProvider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
    def fetch_daily_quotes(self) -> pd.DataFrame:
        """
        獲取上市個股日成交資訊 (STOCK_DAY_ALL)
        """
        url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
        try:
            print("正在抓取 TWSE 上市個股日成交資訊...")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                print("回傳資料為空")
                return pd.DataFrame()
                
            df = pd.DataFrame(data)
            print("原始 API 回傳的欄位有：", df.columns.tolist())
            
            # 兼容大小寫與不同欄位名稱的對應
            rename_mapping = {}
            for col in df.columns:
                lower_col = col.lower()
                if 'code' in lower_col:
                    rename_mapping[col] = 'symbol'
                elif 'name' in lower_col:
                    rename_mapping[col] = 'name'
                elif 'tradevolume' in lower_col or col == 'Volume':
                    rename_mapping[col] = 'volume'
                elif 'tradevalue' in lower_col:
                    rename_mapping[col] = 'value'
                elif 'openprice' in lower_col or col == 'Open':
                    rename_mapping[col] = 'open'
                elif 'highestprice' in lower_col or col == 'High':
                    rename_mapping[col] = 'high'
                elif 'lowestprice' in lower_col or col == 'Low':
                    rename_mapping[col] = 'low'
                elif 'closingprice' in lower_col or col == 'Close':
                    rename_mapping[col] = 'close'
                elif 'change' in lower_col:
                    rename_mapping[col] = 'change'
                elif 'transaction' in lower_col:
                    rename_mapping[col] = 'transactions'
                    
            df = df.rename(columns=rename_mapping)
            
            # 將數值欄位轉成數字
            numeric_cols = ['volume', 'value', 'open', 'high', 'low', 'close', 'change', 'transactions']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
                
            return df
            
        except Exception as e:
            print(f"獲取日行情失敗: {e}")
            return pd.DataFrame()

# 測試用區塊
if __name__ == "__main__":
    provider = TWSEDataProvider()
    df_quotes = provider.fetch_daily_quotes()
    if not df_quotes.empty and 'close' in df_quotes.columns:
        print("✅ 成功抓取日行情！前五筆資料：")
        print(df_quotes[['symbol', 'name', 'close', 'volume']].head())
    else:
        print("❌ 欄位對應失敗或目前無資料。")