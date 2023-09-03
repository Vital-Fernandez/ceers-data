import numpy as np
from pathlib import Path

import pandas as pd
import lime
# from tools.io import encrypt_file, decrypt_file
# from lime.transitions import log_from_line_list

SAMPLE_EXTENSIONS = {'SMACS_v2.0': ['s2d.fits', 'x1d_masked_bpx.fits'],
                     'reduction_v0.1': ['x1d.fits', 's2d.fits'],
                     'reduction_v0.3': ['x1d', 's2d'],
                     'tier1_v1.1': ['x1d.fits', 's2d.fits'],
                     'CEERS_tier1_targets_v1.3': ['x1d', 's2d'],
                     'CEERS_P11-P12_tier1_targets_v1.1_comb': ['x1d', 's2d']}


def file_loop_structure(sample, parent_dir, extension_dict=SAMPLE_EXTENSIONS):

    file_list = []
    ext_list = extension_dict[sample]

    if sample == 'SMACS_v2.0':
        for disp in ['G235M', 'G395M']:
            for pointing in ['Visit_1', 'Visit_2']:
                folder_path = parent_dir / disp / pointing
                obj_dir_list = list(folder_path.iterdir())
                for objDir in obj_dir_list:
                    for ext in ext_list:
                        file_list += list(objDir.glob(f'*{ext}'))

    elif sample in ['reduction_v0.1', 'tier1_v1.1']:
        for ext in ext_list:
            file_list += list(parent_dir.glob(f'*{ext}'))

    elif sample in ['CEERS_P11-P12_tier1_targets_v1.1_comb']:
        pointing_folders = list(parent_dir.iterdir())
        for point_folder in pointing_folders:
            if point_folder.is_dir():
                dispenser_folders = list(point_folder.iterdir())
                for disp_folder in dispenser_folders:
                    if disp_folder.is_dir():
                        obj_folders = list(disp_folder.iterdir())
                        for obj_folder in obj_folders:
                            if obj_folder.is_dir():
                                for ext in ext_list:
                                    if ('CEERS_p12' in obj_folder.as_posix()) and (ext == 'x1d'):
                                        file_list += list(obj_folder.glob(f'*{ext}.fits'))
                                    else:
                                        file_list += list(obj_folder.glob(f'*{ext}*'))

    elif sample in ['reduction_v0.3']:
        pointing_folders = list(parent_dir.glob(f'*S3_*'))
        for point_folder in pointing_folders:
            if point_folder.is_dir():
                disp_folder_list = list(point_folder.iterdir())
                for disp in disp_folder_list:
                    disp_folder = point_folder / disp
                    if disp_folder.is_dir():
                        obj_list = list(disp_folder.iterdir())
                        for obj in obj_list:
                            obj_folder = disp_folder / obj
                            if obj_folder.is_dir():
                                for ext in ext_list:
                                    file_list += list(obj_folder.glob(f'*{ext}.fits'))

    elif sample in ['CEERS_tier1_targets_v1.3']:
        pointing_folders = list(parent_dir.iterdir())
        for point_folder in pointing_folders:
            if point_folder.is_dir():
                disp_folder_list = list(point_folder.iterdir())
                for disp_folder in disp_folder_list:
                    if disp_folder.is_dir():
                        obj_list = list(disp_folder.iterdir())
                        for obj_folder in obj_list:
                            if obj_folder.is_dir():
                                for ext in ext_list:
                                    file_list += list(obj_folder.glob(f'*{ext}.fits'))

    else:
        print(f'WARNING: sample not recognize')
        raise

    return file_list


def infer_obs_id(sample, file_path):

    id = file_path.stem
    file_folder = file_path.parent.as_posix()
    rel_path = Path(*file_path.parts[5:]).as_posix()

    if sample == 'SMACS_v2.0':
        if 'x1d_masked_bpx' in id:
            disp, point_a, point_b, _MPT, ext0, ext1, ext2 = id.split('_')
            ext = f'{ext0}_{ext1}_{ext2}'
        else:
            disp, point_a, point_b, _MPT, ext = id.split('_')
        point = point_a + point_b
        MPT = file_path.parent.name

    elif sample in ['reduction_v0.1', 'tier1_v1.1']:
        point, disp, MPT, _MPT, ext = id.split('_')

    elif sample in ['CEERS_P11-P12_tier1_targets_v1.1_comb']:
        if 'CEERS_p11' in file_folder:
            point = 'p11'
            disp = 'PRISM'
            ext = 'x1d' if 'x1d'in file_folder else 's2d'
            _MPT = id[0:id.find('_')]
            MPT = str(int(_MPT))
        else:
            point, disp, MPT, _MPT, ext = id.split('_')

    elif sample in ['reduction_v0.3']:
        point, disp, MPT, _MPT, ext = id.split('_')

    elif sample in ['CEERS_tier1_targets_v1.3']:
        point, disp, MPT, _MPT, ext = id.split('_')

    else:
        print(f'WARNING: sample not recognize')
        raise

    return id, MPT, disp, point, _MPT, ext, rel_path


