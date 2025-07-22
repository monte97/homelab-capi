1. Seutp cluster managemet con kind

```bash
kind create cluster
```

2. Setup proxmox, creazione creazione utente e tken

3. download talos iso e sistemazione su proxmox

4. configurazione clusterctl
    - download
    - impostare `~/.cluster-api/clusterctl.yaml`
        ```yaml
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
        ```
5. impostare variabili di ambiente

```bash
export PROXMOX_URL=""
export PROXMOX_TOKEN=''
export PROXMOX_SECRET="XXXXXXXXXXXXXXXX"
```


6. init cluster di managmenet

```bash
clusterctl init --infrastructure proxmox --ipam in-cluster --control-plane talos --bootstrap talos
```

7. applicare control plane

```bash
kubectl apply -f controlplane/
```

---

# Setup workers

1. Editare la loro config

2. avviare worker

```bash
kubectl apply -f workers/
```

# Accesso al cluster

```bash
kubectl get secret homelab-cluster-kubeconfig -o jsonpath='{.data.value}' | base64 -d > kubeconfig-cluster
```

```bash
kubectl --kubeconfig kubeconfig-cluster get nodes -o wide
```


---

devo installare qemu-guest-agent su proxmox per consentire di configurare talos in modo corretto

apt install qemu-guest-agent