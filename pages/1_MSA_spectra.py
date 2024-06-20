import streamlit as st
from streamlit import session_state as s_state

from tools.io import load_databases, arcoiris_link #, read_appertures
from format.plots import display_1d_spec, display_2d_spec, multi_spec_plot
from tools.workflow import sidebar_widgets, tabs_object_selection, user_logging


# Display 1D spectrum
def rainbow_link(files_log):

    MPT = files_log['MSA'].to_numpy()

    if len(MPT) > 0:

        st.markdown(f'Selected MPT: {MPT[0]}')

        warning = 'Please use wikis.utexas internal team user/password'
        contact = f'(please contact [Pablo G. Pérez-González](mailto:pgperez@cab.inta-csic.es) with queries on this database.)'
        st.markdown(f'Observation photometry: [Arcoiris link]({arcoiris_link(MPT[0])} "{warning}") {contact}')

    if len(MPT) > 1:
        st.markdown(f'{len(MPT)} observations in selection.')

    return


# Check for logged-user interface
user_logging(check_user=False)

if s_state['auth_status']:

    # Title
    st.markdown(f'# Multi-Shutter Assembly spectra')
    st.markdown(f'Select one observation from the current sample')

    # Load the database
    files_sample, lines_sample = load_databases()

    # Slice the database to the user selection
    idcs_files, idcs_lines = sidebar_widgets(files_sample, lines_sample)

    # Tabs for visualization
    single_tab, multiple_tab = st.tabs(['Single observation', 'Multiple observations'])

    with single_tab:

        # Individual MPT selection
        idcs_tabs = tabs_object_selection(files_sample.frame, idcs_files)

        if idcs_files is not None:

            # Object information
            rainbow_link(files_sample.frame.loc[idcs_tabs])

            # 1D Spectrum
            display_1d_spec(files_sample, idcs_tabs)

            # 2D spectrum
            appertures = None #read_appertures(files_sample.log.loc[idcs_tabs])
            display_2d_spec(files_sample, idcs_tabs, appertures)

    with multiple_tab:

        # Individual MPT selection
        idcs_tabs = tabs_object_selection(files_sample.frame, idcs_files, just_objects=True, key_ID='MPT2')

        # Object information
        rainbow_link(files_sample.frame.loc[idcs_tabs])

        # 1D Spectrum
        idcs_1d = idcs_tabs & files_sample.frame['ext'].str.contains('x1d')
        multi_spec_plot(files_sample[idcs_1d])

# No user
else:
    st.markdown(f'# Please introduce your login details')

