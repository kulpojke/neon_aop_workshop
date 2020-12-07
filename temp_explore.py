#/* cSpell:disable */
#%%
import pandas as pd

#%% [markdown]
# The csv has misaligned rows, maybe there are som commas in fields 
# accidentally? Whatever causes it we will just have to ignore those lines, so first make a df with just columns and no data
 
#%%  
fname = 'exact_locations_within_plots.csv'
df = pd.read_csv(fname)

# %%
l = 0
dropped = 0
with open(fname) as f:
    for line in f:
        if l ==0:
            ncols = len(line.split(',')) 
        else:
            if 
        l = l+1

# %%
l = 0
dropped = 0
with open(fname) as f:
    for line in f:
        print(line)
        l = l+1
        if l > 2:
            break
# %%
