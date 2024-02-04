#  This Dockerfile is to build the development environment for the project
#  It will mainly includes the API server, The LAmmbds Project, and NGrok
#  for connecting to the GPT actions.


# Use an official Ubuntu base image
FROM ubuntu:latest

# Set the working directory in the container
WORKDIR /usr/src/app

# Install necessary packages
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    wget \
    git \
    cmake \
    python3 \
    python3-pip \
    libfftw3-dev \
    libopenmpi-dev

# Clone the LAMMPS repository
RUN git clone -b stable https://github.com/lammps/lammps.git lammps

# Create a build directory
WORKDIR /usr/src/app/lammps/build

# Configure the project with CMake
RUN cmake ../cmake

# Build LAMMPS
RUN make -j $(nproc)
RUN make install

# Set the path to the LAMMPS executable
ENV PATH="/usr/src/app/lammps/build:${PATH}"

# Optional: Install Python packages for interacting with LAMMPS (like PyLammps)
# RUN pip3 install numpy
# RUN pip3 install lammps-cython

# Set the default command for the container
CMD ["bash"]
