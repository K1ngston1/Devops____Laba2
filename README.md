# hmp-server
# security bandit

The backend for HearMyPaper

## Встановлення на Windows

### Передумови
1. Встановіть Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Увімкніть в Docker Desktop WSL 2 backend
3. Встановіть WSL2: `wsl --install` (від адміністратора)
4. Перезавантажте комп'ютер

## kubectl setup

### Встановлення залежностей

**Відкрийте PowerShell від імені адміністратора та виконайте:**


# 1. Спочатку знайдіть де встановлено Chocolatey
# Зазвичай це: C:\ProgramData\chocolatey

# 2. Додайте Chocolatey в PATH (виконайте в PowerShell)
$env:Path += ";C:\ProgramData\chocolatey\bin"

# 3. Перевірте що choco працює
choco --version

# 4. Тепер встановіть minikube та kubectl
choco install minikube kubernetes-cli -y

# 5. Встановіть helm
choco install kubernetes-helm -y


```powershell
# Встановлення Chocolatey (якщо ще не встановлено)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Встановлення minikube та kubectl
choco install minikube kubernetes-cli -y

# Встановлення helm
choco install kubernetes-helm -y

# Запуск minikube з драйвером docker
minikube start --driver=docker

# Перевірка що kubectl налаштовано на minikube
kubectl config use-context minikube


minikube addons enable ingress


kubectl apply -f k8s/

# Запустіть кілька разів, поки статус не стане "Running"
kubectl get pods

# Отримати IP
minikube ip

# Або через describe ingress
kubectl describe ingress hmp-ingress

# Отримати IP та відкрити в браузері
$INGRESS_IP = minikube ip
Start-Process "http://${INGRESS_IP}/docs"


#Oчищення 
kubectl delete -f k8s/

#Helm setup
Застосування prerequisites (ConfigMap та Secret)

#kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/secret.yaml

#helm dependency update helm/

#kubectl get pods -w

#Отримання IP адреси Ingress
$INGRESS_IP = minikube ip
Write-Host "Ingress IP: $INGRESS_IP"
Start-Process "http://${INGRESS_IP}/docs"
