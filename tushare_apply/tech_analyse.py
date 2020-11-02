import json
import talib 
import pandas as pd
import pdb
from collections import OrderedDict

def load_ta_pat_map():
    return json.load(open('talib_pattern_name.json'))
TA_PATTERN_MAP = load_ta_pat_map()


def candle_analyse(df):
    '''
    input:OHLC dataframe
    '''
    cn_names = []
    ## calc all candle score
    for funcname in talib.get_function_groups()[ 'Pattern Recognition']:
        func = getattr(talib,funcname) 
        score_data = func(df['open'],df['high'],df['low'],df['close'])
        cn_name = funcname[3:]        
        df[cn_name] = score_data
        cn_names.append(cn_name)
    
    ###
    total_cdl_score = df[cn_names].sum(axis=1)
    df['CDLScore'] =  total_cdl_score
    cdl_info = {'cdl_total' : '%s'% (total_cdl_score.values[-1]),'data':{} }
    last_cdlrow = df.iloc[-1]
    for name,cdl_vlu in last_cdlrow.iteritems():        
        if cdl_vlu != 0 and name in TA_PATTERN_MAP:
            the_info = TA_PATTERN_MAP[name]
            fig = the_info['figure'].split(' ')[1]
            cn_name = the_info['name'].split(' ')[0]
            en_name = the_info['name'].split(' ')[1]
            intro = the_info['intro']
            intro2 = the_info['intro2']
            cdl_info['data'][name] = {'figure':fig,'score':cdl_vlu,'cn_name':cn_name,'intro':intro,'intro2':intro2,'en_name':en_name}
    # print jsdump(cdl_info)
    return cdl_info,df
    
def pivot_line(open,high,low,close, mode='classic'):
    pivot = (high + low + 2* close )/4
    r1 = pivot*2 - low 
    s1 = pivot*2 - high
    r2 = pivot + r1 - s1
    s2 = pivot - (r1 - s1)
    r3 = high + 2*(pivot - low)
    s3 = low - 2*(high - pivot)
    sm1 = (pivot+s1)/2
    sm2 = (s1+s2)/2
    sm3 = (s2+s3)/2
    rm1 = (pivot+r1)/2
    rm2 = (r1+r2)/2
    rm3 = (r2+r3)/2
    return r3,r2,r1,pivot,s1,s2,s3    
    
def boll_analyse(ohlcv,period=10):
    boll_up, boll_mid, boll_low = talib.BBANDS(ohlcv['close'],period)
    df = pd.DataFrame({'boll_up': boll_up, 'boll_mid':boll_mid, 'boll_low':boll_low })    
    scale = period
    u = talib.LINEARREG_ANGLE(boll_up *scale, timeperiod=2)
    m = talib.LINEARREG_ANGLE(boll_mid*scale, timeperiod=2)    
    l = talib.LINEARREG_ANGLE(boll_low*scale, timeperiod=2)
    if m[-1]>=0:
        res = ['UP']
    else:
        res = ['DOWN']
    if u[-1]-m[-1]>=0:
        res[0] += '-EXPAND'
    else:
        res[0] += '-SHRINK'
    res += ['ANG[MID:%0.2f, UP:%0.2f], MID_PRC:%0.2f'%(m[-1], u[-1]-m[-1], boll_mid[-1])]
    res += ['UP:%0.2f, MID:%0.2f, LOW:%0.2f'%(boll_up[-1],boll_mid[-1],boll_low[-1])]
    return res,df
 
def value_range_judge(vlu,up_down,up_down_name): 
    if vlu>=up_down[0]:
        return up_down_name[0]+': %0.2f'%vlu
    elif vlu<=up_down[1]:
        return up_down_name[1]+': %0.2f'%vlu
    else:
        return "MID"+': %0.2f'%vlu      
    

def cross_judge(row):    
    # pdb.set_trace()
    fast_ag = row['fast_ag']
    slow_ag = row['slow_ag']
    ag_dif = fast_ag - slow_ag
    value_gap = row['fast_line'] - row['slow_line']
    if fast_ag>0 and slow_ag>0:
        res='AftGoldX'
    elif fast_ag>0  and slow_ag<0:
        res='TrnBefGoldX'
    elif ag_dif>0 and slow_ag<0:
        res='CovBefGoldX'
    elif fast_ag<0 and slow_ag<0:
        res='AftDeathX'
    elif fast_ag<0  and slow_ag>0:
        res='TrnBefDeathX'
    elif  ag_dif<0 and slow_ag>0:
        res='CovBefDeathX'
    else:
        res='Unknown[fast_ag:%0.2f, ag_dif:%0.2f, value_gap:%0.2f]'%(fast_ag,ag_dif,value_gap)
    return res
    
def get_crossx_type(fast_line,slow_line):
    fast_ag = talib.LINEARREG_ANGLE(fast_line, timeperiod=2)
    slow_ag = talib.LINEARREG_ANGLE(slow_line, timeperiod=2)
    df=pd.DataFrame({'fast_line':fast_line,'slow_line':slow_line,'fast_ag':fast_ag,'slow_ag':slow_ag})
    df['cross_stage'] = df.apply(cross_judge,axis=1)#,result_type='expand'    
    # print edf
    return df
    
def macd_analyse(ohlcv,period=10):
    dif, dea, hist =  talib.MACD(ohlcv['close'],period)    
    df = pd.DataFrame({'macd_dif': dif, 'macd_dea':dea, 'macd_hist':hist })    
    # pdb.set_trace() 
    res = []    
    df =  get_crossx_type(dif,dea)
    row = df.iloc[-1]     
    print row
    res += ['%s: ANG[IF:%0.2f, EA:%0.2f]'%(row['cross_stage'],row['fast_ag'],row['slow_ag'])]
    res += ['DIF:%0.2f, DEA:%0.2f, MACD:%0.2f'%(dif[-1],dea[-1],hist[-1]*2)]   
    return res,df
   

