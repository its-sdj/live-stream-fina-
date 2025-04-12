pipeline {
    agent any

    environment {
        // Use python3 by default
        PATH = "${env.PATH}:/usr/local/bin"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                script {
                    // Verify Python is installed
                    def pythonVersion = sh(script: 'python3 --version || echo "Python3 not found"', returnStdout: true).trim()
                    if (pythonVersion.contains("not found")) {
                        error("Python 3 is not installed. Please install Python 3 on the Jenkins agent.")
                    }
                    echo "Using ${pythonVersion}"

                    // Create virtual environment
                    sh 'python3 -m venv venv'
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    // Activate venv and install dependencies
                    sh '''
                        . venv/bin/activate
                        pip install --upgrade pip
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        fi
                    '''
                }
            }
        }

        stage('Run Application') {
            steps {
                script {
                    // Run your Python application
                    sh '''
                        . venv/bin/activate
                        python app.py &
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh '''
                pkill -f app.py || true
                rm -rf venv || true
            '''
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
