import numpy as np
import lime
from lime.tools import redshift_calculation
from pathlib import Path
from tools.io import nirspec_load_function


files_log_address = Path('/home/usuario/PycharmProjects/lime_online/data/tables/ceers_file_log.txt')
fits_folder = "/home/usuario/PycharmProjects/lime_online/data/spectra"

files_sample = lime.Sample(files_log_address, load_function=nirspec_load_function,
                           levels=['sample', 'id', 'file'], norm_flux=1e-22, fits_folder=fits_folder)

idx_tupples = [('CEERs_DR0.7', '0', 'hlsp_ceers_jwst_nirspec_nirspec5-000000_comb-mgrat_dr0.7_x1d_masked.fits'),
               ('CEERs_DR0.7', '0', 'hlsp_ceers_jwst_nirspec_nirspec5-000000_comb-mgrat_dr0.7_x1d_masked.fits')]
idx_trues = (files_sample.log.MSA == 0) & (files_sample.log.ext == 'x1d') & (files_sample.log.disp == 'comb-mgrat')

files_sample.loc[files_sample[idx_trues].index.values[0], 'redshift']
files_sample.loc[('CEERs_DR0.7', 0, 'hlsp_ceers_jwst_nirspec_nirspec5-000000_comb-mgrat_dr0.7_x1d_masked.fits'), 'redshift']

spec_1 = files_sample.get_spectrum(idx_trues)

# files_sample.log.loc[idx_trues]
for idx in files_sample.log[idx_trues].index:
    print(files_sample[idx_trues].index)
    spec2 = files_sample.get_spectrum(idx)

# files_sample.log.loc[idx_file]
#
# spec = files_sample.get_spectrum(idx_file)
# spec2 = files_sample.get_spectrum(idx_file)

# MPT_list = np.array([64,  3928,  4000,  5409,  9025, 10010, 10293, 29775, 30796, 30796, 31417, 34459])
#
# files_sample, lines_sample = load_databases()
#
# logF = files_sample.log
# logL = lines_sample.log
#
# for MPT in MPT_list:
#     idcsF = logF['MPT'] == MPT & logF['ext'].str.contains('x1d')
#     idcsL = logL['MPT'] == MPT & logL['ext'].str.contains('x1d')
#
#     id_F_list = logF.loc[idcsF].index.get_level_values('id').unique()
#     sample_F_list = logF.loc[idcsF].index.get_level_values('sample').unique()
#     z_list = logF.loc[idcsF]['z_obj'].to_numpy()
#
#     id_L_list = logL.loc[idcsL].index.get_level_values('id').unique()
#     sample_L_list = logL.loc[idcsL, 'sample'].unique()
#
#     print(f'\n{MPT}) {z_list}')
#     print(f'- Reductions (files log): {sample_F_list.to_numpy()}')
#     print(f'- Reductions (lines log): {sample_L_list}')

# sample.extract_fluxes()
# line_ratios = 'H1_6565A/H1_4862A,H1_4341A/H1_4862A'
# line_ratios = line_ratios.split(',')
# ratio_df = sample.compute_line_ratios(line_ratios=line_ratios, keep_empty_columns=False)
# print(ratio_df)

# print(sample.log)
# df_out = pd.DataFrame(columns=['MPT', 'Sample/reduction', 'Pointing', 'Disp', 'n_lines', 'z_centroid', 'z_std'])
# id_arrays = np.unique(sample.log._get_label_or_level_values('id'))
# for id in id_arrays:
#     lines_log = sample.log.loc[id]
#     sample_ref = lines_log['sample'].unique()[0]
#     MPT = lines_log.MPT.unique()[0]
#     point = lines_log.pointing.unique()[0]
#     disp = lines_log.disp.unique()[0]
#     z_mean, z_std = weighted_redshift_calculation(lines_log)
#     n_lines = lines_log.index.size
#     df_out.loc[id, :] = MPT, sample_ref, point, disp, n_lines, z_mean, z_std
#
#
# print(df_out)
# df_out.sort_values(by=['Sample/reduction', 'MPT', 'Disp', 'Pointing'], ascending=[True, True, False, True], inplace=True)
# lime.save_log(df_out, r'D:\Pycharm Projects\lime_online\data\tables\CEERs_redshift_centroid.txt')
#
# # idcs = files_log.disp.isin(['PRISM'])
# # idcs_sample = files_log.index.get_level_values('sample').isin(['reduction_v0.1', 'tier1_v1.1'])
# # idcs_total = idcs & idcs_sample
# #
# # mpt_list = files_log.loc[idcs_total].MPT.unique()
# # idcs_MPT = lines_log.MPT.isin(mpt_list)
# # line_list = np.sort(lines_log.loc[idcs_MPT].index.get_level_values('line').unique())
# # print(line_list)