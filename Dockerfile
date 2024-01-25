#
# This example Dockerfile illustrates a method to install
# additional packages on top of NVIDIA's TensorFlow container image.
#
# To use this Dockerfile, use the `docker build` command.
# See https://docs.docker.com/engine/reference/builder/
# for more information.
#
FROM nvcr.io/nvidia/tensorflow:23.11-tf2-py3

# Install my-extra-package-1 and my-extra-package-2
RUN apt-get update && apt-get upgrade -y &&apt-get install -y --no-install-recommends \
        wget \
        git \
        vim \
        unzip \
        libgl1-mesa-glx \
        dssp \
        curl && \
    apt-get install -y --no-install-recommends\
          libeigen3-dev \
          libgmp-dev \
          libgmpxx4ldbl \
          libmpfr-dev \
          libboost-dev \
          libboost-thread-dev \
          libtbb-dev \
          python3-pybind11 \
          pybind11-dev \
          libboost-all-dev \
          python3-dev && \
    rm -rf /var/lib/apt/lists/

#TODO
RUN export https_proxy= && \
    export http_proxy=  

RUN mkdir /workspace/cmake_install && \
    cd /workspace/cmake_install 
RUN wget https://github.com/Kitware/CMake/releases/download/v3.27.9/cmake-3.27.9.tar.gz && \
    tar -zxvf cmake-3.27.9.tar.gz && \
    cd cmake-3.27.9 && \
    ./bootstrap --prefix=/workspace/cmake_install && \
    make -j$(nproc) && \
    make install && \
    rm -rf /workspace/cmake_install/cmake-3.27.9.tar.gz
RUN echo alias cmake=/workspace/cmake_install/bin/cmake >> ~/.bash_aliases && \
    source ~/.bash_aliases

RUN mkdir /workspace/install && \
    cd /workspace/install

RUN wget https://github.com/Electrostatics/apbs/releases/download/v3.4.1/APBS-3.4.1.Linux.zip && \
    git clone https://github.com/PyMesh/PyMesh.git && \
    wget https://github.com/Electrostatics/pdb2pqr/archive/refs/tags/v3.6.1.zip && \
    git clone https://github.com/rlabduke/reduce.git && \
    wget https://ccsb.scripps.edu/msms/download/933/

RUN cd PyMesh && \
    git update --init && \
    git submodule foreach 'git checkout -f' && \
    export PYMESH_PATH=`pwd` && \
    pip install -r $PYMESH_PATH/python/requirements.txt && \
    sed -i '20 i #include <cstddef>' /workspace/install/PyMesh/third_party/draco/src/draco/core/hash_utils.h && \
    sed -i '20 a #include <cstring>' /workspace/install/PyMesh/third_party/draco/src/draco/io/parser_utils.cc && \
    sed -i '20 a #include <limits>' /workspace/install/PyMesh/third_party/draco/src/draco/io/parser_utils.cc && \
    echo "SET(CMAKE_C_FLAGS " -fcommon ${CMAKE_C_FLAGS}")" >> /workspace/install/PyMesh/third_party/mmg/CMakeLists.txt && \
    ./build.py all && \
    cd $PYMESH_PATH && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make tests && \
    cd .. && ./setup.py build && \
    ./setup.py install && cd /workspace/install
    #TODO import collections.abc as collections 
    # /usr/local/lib/python3.10/dist-packages/nose/plugins/attrib.py
    # /usr/local/lib/python3.10/dist-packages/nose/suite.py
    # /usr/local/lib/python3.10/dist-packages/nose/case.py
    #TODO np.float->float
    # /usr/local/lib/python3.10/dist-packages/pymesh2-0.3-py3.10-linux-x86_64.egg/pymesh/misc/quaternion.py


# RUN wget https://github.com/Electrostatics/apbs/releases/download/v3.4.1/APBS-3.4.1.Linux.zip && \
RUN unzip APBS-3.4.1.Linux.zip && \
    rm -rf /workspace/install/APBS-3.4.1.Linux.zip

# Run wget https://github.com/Electrostatics/pdb2pqr/archive/refs/tags/v3.6.1.zip && \
RUN unzip v3.6.1.zip && \
    cd pdb2pqr-3.6.1 && \
    python setup.py install && \
    rm -rf /workspace/install/v3.6.1.zip && cd /workspace/install

# RUN git clone https://github.com/rlabduke/reduce.git && \
RUN cd /workspace/install/reduce && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && cd /workspace/install

# RUN wget https://ccsb.scripps.edu/msms/download/933/ && \
RUN mv index.html msms_i86_64Linux2_2.6.1.tar.gz && \
    mkdir msms && cd msms && \
    tar zxvf ../msms_i86_64Linux2_2.6.1.tar.gz && \
    ln -s /workspace/install/msms/msms.x86_64Linux2.2.6.1 /usr/local/bin/msms && \
    ln -s /workspace/install/msms/pdb_to_xyzr* /usr/local/bin && cd /workspace/install
    #TODO fix a bug
    # /workspace/install/msms/atmtypenumbers

# Setup environment variables 
ENV MSMS_BIN /usr/local/bin/msms
ENV APBS_BIN /workspace/install/APBS-3.4.1.Linux/bin
ENV MULTIVALUE_BIN /workspace/install/APBS-3.4.1.Linux/share/apbs/tools/bin/multivalue
ENV PDB2PQR_BIN /workspace/install/pdb2pqr-3.6.1
RUN export PATH="/workspace/install/APBS-3.4.1.Linux/share/apbs/tools/bin:$PATH"
RUN export PATH="/workspace/install/APBS-3.4.1.Linux/bin:$PATH"

RUN pip3 install matplotlib 
RUN pip3 install ipython Biopython scikit-learn networkx open3d dask==2023.9.2 packaging

WORKDIR /workspace
CMD [ "bash" ]