# Kubernetes Cluster YAML Generator

A Python tool for generating parametric YAML configurations for Kubernetes clusters using Cluster API, Talos Linux, and Proxmox infrastructure.

## Overview

This generator creates complete Kubernetes cluster configurations with:
- **Cluster API** for cluster lifecycle management
- **Talos Linux** as the operating system
- **Proxmox** as the infrastructure provider

The tool supports both control plane and worker node configurations with customizable resources, networking, and storage settings.

## Features

- 🚀 **Parametric Configuration**: Generate clusters from JSON/YAML config files
- 🔧 **Command Line Overrides**: Quick parameter changes without editing config files
- 🏗️ **Flexible Architecture**: Support for control plane only or full cluster deployments
- 📋 **Template-based**: Uses Jinja2 templates for clean, maintainable YAML generation
- ⚙️ **Homelab Ready**: Optimized for homelab Proxmox environments

## Prerequisites

- Python 3.7 or higher
- Proxmox VE cluster
- Talos Linux template images in Proxmox
- Cluster API controllers installed in management cluster

## Installation

### 1. Clone or Download the Script

Save the script as `cluster_generator.py` in your working directory.

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv k8s-generator-env

# Activate virtual environment
# On Linux/macOS:
source k8s-generator-env/bin/activate

# On Windows:
k8s-generator-env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install jinja2 pyyaml
```

### 4. Verify Installation

```bash
python cluster_generator.py --help
```

## Quick Start

### 1. Generate Default Configuration

```bash
python cluster_generator.py --create-config config.yaml
```

This creates a `config.yaml` file with sensible defaults for a homelab environment.

### 2. Review and Customize Configuration

Edit the generated `config.yaml` to match your environment:

```yaml
cluster_name: "homelab-cluster"
namespace: "default"
kubernetes_version: "v1.32.0"
replicas: 1
allowed_nodes: ["K8S0", "K8S1", "K8S2"]
control_plane_endpoint:
  host: "192.168.0.30"
  port: 6443
# ... more configuration options
```

### 3. Generate Cluster YAML

```bash
python cluster_generator.py --config config.yaml --output my-cluster.yaml
```

### 4. Apply to Kubernetes

```bash
kubectl apply -f my-cluster.yaml
```

## Configuration Reference

### Basic Cluster Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `cluster_name` | Name of the Kubernetes cluster | `homelab-cluster` |
| `namespace` | Kubernetes namespace for resources | `default` |
| `kubernetes_version` | Kubernetes version to install | `v1.32.0` |
| `replicas` | Number of control plane nodes | `1` |

### Infrastructure Configuration

```yaml
allowed_nodes: ["K8S0", "K8S1", "K8S2"]  # Proxmox nodes available for the cluster
control_plane_endpoint:
  host: "192.168.0.30"    # VIP for control plane
  port: 6443              # API server port
dns_servers: 
  - "8.8.8.8"
  - "8.8.4.4"
ipv4_config:
  addresses: ["192.168.0.20-192.168.0.29"]  # IP range for VMs
  gateway: "192.168.0.254"
  prefix: 24
```

**Note**: The `allowed_nodes` parameter specifies which Proxmox nodes can be used for VM deployment. This is useful for:
- **Resource Control**: Limit cluster to specific hardware
- **Maintenance**: Exclude nodes during maintenance windows  
- **Performance**: Use only high-performance nodes for production
- **Isolation**: Separate different environments

### Machine Template Configuration

#### Control Plane Nodes

```yaml
machine_template:
  disks:
    boot_volume:
      disk: "scsi0"         # Disk interface
      size_gb: 20           # Disk size in GB
      format: "qcow2"       # Disk format
      full: true            # Full clone
  memory_mib: 2048          # RAM in MiB
  network:
    bridge: "vmbr0"         # Proxmox bridge
    model: "virtio"         # Network model
  cpu:
    cores: 2                # CPU cores
    sockets: 1              # CPU sockets
  source_node: "K8S0"       # Source Proxmox node
  template_id: 8700         # Talos template ID
```

#### Worker Nodes

```yaml
workers:
  enabled: true             # Enable/disable workers
  replicas: 2               # Number of worker nodes
  machine_template:         # Same structure as control plane
    memory_mib: 4096        # Typically more RAM for workers
    cpu:
      cores: 2
```

### Talos Configuration

```yaml
talos_config:
  install_disk: "/dev/sda"
  extensions:
    - "ghcr.io/siderolabs/qemu-guest-agent:9.2.0"
  kernel_args:
    - "net.ifnames=0"
  network_interface: "eth0"
  dhcp: false
```

## Command Line Usage

### Basic Usage

```bash
python cluster_generator.py [OPTIONS]
```

### Configuration Management

```bash
# Create default config
python cluster_generator.py --create-config config.yaml