def infer_flux_id(sample, file_path):

    id = file_path.stem
    id = id[0:id.find('_fluxes')]
    log_parent = file_path.parent.as_posix()
    rel_path = Path(*file_path.parts[5:]).as_posix()

    if sample == 'SMACS_v2.0':
        if 'x1d_masked_bpx' in id:
            disp, point_a, point_b, _MPT, ext0, ext1, ext2 = id.split('_')
            ext = f'{ext0}_{ext1}_{ext2}'
        else:
            disp, point_a, point_b, _MPT, ext = id.split('_')
        point = point_a + point_b
        MPT = file_path.parent.name

    elif sample in ['reduction_v0.1', 'tier1_v1.1']:
        point, disp, MPT, _MPT, ext = id.split('_')

    elif sample in ['CEERS_P11-P12_tier1_targets_v1.1_comb']:
        if 'p12' in id:
            point, disp, MPT, _MPT, ext = id.split('_')

        else:
            point = 'p11'
            disp = 'PRISM'
            ext = 'x1d' if 'x1d'in log_parent else 's2d'
            _MPT = id[0:id.find('_')]
            MPT = str(int(_MPT))

    elif sample in ['reduction_v0.3']:
        point, disp, MPT, _MPT, ext = id.split('_')

    elif sample in ['CEERS_tier1_targets_v1.3']:
        point, disp, MPT, _MPT, ext = id.split('_')


    return id, MPT, disp, point, _MPT, ext, rel_path


def generate_files_log(samples_list=None, spectra_folder=None):

    # Use the default spectra location to get the available samples and directories
    if (samples_list is None) and (spectra_folder is None):
        spectra_folder = Path(__file__).parent.parent/f'data/spectra'
        dir_list = list(spectra_folder.iterdir())
        samples_list = [x.name for x in dir_list]
    else:
        samples_list = np.array([samples_list], ndmin=1)
        spectra_folder = Path(spectra_folder)

    #Dictionary to store the files per sample
    files_dict = {}

    # Loop througth the samples tree structure
    for sample in samples_list:
        file_list = file_loop_structure(sample, spectra_folder/sample)
        files_dict[sample] = file_list

    # Convert the list of files into a multi-index dataframe
    log_dict = {}
    columns = ['MPT', 'disp', 'pointing', '_MPT', 'ext', 'path']
    for sample, file_list in files_dict.items():
        sublog = pd.DataFrame(columns=columns)
        for file in file_list:
            id, MPT, disp, point, _MPT, ext, path = infer_obs_id(sample, file)
            sublog.loc[id] = MPT, disp, point, _MPT, ext, path
        log_dict[sample] = sublog

    # Combine into one
    obj_list, obs_list = list(log_dict.keys()), list(log_dict.values())
    sample = lime.Sample(obj_list, log_list=obs_list, level_names=['sample', 'id'])

    return sample


