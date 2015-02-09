import os
import urllib
from astropy.coordinates import SkyCoord
from astropy import units as u

import numpy as np

from astropy.io import ascii
from astropy.io import fits


database_dtype = np.dtype([('id', np.int), ('ra', np.float), ('dec', np.float), ('flag', np.int),
                           ('redshift', np.float), ('redshift_error', np.float), ('magnitude', np.float)])


def download_file(url, directory):
    file_name = url.split('/')[-1]
    if not os.path.exists('%s/%s' % (directory, file_name)):
    print 'Downloading %s to %s' % (url, directory)
    urllib.urlretrieve(url, '%s/%s' % (directory, url.split('/')[-1]))
    else:
        print 'Skipping download of %s...' % file_name


def read_survey_catalog(filename='../survey_list.csv'):
    '''
    :param filename: File name
    :return: csv_data: Survey list data
    '''

    Csv = ascii.Csv()
    return Csv.read(filename)


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


def read_2dfgrs(data_dir='../data/2dFGRS/'):
    survey_name = '2dFGRS'
    survey_columns = {'id': 'serial', 'ra': 'ra2000', 'dec': 'dec2000', 'flag': 'quality', 'redshift': 'z',
                      'redshift_error': None, 'magnitude': 'BJG'}
    survey_data = s_data[s_data['name'] == survey_name][0].data

    download_file(survey_data['catalog_file'], data_dir)
    file_name = survey_data['catalog_file'].split('/')[-1]

    dt = [('serial', np.int)]
    dt.extend((('ra2000_%i' % i, np.float) for i in range(3)))
    dt.extend((('dec2000_%i' % i, np.float) for i in range(3)))
    dt.extend(((key, np.float)) for key in ('BJG', 'z', 'quality'))
    data = np.loadtxt('%s/%s' % (data_dir, file_name), dtype=dt, usecols=(0, 10, 11, 12, 13, 14, 15, 16, 23, 26))
    flag_z = data[survey_columns['flag']] >= 3
    data = data[flag_z]

    out = np.empty(len(data), dtype=database_dtype)

    for key in survey_columns.keys():
        if survey_columns[key] is None:
            out[key] = np.nan
        elif key not in ('ra', 'dec'):
            out[key] = data[survey_columns[key]]
    for i in range(len(data)):
        out['ra'][i], out['dec'][i] = \
            [float(n) for n in SkyCoord('%02i %02i %3.2f  %02i %02i %3.2f' % (data['ra2000_0'][i], data['ra2000_1'][i],
                                                                              data['ra2000_2'][i], data['dec2000_0'][i],
                                                                              data['dec2000_1'][i], data['dec2000_2'][i]),
                                        unit=(u.hourangle, u.deg)).to_string().split(' ')]

    return out

# def read_sdss():
'''




if __name__ == '__main__':
    s_data = read_survey_catalog()
    # data_dir = '../data/'
    kk = read_2dfgrs

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