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

(
 cd "$CLIQUEROOT/deps/lib/python"*"/site-packages/fcdjangoutils"
 git checkout git@github.com:freecode/fcdjangoutils.git
)

wget http://mirror.i2p2.de/i2psource_0.8.1.tar.bz2
tar -xvjf i2psource_0.8.1.tar.bz2
cp -a i2p-0.8.1/apps/sam/python/src/i2p $CLIQUEROOT/deps/lib/python*/site-packages/

cd /
rm -rf "$TMPDIR"