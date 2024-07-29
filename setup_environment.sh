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

# Source the shell configuration to update the PATH
if [[ -f ~/.bashrc ]]; then
    source ~/.bashrc
elif [[ -f ~/.zshrc ]]; then
    source ~/.zshrc
elif [[ -f ~/.profile ]]; then
    source ~/.profile
fi

# Run foundryup to install Foundry
foundryup

# Install Python libraries
pip3 install click pyyaml

# Install Azure CLI if not installed
if ! command -v az &> /dev/null
then
    echo "Azure CLI could not be found. Installing..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
else
    echo "Azure CLI is already installed."
fi

# Confirm installations
echo "Installed versions:"
python3 --version
pip3 --version
ansible --version
docker --version
helm version
az --version
foundry --version

echo "Environment setup complete."
