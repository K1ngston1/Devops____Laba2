# DevOps Lab 2 — Kubernetes + Helm + Minikube

## 📌 Опис проєкту

Ця лабораторна робота демонструє розгортання мікросервісної архітектури в Kubernetes (Minikube) з використанням Helm, Ingress, PostgreSQL та Redis.

---

## 🧱 Використані технології

- Kubernetes (Minikube)
- Helm
- Docker Desktop
- Nginx Ingress Controller
- FastAPI (backend)
- PostgreSQL (Bitnami chart)
- Redis (Bitnami chart)
- kubectl

---

## 🚀 1. Встановлення інструментів

### Встановлення через winget (Windows):

```powershell
winget install Kubernetes.minikube
winget install Kubernetes.kubectl
winget install Helm.Helm

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

minikube start --driver=docker

minikube status


minikube addons enable ingress
kubectl get pods -n ingress-nginx

kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/


kubectl get pods
kubectl get svc
kubectl get ingress


helm dependency update helm/
helm install hearmypaper helm/
helm list

kubectl describe ingress hearmypaper
minikube tunnel
minikube ip
kubectl get all
```