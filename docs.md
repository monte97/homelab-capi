# 📖 Proxmox CAPI Kubernetes - Complete Documentation

Comprehensive guide for deploying Kubernetes clusters on Proxmox using Cluster API, Talos Linux, and the included Python YAML generator.

## 📋 Table of Contents

1. [Environment Setup](#environment-setup)
2. [Proxmox Configuration](#proxmox-configuration)  
3. [Talos Linux Setup](#talos-linux-setup)
4. [Cluster API Installation](#cluster-api-installation)
5. [Python Generator Guide](#python-generator-guide)
6. [Cluster Deployment](#cluster-deployment)
7. [Access and Verification](#access-and-verification)
8. [Worker Node Management](#worker-node-management)
9. [Configuration Reference](#configuration-reference)
10. [Troubleshooting](#troubleshooting)

---

## 🏗️ Environment Setup

### Management Cluster Creation

Create a local Kubernetes cluster to manage your Proxmox clusters:

```bash
# Install kind if not already available
# See: https://kind.sigs.k8s.io/docs/user/quick-start/

# Create management cluster
kind create cluster --name capi-management

# Verify cluster
kubectl cluster-info --context kind-capi-management
```

### Python Environment Setup

The YAML generator requires Python 3.7+ with specific dependencies:

```bash
# Create virtual environment
python3 -m venv k8s-generator-env

# Activate environment
source k8s-generator-env/bin/activate  # Linux/macOS
# k8s-generator-env\Scripts\activate  # Windows

# Install dependencies
pip install jinja2 pyyaml

# Verify installation
python cluster_generator.py --help
```

---

## 🖥️ Proxmox Configuration

### User and Token Setup

1. **Create dedicated user for CAPI**:
   ```bash
   # SSH to Proxmox host
   pveum user add capi@pve --comment "Cluster API User"
   ```

2. **Assign required permissions**:

   ```bash
    pveum user add capi@pve
    pveum aclmod / -user capi@pve -role Administrator
    pveum user token add capi@pve capi-token --privsep 0
   ```

3. **Generate API token**:
   ```bash
   # Create token (save the output!)
   pveum user token add capi@pve capi-token --privsep=0
   ```

  ```console
    ┌──────────────┬──────────────────────────────────────┐                                   
    │ key          │ value                                │                                   
    ╞══════════════╪══════════════════════════════════════╡                                   
    │ full-tokenid │ capi@pve!capi-token                  │                                   
    ├──────────────┼──────────────────────────────────────┤                                   
    │ info         │ {"privsep":"0"}                      │                                   
    ├──────────────┼──────────────────────────────────────┤                                   
    │ value        │ your-generated-secret                │                                   
    └──────────────┴──────────────────────────────────────┘                                   
  ```

---

## 🐧 Talos Linux Setup

### Download and Prepare Template

1. **Download Talos ISO**:
  Get latest release with `nocloud` and `quemu-agent` support neabled
   ```bash
   wget https://factory.talos.dev/image/ce4c980550dd2ab1b17bbf2b08801c7eb59418eafe8f279833297925d67c7515/v1.9.5/metal-amd64.iso
   ```

2. **Create VM template in Proxmox**:
   - Create new VM
   - Configure with appropriate resources
   - enable qemu agent
   - Attach Talos ISO as boot device
   - Convert to template

3. **Install QEMU Guest Agent**:
   ```bash
   # On Proxmox host
   apt install qemu-guest-agent
   ```

---

## ⚙️ Cluster API Installation

### Configure clusterctl

1. **Download clusterctl**:
   ```bash
    # Install clusterctl
    curl -L https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.10.3/clusterctl-linux-amd64 -o clusterctl
    sudo install -o root -g root -m 0755 clusterctl /usr/local/bin/clusterctl
   ```

2. **Setup provider configuration**:
   ```bash
   mkdir -p ~/.cluster-api
   cat > ~/.cluster-api/clusterctl.yaml << EOF
   providers:
     - name: "sidero"
       url: "https://github.com/siderolabs/cluster-api-bootstrap-provider-talos/releases/download/v0.6.7/bootstrap-components.yaml"
       type: "BootstrapProvider"
     - name: "sidero"
       url: "https://github.com/siderolabs/cluster-api-control-plane-provider-talos/releases/download/v0.5.8/control-plane-components.yaml"
       type: "ControlPlaneProvider"  
     - name: "infrastructure-proxmox"
       url: "https://github.com/ionos-cloud/cluster-api-provider-proxmox/releases/download/v0.6.2/infrastructure-components.yaml"
       type: "InfrastructureProvider"
   EOF
   ```

### Environment Variables

Set required environment variables:

```bash
# Proxmox connection details
export PROXMOX_URL="https://your-proxmox-host:8006/api2/json"
export PROXMOX_TOKEN="capi@pve!capi-token"
export PROXMOX_SECRET="your-generated-secret"
```

```bash
# Optional: Make persistent
echo 'export PROXMOX_URL="https://your-proxmox-host:8006/api2/json"' >> ~/.bashrc
echo 'export PROXMOX_TOKEN="capi@pve!capi-token"' >> ~/.bashrc  
echo 'export PROXMOX_SECRET="your-generated-secret"' >> ~/.bashrc
```

### Initialize CAPI

```bash
# Initialize management cluster
clusterctl init --infrastructure proxmox --ipam in-cluster --control-plane talos --bootstrap talos

# Verify installation
kubectl get pods -A | grep -E "(capi|proxmox|talos)"
```

---

## 🐍 Python Generator Guide

### Quick Start with Generator

```bash
# Generate default configuration
python cluster_generator.py --create-config homelab.yaml

# Review and edit the configuration
vim homelab.yaml

# Generate cluster YAML
python cluster_generator.py --config homelab.yaml --output my-cluster.yaml
```

### Command Line Usage

#### Basic Cluster Generation

```bash
# Simple single-node cluster
python cluster_generator.py \
  --cluster-name "dev-cluster" \
  --replicas 1 \
  --workers-disabled \
  --output dev.yaml

# High-availability cluster
python cluster_generator.py \
  --cluster-name "production" \
  --replicas 3 \
  --worker-replicas 5 \
  --control-plane-ip "192.168.1.100" \
  --output production.yaml
```

#### Resource Configuration

```bash
# Custom control plane resources
python cluster_generator.py \
  --memory 6144 \
  --cores 4 \
  --disk-size 50 \
  --output high-spec.yaml

# Custom worker resources  
python cluster_generator.py \
  --worker-memory 8192 \
  --worker-cores 4 \
  --worker-disk-size 100 \
  --output worker-heavy.yaml
```

#### Infrastructure Settings

```bash
# Restrict to specific Proxmox nodes
python cluster_generator.py \
  --allowed-nodes "NODE01,NODE02,NODE03" \
  --replicas 3 \
  --output restricted.yaml

# Custom IP addressing
python cluster_generator.py \
  --control-plane-ip "10.0.1.50" \
  --gateway "10.0.1.1" \
  --dns-servers "10.0.1.1,8.8.8.8" \
  --output custom-network.yaml
```

### Available Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--config, -c` | Configuration file path | None |
| `--create-config` | Create default config file | - |
| `--output, -o` | Output YAML filename | `cluster.yaml` |
| `--cluster-name` | Kubernetes cluster name | `homelab-cluster` |
| `--replicas` | Control plane node count | `1` |
| `--control-plane-ip` | Control plane VIP | `192.168.0.30` |
| `--allowed-nodes` | Proxmox nodes (comma-sep) | `K8S0,K8S1,K8S2` |
| `--memory` | CP memory in MiB | `2048` |
| `--cores` | CP CPU cores | `2` |
| `--disk-size` | CP disk size in GB | `20` |
| `--workers-enabled` | Enable worker nodes | - |
| `--workers-disabled` | Disable worker nodes | - |
| `--worker-replicas` | Worker node count | `2` |
| `--worker-memory` | Worker memory in MiB | `4096` |
| `--worker-cores` | Worker CPU cores | `2` |
| `--worker-disk-size` | Worker disk size in GB | `20` |

---

## 🚀 Cluster Deployment

### Deploy Control Plane

```bash
# Generate cluster configuration
python cluster_generator.py --config homelab.yaml --output homelab-cluster.yaml

# Apply to management cluster
kubectl apply -f homelab-cluster.yaml

# Monitor deployment
kubectl get clusters,machines -A
watch kubectl get machines -A
```

### Deployment Verification

```bash
# Check cluster status
kubectl get cluster homelab-cluster -o wide

# Monitor machine creation
kubectl get machines -A -o wide

# Check Proxmox VMs
# VMs should appear in your Proxmox interface

# Wait for control plane ready
kubectl wait --for=condition=ControlPlaneReady cluster/homelab-cluster --timeout=20m
```

---

## 🔑 Access and Verification

### Retrieve Kubeconfig

```bash
# Extract kubeconfig from secret
kubectl get secret homelab-cluster-kubeconfig -o jsonpath='{.data.value}' | base64 -d > kubeconfig-homelab

# Test cluster access
kubectl --kubeconfig kubeconfig-homelab get nodes -o wide

# Check cluster info
kubectl --kubeconfig kubeconfig-homelab cluster-info
```

### Verify Cluster Health

```bash
# Check all nodes
kubectl --kubeconfig kubeconfig-homelab get nodes

# Check system pods
kubectl --kubeconfig kubeconfig-homelab get pods -A

# Check cluster components
kubectl --kubeconfig kubeconfig-homelab get componentstatuses
```

---

## 👷 Worker Node Management ( ⚠️ TO BE TESTED ⚠️)

### Enable Workers During Generation

```bash
# Generate cluster with workers
python cluster_generator.py \
  --config homelab.yaml \
  --workers-enabled \
  --worker-replicas 3 \
  --output cluster-with-workers.yaml

# Apply complete configuration
kubectl apply -f cluster-with-workers.yaml
```

### Add Workers to Existing Cluster

```bash
# Generate worker-only configuration
python cluster_generator.py \
  --config homelab.yaml \
  --workers-enabled \
  --worker-replicas 2 \
  --output additional-workers.yaml

# Edit to remove cluster/control plane resources (keep only MachineDeployment)
vim additional-workers.yaml

# Apply workers
kubectl apply -f additional-workers.yaml
```

### Scale Workers

```bash
# Scale existing worker deployment
kubectl scale machinedeployment homelab-cluster-workers --replicas=5

# Verify scaling
kubectl get machinedeployment -o wide
kubectl get machines -A | grep worker
```

---

## ⚙️ Configuration Reference

### Sample Configuration File

```yaml
# Basic cluster settings
cluster_name: "homelab-cluster"
namespace: "default"
kubernetes_version: "v1.32.0"
replicas: 1

# Infrastructure configuration
allowed_nodes: ["K8S0", "K8S1", "K8S2"]
control_plane_endpoint:
  host: "192.168.0.30"
  port: 6443

# Network configuration
dns_servers:
  - "8.8.8.8"
  - "8.8.4.4"
ipv4_config:
  addresses: ["192.168.0.20-192.168.0.29"]
  gateway: "192.168.0.254"
  prefix: 24

# Control plane VM specs
machine_template:
  disks:
    boot_volume:
      disk: "scsi0"
      size_gb: 20
      format: "qcow2"
      full: true
  memory_mib: 2048
  network:
    bridge: "vmbr0"
    model: "virtio"
  cpu:
    cores: 2
    sockets: 1
  source_node: "K8S0"
  template_id: 8700

# Worker configuration
workers:
  enabled: true
  replicas: 2
  machine_template:
    disks:
      boot_volume:
        disk: "scsi0"
        size_gb: 30
        format: "qcow2"
        full: true
    memory_mib: 4096
    network:
      bridge: "vmbr0"
      model: "virtio"
    cpu:
      cores: 2
      sockets: 1
    source_node: "K8S0"
    template_id: 8700
    checks:
      skip_cloud_init_status: true

# Talos configuration
talos_config:
  install_disk: "/dev/sda"
    extensions:
      - "ghcr.io/siderolabs/qemu-guest-agent:9.2.0"
    kernel_args:
      - "net.ifnames=0"
    network_interface: "eth0"
    dhcp: false
```
---

## 🔧 Troubleshooting

### Common Issues

#### 1. **Proxmox Authentication Errors**

```bash
# Verify environment variables
echo $PROXMOX_URL
echo $PROXMOX_TOKEN  
echo $PROXMOX_SECRET

# Test API access
curl -k -H "Authorization: PVEAPIToken=$PROXMOX_TOKEN=$PROXMOX_SECRET" \
  "$PROXMOX_URL/version"
```

#### 2. **Template Issues**

```bash
# Verify template exists
qm list | grep 8700

# Check template configuration
qm config 8700

# Verify QEMU guest agent
qm agent 8700 ping
```

#### 3. **Network Configuration Problems** ( ⚠️ TO BE TESTED ⚠️)

```bash
# Check bridge configuration
ip link show vmbr0

# Verify IP range availability
nmap -sn 192.168.0.20-29

# Test VM network connectivity
# SSH to VM and test internet access
```

#### 4. **Cluster API Issues**

```bash
# Check CAPI controllers
kubectl get pods -n capi-system

# Check provider status
kubectl get providers -A

# View controller logs
kubectl logs -n capi-system deployment/capi-controller-manager
kubectl logs -n capx-system deployment/capx-controller-manager
```

#### 5. **Machine Creation Failures** ( ⚠️ TO BE TESTED ⚠️)

```bash
# Check machine status
kubectl get machines -A -o wide

# Describe failed machines
kubectl describe machine <machine-name>

# Check infrastructure machines
kubectl get proxmoxmachines -A -o wide
kubectl describe proxmoxmachine <machine-name>
```

### Debugging Commands ( ⚠️ TO BE TESTED ⚠️)

```bash
# Full cluster status
kubectl get clusters,machines,machinedeployments -A -o wide

# Check all CAPI resources
kubectl api-resources | grep cluster-api

# Monitor events
kubectl get events --sort-by='.lastTimestamp' -A

# Controller logs
kubectl logs -f -n capi-system deployment/capi-controller-manager
kubectl logs -f -n capx-system deployment/capx-controller-manager
kubectl logs -f -n capi-bootstrap-talos-system deployment/capi-bootstrap-talos-controller-manager
```

### Recovery Procedures ( ⚠️ TO BE TESTED ⚠️)

#### Clean Failed Deployment

```bash
# Delete cluster
kubectl delete cluster homelab-cluster

# Wait for cleanup
kubectl get machines -A
kubectl get proxmoxmachines -A

# Clean up any remaining resources
kubectl get all -A | grep homelab-cluster
```

#### Reset Management Cluster

```bash
# Delete management cluster
kind delete cluster --name capi-management

# Recreate and reinitialize
kind create cluster --name capi-management
clusterctl init --infrastructure proxmox --ipam in-cluster --control-plane talos --bootstrap talos
```

---

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Regular cluster health check
kubectl --kubeconfig kubeconfig-homelab get nodes
kubectl --kubeconfig kubeconfig-homelab get pods -A | grep -v Running

# Check cluster events
kubectl --kubeconfig kubeconfig-homelab get events --sort-by='.lastTimestamp'

# Monitor resource usage
kubectl --kubeconfig kubeconfig-homelab top nodes
kubectl --kubeconfig kubeconfig-homelab top pods -A
```

### Backup Considerations

```bash
# Backup management cluster kubeconfig
cp ~/.kube/config ~/.kube/config.backup

# Backup generated cluster configs
cp homelab-cluster.yaml backups/
cp kubeconfig-homelab backups/

# Backup Proxmox VMs (snapshots recommended)
qm snapshot <vmid> backup-$(date +%Y%m%d)
```

---

## 🚀 Advanced Usage ( ⚠️ TO BE TESTED ⚠️)

### Custom Talos Extensions

Add custom extensions to your configuration:

```yaml
talos_config:
  install_disk: "/dev/sda"
  extensions:
    - "ghcr.io/siderolabs/qemu-guest-agent:9.2.0"
    - "ghcr.io/siderolabs/util-linux-tools:2.40.2"
    - "ghcr.io/siderolabs/iscsi-tools:0.1.6"
  kernel_args:
    - "net.ifnames=0"
    - "console=tty0"
    - "console=ttyS0"
```

### Multi-Tenant Deployments

Deploy multiple clusters with namespace isolation:

```bash
# Create dedicated namespaces
kubectl create namespace cluster-dev
kubectl create namespace cluster-staging
kubectl create namespace cluster-prod

# Generate cluster configs
python cluster_generator.py --cluster-name dev-cluster --namespace cluster-dev --output dev.yaml
python cluster_generator.py --cluster-name staging-cluster --namespace cluster-staging --output staging.yaml
python cluster_generator.py --cluster-name prod-cluster --namespace cluster-prod --output prod.yaml
```

---

This comprehensive guide should cover all aspects of your Proxmox CAPI Kubernetes deployment. For additional support or specific use cases not covered here, please refer to the official documentation of the respective components or create an issue in the project repository.