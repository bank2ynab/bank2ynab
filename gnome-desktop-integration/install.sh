#!/bin/bash
cd `dirname "$0"`
echo "[Desktop Entry]" > b2y.desktop
cat <<EOT >> b2y.desktop
Name=bank2ynab
Comment=convert a csv file to ynab format
Exec=`pwd`/run.sh
Terminal=true
Type=Application
Icon=`pwd`/icon.svg
EOT

mv b2y.desktop /home/$USER/.local/share/applications/Bank2YNAB.desktop
chmod 700 /home/$USER/.local/share/applications/Bank2YNAB.desktop
