import streamlit as st
import streamlit.components.v1 as components

from bokeh.palettes import Category10
from bokeh.palettes import inferno, Viridis
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show
from bokeh.models import LinearColorMapper, LogColorMapper, TeX, Whisker, Legend

import mpld3
import itertools
import pandas as pd

from tools.io import FITS_PATH, hdr_to_df
from lime.plots import spectrum_figure_labels
from astropy.visualization import ZScaleInterval, AsinhStretch, simple_norm, ImageNormalize
from pathlib import Path

Z_FUNC_CMAP = ZScaleInterval()


def color_gen(size_pal=10):
    yield from itertools.cycle(Category10[size_pal])


def figure_conversion(in_fig, static_fig=True, height=850):

    # Static figures
    if static_fig:
        st.pyplot(in_fig)

    # Dynamic figures
    else:
        fig_html = mpld3.fig_to_html(in_fig)
        components.html(fig_html, height=height)

    return


def plot_spectrum(spec):

    fig = figure(width=600, height=300, tools="pan,xwheel_pan,xzoom_in,xzoom_out,wheel_zoom,reset")

    fig.step(x=spec.wave, y=spec.flux, mode="center")

    x_label, y_label = spectrum_figure_labels(spec.units_wave, spec.units_flux, spec.norm_flux)

    # units_wave = UNITS_LATEX_DICT[spec.units_wave].replace(r"\AA", "Å")
    # units_flux = UNITS_LATEX_DICT[spec.units_flux].replace(r"\AA", "Å")
    # norm_label = r' \,/\,{}'.format(latex_science_float(spec.norm_flux)) if spec.norm_flux != 1.0 else ''
    #
    # # fig.xaxis.axis_label = f'wavelength (Å)' if spec.units_wave == 'A' else f'$${UNITS_LATEX_DICT[spec.units_wave]}$$'
    # fig.xaxis.axis_label = r'$$\text{Wavelength }' + f'({units_wave}\,\,\,)$$'
    # fig.yaxis.axis_label = r'$$\text{Flux }' + f'({units_flux})' + f'{norm_label}$$'

    fig.xaxis.axis_label = x_label
    fig.yaxis.axis_label = y_label

    return fig


def multi_spec_plot(files_sample):

    st.markdown(f'###  Observations overplotting')

    if files_sample.index.size > 0:

        color = itertools.cycle(inferno(files_sample.index.size))
        fig = figure(width=600, height=600, tools="pan,box_zoom,xzoom_in,xzoom_out,wheel_zoom,reset,save",
                     active_drag='box_zoom') #active_scroll="auto",

        # legend = p.legend.click_policy="hide"
        fig.add_layout(Legend(), 'below')
        fig.legend.click_policy = "hide"

        # Slice to 1d files
        for i, idx_obs in enumerate(files_sample.index):
            multi_index_entry = pd.MultiIndex.from_tuples([idx_obs], names=files_sample.index.names)
            spec = files_sample.get_spectrum(multi_index_entry)
            label = ", ".join(map(str, idx_obs))
            fig.step(x=spec.wave, y=spec.flux, mode="center", color=next(color), legend_label=label)

        # Wording
        x_label, y_label = spectrum_figure_labels(spec.units_wave, spec.units_flux, spec.norm_flux)
        # units_wave = UNITS_LATEX_DICT[spec.units_wave].replace(r"\AA", "Å")
        # units_flux = UNITS_LATEX_DICT[spec.units_flux].replace(r"\AA", "Å")
        # norm_label = r' \,/\,{}'.format(latex_science_float(spec.norm_flux)) if spec.norm_flux != 1.0 else ''
        #
        # fig.xaxis.axis_label = r'$$\text{Wavelength }' + f'({units_wave}\,\,\,)$$'
        # fig.yaxis.axis_label = r'$$\text{Flux }' + f'({units_flux})' + f'{norm_label}$$'
        fig.xaxis.axis_label = x_label
        fig.yaxis.axis_label = y_label

    # Display it
    st.bokeh_chart(fig)

    # Instructions
    st.markdown(f'You can click the +/- loop symbols to magnify on the X axis')

    return


