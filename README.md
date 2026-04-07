# hmp-server

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

The backend for [HearMyPaper](https://github.com/staleread/hearmypaper)

## kubectl setup

Install deps

```bash
sudo pacman -S minikube kubectl
```

Start `minikube`

```bash
minikube start
```

`kubectl` is now configured to use the minikube by default.

Enable Ingress addon:

```bash
minikube addons enable ingress
```

Apply the manifests

```bash
kubectl apply -f k8s/
```

Check for the pods being started (run for a few times)

```bash
kubectl get pods
```

Get the IP address Ingress is listening to:

```bash
kubectl describe ingress hmp-ingress | grep Address
```

Open `http://<IP_address>/docs` in your browser. You should see OpenAPI docs

### Cleanup

```bash
kubectl delete -f k8s/
```

## Helm setup

Install deps

```bash
sudo pacman -S helm
```

Apply the prerequisites (ConfigMap and Secret):

```bash
kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/secret.yaml
```

Pull chart dependencies (bitnami/postgresql, bitnami/redis):

```bash
helm dependency update helm/
```

Install the chart:

```bash
helm install hearmypaper helm/
```

Check for the pods being started (run a few times):

```bash
kubectl get pods
```

Get the IP address Ingress is listening to:

```bash
kubectl describe ingress hearmypaper | grep Address
```

Open `http://<IP_address>/docs` in your browser. You should see OpenAPI docs

### Upgrade and rollback

Change replica count (or any other value) without editing files:

```bash
helm upgrade hearmypaper helm/ --set replicaCount=2
```

Roll back to the previous revision:

```bash
helm rollback hearmypaper
```

List revision history:

```bash
helm history hearmypaper
```

### Cleanup

```bash
helm uninstall hearmypaper
kubectl delete -f k8s/config.yaml
kubectl delete -f k8s/secret.yaml
```
