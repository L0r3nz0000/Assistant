#!/bin/bash
git fetch origin
git reset --hard origin/main
sudo systemctl restart Assistant
