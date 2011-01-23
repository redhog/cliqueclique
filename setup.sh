#! /bin/bash

CLIQUEROOT=$(pwd)

virtualenv deps
source deps/bin/activate

TMPDIR=$(mktemp -d)
cd "$TMPDIR"

pip install django
pip install django-staticfiles
pip install django-idmapper
pip install django-registration
pip install pydot
pip install jogging
# Install matplotlib w/o using pip to work around this bug: http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg12827.html
#pip install matplotlib
easy_install "http://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-0.98.5/matplotlib-0.98.5.3.tar.gz"

(
 cd "$CLIQUEROOT/deps/lib/python"*"/site-packages"
 git clone git://github.com/redhog/fcdjangoutils.git
)

wget http://mirror.i2p2.de/i2psource_0.8.1.tar.bz2
tar -xvjf i2psource_0.8.1.tar.bz2
cp -a i2p-0.8.1/apps/sam/python/src/i2p $CLIQUEROOT/deps/lib/python*/site-packages/

cd /
rm -rf "$TMPDIR"