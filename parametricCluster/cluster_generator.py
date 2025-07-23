#!/usr/bin/env python3
"""
Kubernetes Cluster YAML Generator
Generates parametric YAML configurations for Cluster API with Talos and Proxmox
"""

import json
import yaml
from jinja2 import Template
import argparse
import sys
from pathlib import Path

# YAML Template with Jinja2 variables
CLUSTER_TEMPLATE = """
# =============================================================================
# HOMELAB KUBERNETES CLUSTER CONFIGURATION
# =============================================================================
# Generated cluster configuration using:
# - Cluster API for cluster lifecycle management
# - Talos Linux as the operating system
# - Proxmox as the infrastructure provider
# =============================================================================

---
# =============================================================================
# CLUSTER DEFINITION
# =============================================================================
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: {{ cluster_name }}
  namespace: {{ namespace }}
spec:
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1alpha3
    kind: TalosControlPlane
    name: {{ cluster_name }}-cp
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1alpha1
    kind: ProxmoxCluster
    name: {{ cluster_name }}-proxmox

---
# =============================================================================
# INFRASTRUCTURE CONFIGURATION
# =============================================================================
apiVersion: infrastructure.cluster.x-k8s.io/v1alpha1
kind: ProxmoxCluster
metadata:
  name: {{ cluster_name }}-proxmox
  namespace: {{ namespace }}
spec:
  schedulerHints:
    memoryAdjustment: {{ scheduler_hints.memory_adjustment }}
  allowedNodes:
{%- for node in allowed_nodes %}
    - {{ node }}
{%- endfor %}
  controlPlaneEndpoint:
    host: {{ control_plane_endpoint.host }}
    port: {{ control_plane_endpoint.port }}
  dnsServers:
{%- for dns in dns_servers %}
    - {{ dns }}
{%- endfor %}
  ipv4Config:
    addresses:
{%- for address_range in ipv4_config.addresses %}
      - {{ address_range }}
{%- endfor %}
    gateway: {{ ipv4_config.gateway }}
    prefix: {{ ipv4_config.prefix }}

---
# =============================================================================
# CONTROL PLANE MACHINE TEMPLATE
# =============================================================================
apiVersion: infrastructure.cluster.x-k8s.io/v1alpha1
kind: ProxmoxMachineTemplate
metadata:
  name: {{ cluster_name }}-cp-template
  namespace: {{ namespace }}
spec:
  template:
    spec:
      disks:
        bootVolume:
          disk: {{ machine_template.disks.boot_volume.disk }}
          sizeGb: {{ machine_template.disks.boot_volume.size_gb }}
          format: {{ machine_template.disks.boot_volume.format }}
          full: {{ machine_template.disks.boot_volume.full | lower }}
      memoryMiB: {{ machine_template.memory_mib }}
      network:
        default:
          bridge: {{ machine_template.network.bridge }}
          model: {{ machine_template.network.model }}
      numCores: {{ machine_template.cpu.cores }}
      numSockets: {{ machine_template.cpu.sockets }}
      sourceNode: {{ machine_template.source_node }}
      templateID: {{ machine_template.template_id }}
      checks:
        skipCloudInitStatus: {{ machine_template.checks.skip_cloud_init_status | lower }}

---
# =============================================================================
# CONTROL PLANE CONFIGURATION
# =============================================================================
apiVersion: controlplane.cluster.x-k8s.io/v1alpha3
kind: TalosControlPlane
metadata:
  name: {{ cluster_name }}-cp
spec:
  version: {{ kubernetes_version }}
  replicas: {{ replicas }}
  infrastructureTemplate:
    kind: ProxmoxMachineTemplate
    apiVersion: infrastructure.cluster.x-k8s.io/v1alpha1
    name: {{ cluster_name }}-cp-template
    namespace: {{ namespace }}
  controlPlaneConfig:
    controlplane:
      generateType: controlplane
      strategicPatches:
        - |
          - op: replace
            path: /machine/install
            value:
              disk: {{ talos_config.install_disk }}
              extensions:
{%- for extension in talos_config.extensions %}
                - image: {{ extension }}
{%- endfor %}
        - |
          - op: add
            path: /machine/install/extraKernelArgs
            value:
{%- for arg in talos_config.kernel_args %}
              - {{ arg }}
{%- endfor %}
        - |
          - op: add
            path: /machine/network/interfaces
            value:
              - interface: {{ talos_config.network_interface }}
                dhcp: {{ talos_config.dhcp | lower }}
                vip:
                  ip: {{ control_plane_endpoint.host }}

{%- if workers.enabled %}

---
# =============================================================================
# WORKER NODES DEPLOYMENT
# =============================================================================
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineDeployment
metadata:
  name: {{ cluster_name }}-workers
  namespace: {{ namespace }}
spec:
  clusterName: {{ cluster_name }}
  replicas: {{ workers.replicas }}
  selector:
    matchLabels: null
  template:
    spec:
      bootstrap:
        configRef:
          apiVersion: bootstrap.cluster.x-k8s.io/v1alpha3
          kind: TalosConfigTemplate
          name: {{ cluster_name }}-workers-config
      clusterName: {{ cluster_name }}
      infrastructureRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1alpha1
        kind: ProxmoxMachineTemplate
        name: {{ cluster_name }}-worker-template
      version: {{ kubernetes_version }}

---
# =============================================================================
# WORKER MACHINE TEMPLATE
# =============================================================================
apiVersion: infrastructure.cluster.x-k8s.io/v1alpha1
kind: ProxmoxMachineTemplate
metadata:
  name: {{ cluster_name }}-worker-template
  namespace: {{ namespace }}
spec:
  template:
    spec:
      disks:
        bootVolume:
          disk: {{ workers.machine_template.disks.boot_volume.disk }}
          sizeGb: {{ workers.machine_template.disks.boot_volume.size_gb }}
          format: {{ workers.machine_template.disks.boot_volume.format }}
          full: {{ workers.machine_template.disks.boot_volume.full | lower }}
      memoryMiB: {{ workers.machine_template.memory_mib }}
      network:
        default:
          bridge: {{ workers.machine_template.network.bridge }}
          model: {{ workers.machine_template.network.model }}
      numCores: {{ workers.machine_template.cpu.cores }}
      numSockets: {{ workers.machine_template.cpu.sockets }}
      sourceNode: {{ workers.machine_template.source_node }}
      templateID: {{ workers.machine_template.template_id }}
      checks:
        skipCloudInitStatus: {{ workers.machine_template.checks.skip_cloud_init_status | lower }}

---
# =============================================================================
# WORKER TALOS CONFIGURATION TEMPLATE
# =============================================================================
apiVersion: bootstrap.cluster.x-k8s.io/v1alpha3
kind: TalosConfigTemplate
metadata:
  name: {{ cluster_name }}-workers-config
  namespace: {{ namespace }}
spec:
  template:
    spec:
      generateType: worker
      talosVersion: {{ workers.talos_config.talos_version }}
      configPatches:
        - op: replace
          path: /machine/install
          value:
            disk: {{ workers.talos_config.install_disk }}
{%- if workers.talos_config.extensions %}
            extensions:
{%- for extension in workers.talos_config.extensions %}
              - image: {{ extension }}
{%- endfor %}
{%- endif %}
{%- if workers.talos_config.kernel_args %}
        - op: add
          path: /machine/install/extraKernelArgs
          value:
{%- for arg in workers.talos_config.kernel_args %}
            - {{ arg }}
{%- endfor %}
{%- endif %}
{%- if workers.talos_config.network_interface %}
        - op: add
          path: /machine/network/interfaces
          value:
            - interface: {{ workers.talos_config.network_interface }}
              dhcp: {{ workers.talos_config.dhcp | lower }}
{%- endif %}
{%- endif %}
"""