def flux_scatter(log, ratio_x, ratio_y):

    tools_list = 'hover,pan,wheel_zoom,reset,save'
    fig = figure(width=500, height=500, tools=tools_list)

    fig.xaxis.axis_label = ratio_x
    fig.yaxis.axis_label = ratio_y
    fig.hover.tooltips = [("Object ID", "@desc"),
                          ("(x,y)", "($x, $y)")]

    x_axis = log[ratio_x].to_numpy()
    y_axis = log[ratio_y].to_numpy()

    data_dict = {ratio_x: x_axis,
                 ratio_y: y_axis,
                'ratio_x_up': x_axis + log[f'{ratio_x}_err'].to_numpy(),
                'ratio_x_low': x_axis - log[f'{ratio_x}_err'].to_numpy(),
                'ratio_y_up': y_axis + log[f'{ratio_y}_err'].to_numpy(),
                'ratio_y_low': y_axis - log[f'{ratio_y}_err'].to_numpy(),
                'desc': log.index.to_numpy()}

    source = ColumnDataSource(data=data_dict)

    # st.write(data_dict['ratio_y_low'])
    fig.add_layout(Whisker(dimension='height', base=ratio_x, upper='ratio_y_up', lower='ratio_y_low', source=source))
    fig.add_layout(Whisker(dimension='width', base=ratio_y, upper='ratio_x_up', lower='ratio_x_low', source=source))
    fig.scatter(ratio_x, ratio_y, source=source, alpha=0.7, size=10)

    return fig


def plot_fits_2d(flux_image, wave, limits):

    # Create the image
    fig_cfg = {'width': 600, 'aspect_ratio': 3, 'tools': "hover,wheel_zoom,reset,pan,xzoom_in,xzoom_out",
               'toolbar_location':"below", 'tooltips': [("x", "$x"), ("y", "$y")]}

    fig = figure(**fig_cfg)
    fig.x_range.range_padding = fig.y_range.range_padding = 0

    # Plotting the image
    display_flux = Z_FUNC_CMAP(flux_image)
    # z1, z2 = Z_FUNC_CMAP.get_limits(display_flux)
    l_mapper = LinearColorMapper(palette="Inferno256")  # Oranges256
    im_cfg = {'image': [display_flux], 'x': wave[0], 'y': 0, 'dw': wave[-1]-wave[0], 'dh': flux_image.shape[0],
              'color_mapper': l_mapper,
              'level': "image"}

    fig.image(**im_cfg)
    fig.xaxis.axis_label = r'$$\text{Wavelength }' + f'(Å\,\,\,)$$'
    fig.yaxis.axis_label = r'$$\text{Pixel y coordinate}$$'

    if limits is not None:
        fig.ray(x=wave[0], y=limits[0], length=wave[-1]-wave[0], angle=0, color='black', line_width=1, line_dash="dashed")
        fig.ray(x=wave[0], y=limits[1], length=wave[-1]-wave[0], angle=0, color='black', line_width=1, line_dash="dashed")

    return fig


# Display 1D spectrum
def display_1d_spec(files_sample, idcs_in):


    # Recover the spectrum
    spec1d = files_sample.get_spectrum(idcs_in)

    # Spectra and header tabs geneartation
    spec1D_tab, hdr0_tab, hdr1_tab = st.tabs(['Spectrum', 'Header 0', 'Header 1'])

    with spec1D_tab:
        st.bokeh_chart(plot_spectrum(spec1d))
        st.markdown(f'You can click the +/- loop symbols to magnify along the X axis')

    with hdr0_tab:
        hdr_df = hdr_to_df(spec1d.header[0])
        st.dataframe(hdr_df, width=800)

    with hdr1_tab:
        hdr_df = hdr_to_df(spec1d.header[1])
        st.dataframe(hdr_df, width=800)

    return

# Display 2D spectrum
def display_2d_spec(files_sample, idcs_in, limits=None):


    # Slice to 2d files
    # idcs_2d = idcs_in & files_sample.loc[idcs_in, 'ext'].str.contains('s2d')

    # Show files
    file_list = files_sample.loc[idcs_in].index.get_level_values('file').to_numpy()
    # st.markdown(f'Spectra files in selection: {file_list}')

    # Recover the spectrum

    if len(file_list) > 0:

        wave, e_flux, err, hdr_list = files_sample.get_spectrum(idcs_in)

        # fits2d_path = Path(__file__).parent.parent/'data/spectra'/path_list[0]
        # wave, e_flux, err, hdr_list = load_nirspec_fits(fits2d_path)
        fig = plot_fits_2d(e_flux, wave, limits)
        st.bokeh_chart(fig)
    else:
        st.markdown(f"There aren't 2D files for this observation")

    return