def rsi_analyse(ohlcv,period=10):
    
def round_float(lst):
    return map(lambda x:'%0.2f'%x,lst)    
    
def tech_analyse(df):    
    '''
    input:OHLC dataframe
    '''
    open = df['open'].values
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    vol = df['volume'].values.astype(float)
    ohlcv= {'open':open,'high':high,'low':low,'close':close,'vol':vol}
    
    ana_res = OrderedDict()
    
    
    ## BOLL
    boll_anly_res,bdf = boll_analyse(ohlcv)
    df= pd.concat([df,bdf.set_index(df.index)],axis=1)
    ana_res['BOLL'] =  boll_anly_res
    
    ##MACD
    macd_anly_res,mdf = macd_analyse(ohlcv)
    df= pd.concat([df,mdf.set_index(df.index)],axis=1)
    ana_res['MACD'] = macd_anly_res
    
    ##
    rsi = talib.RSI(close)
    ana_res['RSI'] = value_range_judge( rsi[-1] ,[70,30],['OverBrought','OverSell'])
    
    ##
    roc = talib.ROCR(close)
    
    ##
    slk,sld = talib.STOCH(high,low,close)
    slj = 3*slk-2*sld
    ana_res['KDJ'] = 'KDJ:%s'%([slk[-1],sld[-1], slj[-1] ])
    
    ##
    obv = talib.OBV(close,vol)
    ##
    sar = talib.SAREXT(high,low)
    
    ##
    ema05  = talib.EMA(close,5)
    ema10  = talib.EMA(close,10)
    ema20  = talib.EMA(close,20)
    ema60  = talib.EMA(close,60)
    ema240 = talib.EMA(close,240)
    ##
    sma05  = talib.SMA(close,5)
    sma10  = talib.SMA(close,10)
    sma20  = talib.SMA(close,20)
    sma60  = talib.SMA(close,60)
    sma240 = talib.SMA(close,240)    
    ##
    atr14 = talib.ATR(high,low,close,timeperiod =14)
    atr28 = talib.ATR(high,low,close,timeperiod =28)
    ##
    pivot_point = map(lambda x:round(x[-1],2) , pivot_line(open,high,low,close) )    
    # name = ' '
    analyse_info = OrderedDict({'price':df['close'].values[-1]})
    
    
    
    
    # ana_res['BOLL'] = [bl_upper[-1],bl_middle[-1],bl_lower[-1] ]
    
    
    
    
    
    
    # ana_res['ROC'] = round_float([roc[-3],roc[-2],roc[-1]  ])
    # ana_res['OBV'] = round_float([ obv[-1] ])
    ana_res['SAR'] = round_float([ sar[-1] ])
    # ana_res['EMA'] = round_float([ ema05[-1],ema10[-1],ema20[-1],ema60[-1],ema240[-1] ])
    # ana_res['SMA'] = round_float([ sma05[-1],sma10[-1],sma20[-1],sma60[-1],sma240[-1] ])
    ana_res['VOL_Rate'] = round_float([vol[-1]*1.0/vol[-2]])
    # ana_res['ATR14'] = round_float(list(atr14[-10::2]))
    # ana_res['ATR28'] = round_float(list(atr28[-10::2]))
    ana_res['PIVOT'] = 'Resistance:%s, Mid:%s, Support:%s'%(pivot_point[0:3],pivot_point[3],pivot_point[4:])
    ### put into output 
    analyse_info['data']= ana_res
    # pdb.set_trace()
    return analyse_info,df
    
def jsdump(info, indent=None):
    return json.dumps(info, ensure_ascii=False, indent=indent) 
    
ECODE='gbk'    
def analyse_res_to_str(res):
    intro = {}
    pstr = ''
    for stock in res:
        if stock is None:
            continue        
        code = stock.get('code','no-code')
        name = stock.get('info',{}).get('name','')
        price = stock.get('info',{}).get('price','')
        pstr+= "\n[{0}:{1}] Price:{2}".format(code,name.encode(ECODE),price)
        if 'tech' in stock and stock['tech'] != None:
            tech = stock['tech']
            for key,vlu in tech['data'].items():
                pstr+= '\n  [%s] %s'%(key,jsdump(vlu))
            
        if 'cdl' in stock and stock['cdl'] != None:
            cdl = stock['cdl']
            cdl_ent_str = ','.join([u'[{}:{}]:{}{}'.format(info['score'],info['figure'],name,info['cn_name']) for name,info in cdl['data'].items()])
            for name,info in cdl['data'].items():
                intro[info['en_name']+info['cn_name']] = info['intro2']
            pstr+= "\n  [CDL_Total:{0}]  {1}".format(cdl['cdl_total'], cdl_ent_str.encode(ECODE) )
    for name,intro in intro.items():
        pstr+= u"\n[{}]:{}".format(name,intro).encode(ECODE)  
    return pstr

 
def test():
    import tushare as ts
    
    def pprint(info, indent=None):
        print json.dumps(info, ensure_ascii=False, indent=2).encode('gbk')
    
    # df = ts.get_hist_data('601865')
    # df = ts.get_hist_data('600438')
    # df.to_csv('temp.csv')
    df=pd.read_csv('temp.csv')
    df = df.sort_values('date')
    tinfo,df = tech_analyse(df)
    pprint(tinfo)
    # df.to_csv('temp.csv')
    # pdb.set_trace()
    # cinfo,df = candle_analyse(df)
    # pprint(cinfo)
    
if __name__ == '__main__':
    test()