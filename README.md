# grism_overlap
The Grism Overlap tool is a pure Python (3.7, 3.8, 3.9) application to allow evaluation of which telescope orientations may cause overlap for the NIRISS slitless spectroscopy modes (WFSS and SOSS). 

# Installation

To install, clone this repo or do:

```
pip install grism-overlap
```

# Running The Code

To run the software GUI, open a Terminal session in the `grism_overlap` directory and do:

```
python grism_overlap/grism_overlap_gui.py
```

To test the code one needs at minimum a Mirage NIRISS point source input file, so an example is provided in `stars_bd601753_gaia_allfilters.list`.  This file is for the field of the photometric standard BD+30 1753, the star being source 312 on the list at sky position RA=261.217858, Dec=60.430781.  This is suitable for testing the SOSS mode case.  

Another example more suitable for the WFSS case is provided in the file `stars_wdfield_combined_allfilters.list`.  The target here is WD1657+343.  This star, another photometric standard, is star 158 in the list at sky position RA=254.713015, Dec=34.314677.
 
Documentation is available in the `grism_overlap.pdf` file, which shows how the code can be used.

