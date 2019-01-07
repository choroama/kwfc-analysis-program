import pandas as pd
import numpy as np

data = pd.read_csv('/Users/mmorita/kwfc-analysis/analysis/programs/kwfc-lat_assoc.csv')
number = data['KWFC_data_number'].astype(str)

j = 0
for i in number:
    sextractor = pd.read_table('/Users/mmorita/kwfc-analysis/analysis/0' + i + '_3/test1.cat',  skiprows=17, delim_whitespace=True, header=None)
    # 1観測内固定値
    RA_s = sextractor[11]
    dec_s = sextractor[12]
    # 1観測内変化値
    RA_g = data.iloc[j, :]['RA']  # RA columnのj行目
    dec_g = data.iloc[j, :]['Dec']
    a = data.iloc[j, :]['theta1']
    b = data.iloc[j, :]['theta2']
    phi = data.iloc[j, :]['phi']
    cos = np.cos(np.deg2rad(phi))
    sin = np.sin(np.deg2rad(phi))

    ellipse = pow(((RA_s - RA_g) * cos + (dec_s - dec_g) * sin) / a, 2) + pow(((RA_g - RA_s) * sin + (dec_s - dec_g) * cos) / b, 2)
    combine = pd.concat([sextractor, ellipse], axis=1, ignore_index=True)
    # axis=1で横方向連結になる ignore_index=True:列番号振り直し
    combine.columns = ['NUMBER', 'FLUX_APER', 'FLUXERR_APER', 'MAG_APER', 'MAGERR_APER', 'FLUX_AUTO', 'FLUXERR_AUTO', 'MAG_AUTO', 'MAGERR_AUTO', 'X_IMAGE', ' Y_IMAGE', 'ALPHA_J2000', 'DELTA_J2000', 'FLAGS', 'FWHM_IMAGE', 'FWHM_WORLD', 'CLASS_STAR', 'ELLIPSE']
    ellipse_inner = combine[combine['ELLIPSE'] < 1]

    # zeromagをMAG_APER,MAG_AUTOに反映
    df = pd.read_csv('/Users/mmorita/kwfc-analysis/analysis/programs/zeromag.csv', header=None)
    df.columns = ['KWFC_data_number', 'MAG_ZEROPOINT']
    dg = df + np.array([0, -26.5])
    dg.rename(columns={'MAG_ZEROPOINT': 'MAG_TRANSITION'}, inplace=True)
    mag_trans = dg.iloc[j, 1]  # df.dataframe:行列名指定 ilocなど：行列番号指定
    mag_trans_array = [0, 0, 0, mag_trans, 0, 0, 0, mag_trans, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ellipse_inner += mag_trans_array
    ellipse_inner.to_csv('/Users/mmorita/kwfc-analysis/analysis/0' + i + '_3/ellipse_inner.csv')

    j += 1
