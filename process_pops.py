'''
Input the City of Seattle's csv data on publicly-owned open spaces and output as geojson.
In the csv, the coordinates are not in a form to make valid JSON.

author: David Thaler
date: June 3, 2019
'''
import argparse
import pandas as pd 
import json

# default path to write to
POPS_PATH = '../../data/POPS.csv'

def load_pops(infile):
    'Load the part of the csv file that we use'
    pops = pd.read_csv(infile)
    x = (pops[['Common Name', 'Location', 'Address', 'Built']]
        .rename({'Common Name': 'Name', 'Built': 'Year'}, axis=1))
    #x['Coordinates'] = x.Location.map(lambda s: s.replace('(', '[').replace(')', ']'))
    x['Coordinates'] = pops.Location.map(lambda s: [float(n) for n in s.strip('()').split(',')][::-1])
    return x.drop('Location', axis=1)

def make_feature(r):
    'Makes one geoJSON feature for a feature collection from one row of POPS data frame.'
    properties = {'name': r.Name, 'address': r.Address, 'year': r.Year}
    geometry = {'type': 'Point', 'coordinates': r.Coordinates}
    return {'type': 'Feature', 'properties': properties, 'geometry': geometry}

def make_collection(x):
    'Makes a valid geoJSON feature collection (Point) from POPS data frame.'
    features = x.apply(make_feature, axis=1)
    return {'type': 'FeatureCollection', 'features': list(features)}

def output_collection(d, out, indent=1):
    '''
    Output the dict from make_collection to a file as valid javascript.

    Args:
        d: the dict with valid geojson
        out: output file or path
        indent: number of spaces to indent at each level for pretty-printing.
            Use None for packed (smallest).
    '''
    with open(out, 'w') as f:
        gj = json.dumps(d, indent=indent)
        f.write('var pops = ')
        f.write(gj)
        f.write(';')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Read in the POPS data (csv) from the City, output geojson')
    parser.add_argument('--infile', help='Input csv file', default=POPS_PATH)
    parser.add_argument('--outfile', help='output (javascript) file containing a geojson variable')
    parser.add_argument('--indent', type=int, help='spaces to indent in pretty printing', default=1)
    args = parser.parse_args()
    x = load_pops(args.infile)
    gj = make_collection(x)
    output_collection(gj, args.outfile, args.indent)
