import pandas as pd
import subprocess

df = pd.read_csv('kwfc-lat_assoc.csv')
dg = df['KWFC_data_number'].astype(str)
for i in dg:
    subprocess.call(['curl', '-O', 'http://www.ioa.s.u-tokyo.ac.jp/~tmorokuma/tmp/clean_0' + i + '_3.fits'])
#/Users/mmorita/kwfc-analysis/analysis/fitsfiles/'