def generate_lines_log(samples_list=None, fluxes_folder=None):

    # Use the default spectra location to get the available samples and directories
    if (samples_list is None) and (fluxes_folder is None):
        spectra_folder = Path(__file__).parent.parent/f'data/flux_logs'
        dir_list = list(spectra_folder.iterdir())
        samples_list = [x.name for x in dir_list]
    else:
        samples_list = np.array([samples_list], ndmin=1)
        spectra_folder = Path(fluxes_folder)

    #Dictionary to store the files per sample
    files_dict = {}

    # Loop througth the samples tree structure
    for sample in samples_list:
        file_list = list((spectra_folder/sample).glob('*.pkl'))
        files_dict[sample] = file_list

    for sampleN, files_list2 in files_dict.items():
        print(sampleN, len(files_list2))
        for fileID in files_list2:
            print(fileID.name, f'{sample}')
        print()

    # Convert the list of files into a multi-index dataframe
    # log_dict = {}
    list_ids, lits_logs = [], []
    for sample, file_list in files_dict.items():
        for file in file_list:
            if sample != 'SMACS_v2.0':
                id, MPT, disp, point, _MPT, ext, path = infer_flux_id(sample, file)
                log = decrypt_file(file)
                log.insert(loc=0, column='sample', value=sample)
                log.insert(loc=1, column='MPT', value=MPT)
                log.insert(loc=2, column='disp', value=disp)
                log.insert(loc=3, column='pointing', value=point)
                log.insert(loc=4, column='_MPT', value=_MPT)
                log.insert(loc=5, column='ext', value=ext)
                list_ids.append(id)
                lits_logs.append(log)

                # log_dict[id] = log

    # Combine into one
    # obj_list, log_list = list(log_dict.keys()), list(log_dict.values())
    sample_log = lime.join_logs(list_ids, lits_logs, level_list=['id', 'sample', 'line'])
    sample_log = sample_log.reorder_levels(['sample', 'id', 'line'])

    sample = lime.Sample()
    sample.load_log(sample_log)

    return sample


def clean_up_log(lines_log, comps_dict={}):

    for line_m in ['H1_6565A_m']:
        log_comps = log_from_line_list(line_m[:-2], comps_dict=comps_dict)
        idcs = lines_log.index.get_level_values('line') == line_m
        lines_log.loc[idcs, 'profile_label'] = 'no'
        lines_log.loc[idcs, 'latex_label'] = log_comps.loc[line_m[:-2]].latex_label
        lines_log.rename(index={line_m: line_m[:-2]}, level=1, inplace=True)

    for line_s in ['O2_3727A']:
        log_comps = log_from_line_list(f'{line_s}_m', comps_dict=comps_dict)
        idcs = lines_log.index.get_level_values('line') == line_s
        lines_log.loc[idcs, 'profile_label'] = log_comps.loc[f'{line_s}_m'].profile_label
        lines_log.loc[idcs, 'latex_label'] = log_comps.loc[f'{line_s}_m'].latex_label
        lines_log.rename(index={line_s: f'{line_s}_m'}, level=1, inplace=True)

        # lines_log.xs('O2_3727A_m', level='line', drop_level=False)

    return


def prepare_smacs_files(output_folder):

    smacs_flux_log_folder = Path('/home/usuario/Dropbox/Astrophysics/Data/CEERs/SMACS_v8/fluxes')
    smacs_file_log_file = output_folder/f'smacs_file_log.txt'
    smacs_flux_log_file = output_folder/f'smacs_flux_log.txt'

    # SMACS files Clean up
    SMACS_v2_redshift_path = Path(r'/home/usuario/Dropbox/Astrophysics/Data/NIRSpec_SMACS_sample/data/SMACS_NIRSpec_redshift_table_v8.txt')
    smacs_v2_df = lime.load_log(SMACS_v2_redshift_path)
    smacs_v2_df['path'] = smacs_v2_df['path'].str.replace('/mnt/AstroData/Observations/SMACS_Nirspec_v6/S3_out_clean_custom_pl/', '/SMACS/')
    smacs_v2_df['path'] = smacs_v2_df['path'].str.replace('_x1d_fluxcal_masked_bpx.fits', '_x1d_masked_bpx.fits')

    rename_columns = {'SOURCEID': 'MPT', 'SRCNAME': 'alias', 'path': 'file', 'visit': 'pointing'}
    smacs_v2_df.rename(columns=rename_columns, inplace=True)
    smacs_v2_df.index.rename('id', inplace=True)
    smacs_v2_df['sample'] = 'SMACS'
    smacs_v2_df['ext'] = 'x1d'

    smacs_v2_df['id'] = smacs_v2_df.index.to_numpy()
    smacs_v2_df.set_index(['sample', 'id', 'file'], inplace=True)
    smacs_v2_df = smacs_v2_df[['MPT', 'disp', 'pointing', 'ext', 'redshift', 'alias']]

    # Add s2d files:
    s3d_folder = Path('/home/usuario/AstroData/SMACS_Nirspec_v8/S3_out_clean_custom_pl_v2.0/')
    df_copy = smacs_v2_df.copy()
    for idx in df_copy.index:
        _sample, id_1d, file_1d = idx
        file_2d_root = Path(f"{s3d_folder}{Path(file_1d).parent}")
        file_2d_list = list(file_2d_root.glob('*s2d.fits'))
        print('\n1d: ', Path(f"{s3d_folder}{Path(file_1d)}"), Path(f"{s3d_folder}{Path(file_1d)}").is_file())
        assert len(file_2d_list) == 1
        print('2d: ', file_2d_list[0].as_posix(), file_2d_list[0].is_file())
        data = df_copy.loc[idx]
        data['ext'] = 's2d'
        smacs_v2_df.loc[('SMACS', id_1d, file_2d_list[0].as_posix().replace(s3d_folder.as_posix(), ''))] = data

    lime.save_log(smacs_v2_df, smacs_file_log_file)

    # SMACS fluxes log
    smacs_file_df = lime.load_log(smacs_file_log_file, sample_levels=['sample', 'id', 'file'])

    idcs_x1d = smacs_file_df.ext == 'x1d'
    id_sorted_list = smacs_file_df.loc[idcs_x1d].index.get_level_values('id').to_numpy()

    log_list = []
    for id in id_sorted_list:
        log_address = smacs_flux_log_folder/f'{id}_log.txt'
        if log_address.is_file():
            log_list.append(log_address)

    file_list, id_list = [], []
    for i, log_address in enumerate(log_list):
        id_label = log_address.name[:log_address.name.find('_log.txt')]
        sub_df = smacs_file_df.loc[('SMACS', id_label)]
        file_address = sub_df.loc[sub_df.index.str.contains('x1d')].index

        assert len(file_address) == 1
        file_list.append(file_address[0])
        id_list.append(id_label)

    smacs_fluxes = lime.Sample.from_file_list(id_list=id_list, log_list=log_list, file_list=file_list)
    smacs_fluxes.log['id'] = smacs_fluxes.log.index.get_level_values('id')
    smacs_fluxes.log['file'] = smacs_fluxes.log.index.get_level_values('file')
    smacs_fluxes.log['line'] = smacs_fluxes.log.index.get_level_values('line')
    smacs_fluxes.log['sample'] = 'SMACS'
    smacs_fluxes.log.set_index(['sample', 'id', 'file', 'line'], inplace=True)

    smacs_fluxes.save_log(smacs_flux_log_file)

    return


