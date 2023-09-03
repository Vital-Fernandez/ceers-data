import streamlit as st
import matplotlib.pyplot as plt

from streamlit import session_state as s_state
from numpy import sort, any
from tools.workflow import sidebar_widgets, tabs_object_selection, user_logging
from tools.io import load_databases
from format.plots import figure_conversion


def grid_display(sample_files, sample_fluxes):

    st.markdown(f'## Profile grid: ')

    for idx_obs in sample_files.log.index:

        # Get data
        spec = sample_files.get_spectrum(idx_obs)
        spec.load_log(sample_fluxes.log.xs(idx_obs, level=('sample', 'id', 'file')))

        # Plot
        st.markdown(f'* **Reduction:** {idx_obs[0]}. **File:** {idx_obs[2]}')
        fig_grid = plt.figure(tight_layout=True)
        st.pyplot(spec.plot.grid(in_fig=fig_grid, n_cols=2, fig_cfg={'axes.titlesize': 10}, col_row_scale=(1, 3)))

    return


def line_display(files_sample, flux_log, line_list):

    # st.markdown(f'## Line profile: ')
    line = st.selectbox('Select a line for the profile visualization', line_list, key='line')

    # Loop through the observations
    for idx_obs in files_sample.index:

        log = flux_log.log.xs(idx_obs, level=('sample', 'id', 'file'))

        if line in log.index:

            spec = files_sample.get_spectrum(idx_obs)
            spec.load_log(log)

            # Make the figure
            st.markdown(f'* **Reduction:** {idx_obs[0]}. **File:** {idx_obs[2]}')
            fig_line = plt.figure()
            spec.plot.bands(line, in_fig=fig_line, include_fits=True, fig_cfg={'axes.labelsize': 10,
                                                                              'xtick.labelsize': 10,
                                                                              'ytick.labelsize': 10})
            figure_conversion(fig_line, static_fig=True)

    return


def table_display(files_sample, fluxes_sample):

    st.markdown(f'## Measurements table: ')

    for i, idx_obs in enumerate(files_sample.index):

        log_lines = fluxes_sample.log.xs(idx_obs, level=('sample', 'id', 'file'))
        log_lines.index.name = None

        # Information (Just the first time)
        if i == 0:
            st.markdown(f'* Please check [LiMe](https://lime-stable.readthedocs.io/en/latest/) online documentation for '
                        f'the parameters physical description.')
            st.markdown(f'* The lines are measured in the observed frame.')

            # label_dis, label_flux = UNITS_LATEX_DICT[spec.units_wave], UNITS_LATEX_DICT[spec.units_flux]
            # st.markdown(f'* The dispersion axis is in $${label_dis}$$.')
            # st.markdown(f'* The flux axis is in $${label_flux}$$.')

        st.markdown(f'* **Reduction:** {idx_obs[0]}')
        st.markdown(f'* **.fits file:** {idx_obs[2]}')

        # Table
        st.dataframe(log_lines)

        # Download mechanism
        # string_DF = log_lines.to_string()
        # table_name = idx_obs[2].replace('.fits', '_log.txt')
        # st.download_button('Download', data=string_DF.encode('UTF-8'), file_name=table_name)

    return


# Check for logged-user interface
user_logging(check_user=False)

if s_state['auth_status']:

    # Title
    st.markdown(f'# Line profiles')
    st.markdown(f'Select one observation from the current sample')

    # Load the databases
    files_sample, lines_sample = load_databases()

    # Slice the database to the user selection
    idcs_files, idcs_lines = sidebar_widgets(files_sample, lines_sample)

    # Second user selection
    idcs_target = tabs_object_selection(files_sample.log, idcs_files, just_objects=True)

    # Indexing objects with line measurements
    idcs_lines_crop = lines_sample.log.index.droplevel('line')
    idcs_target = idcs_target & files_sample.log.index.isin(idcs_lines_crop)
    idcs_lines = idcs_lines_crop.isin(files_sample.log.loc[idcs_target].index)

    # Check for measurements
    id_lines_list = idcs_target
    if any(idcs_target) == 0:
        st.markdown(f"## There aren't line measurements for this observation")

    else:

        grid_tab, line_tab, df_tab = st.tabs(['Profile grid', 'Individual line', 'Measurements table'])

        # Grid display
        with grid_tab:
            grid_display(files_sample[idcs_target], lines_sample)

        # Line fitting display
        with line_tab:
            lines_selection = sort(lines_sample.log.loc[idcs_lines].index.get_level_values('line').unique())
            line_display(files_sample[idcs_target], lines_sample, lines_selection)

        # Table measurements
        with df_tab:
            table_display(files_sample[idcs_target], lines_sample)

# No user
else:
    st.markdown(f'# Please introduce your login details')