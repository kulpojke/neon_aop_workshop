#%%
import rasterio as rio 
import gdal
import math
import requests
import zipfile
import os
import pandas as pd 
import geopandas as gpd
import numpy as np
import subprocess
import json

# %%
def round1000(x):
    ''' 
    round1000(x):
    Rounds value to nearest 1000
    '''
    return(1000 * math.floor(x / 1000))
    
# %%
@np.vectorize
def is_on_boundary(x, y):
    '''
    Returns: 
    0 if false,
    'hor' if on horizaontal boundary,
    'ver' if on verticle boudry
    '''
    answer = 0
    r = 20
    extent  = [x - r , x + r , y - r , y + r ]
    names   = ['xMin', 'xMax', 'yMin', 'yMax']
    extent = dict(zip(names, extent)) 

    # get tile coords
    tile_east =  round1000(x)
    tile_north =  round1000(y)

    answer = (f'{tile_east}_{tile_north}')
    
    # If the plot is on a horizontal tile boundary,
    # that boundary falls between yMax and yMin
    bound_below = round1000(extent['yMax'])
    if  bound_below >= extent['yMin']:
        answer = 'hor'

    # If the plot is on a vertical tile boundary,
    # that boundary falls between xMax and xMin
    bound_left = round1000(extent['xMax'])
    if  bound_left >= extent['xMin']:
        answer = 'ver'
        
    return(answer)

# %%
def get_plot_coords(plot_spdf):
    '''
    Takes base column array of plot entries, calculates coordinates
    of tiles and returns them as a column vector of strings
    '''
    x = plot_spdf['easting']
    y = plot_spdf['northing']
    boundary = is_on_boundary(x, y)
    return(boundary)

# %%
def download_plots_shp(data_path='/home/jovyan/data/all_plots/'):
    '''
    Downloads the NEON TOS plots data
    
    --------
    Parameters
    --------
    data_path path to which data will be downloaded
    '''
    # make data directory exists 
    os.makedirs(data_path, exist_ok=True)

    handle = requests.get(url='https://data.neonscience.org/api/v0/documents/All_NEON_TOS_Plots_V8')
    
    with open(data_path + 'All_NEON_TOS_Plots_V8.zip', 'wb') as f:
        f.write(handle.content)
    
    with zipfile.ZipFile(data_path + 'All_NEON_TOS_Plots_V8.zip', 'r') as zip_ref:
        zip_ref.extractall(data_path)

    NEON_all_plots = gpd.read_file(f'{data_path}All_NEON_TOS_Plots_V8/All_NEON_TOS_Plot_Polygons_V8.shp')
    
    return(NEON_all_plots)
    




# %%
def define_sites_of_interest(sitecodes, cull_boundary_plots=True, data_path='/home/jovyan/data/all_plots/'):
    NEON_all_plots = download_plots_shp(data_path)
    for sitecode in sitecodes:
        # find all base plots for the sitecode
        base_plots_SPDF = NEON_all_plots.loc[(NEON_all_plots.siteID == sitecode) & (NEON_all_plots.subtype == 'basePlot')]
        # make a dataframe of plot coordinates
        coord_df =  pd.DataFrame()
        coord_df['plotID'] = base_plots_SPDF.plotID
        coord_df['coord_String'] = get_plot_coords(base_plots_SPDF)
        # Remove plots that cross a mosaic tile boundary.
        # Maybe not necessary if we are using EPTs
        # and cloud based tiled tifs?
        if cull_boundary_plots:
            coord_df = coord_df.loc[(coord_df.coord_String != 'hor') & (coord_df.coord_String != 'ver')]
        # count how many plots are in each mosaic tile
        coord_count = coord_df.groupby('coord_String')['plotID'].apply(list)
        return(coord_count)

