FROM fedora
RUN dnf install -y gcc-c++ gcc make cmake git \
    bzip2 bzip2-devel xz xz-devel hwloc-devel blas blas-devel lapack lapack-devel boost-devel \
    libatomic which compat-openssl10 vim-enhanced wget zlib-devel \
    python3-flake8 gdb sudo python36 openmpi-devel sqlite-devel sqlite \
    findutils openssl-devel lm_sensors-devel

ARG CPUS
ARG BUILD_TYPE=Release

RUN ln -s /usr/lib64/openmpi/lib/libmpi_cxx.so /usr/lib64/openmpi/lib/libmpi_cxx.so.1
RUN ln -s /usr/lib64/openmpi/lib/libmpi.so /usr/lib64/openmpi/lib/libmpi.so.12
ENV PYVER 3.6.8
RUN wget https://www.python.org/ftp/python/${PYVER}/Python-${PYVER}.tgz
RUN tar xf Python-${PYVER}.tgz
WORKDIR /Python-${PYVER}
RUN ./configure
RUN make -j ${CPUS} install

# Make headers available
RUN cp /Python-${PYVER}/pyconfig.h /Python-${PYVER}/Include
RUN ln -s /Python-${PYVER}/Include /usr/include/python${PYVER}

RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org numpy tensorflow keras CNTK pytest
RUN pip3 install numpy tensorflow keras CNTK pytest
RUN pip3 install pandas
WORKDIR /

RUN git clone https://github.com/STEllAR-GROUP/hpx.git && \
    cd /hpx && \
    git checkout -b pearc 21b676197ac8fdcbb63b1b4069cf6983a046fd02 && \
    mkdir -p /hpx/build && \
    cd /hpx/build && \
    cmake -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
      -DHPX_WITH_MALLOC=system \
      -DHPX_WITH_MORE_THAN_64_THREADS=ON \
      -DHPX_WITH_MAX_CPU_COUNT=80 \
      -DHPX_WITH_EXAMPLES=Off \
      .. && \
    make -j ${CPUS} install && \
    rm -f $(find . -name \*.o)

RUN git clone https://github.com/pybind/pybind11.git && \
    cd /pybind11 && \
    git checkout -b pearc 4f72ef846fe8453596230ac285eeaa0ce3278bb4 && \
    mkdir -p /pybind11/build && \
    cd /pybind11/build && \
    cmake -DCMAKE_BUILD_TYPE=${BUILD_TYPE} -DPYBIND11_PYTHON_VERSION=${PYVER} .. && \
    make -j ${CPUS} install && \
    rm -f $(find . -name \*.o)

RUN git clone https://bitbucket.org/blaze-lib/blaze.git && \
    cd /blaze && \
    git checkout -b pearc 48f55121eecd32cfea25d3027be834f74a513e88 && \
    mkdir -p /blaze/build && \
    cd /blaze/build && \
    cmake -DCMAKE_BUILD_TYPE=${BUILD_TYPE} .. && \
    make -j ${CPUS} install && \
    rm -f $(find . -name \*.o)

RUN git clone https://github.com/STEllAR-GROUP/blaze_tensor.git && \
    cd /blaze_tensor && \
    git checkout -b pearc f202f40067992f7370275118911a0cd2f65d6053 && \
    mkdir -p /blaze_tensor/build && \
    cd /blaze_tensor/build && \
    cmake -DCMAKE_BUILD_TYPE=${BUILD_TYPE} .. && \
    make -j ${CPUS} install && \
    rm -f $(find . -name \*.o)

COPY build.sh /usr/local/bin/build.sh
COPY als.py /home/jovyan/als.py
COPY als_phylanx.py /home/jovyan/als_phylanx.py

COPY run_als.sh /home/jovyan/run_als.sh
RUN chmod +x /home/jovyan/run_als.sh

COPY lra.py /home/jovyan/lra.py

COPY MovieLens_20m.csv /home/jovyan/MovieLens_20m.csv
COPY 10kx10k.csv /home/jovyan/10kx10k.csv

RUN chmod +x /usr/local/bin/build.sh

RUN build.sh install
RUN echo "ALL            ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers
COPY Dockerfile /Dockerfile
RUN useradd -m jovyan
RUN chown -R jovyan:jovyan /home/
USER jovyan
WORKDIR /home/jovyan
ENV LD_LIBRARY_PATH /home/jovyan/install/phylanx/lib64:/usr/local/lib64:/home/jovyan/install/phylanx/lib/phylanx:/usr/lib64/openmpi/lib