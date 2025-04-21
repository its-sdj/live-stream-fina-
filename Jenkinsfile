pipeline {
    agent any

    environment {
        FLASK_APP = "app.py"
        VENV_DIR = ".venv"
    }

    stages {
        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/its-sdj/live-stream-fina-.git'
            }
        }

        stage('Build Docker') {
            steps {
                sh 'docker pull python:3.9-slim'
                sh 'docker build -t livestream-app .'
            }
        }

        stage('Run App') {
            steps {
                sh 'docker run -d -p 5000:5000 livestream-app'
            }
        }
    }

    post {
        always {
            echo "Cleaning up..."
        }
        failure {
            echo "Build failed. Debug info:"
        }
    }
}
