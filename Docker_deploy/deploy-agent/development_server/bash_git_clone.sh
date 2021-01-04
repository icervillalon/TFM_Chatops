#! /bin/bash
echo `rm -f requirements.txt`
echo `git clone -n http://icervillalon:FK8YN8QUkksGV6s2Sz69@lab.gsi.upm.es/TFM/tfm-ignaciocervantes.git --depth 1`
echo `git --git-dir /home/tfm/prueba/tfm-ignaciocervantes/.git checkout HEAD development_requirements.txt`
echo `cat development_requirements.txt`