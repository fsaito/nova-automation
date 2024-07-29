#!/bin/bash

# Update the package list
sudo apt update

# Install Python 3 and pip
sudo apt install -y python3 python3-pip

# Install Ansible
sudo apt install -y ansible

# Install Docker
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash

# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Install Python libraries
pip3 install click pyyaml

# Confirm installations
echo "Installed versions:"
python3 --version
pip3 --version
ansible --version
docker --version
helm version
foundry --version

echo "Environment setup complete."

