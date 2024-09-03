#!/bin/bash
sudo apt update
sudo apt install python3 python3-pip portaudio19-dev pulseaudio mpv flac -y

git clone https://github.com/L0r3nz0000/spotify-free-api.git
cd spotify-free-api
python3 -m venv .env
.env/bin/pip install -r requirements.txt
cd ..

if [ ! -d ".venv" ]; then
  echo "Sto creando l'ambiente virtuale"
  python3 -m venv .venv
else
  echo "Ambiente virtuale python già presente"
fi

echo "Attivando l'ambiente virtuale"
source .venv/bin/activate
pip install -r requirements.txt

read -s -p "Inserisci il token api di replicate: " API_TOKEN
echo ""

cd spotify-free-api
chmod +x install.sh
./install.sh
cd ..

echo "[Unit]
Description=Assistente vocale
After=network.target

[Service]
ExecStart=$(pwd)/.venv/bin/python3 $(pwd)/main.py
Environment=\"REPLICATE_API_TOKEN=$API_TOKEN\"
WorkingDirectory=$(pwd)
User=root
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
" | sudo tee /etc/systemd/system/Assistant.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable Assistant
sudo systemctl start Assistant

chmod +x update.sh