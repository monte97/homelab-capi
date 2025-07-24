# 🚀 Proxmox CAPI Kubernetes Cluster Deployment

Deploy production-ready Kubernetes clusters on Proxmox using **Cluster API (CAPI)** with **Talos Linux** and automated YAML generation.

## ⚡ Quick Overview

This project provides:
- 🧠 **Automated provisioning** with Cluster API + Talos Linux
- 🖥️ **Proxmox integration** for VM management  
- 🔧 **Python YAML generator** for parametric cluster configurations
- 🏗️ **Flexible architecture** supporting control plane-only or full clusters
- 📋 **Template-based** configuration with easy customization

## 🛠️ What You Get

- **Control Plane**: Highly available Kubernetes masters
- **Worker Nodes**: Scalable compute nodes (optional)
- **Automated Setup**: Bootstrap to production-ready cluster
- **Homelab Optimized**: Perfect for Proxmox home environments

## 📦 Prerequisites

- **Proxmox VE** with API access
- **Management Cluster** (e.g., `kind`)
- **Python 3.7+** for the generator
- **Talos Linux** template in Proxmox
- **Network access** between bootstrap and Proxmox VMs

## 🚀 Quick Start

### 1. Setup Management Cluster
```bash
kind create cluster
```

### 2. Generate Cluster Configuration
```bash
# Install dependencies
pip install jinja2 pyyaml

# Create default config
python cluster_generator.py --create-config homelab.yaml

# Edit the config to match your environment
vim homelab.yaml

# Generate cluster YAML
python cluster_generator.py --config homelab.yaml --output my-cluster.yaml
```

### 3. Deploy Cluster
```bash
# Setup environment variables
export PROXMOX_URL="https://your-proxmox:8006/api2/json"
export PROXMOX_TOKEN="your-token-id"
export PROXMOX_SECRET="your-token-secret"

# Initialize CAPI
clusterctl init --infrastructure proxmox --ipam in-cluster --control-plane talos --bootstrap talos

# Deploy cluster
kubectl apply -f my-cluster.yaml
```

### 4. Access Your Cluster
```bash
# Get kubeconfig
kubectl get secret homelab-cluster-kubeconfig -o jsonpath='{.data.value}' | base64 -d > kubeconfig-cluster

# Check nodes
kubectl --kubeconfig kubeconfig-cluster get nodes -o wide
```

## 🎯 Example Configurations

### Single Control Plane (Minimal)
```bash
python cluster_generator.py \
  --cluster-name "simple-cluster" \
  --replicas 1 \
  --workers-disabled \
  --output simple.yaml
```

### High Availability Setup
```bash
python cluster_generator.py \
  --cluster-name "ha-cluster" \
  --replicas 3 \
  --worker-replicas 3 \
  --memory 4096 \
  --worker-memory 8192 \
  --output ha-cluster.yaml
```

### Custom Resource Allocation
```bash
python cluster_generator.py \
  --cluster-name "custom-cluster" \
  --memory 6144 \
  --cores 4 \
  --disk-size 50 \
  --worker-memory 8192 \
  --worker-cores 4 \
  --output custom.yaml
```

## 📊 Resource Planning

| Component | CPU | RAM | Disk | Notes |
|-----------|-----|-----|------|-------|
| Control Plane | 2 vCPU | 2GB | 20GB | Per node, default config |
| Worker Node | 2 vCPU | 4GB | 20GB | Per node, default config |
| Management | 2 vCPU | 2GB | 10GB | Kind cluster |

## 🔧 Configuration Highlights

The generator supports extensive customization:

- **Infrastructure**: Proxmox nodes, networking, storage
- **Resources**: CPU, RAM, disk per node type  
- **Scaling**: Control plane and worker node counts
- **Network**: IP ranges, DNS, gateway configuration
- **Talos**: Extensions, kernel args, install options

## 📚 Documentation

- **[Complete Setup Guide](docs.md)** - Detailed installation and configuration
- **[Configuration Reference](docs.md#configuration-reference)** - All available options
- **[Troubleshooting](docs.md#troubleshooting)** - Common issues and solutions
- **[Examples](docs.md#examples)** - Real-world deployment scenarios

## 🎛️ Generator Features

The Python generator provides:

```bash
# Quick parameter overrides
python cluster_generator.py \
  --cluster-name "production" \
  --control-plane-ip "10.0.0.100" \
  --allowed-nodes "PROD01,PROD02,PROD03" \
  --replicas 3

# Flexible worker configuration  
python cluster_generator.py \
  --workers-enabled \
  --worker-replicas 5 \
  --worker-memory 8192

# Template-based customization
python cluster_generator.py --config custom.yaml
```

## 🏷️ Project Structure

```
├── cluster_generator.py    # Main YAML generator
├── README.md              # This overview
├── docs.md               # Detailed documentation  
├── examples/             # Sample configurations
│   ├── simple.yaml      # Single node setup
│   ├── ha.yaml          # HA configuration
│   └── homelab.yaml     # Typical homelab setup
└── templates/           # Jinja2 templates (embedded)
```

## 🪪 License

MIT License - Use freely for homelab and production environments.

---

**Need help?** Check the [detailed documentation](docs.md) or create an issue for support.