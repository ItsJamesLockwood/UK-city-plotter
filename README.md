# UK-city-plotter

This project was created as an exercise in using 'tkinter' and plotting packages in Python.

The project consists of a UI-interface class, 'Geoplotter', which requires the loading of two files: a CSV-file and a map of the UK (see ```./data```).
The user is then able to select from a host of settings to customise the plotting of the top 100 british cities and towns.

![image](https://user-images.githubusercontent.com/33159939/129880170-2757381f-ec9a-4e54-bbfe-f4cc07b74a70.png)

These settings include:
 - distinguishing between towns and cities
 - distinguishing between population sizes
 - include placenames for top 10 cities and towns
 - include legend
 - include hyperlinks leading to Wikipedia pages when placename is clicked

The position of the cities is determined by one of two options:
 - provide the pixel and geographical coordinates of two distinct cities to interpolate the locations of other cities
 - provide geographical coordinates of the image boundaries 

The boundaries for the default image provided in the repository is already encoded as a default option.

The result when the ```Run``` button is pressed is to execute the settings selected by the use to plot the cities and towns on a map of the UK.

![image](https://user-images.githubusercontent.com/33159939/129881545-d6192e28-7a3d-490a-a780-3fb273a33f0f.png)

