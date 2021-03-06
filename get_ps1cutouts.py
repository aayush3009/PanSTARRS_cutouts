
# Query the PanSTARRS-1 image server and download relevant FITS images for objects in a target list
# Create cutouts around the RA and Dec provided
# Has built-in capability to work with some or all filters!
# Created by Aayush Saxena (Leiden Observatory)
# 02/03/2017


import numpy as np
import glob
import os
import urllib

from astropy.io import fits
from astropy.io.fits import getheader

#########################################
# Input text file format: ID RA DEC
# Edit filename here:
input_file = "id_ra_dec.txt"
# Currently, ID must be a number but this
# will be updated in a future version
#########################################

data = np.genfromtxt(input_file) # Input file containing the catalogue

objid = np.zeros(len(data))
ra = np.zeros(len(data))
dec = np.zeros(len(data))

for i in range(len(data)):
    objid[i] = data[i][0]   # Object ID column in the input table
    ra[i] = data[i][1]      # RA column
    dec[i] = data[i][2]     # Dec column
    
###########################################
# Choose the size of cutout (degrees)
cutout_size = 0.1
###########################################


# Build the PS data query script

filters = ['g', 'r', 'i', 'z', 'y']

for filt in filters:
    for i in range(len(data)):
        script = "http://ps1images.stsci.edu/cgi-bin/ps1filenames.py?ra=%.3f&dec=%.3f&filters=%s" %(ra[i], dec[i], filt)

        urllib.urlretrieve(script,'test.txt')
        f1 = open('test.txt', 'r')

        # Split the output generated by the script to target the image file in PS1 server
        for line in f1:
            splitline = line.split()
            print splitline[7]

        # Build the url that points to the relevant image in the PS1 server
        obj = str(objid[i])[:-2]
        outfile_name = obj+'cutout_online.fits'
        url = 'http://ps1images.stsci.edu'+splitline[7]
        os.system('wget %s -O %s' %(url, outfile_name))

        # PS1 images do not have image data as PrimaryHDU for some reason
        # Now save the primary HDU as a new fits file
        hdu = fits.open(outfile_name)
        hdr = getheader(outfile_name, 1)

        scidata = hdu[1].data
        scidata.shape

        outfile = obj+'cutout.fits'
        fits.writeto(outfile, scidata, hdr, overwrite=True)
        # Clean up unnecessary files
        os.system('rm %s' %outfile_name)

        hdu.close()

        # Finally, create cutout
        cutout_file = obj+'ps1_'+filt+'.fits'
        # Here is where mSubimage and Montage come into the picture
        os.system('mSubimage %s %s %.2f %.2f %f' %(outfile, cutout_file, ra[i], dec[i], cutout_size))

        os.system('rm %s' %outfile)

    print "All objects for filter %s done!!" %filt
    
    # Additional bits of code to move cutouts into different directories for different filters
    # Uncomment to enable this.
#     os.system('mkdir ps1_%s_cutouts' %filt)
#     os.system('mv *%s.fits ps1_%s_cutouts' %(filt, filt))

print "All done!!!"

