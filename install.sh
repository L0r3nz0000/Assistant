sudo su
apt update
apt install python3 python3-pip portaudio19-dev -y

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

