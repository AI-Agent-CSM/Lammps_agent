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
    libopenmpi-dev \
    vim

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

WORKDIR /
RUN git clone https://github.com/AI-Agent-CSM/Lammps_agent.git
RUN apt install python3.12-venv -y
# Create a virtual environment and install dependencies
RUN python3 -m venv venv \
    && . venv/bin/activate \
    && cd Lammps_agent \
    && pip3 install -r requirements.txt
# Install Grobid client
WORKDIR /Lammps_agent/src/api
RUN git clone https://github.com/kermitt2/grobid_client_python &&\
    cd grobid_client_python &&\
    python3 setup.py install

WORKDIR /Lammps_agent/

# Set the default command for the container
CMD ["bash"]
