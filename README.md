# MASIF for RBP

## Build the environment

The coding environment can be setted up by *Docker build* using the Dockerfile in this repository.

The docker image is built based on the image *nvcr.io/nvidia/tensorflow:23.11-tf2-py3*.

### Fix some bugs

There are some bugs in the building process, whose instructions are written in the Dockerfile.

## Download data

The following code is inherited from [https://github.com/LPDI-EPFL/masif](https://github.com/LPDI-EPFL/masif "https://github.com/LPDI-EPFL/masif").

Using the code and RBP_code in the folder data_preparation, we can easily download their PDB information from the PDB database and precalculate some vital features.

## MASIF site

Using the method metioned in [https://github.com/LPDI-EPFL/masif](https://github.com/LPDI-EPFL/masif "https://github.com/LPDI-EPFL/masif"), the code in both *masif_modules* and *masif_site* provides an example to use this kind of frame. 

The code in this part has not been heavily modified
