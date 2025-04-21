pipeline {
    agent any

    environment {
        // Use python3 by default and set path for Jenkins agent
        PATH = "${env.PATH}:/usr/local/bin"
        VENV_DIR = 'venv'
        FLASK_APP = 'app.py'
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
                    sh 'python3 -m venv ${VENV_DIR}'
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    // Activate venv and install dependencies
                    sh '''
                        . ${VENV_DIR}/bin/activate
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
                    echo 'Running the Flask app...'
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        python ${FLASK_APP} &
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh '''
                pkill -f ${FLASK_APP} || true
                rm -rf ${VENV_DIR} || true
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