# Use custom config
python cluster_generator.py --config config.yaml --output cluster.yaml
```

### Quick Overrides

```bash
# Override basic settings
python cluster_generator.py \
  --cluster-name "production-cluster" \
  --replicas 3 \
  --control-plane-ip "10.0.0.100" \
  --allowed-nodes "PROD01,PROD02,PROD03" \
  --output prod-cluster.yaml

# Control plane resource overrides
python cluster_generator.py \
  --memory 4096 \
  --cores 4 \
  --disk-size 50 \
  --output high-spec-cluster.yaml

# Worker configuration
python cluster_generator.py \
  --workers-enabled \
  --worker-replicas 5 \
  --worker-memory 8192 \
  --worker-cores 4 \
  --output large-cluster.yaml

# Control plane only
python cluster_generator.py \
  --workers-disabled \
  --output cp-only-cluster.yaml
```

### Command Line Options

#### Configuration Options
- `--config, -c`: Configuration file (JSON or YAML)
- `--create-config`: Create default configuration file
- `--output, -o`: Output YAML file (default: cluster.yaml)



#### Control Plane Resource Options
- `--memory`: Memory in MiB for control plane VMs
- `--cores`: CPU cores for control plane VMs
- `--disk-size`: Disk size in GB for control plane VMs

#### Worker Node Options
- `--workers-enabled`: Enable worker nodes
- `--workers-disabled`: Disable worker nodes
- `--worker-replicas`: Number of worker nodes
- `--worker-memory`: Memory in MiB for worker VMs
- `--worker-cores`: CPU cores for worker VMs
- `--worker-disk-size`: Disk size in GB for worker VMs

## Examples

### Single Control Plane Node

```bash
python cluster_generator.py \
  --cluster-name "simple-cluster" \
  --replicas 1 \
  --workers-disabled \
  --output simple.yaml
```

### High Availability Cluster

```bash
python cluster_generator.py \
  --cluster-name "ha-cluster" \
  --replicas 3 \
  --worker-replicas 3 \
  --memory 4096 \
  --worker-memory 8192 \
  --output ha-cluster.yaml
```

### Development Environment

```bash
python cluster_generator.py \
  --cluster-name "dev-cluster" \
  --replicas 1 \
  --worker-replicas 1 \
  --memory 2048 \
  --worker-memory 2048 \
  --cores 2 \
  --worker-cores 2 \
  --output dev-cluster.yaml
```

### Restrict to Specific Proxmox Nodes

```bash
python cluster_generator.py \
  --cluster-name "restricted-cluster" \
  --allowed-nodes "NODE01,NODE02" \
  --replicas 2 \
  --output restricted.yaml
```

```bash
python cluster_generator.py --create-config custom.yaml
```

Edit `custom.yaml` to your needs, then generate:

```bash
python cluster_generator.py --config custom.yaml --output custom-cluster.yaml
```

## Generated YAML Structure

The tool generates a complete Cluster API configuration including:

1. **Cluster Definition**: Main cluster resource
2. **Infrastructure Configuration**: Proxmox cluster settings
3. **Control Plane Machine Template**: VM specifications for control plane
4. **Control Plane Configuration**: Talos-specific control plane setup
5. **Worker Deployment** (optional): Worker node deployment
6. **Worker Machine Template** (optional): VM specifications for workers
7. **Worker Configuration Template** (optional): Talos worker configuration

## Troubleshooting

### Common Issues

**Import Error: No module named 'jinja2'**
```bash
# Make sure virtual environment is activated and dependencies installed
pip install jinja2 pyyaml
```

**Configuration File Not Found**
```bash
# Create default config first
python cluster_generator.py --create-config config.yaml
```

**Invalid YAML Output**
- Check your configuration file syntax
- Ensure all required fields are present
- Validate generated YAML with `kubectl --dry-run=client apply -f cluster.yaml`

### Validation

Validate generated YAML before applying:

```bash
# Syntax check
kubectl --dry-run=client apply -f cluster.yaml

# Schema validation (if cluster API CRDs are installed)
kubectl apply --dry-run=server -f cluster.yaml
```

## Environment Management

### Virtual Environment Commands

```bash
# Create environment
python3 -m venv k8s-generator-env

# Activate (Linux/macOS)
source k8s-generator-env/bin/activate

# Activate (Windows)
k8s-generator-env\Scripts\activate

# Deactivate
deactivate

# Remove environment
rm -rf k8s-generator-env  # Linux/macOS
rmdir /s k8s-generator-env  # Windows
```

### Requirements File

Create `requirements.txt`:

```
jinja2>=3.0.0
PyYAML>=6.0
```

Install from requirements:

```bash
pip install -r requirements.txt
```

## Contributing

To extend the generator:

1. Modify the `CLUSTER_TEMPLATE` for YAML structure changes
2. Update `create_default_config()` for new configuration options
3. Add command line arguments in the `argparse` section
4. Update documentation accordingly

## License

This tool is provided as-is for homelab and educational use. Modify and distribute freely.