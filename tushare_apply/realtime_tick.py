import os
from datetime import datetime,timedelta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tushare as ts
# import seaborn as sns
import datetime

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',None)
pd.options.display.float_format = '{:.2f}'.format


def real_time_tick(tick,use_cache = True):
    fname = 'data/today_tick.%s.csv'%tick
    if not use_cache:
        try:
            df = ts.get_today_ticks(tick)
            df.index.name = 'id'
            df.to_csv(fname,encoding='utf8')
        except:
            print 'Fail On URL'
            pass
    df = pd.read_csv(fname,encoding='utf8',index_col='id')
    print tick
    print df.groupby('type').agg({'volume':'sum','price':'mean','change':'count'})
    print str(df.groupby(['change']).agg({'volume':'sum','price':'mean'})).decode('utf8').encode('gbk')
    print df.corr()
    
    df['time'] = pd.to_datetime(df['time'].apply(lambda x:'2019-08-22 '+x))
    vcut =  pd.cut(df['volume'],5)
    ccut =  pd.cut(df['change'],5)    
    tcut =  pd.cut(df['time'],5)
    print pd.crosstab( vcut,df['type'])
    print pd.crosstab( ccut,df['type'])
    print pd.crosstab( ccut,vcut)
    print pd.crosstab( tcut,vcut)
    print df.describe()
    # df2 = ts.get_tick_data(tick,date=dt,src='tt')
    # df3 = ts.get_hist_data(tick)
    rdf = ts.get_realtime_quotes(tick) 
    # print rdf.melt()

def pro_api():
    ts.set_token('7e30dd0a070cd4306193a5925ec5b3c250a694f08ea390d7cc3af2d6')
    pro = ts.pro_api()
    df = pro.fina_mainbz(ts_code='000627.SZ', period='20171231', type='P')
    # df = pro.index_basic('sw')
    # df = pro.cashflow(ts_code='600000.SH', start_date='20180101', end_date='20180730')
    # df =ts.moneyflow_hsgt()
    # ts.cashflow(symbol)
    print df.describe()
    # ts.get_k_data
    # ts.get_hist_data
    # ts.get_today_all
    # print df1,df2
    # df2.to_csv('%s.today.csv'%symbol,encoding ='gbk' )
    # print df
    # exit()
    
def test():
    df=pd.DataFrame(np.random.randn(10002,3),columns=['x','y','z'])
    # sns.violinplot(y='y',data=df)
    plt.show()
    
def main():
    dt=datetime.datetime.now().strftime('%Y%m%d')    
    tick='300072'
    tick='300330'
    tick='600868'
    tick='002384'
    tick='002430'
    tick='002382'
    tick='518800'
    tick='600438'
    real_time_tick(tick)
    
    
if __name__ == '__main__':
    main()