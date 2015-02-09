import os
import urllib

import numpy as np

from astropy.io import ascii
from astropy.io import fits

def download_file(url, directory):
    print 'Downloading %s to %s' % (url, directory)
    urllib.urlretrieve(url, '%s/%s' % (directory, url.split('/')[-1]))

def read_survey_catalog(filename='../survey_list.csv'):
    '''
    :param filename: File name
    :return: csv_data: Survey list data
    '''

    Csv = ascii.Csv()
    return Csv.read(filename)

s_data = read_survey_catalog()

def read_vipers(data_dir='../data/VIPERS/'):
    '''
    VIPERS survey

    FLAGs considered here are:
        4 a high-confidence, highly secure redshift, based on a high SNR
          spectrum and supported by obvious and consistent spectral
          features. The confidence level of Flag 4 measurements is estimated
          to be 99% secure.
        3 also a very secure redshift, comparable in confidence with Flag
          4, supported by clear spectral features in the spectrum, but not
          necessarily with high SNR.
        2 a fairly secure, ~90% confidence redshift measurement, supported
          by cross-correlation results, continuum shape and some spectral
          features.

        14 secure AGN with a >95% secure redshift, at least 2 broad lines;
        13 secure AGN with good confidence redshift, based on one broad line
           and some faint additional feature;
        12 a >95% secure redshift measurement, but lines are not
           significantly broad, might not be an AGN;

    :param data_dir:
    :return:
    '''

    survey_name = 'VIPERS'
    survey_columns = {'id': None,'ra': 'alpha', 'dec': 'delta', 'flag': 'zflg', 'redshift': 'zspec', 'redshift_error': None}
    survey_data = s_data[s_data['name'] == survey_name][0].data

    # Read survey files:
    n_good_total = 0
    urls = survey_data['catalog_file'].split(';')
    for url in urls:
        file_name = url.split('/')[-1]
        if not os.path.exists('%s/%s' % (data_dir, file_name)):
            download_file(url, data_dir)
        else:
            print 'Skipping download of %s...' % file_name
        fits_data = fits.open('%s/%s' % (data_dir, file_name))[1].data
        flag_z = np.bitwise_and(fits_data[survey_columns['flag']] >= 2, fits_data[survey_columns['flag']] <= 4)
        flag_z += np.bitwise_and(fits_data[survey_columns['flag']] >= 12, fits_data[survey_columns['flag']] <= 14)
        n_good = flag_z.sum()
        print 'n_z good / total = %i / %i' % (n_good, len(fits_data))
        n_good_total += n_good

    return np.array()



data_dir = '../data/SDSS'

# def read_sdss():
'''

SDSS selection query:


:return:
'''

survey_name = 'SDSS'
survey_columns = {'id': 'BESTOBJID', 'ra': 'PLUG_RA', 'dec': 'PLUG_DEC', 'flag': 'ZWARNING', 'redshift': 'Z', 'redshift_error': 'Z_ERR'}

survey_data = s_data[s_data['name'] == survey_name][0].data
urls = survey_data['catalog_file'].split(';')
for url in urls:
    file_name = url.split('/')[-1]
    if not os.path.exists('%s/%s' % (data_dir, file_name)):
        download_file(url, data_dir)
    else:
        print 'Skipping download of %s...' % file_name
    fits_data = fits.open('%s/%s' % (data_dir, file_name))[1].data
    flag_z = fits_data[survey_columns['flag']] == 0