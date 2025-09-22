# 1. Prerequisites
```
1- Before starting, make sure you have:
-A Google Cloud account with billing enabled

2- Installed the following tools:

-Google Cloud SDK
-kubectl
 (installable via gcloud components install kubectl)

3- A project set in Google Cloud (use google cloud SDK Shell CLI):

gcloud auth login
gcloud config set project <PROJECT_ID>
Replace <PROJECT_ID> with your actual Google Cloud project ID.
```

# 2. Clone the Repository
```
git clone https://github.com/Uzi78/GKE_Hackathon.git
cd GKE_Hackathon

Create a .env file using the .env.example file in the same directory
Enter your API keys in the respective fields

```

# 3. Create a GKE Cluster
```
1- Run the following command to create a Kubernetes cluster:
gcloud container clusters create gke-cluster --num-nodes=2 --zone=asia-south1-a --machine-type=e2-small --disk-type=pd-standard

2- Fetch cluster credentials:
gcloud container clusters get-credentials gke-cluster --zone=asia-south1-a
```

# 4. Build & Push the Docker Image
```
1- From the project root, run:
gcloud builds submit --tag gcr.io/<PROJECT_ID>/hackathon-app:latest .
Replace <PROJECT_ID> with your actual Google Cloud project ID.
```

# 5. Deploy to Kubernetes
```
The Kubernetes manifests are located in the /k8s directory, Apply them:

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

# 6. Get External IP
```
Run:
kubectl get service hackathon-service
Wait until the EXTERNAL-IP field shows an IP address.
Open the app in your browser:

http://<EXTERNAL-IP>
```