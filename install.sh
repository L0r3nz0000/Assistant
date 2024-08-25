sudo su
apt update
apt install python3 python3-pip portaudio19-dev pulseaudio sox flac -y

if [ -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt

cd /etc/systemd/system/

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
" > Assistant.service

systemctl daemon-reload