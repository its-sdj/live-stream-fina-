pipeline {
    agent any

    environment {
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

        stage('Check Python Installation') {
            steps {
                script {
                    def pythonVersion = sh(script: 'python3 --version || echo "Python3 not found"', returnStdout: true).trim()
                    if (pythonVersion.contains("not found")) {
                        error("Python 3 is not installed. Please install Python 3 on the Jenkins agent.")
                    }
                    echo "Using ${pythonVersion}"
                    
                    // Additional check for venv module
                    def venvCheck = sh(script: 'python3 -c "import venv; print(\"venv module available\")" || echo "venv module missing"', returnStdout: true).trim()
                    if (venvCheck.contains("missing")) {
                        error("Python venv module is not available. Please ensure Python 3 venv is installed.")
                    }
                }
            }
        }

        stage('Create Virtual Environment') {
            steps {
                script {
                    // Verify venv creation and directory
                    sh '''
                        python3 -m venv ${VENV_DIR} || exit 1
                        [ -f ${VENV_DIR}/bin/activate ] || exit 1
                    '''
                    echo "Virtual environment created successfully at ${VENV_DIR}"
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        else
                            echo "Warning: requirements.txt not found"
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
                        nohup python ${FLASK_APP} > flask.log 2>&1 &
                        sleep 5  # Give the app time to start
                        pgrep -f ${FLASK_APP} || { echo "Application failed to start"; exit 1; }
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
