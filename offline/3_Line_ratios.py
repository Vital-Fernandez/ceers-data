import streamlit as st
from streamlit import session_state as s_state
from tools.workflow import sidebar_widgets, save_objSample
from tools.io import load_databases
from format.plots import flux_scatter


# Make sure the user is recognized
if 'auth_status' not in s_state:
    if 'auth_status_hold' in s_state:
        s_state['auth_status'] = s_state['auth_status_hold']
    else:
        s_state['auth_status'] = False

if s_state['auth_status']:

    # Title
    st.markdown(f'# Flux ratio calculation')
    st.markdown(f'Introduce the line ratios to calculate. You can use the drop-down menu on the side-bar to'
                f'check the lines detected on your current sample selection.')

    # Load the databases
    files_sample, lines_sample = load_databases()

    # Slice the database to the user selection
    idcs_files, idcs_lines = sidebar_widgets(files_sample, lines_sample)

    # Object selection widgets
    col_text, col_selection = st.columns(2)

    ratios_df = None

    with col_text:
        label_text = 'Comma-separated flux ratios'
        help_text = 'The lines fluxes are measured in the observed frame using vacuum wavelengths.'
        place_holder_text = 'H1_6565A/H1_4862A,H1_4341A/H1_4862A'
        line_ratios = st.text_area(label=label_text, value='', key='LINERATIOS', on_change=save_objSample,
                                   args=("LINERATIOS",), placeholder=place_holder_text, help=help_text)

    with col_selection:

        flux_types = ['mixture', 'Integrated', 'Gaussian']
        help_text = f'In the "mixture" option, the integrated fluxes are reported for single lines, while blended lines' \
                    f' display the Gaussian fluxes. The "intg" and "gauss" options report the integrated or Gaussian' \
                    f' fluxes for line types respectively.'
        flux_type = st.selectbox('Select flux type for calculation', flux_types, key='FLUXTYPE',
                                           on_change=save_objSample, args=("FLUXTYPE",), help=help_text)

        if flux_type != 'mixture':
            if flux_type == 'Integrated':
                flux_type = 'intg'
            else:
                flux_type = 'gauss'

        # Compute the flux type
        lines_sample.extract_fluxes(flux_type)

        if line_ratios != '':
            line_ratios = line_ratios.replace('\n', '')
            line_ratios_list = line_ratios.split(',')
            try:
                ratios_df = lines_sample.compute_line_ratios(line_ratios_list, sample_levels=['sample', 'id', 'line'])

                st.markdown(f'Input ratios: {line_ratios_list}')

            except:
                st.warning('Some of the input fluxes are not recognized please try again:'
                           f'Line ratio list: {line_ratios}, {line_ratios_list}')
        else:
            st.markdown(f'Please introduce some line ratios')
    # Plot
    if ratios_df is not None:

        st.markdown('## Ratio scatter plot')

        if len(ratios_df.columns) == 2:
            st.markdown(f'1 line ratio recognized')

        if len(ratios_df) >= 4:

            columns_list = ratios_df.columns
            input_list = ['None'] + line_ratios_list

            col_num, col_denom = st.columns(2)
            with col_num:
                num = st.selectbox(label='X axis', options=input_list, key='NUMLINE', on_change=save_objSample,
                                   args=("NUMLINE",))

            with col_denom:
                denom = st.selectbox(label='Y axis', options=input_list, key='DENOLINE', on_change=save_objSample,
                                     args=("DENOLINE",))

            if (num != 'None') and (denom != 'None'):
                st.bokeh_chart(flux_scatter(ratios_df, num, denom))

    # Table/download
    if ratios_df is not None:
        if len(ratios_df.columns) >= 4:
            st.markdown('## Ratios table')

            string_DF = ratios_df.to_string()
            st.download_button('Download', data=string_DF.encode('UTF-8'), file_name=f'ratios_dataframe.txt')

            st.dataframe(ratios_df)

# No user
else:
    st.markdown(f'# Please introduce your login details')
