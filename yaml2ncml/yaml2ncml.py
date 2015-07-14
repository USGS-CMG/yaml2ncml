import os
import sys
import yaml
import netCDF4

from docopt import docopt

__doc__ = """
Generate ncml based on a yaml file.

Usage:
    yaml2ncml INFILE [--output=OUTFILE]

    yaml2ncml (-h | --help | --version)

Examples:
    yaml2ncml roms.yaml
    yaml2ncml roms.yaml --output=roms.ncml

Arguments:
  file      yaml file.

Options:
  -h --help     Show this screen.
  -v --version     Show version.
"""


def attribute_name(name, value):
    if isinstance(value, list):
        value = ','.join(value)
    msg = '  <attribute name="{:s}" type="String" value="{:s}"/>\n'
    return msg.format(name, value)


def header():
    conventions = attribute_name('Conventions', 'CF-1.6, SGRID-0.1, ACDD-1.3')
    cdm = attribute_name('cdm_data_type', 'Grid')

    text = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<netcdf xmlns='
            '"http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2">\n'
            '{}{}'.format(conventions, cdm))
    return text


def footer(text):
    text += '</netcdf>\n'
    return text


def add_global_atts(text, a):
    d = a['dataset']
    for key, value in d.items():
        # Handle simple attribute pairs first.
        if key in ['id', 'license', 'summary', 'title', 'project',
                   'naming_authority', 'references', 'acknowledgments']:
            text += attribute_name(key, value)
        elif key in ['creator', 'publisher']:
            email = value.get("email", None)
            if email:
                text += attribute_name('_'.join([key, 'email']), email)
            url = value.get("url", None)
            if url:
                text += attribute_name('_'.join([key, 'url']), url)
            name = value.get("name", None)
            if name:
                text += attribute_name('_'.join([key, 'name']), name)
        elif key in ['contributor']:
            role = value.get("role", None)
            if email:
                text += attribute_name('_'.join([key, 'role']), role)
            email = value.get("email", None)
            if email:
                text += attribute_name('_'.join([key, 'email']), email)
            url = value.get("url", None)
            if url:
                text += attribute_name('_'.join([key, 'url']), url)
            name = value.get("name", None)
            if name:
                text += attribute_name('_'.join([key, 'name']), name)
    return text


def add_var_atts(text, a):
    ncfile = os.path.join(a['aggregation']['dir'],
                          a['aggregation']['sample_file'])
    nc = netCDF4.Dataset(ncfile)
    ncv = nc.variables

    # Get a list of all variables more than 1D.
    vars = [var for var, vart in ncv.items() if vart.ndim > 1]
    vars_all = set(vars)
    vars_include = set(a['variables']['include'])
    vars_exclude = set(a['variables']['exclude'])
    if a['variables']['exclude']:
        vars = list(vars_all - vars_all.intersection(vars_exclude))
    else:
        if a['variables']['include']:
            vars = list(vars_all.intersection(vars_include))
    rho_vars = [var for var, vart in ncv.items() if 'eta_rho' in
                vart.dimensions and 'xi_rho' in vart.dimensions]
    u_vars = [var for var, vart in ncv.items() if 'eta_u' in
              vart.dimensions and 'xi_u' in vart.dimensions]
    v_vars = [var for var, vart in ncv.items() if 'eta_v' in
              vart.dimensions and 'xi_v' in vart.dimensions]

# write standard_name for time coordinate variable
    var = 'ocean_time'
    if var in ncv.keys():
        try:
            str += '\n<variable name="{:s}">\n'.format(var)
            str += str_att('standard_name',cf[var]) 
            str += '</variable>\n\n'
        except:
            pass
    

    for var in vars:
        text += '<variable name="{:s}">\n'.format(var)
        try:
            text += attribute_name('standard_name', cf[var])
        except:
            pass
        text += attribute_name('grid', 'grid')
        text += attribute_name('content_coverage_type', 'modelResult')
        if var in rho_vars:
            text += attribute_name('location', 'face')
        elif var in u_vars:
            text += attribute_name('location', 'edge1')
        elif var in v_vars:
            text += attribute_name('location', 'edge2')
        text += '</variable>\n\n'
    return text


def write_grid_var(text, template='roms'):
    if template == 'roms':
        tpl = 'roms.tpl'
    else:
        raise ValueError('Template {!r} is not implemented!'.format(template))

    fname = os.path.join(os.path.dirname(__file__), 'templates', tpl)
    with open(fname) as f:
        grid_var = '{}'.format(f.read())
    text += grid_var
    return text


def add_aggregation_scan(text, a):
    agg = a['aggregation']
    join_existing = ' <aggregation dimName="{:s}" type="joinExisting">\n'
    scan = ('<scan location="." regExp="{:s}" subdirs="false"/>\n'
            '</aggregation>\n')
    text += join_existing.format(agg['time_var'])
    text += scan.format(agg['pattern'])
    return text

# Map ROMS variables to CF standard_names.
cf = dict(ocean_time='time',
          zeta='sea_surface_height_above_datum',
          temp='sea_water_potential_temperature',
          salt='sea_water_salinity',
          u='x_sea_water_velocity',
          v='y_sea_water_velocity',
          ubar='barotropic_x_sea_water_velocity',
          vbar='barotropic_y_sea_water_velocity',
          Hwave='sea_surface_wave_significant_height')


def build(yml):
    text = header()
    text = add_global_atts(text, yml)
    text = add_var_atts(text, yml)
    text = write_grid_var(text)
    text = add_aggregation_scan(text, yml)
    text = footer(text)
    return text


def main():
    args = docopt(__doc__, version='0.1.0')
    fname = args.get('INFILE')
    fout = args.get('--output', None)

    with open(fname, 'r') as stream:
        yml = yaml.load(stream)

    text = build(yml)

    if fout:
        with open(fout, 'w') as f:
            f.write("{:s}".format(text))
    else:
        sys.stdout.write(text)
