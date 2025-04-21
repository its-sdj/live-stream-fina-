pipeline {
    agent any
    
    environment {
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials')
        FLASK_ENV = 'production'
        PYTHON_VERSION = '3.9'  // Match your runtime
    }

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        // Stage 1: Prepare Environment
        stage('Clean & Setup') {
            steps {
                cleanWs()
                sh 'python${PYTHON_VERSION} -m venv venv'
                sh '. venv/bin/activate && pip install --upgrade pip wheel'
            }
        }

        // Stage 2: Checkout Code
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [
                        [$class: 'CleanBeforeCheckout'],
                        [$class: 'CloneOption', depth: 1, shallow: true]
                    ],
                    userRemoteConfigs: [[
                        url: 'https://github.com/its-sdj/live-stream-fina-.git'
                    ]]
                ])
                sh 'ls -la'  // Verify files
            }
        }

        // Stage 3: Install & Verify
        stage('Dependencies') {
            steps {
                sh '''
                . venv/bin/activate
                pip install -r requirements.txt
                pip install pytest pytest-cov flake8 black
                '''
            }
        }

        // Stage 4: Code Quality
        stage('Linting') {
            steps {
                sh '''
                . venv/bin/activate
                flake8 app.py --max-line-length=120 --exit-zero
                black --check app.py
                '''
            }
        }

        // Stage 5: Testing
        stage('Unit Tests') {
            steps {
                sh '''
                . venv/bin/activate
                python -m pytest \
                    --cov=app \
                    --cov-report=xml:coverage.xml \
                    tests/ -v
                '''
            }
            post {
                always {
                    junit '**/test-reports/*.xml'
                    cobertura 'coverage.xml'
                }
            }
        }

        // Stage 6: Build Docker Image
        stage('Docker Build') {
            when {
                branch 'main'
            }
            steps {
                script {
                    dockerImage = docker.build(
                        "your-dockerhub/live-stream-app:${env.BUILD_ID}",
                        "--build-arg PYTHON_VERSION=${PYTHON_VERSION} ."
                    )
                }
            }
        }

        // Stage 7: Integration Test
        stage('Container Test') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                docker run -d -p 5000:5000 --name test-container \
                    your-dockerhub/live-stream-app:${BUILD_ID}
                sleep 10  # Wait for app startup
                curl -s http://localhost:5000/health | grep "OK" || exit 1
                docker stop test-container && docker rm test-container
                '''
            }
        }

        // Stage 8: Deploy
        stage('Deploy') {
            when {
                branch 'main'
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', DOCKER_HUB_CREDENTIALS) {
                        dockerImage.push()
                        dockerImage.push('latest')  // Only for stable releases
                    }
                }
                // Add your deployment commands (K8s/ECS/etc)
                // Example for Kubernetes:
                // sh 'kubectl apply -f k8s-deployment.yaml'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '**/app.py,**/requirements.txt'
            cleanWs()
        }
        success {
            slackSend channel: '#devops',
                message: "SUCCESS: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend channel: '#devops',
                message: "FAILED: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER}"
        }
    }
}
