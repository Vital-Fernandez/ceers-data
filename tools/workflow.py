import numpy as np
import streamlit as st
from streamlit import session_state as s_state, secrets
from pathlib import Path
from tools.io import decrypt_file
import streamlit_authenticator as stauth


DEFAULTS = {'disp':         'G235M',
            'flux_check':   False,
            'SOURCEID':     'All',
            'LINEID':       'Any',
            'MPT_ID':       'All',
            'LINERATIOS':   '',
            'LINES_Z':      '',
            'Z_WEIGHT':     'None',
            'FLUXTYPE':     'mixture',
            'OBJLIST':      None,
            'FITS_1D':      None,
            'FITS_2D':      None,
            'NUMLINE':      'None',
            'DENOLINE':     'None',
            'MPTUSERLIT':   '',
            'sample_list':  ['CEERs_DR0.7'],
            'disp_list':    ['comb-mgrat', 'g140m', 'g235m', 'g395m', 'prism'],
            'point_list':   ['nirspec4', 'nirspec5', 'nirspec7', 'nirspec8', 'nirspec9', 'nirspec10', 'nirspec11', 'nirspec12']}


def user_logging(check_user=False):

    if check_user:
        user_file = Path(__file__).parent / 'users_hashed.pkl'
        CREDENTIALS = decrypt_file(user_file)
        authenticator = stauth.Authenticate(CREDENTIALS, 'CEERs_LIME', 'aBcDeF', cookie_expiry_days=60)

        name, auth_status, username = authenticator.login(f'CEERs measurements', 'main')
        s_state['auth_status'] = auth_status
        s_state['auth_status_hold'] = s_state['auth_status']
        s_state['user'] = name

    else:
        s_state['auth_status'] = True
        s_state['auth_status_hold'] = True
        s_state['user'] = None

    return


def check_logging():

    if 'auth_status' not in s_state:
        if 'auth_status_hold' in s_state:
            s_state['auth_status'] = s_state['auth_status_hold']
        else:
            s_state['auth_status'] = False

    return

def tabs_object_selection(log, group_indeces, just_objects=False, key_ID = 'MPT'):

    # Sub-grouping to plot the spectra
    objCol, sampleCol, dispCol, pointCol = st.columns(4)

    # pre-Selection doest not have objects
    if group_indeces is None:
        st.markdown(f'The current sample selection does not contain objects. Please change the observation parameters.')
        idcs_out = None

    # 2nd widget selection
    else:

        with objCol:
            objList = np.sort(log.loc[group_indeces].MSA.unique())
            objSelect = st.selectbox('MSA', objList, key=key_ID)

        # If we want to select everything
        if not just_objects:

            with sampleCol:
                idcs_subGroup = group_indeces & (log.MSA == objSelect)
                sampleList = np.sort(log.loc[idcs_subGroup].index.get_level_values('sample').unique())
                sampleSelect = st.selectbox('Sample', sampleList)

            with dispCol:
                idcs_subGroup = group_indeces & (log.MSA == objSelect) & (
                            log.index.get_level_values('sample') == sampleSelect)
                dispList = np.sort(log.loc[idcs_subGroup].disp.unique())
                dispSelect = st.selectbox('Dispenser', dispList)

            with pointCol:
                idcs_subGroup = group_indeces & (log.MSA == objSelect) & (
                            log.index.get_level_values('sample') == sampleSelect) & \
                                (log.disp == dispSelect)
                pointList = np.sort(log.loc[idcs_subGroup].pointing.unique())
                pointSelect = st.selectbox('Pointing', pointList)

            # One object selection
            idcs_out = group_indeces & (log.MSA == objSelect) \
                       & (log.index.get_level_values('sample') == sampleSelect) \
                       & (log.disp == dispSelect) \
                       & (log.pointing == pointSelect)

        else:
            idcs_out = group_indeces & (log.MSA == objSelect)

    return idcs_out


def user_MPT_to_numpy(str_list):
    output = str_list.replace('\n', '')
    output = output.replace(' ', '')
    output = np.array(output.split(',')).astype(int)

    return output


def save_objSample(param):
    s_state[f'{param}_hold'] = s_state[f'{param}']

    return


def observation_indexing(log):
    sample_list, disp_list, point_list = s_state['sample_list'], s_state['disp_list'], s_state['point_list']
    flux_check, r_range = s_state['flux_check'], s_state['z_range']

    # Make sure the observation properties are not empty
    security_check = True
    for input_list in [sample_list, disp_list, point_list]:
        if len(input_list) == 0:
            security_check = False

    # Good selection
    if security_check:

        idcs_obs = log.index.get_level_values('sample').isin(sample_list) & \
                   log['disp'].isin(disp_list) & \
                   log['pointing'].isin(point_list)

        if flux_check:
            idcs_z = (log['redshift'] >= r_range[0]) & (log['redshift'] <= r_range[1])
            idcs_obs = idcs_obs & idcs_z

    # Bad selection
    else:
        st.warning('Please make sure that the check lists above have at least one selection criterion')
        idcs_obs = None

    return idcs_obs


