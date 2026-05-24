pipeline {
    agent any

    environment {
        IMAGE_NAME = "dsaf-lab:v1"
        SONAR_HOST_URL = "http://localhost:9000"
        SONAR_TOKEN = credentials('sonar-token')
        SNYK_TOKEN = credentials('snyk-token')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Secrets Scan') {
            steps {
                sh '''
                    gitleaks detect \
                    --source . \
                    --report-format json \
                    --report-path gitleaks-report.json
                '''
            }
        }

        stage('Dependency Scan') {
            steps {
                sh '''
                    rm -rf "$HOME/venv"
        
                    python3 -m venv "$HOME/venv"
        
                    . "$HOME/venv/bin/activate"
        
                    python3 -m pip install --upgrade pip
        
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
        
                    snyk auth "$SNYK_TOKEN"
        
                    snyk test \
                        --org=0b719955-55fd-4d80-ac96-17853f7eda80 \
                        --file=requirements.txt \
                        --json-file-output=snyk-report.json
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t $IMAGE_NAME .
                    docker images | grep dsaf-lab
                '''
            }
        }

        stage('Container Image Scan') {
            steps {
                sh '''
                    trivy image \
                    --format json \
                    --output trivy-report.json \
                    $IMAGE_NAME
                '''
            }
        }

        stage('Static Application Security Testing') {
            steps {
                sh '''
                    docker run --rm \
                    --network=host \
                    -e SONAR_HOST_URL="$SONAR_HOST_URL" \
                    -e SONAR_TOKEN="$SONAR_TOKEN" \
                    -v "$PWD:/usr/src" \
                    sonarsource/sonar-scanner-cli
                '''
            }
        }

        stage('Load Image to Minikube') {
            steps {
                sh '''
                    minikube start --driver=docker
                    minikube image load $IMAGE_NAME
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl apply -f k8s/rbac.yaml
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl get pods
                    kubectl get svc
                '''
            }
        }

        stage('Kubernetes Benchmark Audit') {
            steps {
                sh '''
                    kubectl delete job kube-bench --ignore-not-found=true

                    kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml

                    sleep 20

                    kubectl logs job/kube-bench > kube-bench-report.txt || true

                    kubectl delete job kube-bench --ignore-not-found=true
                '''
            }
        }

        stage('Get Service URL'){
            steps{
                sh '''
                minikube service dsaf-service --url 
                '''
            }
        }

        stage('Dynamic Application Security Testing') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '''
                        chmod +x scripts/zap-scan.sh
                        ./scripts/zap-scan.sh
                    '''
                }
            }

            post {
                always {
                    echo 'OWASP ZAP completed. Findings are reported for remediation and do not block deployment automatically.'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.json,*.txt,*.html', fingerprint: true
        }

        failure {
            echo 'Pipeline stopped due to a failed security gate.'
        }

        success {
            echo 'Pipeline completed successfully.'
        }
    }
}
