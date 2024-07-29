import click
import os
import subprocess
import shutil
import yaml

def check_azure_cli():
    if shutil.which("az") is None:
        click.echo("Azure CLI not found. Installing...")
        subprocess.run(['curl', '-sL', 'https://aka.ms/InstallAzureCLIDeb', '|', 'sudo', 'bash'], check=True)
    else:
        click.echo("Azure CLI is already installed.")

@click.command()
@click.option('--eth-rpc-url', prompt='ETH RPC URL', help='The ETH RPC endpoint.')
@click.option('--deployer-address', prompt='Deployer Address', help='The address to deploy contracts.')
@click.option('--deployer-private-key', prompt='Deployer Private Key', hide_input=True, help='The private key of the deployer.')
@click.option('--selic-sequencer-address', prompt='SELIC Sequencer Address', help='The address for SELIC sequencer.')
@click.option('--bcb-sequencer-address', prompt='BCB Sequencer Address', help='The address for BCB sequencer.')
@click.option('--selic-cnpj8', prompt='SELIC CNPJ8', help='The CNPJ8 code for SELIC.')
@click.option('--bcb-cnpj8', prompt='BCB CNPJ8', help='The CNPJ8 code for BCB.')
@click.option('--bank-a-cnpj8', prompt='Bank A CNPJ8', help='The CNPJ8 code for Bank A.')
@click.option('--bank-b-cnpj8', prompt='Bank B CNPJ8', help='The CNPJ8 code for Bank B.')
@click.option('--bank-a-sequencer-address', prompt='Bank A Sequencer Address', help='The address for Bank A sequencer.')
@click.option('--bank-b-sequencer-address', prompt='Bank B Sequencer Address', help='The address for Bank B sequencer.')
@click.option('--deployment-type', type=click.Choice(['local', 'kubernetes', 'aks']), prompt='Deployment Type', help='The type of deployment (local, kubernetes, aks).')
@click.option('--azure-subscription-id', prompt='Azure Subscription ID', help='The Azure Subscription ID.')
@click.option('--azure-resource-group', prompt='Azure Resource Group', help='The Azure Resource Group containing the AKS cluster.')
@click.option('--aks-cluster-name', prompt='AKS Cluster Name', help='The name of the AKS cluster.')
def setup_nova(eth_rpc_url, deployer_address, deployer_private_key, selic_sequencer_address, bcb_sequencer_address, selic_cnpj8, bcb_cnpj8, bank_a_cnpj8, bank_b_cnpj8, bank_a_sequencer_address, bank_b_sequencer_address, deployment_type, azure_subscription_id, azure_resource_group, aks_cluster_name):
    """Simple program to set up and deploy Nova rollup node."""

    env_content = f"""
export ETH_RPC_URL={eth_rpc_url}
export DEPLOYER_ADDRESS={deployer_address}
export DEPLOYER_PRIVATE_KEY={deployer_private_key}
export SELIC_SEQUENCER_ADDRESS={selic_sequencer_address}
export BCB_SEQUENCER_ADDRESS={bcb_sequencer_address}
export SELIC_CNPJ8={selic_cnpj8}
export BCB_CNPJ8={bcb_cnpj8}
export BANK_A_CNPJ8={bank_a_cnpj8}
export BANK_B_CNPJ8={bank_b_cnpj8}
export BANK_A_SEQUENCER_ADDRESS={bank_a_sequencer_address}
export BANK_B_SEQUENCER_ADDRESS={bank_b_sequencer_address}
export ROLLUP_BATCH_EXPIRE_BLOCK=64
export USE_MOCK_VERIFIER=false
"""

    with open('/opt/nova/contracts/example.env', 'w') as env_file:
        env_file.write(env_content)
    
    click.echo('Environment variables saved to /opt/nova/contracts/example.env')

    if deployment_type == 'local':
        deploy_local()
    elif deployment_type == 'kubernetes':
        deploy_kubernetes()
    elif deployment_type == 'aks':
        deploy_aks(azure_subscription_id, azure_resource_group, aks_cluster_name)

def deploy_local():
    click.echo('Starting local deployment...')
    # Load Docker images
    subprocess.run(['docker', 'load', '-i', '/opt/nova/nova-rollup_20240609.tar'])

    click.echo('Docker images loaded successfully.')

    # Unzip smart contract tarball
    subprocess.run(['tar', '-zxf', '/opt/nova/nova-smartcontract_20240615.tar.gz', '-C', '/opt/nova/contracts/'])

    click.echo('Smart contract files unzipped successfully.')

    # Install Foundry
    subprocess.run(['curl', '-L', 'https://foundry.paradigm.xyz', '|', 'bash'])
    subprocess.run(['foundryup'])

    click.echo('Foundry installed successfully.')

    # Generate keypairs
    keypairs = subprocess.run(['cast', 'wallet', 'new'], capture_output=True, text=True).stdout
    with open('/opt/nova/keypairs.txt', 'w') as key_file:
        key_file.write(keypairs)

    click.echo('Keypairs generated and saved to /opt/nova/keypairs.txt')

    # Deploy smart contracts
    subprocess.run(['bash', '-c', 'source /opt/nova/contracts/example.env && cd /opt/nova/contracts && yarn && npx hardhat compile && npx hardhat run script/hardhat/deploy-common.ts --network pilot && npx hardhat run script/hardhat/deploy-wcbdc.ts --network pilot && npx hardhat run script/hardhat/deploy-rcbdc.ts --network pilot'])

    click.echo('Smart contracts deployed successfully.')

def deploy_kubernetes():
    click.echo('Starting Kubernetes deployment...')
    subprocess.run(['ansible-playbook', '-i', 'ansible/kubernetes_hosts', 'ansible/deploy_nova_k8s.yml'])

def deploy_aks(azure_subscription_id, azure_resource_group, aks_cluster_name):
    click.echo('Starting AKS deployment...')
    # Ensure Azure CLI is installed
    check_azure_cli()
    # Login to Azure
    subprocess.run(['az', 'login'], check=True)
    # Set the Azure subscription
    subprocess.run(['az', 'account', 'set', '--subscription', azure_subscription_id], check=True)
    # Get AKS credentials
    subprocess.run(['az', 'aks', 'get-credentials', '--resource-group', azure_resource_group, '--name', aks_cluster_name], check=True)
    # Run the Ansible playbook for AKS
    subprocess.run(['ansible-playbook', '-i', 'ansible/aks_hosts', 'ansible/deploy_nova_aks.yml'])

if __name__ == '__main__':
    setup_nova()
