import pickle
import numpy as np
import pandas as pd
import streamlit as st
import lime

from streamlit import session_state as s_state, secrets
from cryptography.fernet import Fernet
from PIL import Image
from pathlib import Path
from astropy.io import fits

LOCAL_FOLDER = Path(__file__).parent
FITS_PATH = Path(__file__).parent.parent/'data/spectra'

@st.cache_resource
def logo_load(file_address=Path('..format/CEERS_white.png')):
    return Image.open(file_address)


# Function to open nirspec fits files
def load_nirspec_fits(file_address, ext=None):

    file_address = file_address.as_posix() if isinstance(file_address, Path) else file_address

    # Stablish the file type
    if 'x1d' in file_address:
        ext = 1
        spec_type = 'x1d'

    elif 's2d' in file_address:
        ext = 1
        spec_type = 's2d'

    elif 'uncal' in file_address:
        ext = 1
        spec_type = 's2d'

    elif 'cal' in file_address:
        ext = 1
        spec_type = 'cal'

    else:
        print('Spectrum type could not be guessed')

    # Open the fits file
    with fits.open(file_address) as hdu_list:

        if spec_type == 'x1d':
            data_table, header = hdu_list[ext].data, (hdu_list[0].header, hdu_list[ext].header)
            wave_array, flux_array, err_array = data_table['WAVELENGTH'], data_table['FLUX'], data_table['FLUX_ERROR']

        elif spec_type == 'cal':
            wave_array, flux_array, err_array = None, None, None

        elif spec_type == 's2d':
            header = (hdu_list[0].header, hdu_list[1].header)
            wave_array = np.linspace(header[1]['WAVSTART'], header[1]['WAVEND'], header[1]['NAXIS1'], endpoint=True) * 1000000
            err_array = hdu_list[2].data
            flux_array = hdu_list[1].data

    return wave_array, flux_array, err_array, header


def nirspec_load_function(log_df, id_spec, root_address, **kwargs):

    z_obj = log_df.loc[id_spec].redshift.values[0]
    file_spec = Path(root_address)/log_df.loc[id_spec].file_path.values[0]

    # 1d files
    if "x1d" in file_spec.as_posix():
        wave, flux, err, header = load_nirspec_fits(file_spec)
        norm_flux = kwargs['norm_flux']

        z_obj = None if np.isnan(z_obj) else z_obj
        mask = np.isnan(err) & np.isnan(flux)
        objSpec = lime.Spectrum(wave, flux, err, redshift=z_obj, units_wave='um', units_flux='Jy', pixel_mask=mask)
        objSpec.unit_conversion(wave_units_out='Angstrom', flux_units_out='FLAM', norm_flux=norm_flux)
        objSpec.header = header

    # 2d files
    else:
        wave, flux, err, header = load_nirspec_fits(file_spec)
        objSpec = wave, flux, err, header

    return objSpec

@st.cache_resource
def load_databases(database_folder=None):

    # Load the files and fluxes log tables
    if database_folder is None:
        database_folder = LOCAL_FOLDER.parent

    # Generate sample logs and load the data
    files_sample = lime.Sample(database_folder/secrets.data.files_log_path, load_function=nirspec_load_function,
                               folder_obs=database_folder / f'data/spectra',
                               levels=['sample', 'id', 'file'], norm_flux=1e-22)

    lines_sample = lime.Sample(database_folder/secrets.data.fluxes_log_path, load_function=nirspec_load_function,
                               folder_obs=database_folder / f'data/spectra',
                               levels=['sample', 'id', 'file', 'line'], norm_flux=1e-22)

    return files_sample, lines_sample


@st.cache_resource
def arcoiris_link(MPT):

    link = f'http://arcoirix.cab.inta-csic.es/Rainbow_navigator_public/' \
           f'galstamp.php?caller=0&f_database=groth&f_selband=CANDELS_F160W_DR1&f_size=40&' \
           f'nomes=true&undet=true&labels=off&invert=off&justsed=off&noper=0&' \
           f'f_id={MPT}'

    return link




# @st.cache_resource
# def get_obj_spec(fits_address, obs_lines_log=None, norm_flux=1e-20, z_obj=0, header=False):
#
#     wave, e_flux, err, hdr = load_nirspec_fits(fits_address)
#     flux = de_calibrate_func(e_flux)
#     z_obj = 0 if np.isnan(z_obj) else z_obj
#     # mask = np.isnan(err)
#
#     spec = lime.Spectrum(wave, flux, err, redshift=z_obj, units_wave='um', units_flux='Jy')#, pixel_mask=mask)
#     spec.unit_conversion(units_wave='A', units_flux='Flam', norm_flux=norm_flux)
#
#     if obs_lines_log is not None:
#         spec.load_log(obs_lines_log)
#
#     output = spec if header is False else (spec, hdr)
#
#     return output

