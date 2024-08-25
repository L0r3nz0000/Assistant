sudo apt update
sudo apt install python3 python3-pip portaudio19-dev pulseaudio sox flac -y

if [ -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt

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

sudo chmod +x start.sh

sudo systemctl daemon-reload