pikayboardexe="#!${SHELL}\ncd \"${PWD}\"\npython pikayboard"

pykayboarddesk="[Desktop Entry]
Type=Application
Version=0.0.1
Name=PikaYboard
Comment=Autocomplete words programme
Exec=/usr/bin/pikayboard
Icon=${PWD}/icon.png
Terminal=false
Categories=Languages;"

sudo make clean

# shellcheck disable=SC2024
sudo echo -n -e "${pykayboarddesk}" > /usr/share/applications/pikayboard.desktop
# shellcheck disable=SC2024
sudo echo -n -e "${pikayboardexe}" > /usr/bin/pikayboard

sudo make all