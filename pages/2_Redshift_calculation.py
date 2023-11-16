import pandas as pd
import streamlit as st

import lime
from numpy import any
from streamlit import session_state as s_state
from tools.workflow import sidebar_widgets, save_objSample, parse_str_list, user_logging
from tools.io import load_databases

# Check for logged-user interface
user_logging(check_user=False)

if s_state['auth_status']:

    # Title
    st.markdown(f'# Redshift calculation')
    st.markdown(f'In this section you can calculate the mean redshift from the centroid of the Gaussian line'
                f' fittings. The user can specify a sub-set of lines and a weighting parameter for the calculation.'
                f' If none is provided the calculation uses all the lines available with a uniform weight.')

    # Load the databases
    files_sample, lines_sample = load_databases()

    # Slice the database to the user selection
    idcs_files, idcs_lines = sidebar_widgets(files_sample, lines_sample)

    # Indexing objects with line measurements
    idcs_lines_crop = lines_sample.log.index.droplevel('line')
    idcs_target = idcs_files & files_sample.log.index.isin(idcs_lines_crop)
    idcs_lines = idcs_lines_crop.isin(files_sample.log.loc[idcs_target].index)

    # Object selection widgets
    col_line_selection, col_params_selection = st.columns(2)

    with col_line_selection:
        label_text = 'Comma-separated lines for redshift calculation'
        help_text = 'Observations with empty rows do not have any of the of the input lines.'
        place_holder_text = 'All'

        lines_list = st.text_area(label=label_text, value='', key='LINES_Z', on_change=save_objSample,
                                   args=("LINES_Z",), placeholder=place_holder_text, help=help_text)

        # Parse the list
        lines_list = parse_str_list(lines_list, default_in='', default_out=None)

    with col_params_selection:
        z_params_weight = ['None', 'intg_flux', 'gauss_flux', 'eqw']
        help_text = 'The equivalent width measurements high redshift observations have very large uncertainties.'
        z_weight = st.selectbox(label='Redshift weight parameter', options=z_params_weight, key='Z_WEIGHT',
                           on_change=save_objSample, args=("Z_WEIGHT",), help=help_text)
        z_weight = None if z_weight == 'None' else z_weight

    # Constrain the selection
    if any(idcs_target):
        files_log_selection = files_sample.log.loc[idcs_target]
        lines_log_selection = lines_sample.log.loc[idcs_lines]

    else:
        files_log_selection = files_sample.log
        lines_log_selection = lines_sample.log

    z_df = lime.redshift_calculation(lines_log_selection, line_list=lines_list, weight_parameter=z_weight)

    out_df = pd.DataFrame(index=z_df.index, columns=list(['pointing', 'disp'] + list(z_df.columns.to_numpy())))

    for id_MPT in z_df.index:
        out_df.loc[id_MPT, 'z_mean':'weight'] = z_df.loc[id_MPT].to_numpy()
        out_df.loc[id_MPT, 'disp'] = files_log_selection.loc[id_MPT, 'disp']
        out_df.loc[id_MPT, 'pointing'] = files_log_selection.loc[id_MPT, 'pointing']

    # Sort by dataframe
    out_df.sort_values(by=['id', 'disp', 'pointing'], ascending=[True, False, True], inplace=True)

    # Results section
    col_title, col_download = st.columns(2)

    # Title
    with col_title:
        st.markdown(f'## Results')

    # Download button
    with col_download:
        st.write(' \n')
        string_DF = out_df.to_string()
        st.download_button('Download', data=string_DF.encode('UTF-8'), file_name=f'CEERs_redshift_table.txt')

    # Generate slice to a df combining files and z
    label_text = 'The first four columns correspond to the sample/reduction, MPT, pointing and dispenser of the corresponding ' \
                 'spectrum. The final four columns provide the redshift mean and estandar deviation values along with the lines' \
                 'used in the calculation and the weighting parameter.'
    st.markdown(label_text)

    st.dataframe(out_df)
