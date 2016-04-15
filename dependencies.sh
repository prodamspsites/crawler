#!/usr/bin/env bash
# Install Centos packages dependencies
sudo yum -y install openssl-devel
sudo yum -y install mysql-devel
sudo yum -y groupinstall "Development Tools"
sudo yum -y install zlib-devel
sudo yum -y install xz-libs

# Create installation directory
mkdir $HOME/crawler_installation
cd $HOME/crawler_installation

# Install Python 2.7
wget https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tar.xz
xz -d Python-2.7.11.tar.xz
tar -xvf Python-2.7.11.tar
cd Python-2.7.11
./configure --prefix=$HOME/python2.7
make && make install
PYTHON=$HOME/python2.7/bin/python
PYTHON_DIR=$HOME/python2.7/bin/

# Install Setuptools
cd $HOME/crawler_installation
wget https://pypi.python.org/packages/source/s/setuptools/setuptools-20.2.2.tar.gz#md5=bf37191cb4c1472fb61e6f933d2006b1
tar -xvf setuptools-20.2.2.tar.gz
cd setuptools-20.2.2
${PYTHON} setup.py install

# Install PIP
cd $HOME/crawler_installation
wget https://bootstrap.pypa.io/get-pip.py
${PYTHON} get-pip.py

# Install Virtualenv
${PYTHON_DIR}/pip install virtualenv

# Create virtualenv directory
${PYTHON_DIR}/virtualenv $HOME/env27/

# Install Python libraries
cd $HOME
source $HOME/env27/bin/activate
git clone https://github.com/monjebour/crawler.git
cd crawler
pip install -r requirements.txt

# Remove installation dir
sudo rm -rf $HOME/crawler_installation
echo "Installation process finished!"