if __name__ == "__main__":

    tables_folder = Path('/home/usuario/PycharmProjects/lime_online/data/tables')

    # SMACS field
    prepare_smacs_files(tables_folder/'samples')

    # # CEERs field
    # ceers_sample_df_file = Path(f'/home/usuario/Dropbox/Astrophysics/Data/CEERs/ceers_sample.txt')
    # ceers_df = lime.load_log(ceers_sample_df_file)



    # SMACS_v2_log = files_sample.log.xs('SMACS_v2.0', level='sample')
    #
    # for MPT in SMACS_v2_redshift_df.SOURCEID.unique():
    #     MPT_str = str(MPT)
    #     idcs = SMACS_v2_redshift_df.SOURCEID == MPT
    #     redshift = np.median(SMACS_v2_redshift_df.loc[idcs, 'redshift'])
    #     idcs_files = SMACS_v2_log.MPT == MPT_str
    #     SMACS_v2_log.loc[idcs_files, 'z_obj'] = redshift



    # # Log with the each sample file
    # files_sample = generate_files_log()
    # lines_sample = generate_lines_log()

    # # Add redshift values
    # files_sample.log['z_obj'] = np.nan
    #
    # # CEERs 12/2022
    # samples_online = ['reduction_v0.1', 'tier1_v1.1', 'CEERS_P11-P12_tier1_targets_v1.1_comb',
    #                   'reduction_v0.3', 'CEERS_tier1_targets_v1.3']
    #
    # for sample_label in samples_online:
    #     sample_slice_log = files_sample.log.xs(sample_label, level='sample')
    #     for idx_obs in sample_slice_log.index:
    #         MPT_label = sample_slice_log.loc[idx_obs, 'MPT']
    #         MPT_int = int(MPT_label)
    #         if MPT_int in ceers_df.index:
    #             z_obj = ceers_df.loc[MPT_int, 'z_obj']
    #             z_obj = np.nan if z_obj == 0 else z_obj
    #             sample_slice_log.loc[idx_obs, 'z_obj'] = z_obj
    #
    # # Logs clean up
    # clean_up_log(lines_sample.log, comps_dict={'O2_3727A_m': 'O2_3727A-O2_3729A'})

    # # Save the logs
    # files_sample.save_log(Path(__file__).parent.parent/f'data/tables/file_log.txt')
    # lines_sample.save_log(Path(__file__).parent.parent/f'data/tables/fluxes_log.txt')