# def read_appertures(files_log):
#
#     MPT = files_log['MPT'].to_numpy()[0]
#     disp = files_log['disp'].to_numpy()[0]
#     point = files_log['pointing'].to_numpy()[0]
#
#     disp_check = disp == 'PRISM'
#     label_disp = 'prism' if disp_check else 'Mgrat'
#     pkl_path = LOCAL_FOLDER.parent/f'data'/f'appertures'/f'{point.capitalize()}_{label_disp}_custaper.pkl'
#
#     lims = None
#     if pkl_path.is_file():
#
#         apper_df = decrypt_file(pkl_path)
#
#         if MPT in apper_df.index:
#
#             if disp_check:
#                 lims = apper_df.loc[MPT, 'px1':'px2'].to_numpy()
#             else:
#                 lims = apper_df.loc[MPT, f'px1_{disp}':f'px2_{disp}'].to_numpy()
#
#     return lims

# def load_nirspec_fits(file_address, ext=None):
#
#     file_address = file_address.as_posix() if isinstance(file_address, Path) else file_address
#
#     # Stablish the file type
#     if 'x1d' in file_address:
#         ext = 1
#         spec_type = 'x1d'
#
#     elif 's2d' in file_address:
#         ext = 1
#         spec_type = 's2d'
#
#     elif 'uncal' in file_address:
#         ext = 1
#         spec_type = 's2d'
#
#     elif 'cal' in file_address:
#         ext = 1
#         spec_type = 'cal'
#
#     else:
#         print('Spectrum type could not be guessed')
#
#     # Open the fits file
#     with fits.open(file_address) as hdu_list:
#
#         if spec_type == 'x1d':
#             data_table, header = hdu_list[ext].data, (hdu_list[0].header, hdu_list[ext].header)
#             wave_array, flux_array, err_array = data_table['WAVELENGTH'], data_table['FLUX'], data_table['FLUX_ERROR']
#
#         elif spec_type == 'cal':
#             wave_array, flux_array, err_array = None, None, None
#
#         elif spec_type == 's2d':
#             header = (hdu_list[0].header, hdu_list[1].header)
#             wave_array = np.linspace(header[1]['WAVSTART'], header[1]['WAVEND'], header[1]['NAXIS1'], endpoint=True) * 1000000
#             err_array = hdu_list[2].data
#             flux_array = hdu_list[1].data
#
#     return wave_array, flux_array, err_array, header
#
#
# def calibrate_func(data_array, factor=secrets.calibration.factor, k1=secrets.calibration.k1, k2=secrets.calibration.k2,
#                    k3=secrets.calibration.k3, k4=secrets.calibration.k4, norm=secrets.calibration.norm):
#
#     # 2D data
#     if len(data_array.shape) > 1:
#         data_array = data_array/norm
#         calib_data = (data_array/np.exp(factor)) + (k1 + k2 * factor + k3 * factor*factor) * np.arange(data_array.shape[1])/factor**k4
#
#     # 1d Data
#     else:
#         calib_data = (data_array/(np.exp(factor))) + (k1 + k2 * factor + k3 * factor*factor) * np.arange(data_array.size)/factor**k4
#
#     return calib_data
#
#
# def de_calibrate_func(data_array, factor=secrets.calibration.factor, k1=secrets.calibration.k1, k2=secrets.calibration.k2,
#                       k3=secrets.calibration.k3, k4=secrets.calibration.k4, norm=secrets.calibration.norm):
#
#     # 2D data
#     if len(data_array.shape) > 1:
#         calib_data = ((data_array) - (k1 + k2 * factor + k3 * factor*factor) * np.arange(data_array.shape[1])/factor**k4) * np.exp(factor)
#         calib_data = calib_data * norm
#
#     # 1d Data
#     else:
#         calib_data = (data_array - (k1 + k2 * factor + k3 * factor*factor) * np.arange(data_array.size)/factor**k4) * np.exp(factor)
#
#     return calib_data
#
#
# def encrypt_file(filepath, variable, key=secrets.calibration.key):
#
#     #Save variable to pickle file
#     with open(filepath, "wb") as outfile:
#         pickle.dump(variable, outfile)
#
#     f = Fernet(key)
#     with open(filepath, "rb") as file:
#         file_data = file.read()
#
#     encrypted_data = f.encrypt(file_data)
#     with open(filepath, "wb") as file:
#         file.write(encrypted_data)
#
#     return
#
#
def decrypt_file(pickle_file, key=st.secrets.calibration.key):

    f = Fernet(key)
    with open(pickle_file, "rb") as file:
        encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        data = pickle.loads(decrypted_data)

    return data


def hdr_to_df(header):

    key_list = list(header.keys())
    comments_list = header.comments

    df = pd.DataFrame(index=key_list, columns=['Value', 'Comment']).fillna('')
    for idx in df.index:
        df.loc[idx, 'Value'] = header.get(idx, '')
        df.loc[idx, 'Comment'] = comments_list[idx]

    return df
