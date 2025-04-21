pipeline {
    agent any

    environment {
        FLASK_APP = "app.py"
        VENV_DIR = ".venv"
    }

    stages {
        stage('Clone') {
            steps {
                // Checkout code from the Git repository with the branch specified
                checkout scm
            }
        }

        stage('Build Docker') {
            steps {
                // Pull the base Python Docker image and build the Docker image
                sh 'docker pull python:3.9-slim'
                sh 'docker build -t livestream-app .'
            }
        }

        stage('Run App') {
            steps {
                // Run the Docker container in detached mode on port 5000
                sh 'docker run -d -p 5000:5000 livestream-app'
            }
        }
    }

    post {
        always {
            // Ensure that cleanup is done
            echo "Cleaning up..."
        }
        failure {
            // Output debug information if the build fails
            echo "Build failed. Debug info:"
        }
    }
}
