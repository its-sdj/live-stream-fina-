pipeline {
    agent any

    environment {
        FLASK_APP = "app.py"
        VENV_DIR = ".venv"
    }

    stages {
        stage('Clone') {
            steps {
                // Checkout the code from the Git repository triggered by Jenkins
                checkout scm
            }
        }

        stage('Build Docker') {
            steps {
                // Pull the Python Docker image and build the Docker image
                sh 'docker pull python:3.9-slim'
                sh 'docker build -t livestream-app .'
            }
        }

        stage('Run App') {
            steps {
                // Run the Docker container on port 5000
                sh 'docker run -d -p 5000:5000 livestream-app'
            }
        }
    }

    post {
        always {
            // Clean up after the build
            echo "Cleaning up..."
        }
        failure {
            // Display additional debug info if the build fails
            echo "Build failed. Debug info:"
        }
    }
}