#%%
def download_cyverse_iput(files_dict, iput_path, username):
    '''
    NOT DONE
    
    Downloads and saves data to iROD server using cyverse
    using icomands.  A connection must be established using
    iinit before this can be used. For more info see:
    https://cyverse-2020-neon-aop-workshop.readthedocs-hosted.com/en/latest/step4.html

    --------
    Parameters
    --------
    files_dict - a dictionary with file names as keys and api urls as values
    iput_path  - path on the server where files are to be stored
    username   - cyverse userneame    
    '''
    for fname, url in files_dict.items():
        # make sure target directory exists on server
        
        
        
        # download 
        response = requests.get(url)
        with open(f'data/{fname}', 'wb') as f:
            f.write(response.content)
        # copy to server
        cmd = f'iput -KPf {fname} /iplant/home/{username}/data/{fname}'
        answer = subprocess.call(cmd, shell=True)
        # verify transfer
        if 'ERROR' in answer:
            print(answer)
        
        # remove local file

#%%
def download_local(files_dict, savedir, username=None):
    '''
    saves files into savedir.
    username only exists to make the signature match
    that of download_cyverse_iput
    '''
    savedir.rstrip('/')
    for fname, url in files_dict.items():
        # make sure target directory exists 
        os.makedirs(savedir, exist_ok=True)       
        # download 
        response = requests.get(url)
        with open(f'{savedir}/{fname}', 'wb') as f:
            f.write(response.content)

def get_AOP_from_API(coord_count, sitecodes, productcodes, daterange = 'most recent', download_func=download_local, username=None, savedir='data'):
    '''
    Downloads files from the NEON AOP API.
    
    --------
    Parameters
    --------
    coord_count   - list of local UTM coordinates, as strings,  seperated by '_', 
                    like the output of define_sites_of_interest()
    
    sitecodes     - list of NEON sitecodes, e.g. ['BART', 'TEAK']
    
    productcodes  - list of NEON AOP product codes, e.g.
                    ['DP3.30006.001', 'DP3.30006.001'].
                    If codes are not for AOP products errors will result.
                    There is no exception handling built in for this case.
    
    daterange     - list of yyyy-mm dates for each desired month, e.g.
                    ['2019-08', '2019-09', '2019-10'], or 'most recent'
                    for most recent available month.
                   
    download_func - function specifying where the data should be saved.
                    Some functions are provided in this library (download_local 
                    and download_cyverse_iput)User defined functions must fit 
                    the signature func(files_dict, savedir, username), where:
                        - files_dict is a dictionary of the form 
                          {'filename' : 'download_url'}
                        - savedir specifies the directory where files will be saved 
                          (specified by the keyword argument 'savedir' (see below).)
                        - username if needed is is a username to access remote storage,
                          if not needed  is None. (this argument is need for 
                          download_cyverse_iput)
                    If not specified, defaults to download_local, see docstring of
                    download_local and download_cyverse_iput for more information.
    
    username      - Username for remote storage if needed. Defaults to None.

    savedir       - Path to directory where downloads will be saved.  
    
    '''    
    server = 'https://data.neonscience.org/api/v0/'
    for site in sitecodes:
        for product in productcodes:
            url = f'{server}sites/{site}'
            response = requests.get(url)
            data = response.json()['data']
            dates = data['dataProducts'][0]['availableMonths']
            if daterange == 'most recent':
                # get the most recent date
                dates = [max(dates)]
            else:
                try:
                    # get dates in the range
                    assert isinstance(daterange,list)
                    begin, terminate = min(daterange), max(daterange)
                    dates = [d  for d in dates if (d >= begin) and (d <= terminate)]                 
                except AssertionError:
                    print('daterange must be a list, e.g. [\'2020-10\', \'2019-10\']')
                    return(None)
            # determine the existing products for the dates 
            for date in dates:
                url = f'{server}data/{product}/{site}/{date}'
                response = requests.get(url)
                data = response.json()
                fnames = data['data']['files']
                files_dict = dict()
                plots_list = []
                for f in fnames:
                    for coord, plotIDs in coord_count.items():
                        if coord in f['name']:
                            files_dict[f['name']] = f['url']
                            plots_list.append(plotIDs) 
            # download the files
            try:
                download_func(files_dict, savedir, username)
            except Exception as e:
                print(f'This happened:\n\n{e}')
        print(f'Done downloading files to {savedir}') 
    files_df = pd.DataFrame.from_dict(files_dict, orient='index', columns=['url'])
    files_df['plotIDs'] = plots_list
    return(files_df, sitecodes)
                
