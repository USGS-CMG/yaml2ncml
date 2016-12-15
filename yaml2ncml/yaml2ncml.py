from __future__ import (absolute_import, division, print_function)

import os
import sys

from collections import OrderedDict

import netCDF4
import ruamel.yaml as yaml

from docopt import docopt
from jinja2 import Template

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


def add_bed_coord(text, yml):
    ncfile = os.path.join(yml['aggregation']['dir'],
                          yml['aggregation']['sample_file'])
    nc = netCDF4.Dataset(ncfile)
    bed_coord_var = """<variable name="Nbed" shape="Nbed" type="double">
      <attribute name="long_name" value="pseudo coordinate at seabed points"/>
      <attribute name="standard_name" value="ocean_sigma_coordinate"/>
      <attribute name="positive" value="up"/>
      <attribute name="formula_terms" value="sigma: Nbed eta: zeta depth: h"/>
      <values start="-1.0" increment="-0.01"/>
    </variable>\n """
    if 'Nbed' in nc.dimensions.keys():
        text += bed_coord_var
    return text


def add_var_atts(text, yml):
    ncfile = os.path.join(yml['aggregation']['dir'],
                          yml['aggregation']['sample_file'])
    nc = netCDF4.Dataset(ncfile)
    ncv = nc.variables

    # Get a list of all variables more than 1D.
    vars = [var for var, vart in ncv.items() if vart.ndim > 1]


#   identify all the rho, u and v vars

    rho_vars = [var for var in vars if 'eta_rho' in
                ncv[var].dimensions and 'xi_rho' in ncv[var].dimensions]
    u_vars = [var for var in vars if 'eta_u' in
              ncv[var].dimensions and 'xi_u' in ncv[var].dimensions]
    v_vars = [var for var in vars if 'eta_v' in
              ncv[var].dimensions and 'xi_v' in ncv[var].dimensions]

    vars_all = set(vars)
    vars_include = set(yml['variables']['include'])
    vars_exclude = set(yml['variables']['exclude'])

#   include/exclude only variables that actually occur in variable list

    vars_include = vars_all.intersection(vars_include)
    vars_exclude = vars_all.intersection(vars_exclude)

#   If there are variables excluded, exclude them and keep all rest.
#   If no variables are excluded, take just the included variables
#   If no variables are included or excluded, take all variables (leave
#     list of variables unchanged)

    if vars_exclude:
        vars_display = vars_all - vars_all.intersection(vars_exclude)
    else:
        if vars_include:
            vars_display = vars_all.intersection(vars_include)
        else:
            vars_display = vars_all

#   remove some variables we never want (if they exist)
    Tobc = set(['Tobc_in', 'Tobc_out'])
    vars_display = vars_display - vars_display.intersection(Tobc)

    vars_display = list(vars_display)

# add the variable attributes: S-grid stuff, display=T|F, ...
    for var in vars:
        text += '<variable name="{:s}">\n'.format(var)
        try:
            text += attribute_name('standard_name', cf[var])
        except:
            pass
        text += attribute_name('grid', 'grid')

        if 'Nbed' in ncv[var].dimensions:
            text += attribute_name('coordinates', ncv[var].coordinates+' Nbed')

        if var in vars_display:
            text += attribute_name('display', 'True')
        else:
            text += attribute_name('display', 'False')

        text += attribute_name('content_coverage_type', 'modelResult')
        if var in rho_vars:
            text += attribute_name('location', 'face')
        elif var in u_vars:
            text += attribute_name('location', 'edge1')
        elif var in v_vars:
            text += attribute_name('location', 'edge2')
        text += '</variable>\n\n'

# write standard_name for time coordinate variable
    var = 'ocean_time'
    if var in ncv.keys():
        try:
            text += '\n<variable name="{:s}">\n'.format(var)
            text += attribute_name('standard_name', cf[var])
            text += '</variable>\n\n'
        except:
            pass

    nc.close()
    return text


def write_grid_var(text):
    grid_var = """<variable name="grid" type="int">
        <attribute name="cf_role" value="grid_topology"/>
        <attribute name="topology_dimension" type="int" value="2"/>
        <attribute name="node_dimensions" value="xi_psi eta_psi"/>
        <attribute name="face_dimensions"
            value="xi_rho: xi_psi (padding: both) eta_rho: eta_psi (padding: both)"/>
        <attribute name="edge1_dimensions" value="xi_u: xi_psi eta_u: eta_psi (padding: both)"/>
        <attribute name="edge2_dimensions" value="xi_v: xi_psi (padding: both) eta_v: eta_psi"/>
        <attribute name="node_coordinates" value="lon_psi lat_psi"/>
        <attribute name="face_coordinates" value="lon_rho lat_rho"/>
        <attribute name="edge1_coordinates" value="lon_u lat_u"/>
        <attribute name="edge2_coordinates" value="lon_v lat_v"/>
        <attribute name="vertical_dimensions" value="s_rho: s_w (padding: none)"/>
    </variable>\n"""  # noqa
    text += grid_var
    return text


def add_aggregation_scan(text, yml):
    agg = yml['aggregation']
    text += '<aggregation dimName="{:s}" type="joinExisting">\n'.format(
        agg['time_var'])
    text += '<scan location="{:s}" regExp="{:s}" subdirs="false"/>\n</aggregation>\n'.format(agg['dir'], agg['pattern'])  # noqa
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
          Hwave='sea_surface_wave_significant_height',
          bed_thickness='sediment_bed_thickness')


def _compose(attrs, name):
    return OrderedDict(
        ('_'.join([name, key]), attrs[name].get(key))
        for key in attrs[name].keys() if attrs[name].get(key)
    )


templ = Template("""<?xml version="1.0" encoding="UTF-8"?>
<netcdf xmlns="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2">
{% for name, value in global_attrs | dictsort %}  <attribute name="{{ name }}" type="String" value="{{ value }}"/>
{% endfor %}
</netcdf>""")  # noqa


def build(yml):
    global_attrs = OrderedDict([('Conventions', 'CF-1.6, SGRID-0.1, ACDD-1.3'),
                                ('cdm_data_type', 'Grid')])

    attrs = yml['dataset']
    # Simple attribute.
    simple_pairs = ['id', 'title', 'summary', 'naming_authority', 'project',
                    'license', 'references', 'acknowledgments']
    global_attrs.update(OrderedDict((key, attrs.get(key))
                                    for key in simple_pairs if attrs.get(key)))
    # Composed attributes.
    global_attrs.update(_compose(attrs, name='creator'))
    global_attrs.update(_compose(attrs, name='publisher'))
    global_attrs.update(_compose(attrs, name='contributor'))

    text = templ.render(global_attrs=global_attrs)

    text = add_var_atts(text, yml)
    text = write_grid_var(text)
    text = add_bed_coord(text, yml)
    text = add_aggregation_scan(text, yml)
    text += '</netcdf>\n'
    return text


def main():
    args = docopt(__doc__, version='0.6.0')
    fname = args.get('INFILE')
    fout = args.get('--output', None)

    with open(fname, 'r') as stream:
        yml = yaml.load(stream, Loader=yaml.RoundTripLoader)

    text = build(yml)

    if fout:
        with open(fout, 'w') as f:
            f.write("{:s}".format(text))
    else:
        sys.stdout.write(text)
