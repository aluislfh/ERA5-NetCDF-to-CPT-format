import os, glob, sys
import netCDF4
import numpy as np
from datetime import datetime, timedelta
import multiprocessing
import time


def main():

    wdir = '/home/adrian/NWP/S2S_data/ERA5/arnoldo_enviar'
    odir = wdir+'/output_data'

    os.system('mkdir -p ' + odir)

    os.chdir(wdir)
    flist = ['t2m_test_data.nc']  # sorted(glob.glob('*.nc'))

    # Converting all files
    for ffile in flist:
        # open nc file and dims
        nc = netCDF4.Dataset(wdir + '/' + ffile)

        time_var = nc.variables['time']
        times = netCDF4.num2date(time_var, time_var.units)

        lons = nc.variables['longitude'][:]+360
        lats = nc.variables['latitude'][:]

        # load all file variables
        for ncvar in sorted(nc.variables):
            if ncvar != 'longitude' and ncvar != 'latitude' and ncvar != 'time' and ncvar != 'level' and ncvar != 'expver':

                dataproc(ncvar, wdir, odir, ffile, nc, times, lons, lats)


        nc.close()


def dataproc(ncvar, wdir, odir, ffile, nc, times, lons, lats):

    ncdata0 = nc.variables[ncvar]

    if len(ncdata0[:].shape) == 3:
        ftype = ', cpt:zlev='
        levs = ['0.0 meters']
        ncdata = nc.variables[ncvar][:,:,:]

    else:
        ftype = ', cpt:P='
        levs = []
        for z in nc.variables['level'][:]:
            levs.append(str(z)+' mb')
        ncdata = nc.variables[ncvar][:,:,:,:]

    for flev in range(len(levs)):

        nclev = levs[flev]

        print(ffile, nclev, ncvar)

        fout = open(odir+'/era5_'+ncvar+'_z'+nclev.split(' ')[0]+'_'+ffile+'.tsv','w')
        ftext = "xmlns:cpt=http://iri.columbia.edu/CPT/v10/\n"
        fout.write(ftext)
        ftext = "cpt:nfields=1\n"
        fout.write(ftext)
        ftext = "cpt:T	"
        fout.write(ftext)

        for fdate in range(len(times)):
            if fdate == len(times)-1:
                ftime = '%s' % (times[fdate].strftime('%Y-%m'))
                fout.write(ftime)
            else:
                ftime = '%s' % (times[fdate].strftime('%Y-%m'))
                fout.write(ftime+'\t')
        fout.write('\n')


        for fdate in range(len(times)):
            ftime = '%s' % (times[fdate].strftime('%Y-%m'))

            fout.write('cpt:field='+ncvar)
            fout.write(ftype+levs[flev])
            fout.write(', cpt:T='+ftime+', cpt:nrow=')
            fout.write(str(ncdata[:].shape[-1])+', cpt:ncol='+str(ncdata[:].shape[-2]))
            fout.write(', cpt:row=Y, cpt:col=X, cpt:units=')
            fout.write(str(ncdata0.units)+', cpt:missing='+str(ncdata0.missing_value)+'\n')

            yi, xi = (ncdata[:].shape[-2],ncdata[:].shape[-1])

            fout.write('\t')
            for i in range(xi):
                if i == xi-1:
                    fout.write(str(lons[i]))
                else:
                    fout.write(str(lons[i])+'\t')

            fout.write('\n')

            for j in range(yi):
                fout.write(str(lats[j])+'\t')

                for i in range(xi):

                    if len(ncdata[:].shape) == 3:
                        if i == xi-1:
                            fout.write(str(ncdata[fdate,j,i]).center(13))
                        else:
                            fout.write(str(ncdata[fdate,j,i]).center(13)+'\t')

                    else:
                        if i == xi-1:
                            fout.write(str(ncdata[fdate,flev,j,i]).center(13))
                        else:
                            fout.write(str(ncdata[fdate,flev,j,i]).center(13)+'\t')

                fout.write('\n')


if __name__ == '__main__':
    main()



