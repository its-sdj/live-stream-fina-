pipeline {
    agent {
        docker {
            image 'python:3.9-slim'
            args '-u root -v /tmp:/tmp'
        }
    }

    environment {
        VENV_DIR = "${WORKSPACE}/venv"
        FLASK_APP = "app.py"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Verify Python Setup') {
            steps {
                script {
                    sh '''
                        echo "Python version:"
                        python --version
                        echo "Pip version:"
                        pip --version
                        python -c "import venv; print('venv module available')"
                    '''
                }
            }
        }

        stage('Create Virtual Environment') {
            steps {
                script {
                    sh """
                        echo "Creating virtual environment..."
                        python -m venv ${VENV_DIR}
                        echo "Verifying virtual environment..."
                        [ -f ${VENV_DIR}/bin/activate ] || exit 1
                        echo "Virtual environment created successfully at ${VENV_DIR}"
                    """
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh """
                        echo "Activating virtual environment..."
                        . ${VENV_DIR}/bin/activate
                        echo "Upgrading pip..."
                        pip install --upgrade pip
                        echo "Installing dependencies..."
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        else
                            echo "Warning: requirements.txt not found"
                        fi
                        echo "Installed packages:"
                        pip list
                    """
                }
            }
        }

        stage('Run Application') {
            steps {
                script {
                    sh """
                        . ${VENV_DIR}/bin/activate
                        echo "Starting Flask application..."
                        nohup python ${FLASK_APP} > flask.log 2>&1 &
                        sleep 5
                        echo "Checking if app is running..."
                        pgrep -f ${FLASK_APP} || { echo "Application failed to start"; exit 1; }
                        echo "Application started successfully"
                        echo "Server logs:"
                        cat flask.log
                    """
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh """
                pkill -f ${FLASK_APP} || true
                rm -rf ${VENV_DIR} || true
                rm -f flask.log || true
            """
        }
        failure {
            echo 'Pipeline failed! Debug information:'
            sh """
                echo "Workspace contents:"
                ls -la
                echo "Python environment info:"
                which python
                python --version
                echo "Virtual environment check:"
                ls -la ${VENV_DIR}/bin/ || true
            """
        }
    }
}