def observation_properties_filtering(log):

    st.markdown(f'# Observation properites')

    tab1, tab2, tab3, tab4 = st.tabs(['Sample', 'Dispenser', 'Pointing', 'Redshift'])

    with tab1:
        default_samples = log.index.get_level_values('sample').unique().to_numpy()
        st.multiselect('Sample selection:', options=default_samples, key='sample_list', on_change=save_objSample,
                       args=("sample_list",))

    with tab2:
        idcs_obs = log.disp.isin([s_state['sample_list']]).index
        default_disp = log.loc[idcs_obs, 'disp'].unique()
        st.multiselect('Dispenser selection:', options=default_disp, key='disp_list', on_change=save_objSample,
                       args=("disp_list",))

    with tab3:
        idcs_obs = log.disp.isin([s_state['sample_list']]).index
        default_pointings = log.loc[idcs_obs, 'pointing'].unique()
        st.multiselect('Pointing selection:', options=default_pointings, key='point_list', on_change=save_objSample,
                       args=("point_list",))

    with tab4:
        warn_text = 'This check constrains the selection to those objects with a positive emission line detection.'
        st.checkbox(label="Redshift measurement", key="flux_check", help=warn_text, on_change=save_objSample,
                    args=("flux_check",))

        z_range = (float(log['redshift'].min()), float(log['redshift'].max()))

        if s_state["flux_check"]:
            st.slider('Redshift range selection:', min_value=z_range[0], max_value=z_range[1], step=0.2,
                      key='z_range', value=z_range)
        else:
            s_state['z_range'] = z_range

    return


def MPT_filtering(log, idcs_in):

    if idcs_in is not None:

        st.markdown(f'# Object selection')

        # Widget selection
        label_text = 'Comma-separated MSA IDs'
        help_text = 'The observations list is limited to the input IDs'
        place_holder_text = '3,1027,80026'
        st.text_area(label=label_text, value='', key='MPTUSERLIT', on_change=save_objSample,
                     args=("MPTUSERLIT",), placeholder=place_holder_text, help=help_text)

        if (s_state['MPTUSERLIT'] != '') and (s_state['MPTUSERLIT'] != '\n'):

            user_MPTs = user_MPT_to_numpy(s_state['MPTUSERLIT'])

            idcs_selection = log['MPT'].isin(user_MPTs)
            MPT_found = log.loc[idcs_selection, 'MPT'].unique()
            MPT_common = np.intersect1d(MPT_found, user_MPTs)

            if np.sum(MPT_common) > 0:
                st.info(f'Objects {", ".join(list(MPT_common.astype(str)))} were found the sample selection')
                idcs_out = idcs_in & idcs_selection

            else:
                st.warning('None of the objects in the input MPT list was found')
                idcs_out = idcs_in

        else:
            idcs_out = idcs_in

    else:
        idcs_out = None

    return idcs_out


def line_filtering(log_files, log_lines, idcs_in):

    if idcs_in is not None:

        st.markdown(f'# Emission line detection:')
        mpt_list = log_files.loc[idcs_in].MSA.unique()
        idcs_MPT = log_lines.index.get_level_values('id').isin(mpt_list)
        line_list = ['Any'] + list(np.sort(log_lines.loc[idcs_MPT].index.get_level_values('line').unique()))

        # Security check for the object selection
        if s_state['LINEID'] not in line_list:
            st.sidebar.warning(f'Line {s_state["LINEID"]} not found for the current observation criteria, the line '
                               f'selection has been reset')
            s_state['LINEID'] = 'Any'

        st.selectbox('Query by line detection', line_list, key='LINEID', on_change=save_objSample, args=("LINEID",))

        if s_state["LINEID"] == 'Any':
            idcs_out = idcs_in
        else:
            idcs_line = log_lines.index.get_level_values('line').isin([s_state["LINEID"]])
            mpt_list = log_lines.loc[idcs_line].MSA.unique()
            idcs_out = idcs_in & log_files.MPT.isin(mpt_list)

        n_MPTs = log_files.loc[idcs_out].MSA.unique().size
        n_files = log_files.loc[idcs_out].index.get_level_values('file').str.contains('x1d').size

        if s_state["LINEID"] == 'Any':
            st.markdown(f'{n_MPTs} objects in selection ({n_files} spectra)')

        else:
            st.markdown(f'{s_state["LINEID"]} detected in {n_MPTs} {"objects" if n_MPTs > 1 else "object"}')

    else:
        idcs_out = None

    return idcs_out


def parse_str_list(input_str, default_in=None, default_out=None, split_key=','):
    if input_str == default_in:
        output = default_out

    else:
        if isinstance(input_str, str):
            output = input_str.replace('\n', '')
            output = output.replace(' ', '')
            output = np.array(output.split(split_key))

        else:
            st.warning('Input not recognized')
            output = default_out

    return output


def sidebar_widgets(files_sample, lines_sample):

    # Default selection values
    for item, value in DEFAULTS.items():
        if f'{item}_hold' not in s_state:
            s_state[f'{item}_hold'] = value
        s_state[item] = s_state[f'{item}_hold']

    # Adjust the sidebar to the sample
    with st.sidebar:

        # Observation filtering
        observation_properties_filtering(files_sample.log)

        # Observation selection
        idcs_obs = observation_indexing(files_sample.log)

        # Object selection
        idcs_objs = MPT_filtering(files_sample.log, idcs_obs)

        # Line selection
        idcs_objs = line_filtering(files_sample.log, lines_sample.log, idcs_objs)
        s_state['OBJLIST'] = idcs_objs

        # Indexing objects with line measurements
        idcs_lines_crop = lines_sample.log.index.droplevel('line')
        idcs_target = idcs_objs & files_sample.log.index.isin(idcs_lines_crop)
        idcs_lines = idcs_lines_crop.isin(files_sample.log.loc[idcs_target].index)

        # unique_sample = files_sample.log.loc[idcs_objs].index.get_level_values('sample').unique()
        # unique_id = files_sample.log.loc[idcs_objs].index.get_level_values('id').unique()
        #
        # idcs_lines = lines_sample.log.index.get_level_values('sample').isin(unique_sample) & \
        #              lines_sample.log.index.get_level_values('id').isin(unique_id)

    return idcs_objs, idcs_lines
