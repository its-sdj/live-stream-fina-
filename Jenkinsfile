pipeline {
    agent any
    
    environment {
        DOCKER_HUB_CREDENTIALS = 'docker-hub-credentials'
        GITHUB_CREDENTIALS = 'github-credentials'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', credentialsId: env.GITHUB_CREDENTIALS, url: 'https://github.com/its-sdj/live-stream-fina-.git'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("live-stream-app:${env.BUILD_ID}")
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    docker.image("live-stream-app:${env.BUILD_ID}").inside('--link mongo:mongo') {
                        sh 'python -m unittest discover -s tests'
                    }
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_HUB_CREDENTIALS) {
                        docker.image("live-stream-app:${env.BUILD_ID}").push()
                        docker.image("live-stream-app:${env.BUILD_ID}").push('latest')
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    sh 'docker stop live-stream-app || true && docker rm live-stream-app || true'
                    sh 'docker run -d --name live-stream-app -p 5000:5000 --link mongo:mongo live-stream-app:latest'
                }
            }
        }
    }
    
    post {
        always {
            sh 'docker rmi live-stream-app:${env.BUILD_ID} || true'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
} 
