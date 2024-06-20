import numpy as np
import pandas as pd
from tools.io import logo_load, load_databases
from pandas import isnull
files_sample, lines_sample = load_databases()

# idcs_nan = pd.isnull(lines_sample.frame['group_label'])
# lines_sample.frame.loc[idcs_nan, 'group_label'] = 'none'


lines_sample.frame.rename(columns={'std_cont': 'cont_err'}, inplace=True)


print(lines_sample.frame.group_label)
output_address = '/home/vital/PycharmProjects/ceers-data/data/tables/CEERs_DR0.7_flux_log.txt'
lines_sample.save_frame(output_address)
