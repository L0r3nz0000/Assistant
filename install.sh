sudo apt update
sudo apt install python3 python3-pip portaudio19-dev pulseaudio sox flac -y

if [ ! -d ".venv" ]; then
  echo "Sto creando l'ambiente virtuale"
  python3 -m venv .venv
else
  echo "Ambiente virtuale python già presente"
fi

echo "Attivando l'ambiente virtuale"
source .venv/bin/activate
pip install -r requirements.txt

echo "Creando il file start.sh"
echo "pulseaudio --start
source $(pwd)/.venv/bin/activate
python3 $(pwd)/main.py" > start.sh

sudo chmod +x start.sh

echo "[Unit]
Description=Assistente vocale
After=network.target

[Service]
ExecStart=$(pwd)/start.sh
WorkingDirectory=$(pwd)
User=$(whoami)
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
" | sudo tee /etc/systemd/system/Assistant.service > /dev/null

sudo systemctl daemon-reload