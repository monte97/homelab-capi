# 🚀 Proxmox CAPI Kubernetes Cluster Deployment

Easily deploy a production-grade Kubernetes cluster on your **Proxmox** homelab using **Cluster API (CAPI)** 🧩

## ⚙️ Features

- 🧠 Automated provisioning with Cluster API
- 🖥️ Configurable control plane and worker node specs
- 🔁 Scalable node count
- 🔌 Seamless integration with Proxmox VMs
- 🛰️ Flexible IP addressing for control plane nodes

## 🧾 Configuration Options

You can customize the following parameters:

- **🧱 Control Plane Node Count** – number of control plane nodes
- **🔧 Worker Node Count** – number of worker nodes
- **🧮 Control Plane Specs** – CPU, RAM, disk, network
- **🛠️ Worker Specs** – CPU, RAM, disk, network
- **📡 Control Plane Starting IP** – starting address for CP nodes (auto-incremented)

## 📦 Requirements

- Proxmox VE with API access
- [`clusterctl`](https://cluster-api.sigs.k8s.io/) installed
- A working bootstrap cluster (e.g., with [`kind`](https://kind.sigs.k8s.io/))
- Proxmox credentials with VM provisioning rights
- Network config allowing bootstrap to reach Proxmox VMs

## 🚦 Usage

1. `git clone` this repository
2. Edit the config files (`.env`, YAML, or equivalent)
3. Bootstrap CAPI on your management cluster
4. Run the deploy workflow

> See the `docs/` folder for more in-depth instructions.

## 🪪 License

MIT License
