# Copyright Cartopy Contributors
#
# This file is part of Cartopy and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.

from __future__ import (absolute_import, division, print_function)

import matplotlib.pyplot as plt
from matplotlib.testing.decorators import cleanup
import pytest

from cartopy.tests.mpl import MPL_VERSION, ImageTesting
import cartopy.crs as ccrs
from cartopy.io.ogc_clients import _OWSLIB_AVAILABLE


@pytest.mark.network
@pytest.mark.skipif(not _OWSLIB_AVAILABLE, reason='OWSLib is unavailable.')
@pytest.mark.xfail(raises=KeyError, reason='OWSLib WMTS support is broken.')
@ImageTesting(['wmts'], tolerance=7.56 if MPL_VERSION < '2' else 0)
def test_wmts():
    ax = plt.axes(projection=ccrs.PlateCarree())
    url = 'https://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi'
    # Use a layer which doesn't change over time.
    ax.add_wmts(url, 'MODIS_Water_Mask')


@pytest.mark.network
@pytest.mark.skipif(not _OWSLIB_AVAILABLE, reason='OWSLib is unavailable.')
@cleanup
def test_wms_tight_layout():
    ax = plt.axes(projection=ccrs.PlateCarree())
    url = 'http://vmap0.tiles.osgeo.org/wms/vmap0'
    layer = 'basic'
    ax.add_wms(url, layer)
    ax.figure.tight_layout()


@pytest.mark.network
@pytest.mark.xfail((5, 0, 0) <= ccrs.PROJ4_VERSION < (5, 1, 0),
                   reason='Proj Orthographic projection is buggy.',
                   strict=True)
@pytest.mark.skipif(not _OWSLIB_AVAILABLE, reason='OWSLib is unavailable.')
@ImageTesting(['wms'], tolerance=7.79 if MPL_VERSION < '2' else 0.02)
def test_wms():
    ax = plt.axes(projection=ccrs.Orthographic())
    url = 'http://vmap0.tiles.osgeo.org/wms/vmap0'
    layer = 'basic'
    ax.add_wms(url, layer)
