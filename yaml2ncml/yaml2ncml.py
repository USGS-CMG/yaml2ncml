import os
import netCDF4

import yaml


def str_att(name, value):
    if isinstance(value, list):
        value = ','.join(value)
    msg = '  <attribute name="{:s}" type="String" value="{:s}"/>\n'
    return msg.format(name, value)


def header():
    text = '<?xml version="1.0" encoding="UTF-8"?>\n<netcdf xmlns='
    text += '"http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2">\n'
    text += str_att('Conventions','CF-1.6, SGRID-0.1, ACDD-1.3')
    text += str_att('cdm_data_type','Grid')
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
            text += str_att(key,value)
        elif key in ['creator', 'publisher']:
            email = value.get("email", None)
            if email:
                text += str_att('_'.join([key, 'email']), email)
            url = value.get("url", None)
            if url:
                text += str_att('_'.join([key, 'url']), url)
            name = value.get("name", None)
            if name:
                text += str_att('_'.join([key, 'name']), name)
        elif key in ['contributor']:
            role = value.get("role", None)
            if email:
                text += str_att('_'.join([key, 'role']), role)
            email = value.get("email", None)
            if email:
                text += str_att('_'.join([key, 'email']), email)
            url = value.get("url", None)
            if url:
                text += str_att('_'.join([key, 'url']), url)
            name = value.get("name", None)
            if name:
                text += str_att('_'.join([key, 'name']), name)
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

    for var in vars:
        text += '<variable name="{:s}">\n'.format(var)
        try:
            text += str_att('standard_name',cf[var])
        except:
            pass
        text += str_att('grid','grid')
        text += str_att('content_coverage_type','modelResult')
        if var in rho_vars:
            text += str_att('location','face')
        elif var in u_vars:
            text += str_att('location','edge1')
        elif var in v_vars:
            text += str_att('location','edge2')
        text += '</variable>\n\n'
    return text

def write_grid_var(text):
    grid_var="""<variable name="grid" type="int">
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
    </variable>\n """
    text += grid_var
    return text

def add_aggregation_scan(text, a):
    agg = a['aggregation']
    text += '<aggregation dimName="{:s}" type="joinExisting">\n'.format(agg['time_var'])
    text += '<scan location="." regExp="{:s}" subdirs="false"/>\n</aggregation>\n'.format(agg['pattern'])
    return text

# Map ROMS variables to CF standard_names.
cf = dict(zeta='sea_surface_height_above_datum',
          temp='sea_water_potential_temperature',
          salt='sea_water_salinity',
          u='x_sea_water_velocity',
          v='y_sea_water_velocity',
          ubar='barotropic_x_sea_water_velocity',
          vbar='barotropic_y_sea_water_velocity',
          Hwave='sea_surface_wave_significant_height')

if __name__ == '__main__':
    with open("./tests/roms.yaml", 'r') as stream:
        a = yaml.load(stream)

    text = header()
    text = add_global_atts(text, a)
    text = add_var_atts(text, a)
    text = write_grid_var(text)
    text = add_aggregation_scan(text, a)
    text = footer(text)

    with open('{:s}/test6.ncml'.format(a['aggregation']['dir']),'w') as text_file:
        text_file.write("{:s}".format(text))