#%%
def make_tile_csv(files_df, sitecodes, savedir='data'):
    part = '_'.join(sitecodes)
    filename = f'tile_list_{part}.csv'
    files_df.to_csv(filename)
    return(filename)

# %%
def findDatesAvailable(dpID, site):
    server = 'https://data.neonscience.org/api/v0/'
    url = f'{server}sites/{site}'
    response = requests.get(url)
    data = response.json()['data']
    dataProducts = data['dataProducts']
    dates = None
    for dp in dataProducts:
        if dp['dataProductCode'] == dpID:
            dates = dp['availableMonths']
    return(dates)

# %%
dates = findDatesAvailable('DP3.30015.001', 'BART')
date = dates[-1]

# %%
def downLoadByProduct(dpID, site, date, savedir='data', metadict=False):
    '''
    This may not work correctly in general, needs review
    
    Downloads files, places them within savedir in sub directories:
    savedir/site/dpID/date
    
    Optionally returns metadata csvs as dataframes inside of a dict. The key for each df
    is the meaningful part of the filename.
    
    --------
    Parameters
    --------
    dpID     - String, Product ID, e.g. 'DP1.10098.001'
    site     - String, NEON site abbreviation, e.g. 'BART' 
    date     - String, Month of data to download e.g. '2019-08'
    savedir  - String, optional, directory where files will be saved. Defaults to ./data
    metadict - Boolean, optional, If True returns dictionary with metadata. Defaults to False.
    '''
    savedir.rstrip('/')
    # make sure target directory exists 
    os.makedirs(savedir, exist_ok=True)
    # make sure data exists for date
    try:
        assert date in findDatesAvailable(dpID, site)
    except:    
        print(f'{dpID} is not available for {site} in the month{date}.\n Try using findDatesAvailable(dpID, site)')
    # See what files theree are
    try:
        server = 'https://data.neonscience.org/api/v0/'
        url = f'{server}data/{dpID}/{site}/{date}'
        response = requests.get(url)
    except Exception as e:
        print(e)
    stuff = response.json()
    # download the files
    files = []
    for f in stuff['data']['files']:
        fname = f['name']
        response = requests.get(f['url'])
        with open(f'{savedir}/{fname}', 'wb') as f:
            f.write(response.content)
        files.append(fname)
    data = [f for f in files if (date in f and 'zip' in f)]
    for f in data:
        directory = f'{savedir}/{site}/{dpID}/{date}'
        os.makedirs(directory, exist_ok=True)
        z= zipfile.ZipFile(f'{savedir}/{f}')
        z.extractall(directory)
        z.close
    frames = dict()
    if metadict:
        for f in files:
            if f.endswith('.csv'):
                name = f.partition(dpID+'.')[-1].split('.')[0]
                if name:
                    # make a dataframe and put it in frames with the 
                    # important part of the filename as key
                    s = f'frames[name] = pd.read_csv(\'{savedir}/{f}\')'
                    exec(s)
        return(frames)
#%%

'''TODO: it woould be nice to finish this so I don't have to
resort to R for this step
'''
def get_plant_locs_for_obs_plot(plotID, locmap=vst_mappingandtagging):
    for x in locmap['namedLocation']:
        response = requests.get(f'http://data.neonscience.org/api/v0/locations/{x}')
        properties = response.json()['data']['locationProperties']
        vals = response.json()['data']
        # we do not need locationProperties or locationChildren
        _ = vals.pop('locationProperties')
        _ = vals.pop('locationChildren')



#%%
# %%
data_path='/media/data/all_plots/'
NEON_all_plots = download_plots_shp(data_path=data_path)
sitecodes = ['BART', 'TEAK', 'HARV']
coord_count = define_sites_of_interest(sitecodes, data_path=data_path)
#files_df, sitecodes = get_AOP_from_API(coord_count, ['BART'],productcodes=['DP3.30006.001'] ,daterange=['2019-08', '2019-08'],savedir='/media/data/AOP')
#fname = make_tile_csv(files_df, sitecodes)

frames = downLoadByProduct('DP1.10098.001', 'BART', date, metadict=True)
vst_mappingandtagging =frames['vst_mappingandtagging']
vst_mappingandtagging.dropna(subset=['pointID'], inplace=True)
vst_mappingandtagging
# %%
