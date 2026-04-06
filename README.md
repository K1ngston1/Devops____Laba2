# hmp-server

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

The backend for [HearMyPaper](https://github.com/staleread/hearmypaper)

## Minikube setup

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