def load_config(config_file):
    """Load configuration from JSON or YAML file"""
    try:
        with open(config_file, 'r') as f:
            if config_file.endswith('.json'):
                return json.load(f)
            else:
                return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found")
        sys.exit(1)
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        print(f"Error parsing configuration file: {e}")
        sys.exit(1)

def create_default_config():
    """Create default configuration structure"""
    return {
        "cluster_name": "homelab-cluster",
        "namespace": "default",
        "kubernetes_version": "v1.32.0",
        "replicas": 1,
        "allowed_nodes": ["K8S0", "K8S1", "K8S2"],
        "control_plane_endpoint": {
            "host": "192.168.0.30",
            "port": 6443
        },
        "dns_servers": ["8.8.8.8", "8.8.4.4"],
        "ipv4_config": {
            "addresses": ["192.168.0.20-192.168.0.29"],
            "gateway": "192.168.0.254",
            "prefix": 24
        },
        "scheduler_hints": {
            "memory_adjustment": 0
        },
        "machine_template": {
            "disks": {
                "boot_volume": {
                    "disk": "scsi0",
                    "size_gb": 20,
                    "format": "qcow2",
                    "full": True
                }
            },
            "memory_mib": 2048,
            "network": {
                "bridge": "vmbr0",
                "model": "virtio"
            },
            "cpu": {
                "cores": 2,
                "sockets": 1
            },
            "source_node": "K8S0",
            "template_id": 8700,
            "checks": {
                "skip_cloud_init_status": True
            }
        },
        "talos_config": {
            "install_disk": "/dev/sda",
            "extensions": ["ghcr.io/siderolabs/qemu-guest-agent:9.2.0"],
            "kernel_args": ["net.ifnames=0"],
            "network_interface": "eth0",
            "dhcp": False
        },
        "workers": {
            "enabled": True,
            "replicas": 2,
            "machine_template": {
                "disks": {
                    "boot_volume": {
                        "disk": "scsi0",
                        "size_gb": 20,
                        "format": "qcow2",
                        "full": True
                    }
                },
                "memory_mib": 4096,
                "network": {
                    "bridge": "vmbr0",
                    "model": "virtio"
                },
                "cpu": {
                    "cores": 2,
                    "sockets": 1
                },
                "source_node": "K8S0",
                "template_id": 8700,
                "checks": {
                    "skip_cloud_init_status": True
                }
            },
            "talos_config": {
                "talos_version": "v1.9",
                "install_disk": "/dev/sda",
                "extensions": ["ghcr.io/siderolabs/qemu-guest-agent:9.2.0"],
                "kernel_args": ["net.ifnames=0"],
                "network_interface": "eth0",
                "dhcp": False
            }
        }
    }

