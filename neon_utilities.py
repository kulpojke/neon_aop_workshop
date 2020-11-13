import requests
import json
import urllib.request
import binascii
import re


def zipsByProduct(dpID, site='all', startDate=None, endDate=None, package='basic', avg='all', check_size=True, savepath=None, load=False):
    if dpID_check(dpID) == 'Fail' or package_check(package) == 'Fail':
        return(None)
    product_url = 'http://data.neonscience.org/api/v0/products/{}'.format(dpID)
    response = requests.get(product_url)
    if not response.ok:
        print('No data found for product {}'.format(dpID))
    else:
        stuff = response.json()
        print(stuff['data'].keys())


def dpID_check(dpID):
    if not re.compile('DP[1-4]{1}.[0-9]{5}.001').match(dpID):
        print('dpID is not of the correct format\n The correct format is DP#.#####.001')
        return('Fail')
    elif re.compile('DP3').match(dpID):
        print('{}is a remote sensing data product. Use the byFileAOP() function.'.format(dpID))
        return('Fail')
    elif dpID == 'DP1.00033.001' or dpID == 'DP1.00042.001':
        print('{} is a phenological image product, data are hosted by Phenocam.'.format(dpID))
        return('Fail')


def package_check(package):
    if package != 'basic' and package!= 'expanded':
        print('{} is not a valid package name. Package must be basic or expanded'.format(package))
        return('Fail')