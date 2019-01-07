import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from astropy.io import fits
import aplpy

data = pd.read_csv\
('/Users/mmorita/kwfc-analysis/analysis/programs/kwfc-lat_assoc.csv')

gammaid = input("input gammaid (dirname): ")  #input
#gammaid = 'J2145+1007'
dir = os.path.dirname('/Users/mmorita/kwfc-analysis/analysis/' + gammaid + '/')  # ディレクトリ取得
files = os.listdir(dir) #ファイルリスト取得

#obsid,time,fileの取得
obsids = []
time = []
f = []
for i in range(len(files)):
    obsnumber0, ext = os.path.splitext(files[i])
    time.append(data.query('KWFC_data_number == @obsnumber0')['time(h)'].tolist()[0])
    f.append(pd.read_csv(dir + '/' + files[i]).sort_values('MAG_APER'))
    obsids.append(obsnumber0)
#dataframeとは違い1次元配列なので横(次列)に追加されて行く。

#空のデータフレーム作成
df = pd.DataFrame(index=[], columns=[])

#追加する行をseriesで作成
#############################\Sigma_(i != j) のループ(start)#################
for m in range(len(files)):
    for n in range(len(files)):
        if n == m :
            continue  # 比較するファイルが同じだったら次へ行く
        for i in range(len(f[m])):  # ellipse_iはstr。floatではない
#############################\Sigma_(i != j) のループ(end)#################
            for j in range(len(f[n])):
                diff_ell = abs(f[m]['ELLIPSE'].iat[i] - f[n]['ELLIPSE'].iat[j])
                if diff_ell < 0.001:  # 0.001以下なら追記確定(ではない）

                    if df.empty:  # 空のdfである場合
                        #series = pd.Series([f[m].loc[i,'FLUX_APER':'MAGERR_APER'], time[m], f[n].loc[j,'FLUX_APER':'MAGERR_APER'], time[n]])
                        series = pd.Series([f[m]['ALPHA_J2000'].iat[i], f[m]['DELTA_J2000 '].iat[i], f[m]['ELLIPSE'].iat[i],\
                                            f[m]['FLUX_APER'].iat[i], f[m]['FLUXERR_APER'].iat[i], f[m]['MAG_APER'].iat[i], f[m]['MAGERR_APER'].iat[i], time[m],\
                                            f[n]['FLUX_APER'].iat[j], f[n]['FLUXERR_APER'].iat[j], f[n]['MAG_APER'].iat[j], f[n]['MAGERR_APER'].iat[j], time[n]])
                        df = df.append([series], ignore_index=True)  # 必ずdf.append([], ignore_index=True)
                        break  #dfへの追記が完了したら次のiへ

                    for k in range(len(df)):  # 既存のdf(ellipse)のk行目のELLIPSEと比較 ※最初の1回は例外処理。（上記）
                        diff_ell_df = abs(df[2].iat[k] - f[n]['ELLIPSE'].iat[j])
                        if diff_ell_df < 0.001:  # k行目のもののellipseと一致。重複がなければ最後尾に追加

                            if any(abs(x - time[n]) < 0.01 for x in df.iloc[k]) ==False:  #k行目で時間の重複がない場合

                                for column in range(6,len(df.columns)):  # 列をしらみつぶしていく
                                    if df.isnull()[column].iat[k] == True:  # そのcolumnがNaNならば
                                        df.at[k,column] = f[n]['FLUX_APER'].iat[j]
                                        df.at[k,column + 1] = f[n]['FLUXERR_APER'].iat[j]
                                        df.at[k,column + 2] = f[n]['MAG_APER'].iat[j]
                                        df.at[k,column + 3] = f[n]['MAGERR_APER'].iat[j]
                                        df.at[k,column + 4] = time[n]  #ここ入れても入れなくても同じ？
                                        break  # 次のiへ行くため、3連続breakしたい    ＃＃＃＃＃＃＃＃＃＃＃＃
                                    elif column == len(df.columns) - 1:  # k行目column列目がNaN出ない場合
                                        #print(column, len(df.columns))
                                        #print(df)
                                        df.at[k,column + 1] = f[n]['FLUX_APER'].iat[j]
                                        df.at[k,column + 2] = f[n]['FLUXERR_APER'].iat[j]
                                        df.at[k,column + 3] = f[n]['MAG_APER'].iat[j]
                                        df.at[k,column + 4] = f[n]['MAGERR_APER'].iat[j]
                                        df.at[k,column + 5] = time[n]  #ここは必須
                                        break
                                    else:
                                        continue  #次のcolumnへ
                                break
                            else:  # 時間の重複がある場合
                                break  #次のiへ行くため、連続breakしたい
                        elif k < len(df) - 1:  # k行目のellipseと一致せず、最終行に達しない場合
                            #print(k,len(df))
                            continue
                        else:   # 最終行のellipseと一致しない場合、次の行へ追加(空のdfの時と同じ処理)
                            #series = pd.Series([f[m].loc[i,'FLUX_APER':'MAGERR_APER'], time[m], f[n].loc[j,'FLUX_APER':'MAGERR_APER'], time[n]])
                            series = pd.Series([f[m]['ALPHA_J2000'].iat[i], f[m]['DELTA_J2000 '].iat[i], f[m]['ELLIPSE'].iat[i],\
                                                f[m]['FLUX_APER'].iat[i], f[m]['FLUXERR_APER'].iat[i], f[m]['MAG_APER'].iat[i], f[m]['MAGERR_APER'].iat[i], time[m],\
                                                f[n]['FLUX_APER'].iat[j], f[n]['FLUXERR_APER'].iat[j], f[n]['MAG_APER'].iat[j], f[n]['MAGERR_APER'].iat[j], time[n]])
                            df = df.append([series], ignore_index=True)
                    break  #次のiへ
# グラフ化
for i in range(len(df)):
    fluxlist = []
    fluxerrlist = []
    maglist = []
    magerrlist = []
    timelist = []
    for j in range(len(files)):
        flux_column = (3 + 5 * j)
        fluxerr_column = (4 + 5 * j)
        mag_column = (5 + 5 * j)
        magerr_column = (6 + 5 * j)
        time_column = (7 + 5 * j)
        fluxlist.append(df[flux_column].iat[i])
        fluxerrlist.append(df[fluxerr_column].iat[i])
        maglist.append(df[mag_column].iat[i])
        magerrlist.append(df[magerr_column].iat[i])
        timelist.append(df[time_column].iat[j])
        print(fluxlist)

    #plt.scatter(timelist, maglist, s=40)
    plt.errorbar(timelist, maglist, yerr=magerrlist, fmt='ro', ecolor='g')
    plt.xlabel("observation time(h)")
    plt.ylabel("aperture magnitude")
    plt.grid(True)
    plt.title(str(gammaid) + ': source id = ' + str(i))
    plt.savefig('/Users/mmorita/kwfc-analysis/analysis/' + gammaid + '/lc_' + str(i) + '.png')
    plt.show()
    plt.clf()

    df.to_csv(dir + '/lightcurve.csv')
