import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1.panstarrs検索結果の調整
data = pd.read_csv('/Users/mmorita/kwfc-analysis/analysis/programs/kwfc-lat_assoc.csv')
number = data['KWFC_data_number'].astype(str)

for i in number:
    # i = 52
    a = pd.read_csv('/Users/mmorita/kwfc-analysis/analysis/0' + i + '_3/panstarrs_search.txt', skiprows=1)
    panst = a.query('objName.str.contains("(PSO|no rows found)")', engine='python')
    # なぜかpython engineの宣言。,str.contains('(A|B|...)')でAまたはB...を含む行を抽出
    kwfc = pd.read_csv('/Users/mmorita/kwfc-analysis/analysis/0' + i + '_3/fwhmlimit.csv')
    kwfc_mag = kwfc['3'].astype(float)
    kwfc_magerr = kwfc['4'].astype(float)
    panst_mag = panst['gMeanApMag']
    panst_mask = (panst_mag.mask(panst_mag == '-999')).astype(float)
    panst_mask_r = panst_mask.reset_index(drop=True)
    # .reset_indexで新たなindexを追加。引数dropを指定するとindex上書きになる
    #dm = panst_mask_r - kwfc_mag
    dm = panst_mask_r - kwfc_mag + 26.5 #最終的にここの値補正を削る
    #dmlim = (dm.mask(dm < -0.5).mask(dm > 0.5)).astype(float)
    dmlim = (dm.mask(dm < 26.0).mask(dm > 27.0)).astype(float)
    dm_median = np.nanmedian(dm)
    dmlim_median = np.nanmedian(dmlim)
    dmlim_mean = np.nanmean(dmlim)
    #dmに制限を加える


    plt.scatter(panst_mask_r, dm, s=3)
    plt.hlines(dm_median, 12, 19, "red", linestyles='dashed')
    plt.xlabel("Panstarrsmag(Aper)")
    plt.ylabel("PanStarrsmag(Aper) - kwfcmag(Aper)")
    plt.title(i)
    plt.grid(True)
    #plt.ylim(25.0, 27.0)
    #plt.ylim(-0.5, 0.5)
    plt.savefig('/Users/mmorita/kwfc-analysis/analysis/programs/zeromagpic/zeromag_def' + i + '.png')
    plt.figure() #さもなくばグラフはリセットされない

    plt.scatter(panst_mask_r, dmlim, s=3)
    plt.hlines(dm_median, 12, 19, "red", linestyles='dashed')
    plt.xlabel("Panstarrsmag(Aper)")
    plt.ylabel("PanStarrsmag(Aper) - kwfcmag(Aper)")
    plt.title(i)
    plt.grid(True)
    plt.xlim(12, 19)
    plt.ylim(26.0, 27.0)
    #plt.ylim(-0.5, 0.5)
    plt.savefig('/Users/mmorita/kwfc-analysis/analysis/programs/zeromagpic/zeromag_lim' + i + '.png')
    plt.figure()
    # medianをzeromagに反映し

    #zeromag = 26.5 + dm_median
    #zeromag_lim = 26.5 + dmlim_median
    #zeromag_mean = 26.5 + dmlim_mean
    zeromag = dm_median
    zeromag_lim = dmlim_median
    zeromag_mean = dmlim_mean
    # 対象天体がIDなら対応天体のFWHMも反映しsextractor
    # 対象天体がunIDならreg fileの範囲を参照し、同じFWHMでsextractorをかけてリストをえる。
    # こっからはfile分岐した方がいいか？
    # とりあえず,obsnumberとzeromagを出力して終わる。
    with open("zeromag_lim.csv", 'a') as f:
        print(i, zeromag - zeromag_lim, sep=',', file=f)