def save_default_config(filename):
    """Save default configuration to file"""
    config = create_default_config()
    
    if filename.endswith('.json'):
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
    else:
        with open(filename, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"Default configuration saved to '{filename}'")

def generate_cluster_yaml(config):
    """Generate cluster YAML from configuration"""
    template = Template(CLUSTER_TEMPLATE)
    return template.render(**config)

def main():
    parser = argparse.ArgumentParser(
        description="Generate Kubernetes cluster YAML configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate default config file
  python cluster_generator.py --create-config config.yaml
  
  # Generate cluster YAML with workers
  python cluster_generator.py --config config.yaml --output cluster.yaml
  
  # Generate cluster with workers disabled
  python cluster_generator.py --workers-disabled --output control-plane-only.yaml
  
  # Generate with custom worker configuration
  python cluster_generator.py --worker-replicas 5 --worker-memory 8192 --worker-cores 4 --output large-cluster.yaml
  
  # Restrict to specific Proxmox nodes
  python cluster_generator.py --allowed-nodes "NODE01,NODE02,NODE03" --output restricted.yaml
        """
    )
    
    # Configuration options
    parser.add_argument('--config', '-c', help='Configuration file (JSON or YAML)')
    parser.add_argument('--create-config', help='Create default configuration file')
    parser.add_argument('--output', '-o', default='cluster.yaml', help='Output YAML file')
    
    # Quick override options
    parser.add_argument('--cluster-name', help='Cluster name')
    parser.add_argument('--replicas', type=int, help='Number of control plane replicas')
    parser.add_argument('--control-plane-ip', help='Control plane endpoint IP')
    parser.add_argument('--allowed-nodes', help='Comma-separated list of allowed Proxmox nodes')
    parser.add_argument('--memory', type=int, help='Memory in MiB for control plane VMs')
    parser.add_argument('--cores', type=int, help='CPU cores for control plane VMs')
    parser.add_argument('--disk-size', type=int, help='Disk size in GB for control plane VMs')
    
    # Worker-specific options
    parser.add_argument('--workers-enabled', action='store_true', help='Enable worker nodes')
    parser.add_argument('--workers-disabled', action='store_true', help='Disable worker nodes')
    parser.add_argument('--worker-replicas', type=int, help='Number of worker nodes')
    parser.add_argument('--worker-memory', type=int, help='Memory in MiB for worker VMs')
    parser.add_argument('--worker-cores', type=int, help='CPU cores for worker VMs')
    parser.add_argument('--worker-disk-size', type=int, help='Disk size in GB for worker VMs')
    
    args = parser.parse_args()
    
    # Create default config if requested
    if args.create_config:
        save_default_config(args.create_config)
        return
    
    # Load configuration
    if args.config:
        config = load_config(args.config)
    else:
        config = create_default_config()
        print("Using default configuration. Use --create-config to customize.")
    
    # Apply command line overrides
    if args.cluster_name:
        config['cluster_name'] = args.cluster_name
    if args.replicas:
        config['replicas'] = args.replicas
    if args.control_plane_ip:
        config['control_plane_endpoint']['host'] = args.control_plane_ip
    if args.allowed_nodes:
        # Parse comma-separated list of nodes
        config['allowed_nodes'] = [node.strip() for node in args.allowed_nodes.split(',')]
    if args.memory:
        config['machine_template']['memory_mib'] = args.memory
    if args.cores:
        config['machine_template']['cpu']['cores'] = args.cores
    if args.disk_size:
        config['machine_template']['disks']['boot_volume']['size_gb'] = args.disk_size
    
    # Worker-specific overrides
    if args.workers_enabled:
        config['workers']['enabled'] = True
    if args.workers_disabled:
        config['workers']['enabled'] = False
    if args.worker_replicas:
        config['workers']['replicas'] = args.worker_replicas
    if args.worker_memory:
        config['workers']['machine_template']['memory_mib'] = args.worker_memory
    if args.worker_cores:
        config['workers']['machine_template']['cpu']['cores'] = args.worker_cores
    if args.worker_disk_size:
        config['workers']['machine_template']['disks']['boot_volume']['size_gb'] = args.worker_disk_size
    
    # Generate YAML
    cluster_yaml = generate_cluster_yaml(config)
    
    # Write output
    with open(args.output, 'w') as f:
        f.write(cluster_yaml)
    
    print(f"Cluster YAML generated successfully: {args.output}")
    print(f"Cluster name: {config['cluster_name']}")
    print(f"Control plane replicas: {config['replicas']}")
    print(f"Control plane endpoint: {config['control_plane_endpoint']['host']}:{config['control_plane_endpoint']['port']}")
    print(f"Allowed nodes: {', '.join(config['allowed_nodes'])}")
    
    if config.get('workers', {}).get('enabled', False):
        print(f"Worker nodes enabled: {config['workers']['replicas']} replicas")
        print(f"Worker specs: {config['workers']['machine_template']['cpu']['cores']} cores, {config['workers']['machine_template']['memory_mib']}MB RAM")
    else:
        print("Worker nodes: disabled")

if __name__ == '__main__':
    main()