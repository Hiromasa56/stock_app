import pandas as pd
import yfinance as yf           #株価取得のライブラリ
import altair as alt              #可視化ライブラリ
import streamlit as st

st.title('米国株価可視化アプリ')

st.sidebar.write('''
# GAFA株価
こちらは株価可視化ツール。以下のオプションから表示日数を指定
''')

st.sidebar.write('''
## 表示日数の選択
''')

days = st.sidebar.slider('日数', 1, 50, 20)   #選択した日付が変数に入る

st.write(f'''
### 過去 **{days}日間** のGAFA株価
'''     )

#yfinanceにより企業のその日の株価の終値を取得する関数
@st.cache
def get_data(days, tickers):
    df = pd.DataFrame()  #複数の企業のデータを入れるデータフレーム
    for company in tickers.keys():

        tkr = yf.Ticker(tickers[company]) 

        hist = tkr.history(period=f'{days}d') 
        hist.index = hist.index.strftime('%d %B %Y') 
        hist = hist[['Close']]  
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])     #dfにそれぞれのデータを追加できる。axis=0でくっつける
    return df

#例外処理は構文的にはエラーがないが、存在しない変数の指定や0で割るなどを行った場合おこるもの。
#エラーは構文がおかしい場合
try:    #例外処理
    st.sidebar.write('''
    ## 株価の範囲指定
    ''')
    y_min, y_max = st.sidebar.slider(
        '範囲を指定してください。',
        0.0, 3500.0, (0.0, 3500.0)
    )

    #取得したい会社名とticker名を辞書型で指定
    tickers = {
        'apple': 'AAPL',
        'facebook': 'FB',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN'
    }

    df = get_data(days, tickers)

    #会社を選ぶような画面の表示
    companies = st.multiselect(
        '会社名を選択してください',
        list(df.index),
        ['google', 'amazon', 'facebook', 'apple']   #デフォルト値
    )

    #会社が選ばれていたらデータとグラフを表示
    if not companies:
        st.error('少なくとも1社は選んでください')
    else:
        data = df.loc[companies]
        st.write('### 株価(USD)', data.sort_index())  #データフレームの表示
        #データの成型
        data = data.T.reset_index()   #グラフはDateのデータが必要だから
        #melt関数でDateを基準にそれぞれのカラム毎にデータをばらしている
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )

        #可視化の設定
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x='Date:T',
                y=alt.Y('Stock Prices(USD):Q', stack=None, scale=alt.Scale(domain=[y_min, y_max])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)

except:
        st.error(
            'エラーが発生しました'
        )