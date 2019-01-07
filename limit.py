from astropy.io import fits
import numpy as np
import math
import pandas as pd
import subprocess
import os

snlimit = 5  # 検出限界とするS/N比
t = 120  # 積分時間
sigma = 15  # 読み出し雑音
gain = 2.3  # e-/EDU(=count)
df = pd.read_csv('kwfc-lat_assoc.csv')
dg = df['KWFC_data_number'].astype(str)

for i in dg:
    # 最初のsextractor実行(sextractor.shを包含)
    # subprocess.call(['cd', '/Users/mmorita/kwfc-analysis/analysis/0' + i + '_3/'])  #subprocessだとcdできてない
    os.chdir('/Users/mmorita/kwfc-analysis/analysis/0' + i + '_3/')
    # subprocess.call(['sex', '/Users/mmorita/kwfc-analysis/analysis/fitsfiles/clean_0'+ i +'_3.fits'])

    # skyの取得
    a = fits.open('/Users/mmorita/kwfc-analysis/analysis/fitsfiles/clean_0' + i + '_3.fits')
    sky = (a[0].header["BGAVETOP"] + a[0].header["BGAVEBTM"]) / 2
    # FWHMの取得
    b = pd.read_table('/Users/mmorita/kwfc-analysis/analysis/0' + i + '_3/test.cat', skiprows=17, delim_whitespace=True, header=None)
    FWHM = b[14].astype(float)
    FLUX = b[1].astype(float)
    # SNの計算
    sn = (FLUX * np.sqrt(2 * gain) / np.sqrt(FLUX + np.pi * pow(FWHM / 2, 2) * sky)).astype(float)
    # SN結合・抽出
    combine = pd.concat([b, sn], axis=1, ignore_index=True)  # axis=1で横方向連結、なければ縦
    row = len(combine.columns) - 1  # 最後列にsnを追加したのでその列数を抽出
    sn5 = combine[(combine[row] > 5) & (combine[13] == 0)]  # SN>5 with no Flag

    fwhmlimit = sn5[(sn5[14] > 4) & (sn5[14] < 6)]
    FWHM_median = str(np.median(fwhmlimit[14]))
    aper = str(2 * np.median(fwhmlimit[14]))
    subprocess.call(['sex', '/Users/mmorita/kwfc-analysis/analysis/fitsfiles/clean_0' + i + '_3.fits', '-SEEING_FWHM=' + FWHM_median, '-PHOT_APERTURES=' + aper, '-CATALOG_NAME=test1.cat'])

    # 度制限を加える
    b = pd.read_table('/Users/mmorita/kwfc-analysis/analysis/0' + i + '_3/test1.cat', skiprows=17, delim_whitespace=True, header=None)
    FWHM = b[14].astype(float)
    FLUX = b[1].astype(float)
    # SNの計算
    sn = (FLUX * np.sqrt(2 * gain) / np.sqrt(FLUX + np.pi * pow(FWHM / 2, 2) * sky)).astype(float)
    snlimitmag = -2.5 * math.log10(snlimit / (4 * gain) * (snlimit + np.sqrt(pow(snlimit, 2) + 2 * gain * sky * np.pi * pow(float(FWHM_median), 2)))) + 26.5
    with open("/Users/mmorita/kwfc-analysis/analysis/programs/snlimitmag.txt", 'a') as f:
        print(snlimitmag, a[0].header["SN5mag"], file=f)  # 手計算snlimitmagとsn5magを比較
    # FWHMに制限を加え、抽出
    # SN結合・抽出
    combine = pd.concat([b, sn], axis=1, ignore_index=True)  # axis=1で横方向連結、なければ縦
    row = len(combine.columns) - 1  # 最後列にsnを追加したのでその列数を抽出
    sn5 = combine[(combine[row] > 5) & (combine[13] == 0)]  # SN>5 with no Flag
    fwhmlimit = sn5[(sn5[14] > 4) & (sn5[14] < 6)]
    fwhmlimit_radec = fwhmlimit.iloc[:, [11, 12]]  # 2行目以降、11,2列目
    fwhmlimit.to_csv("fwhmlimit.csv", sep=',')
    fwhmlimit_radec.to_csv("fwhmlimit_radec.csv", sep=',', header=False, index=False)
    # FWHM = str(np.median(fwhmlimit[14]))
    # aper = str(2 * np.median(fwhmlimit[14]))
    # subprocess.call(['sex', '/Users/mmorita/kwfc-analysis/analysis/fitsfiles/clean_0'+ i +'_3.fits',  '-SEEING_FWHM=' + FWHM, '-PHOT_APERTURES=' + aper, '-CATALOG_NAME=test1.cat'])
