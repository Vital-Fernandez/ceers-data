import streamlit as st
from streamlit import session_state as s_state

from pathlib import Path
from tools.io import logo_load, load_databases
from tools.workflow import sidebar_widgets, user_logging

text_format = 'style="font-size: 25px;"'
nirspec_link = '<a href="https://jwst-docs.stsci.edu/jwst-near-infrared-spectrograph">NIRSpec</a>'
ceers_link = '<a href="https://ceers.github.io/">website</a>'
reduction_link = '<a href="https://www.nature.com/articles/s41586-023-06521-7">Pablo et al. (2023)</a>'
publications_link = '<a href="https://ceers.github.io/papers.html">publications</a>'
mail_link = '<a href="mailto:vgf@umich.edu">author</a>'
limelogo_link = ('<img src="https://github.com/Vital-Fernandez/lime/blob/0afedb150b0169deec6c7f159def99750a3a30da/docs/source/_static/logo_transparent.png?raw=true"'
                 ' alt="LiMe" width="80" height="60">')
dr07_link = '<a href="https://ceers.github.io/dr07.html">link</a>'

INTRODUCTION_TEXT = (f'<p {text_format}> '
                     f'- On this site you can visualize the {nirspec_link} observations from the CEERs survey.<br>'
                     f'- You may check the latest CEERs products from its {ceers_link} and the {publications_link}.<br>'
                     f'- The spectra on this site have been reduced and calibrated using the methodology described in {reduction_link}.<br>'
                     f'- The line fluxes have been measured using {limelogo_link}. You may contact the {mail_link}, regarding any issue with the measurements or the site operation.'
                     f'</p>')

RELEASE_TEXT = (f'<p {text_format}> '
                f'- The available data belongs to the CEERs Data release 0.9'
                # f'- The available data belongs to the CEERs Data release 0.9. You can download these spectra from this {dr07_link}.<br>'
                f'</p>')


def run():

    # Sidebar
    menu_items = {'About': '## Learn more about the CEERs survey at https://ceers.github.io/',
                  'Report a bug': "https://github.com/Vital-Fernandez/lime",
                  'Get help': "https://lime-stable.readthedocs.io/en/latest/"}
    st.set_page_config(page_title="CEERs data", layout='wide', menu_items=menu_items)

    # Check for logged-user interface
    force_id = False
    user_logging(check_user=force_id)

    if s_state['auth_status_hold'] is False and force_id is True:
        st.error(f'Username/password is incorrect')

    elif s_state['auth_status_hold'] is None and force_id is True:
        st.warning(f'Please enter you username and password')

    else:

        # Website-page selection message
        st.sidebar.success("Access the data from the sections above")

        # CEERs logo and welcome
        col_logo, col_welcome = st.columns([0.3, 0.7], gap='large')

        with col_logo:
            logo_address = Path(f'format/CEERS_white.png')
            image = logo_load(logo_address)
            st.image(image, width=300)

        with col_welcome:
            welcome_message = f'# Welcome to the CEERs data release'
            if s_state["user"] is not None:
                welcome_message += f',\n# {s_state["user"]}'
            for i in range(8):
                st.write("\n")
            st.markdown(welcome_message)

        # Introduction text
        st.markdown("***")
        st.markdown(INTRODUCTION_TEXT, unsafe_allow_html=True)

        # Load the database
        files_sample, lines_sample = load_databases()

        # Sidebar to select the data
        _idcs_files, _idcs_lines = sidebar_widgets(files_sample, lines_sample)

        # The current
        st.markdown("***")
        st.markdown(RELEASE_TEXT, unsafe_allow_html=True)
        st.dataframe(files_sample.loc[_idcs_files], width=1600)


if __name__ == "__main__":
    run()


