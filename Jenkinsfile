pipeline {
    agent any
    
    environment {
        // Credentials and configurations
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials')
        AWS_CREDENTIALS = credentials('aws-credentials')  // For ECS/ECR deployments
        FLASK_ENV = 'production'
        PYTHON_VERSION = '3.9'
        DOCKER_REGISTRY = 'your-dockerhub'  // Change to your registry
        APP_NAME = 'live-stream-app'
    }

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 45, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        // Stage 1: Environment Setup
        stage('Initialize') {
            steps {
                cleanWs()
                sh 'printenv | sort'  // Debug env variables
            }
        }

        // Stage 2: SCM Checkout
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [
                        [$class: 'CleanBeforeCheckout'],
                        [$class: 'CloneOption', 
                         depth: 1, 
                         noTags: false, 
                         shallow: true,
                         timeout: 10],
                        [$class: 'RelativeTargetDirectory', 
                         relativeTargetDir: 'src']
                    ],
                    userRemoteConfigs: [[
                        url: 'https://github.com/its-sdj/live-stream-fina-.git',
                        credentialsId: 'github-credentials'  // If private repo
                    ]]
                ])
                
                dir('src') {
                    sh '''
                    echo "### WORKSPACE CONTENTS ###"
                    ls -la
                    echo "### PYTHON REQUIREMENTS ###"
                    cat requirements.txt || true
                    '''
                }
            }
        }

        // Stage 3: Python Environment
        stage('Python Setup') {
            steps {
                dir('src') {
                    sh """
                    python${PYTHON_VERSION} -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip==23.0.1 wheel==0.40.0
                    pip install -r requirements.txt --no-cache-dir
                    pip install pytest==7.4.0 \
                                 pytest-cov==4.1.0 \
                                 flake8==6.1.0 \
                                 black==23.7.0 \
                                 safety==2.3.5
                    """
                }
            }
        }

        // Stage 4: Security Scan
        stage('Security Check') {
            steps {
                dir('src') {
                    sh '''
                    . venv/bin/activate
                    safety check --full-report
                    '''
                }
            }
        }

        // Stage 5: Code Quality
        stage('Linting') {
            steps {
                dir('src') {
                    sh '''
                    . venv/bin/activate
                    echo "### FLAKE8 RESULTS ###"
                    flake8 app.py --max-line-length=120 --statistics || true
                    echo "### BLACK CHECK ###"
                    black --check app.py --diff || true
                    '''
                }
            }
        }

        // Stage 6: Testing
        stage('Unit Tests') {
            steps {
                dir('src') {
                    sh '''
                    . venv/bin/activate
                    mkdir -p test-reports
                    python -m pytest \
                        --junitxml=test-reports/junit.xml \
                        --cov=app \
                        --cov-report=xml:coverage.xml \
                        tests/ -v
                    '''
                }
            }
            post {
                always {
                    junit 'src/test-reports/*.xml'
                    cobertura 'src/coverage.xml'
                }
            }
        }

        // Stage 7: Docker Build
        stage('Docker Build') {
            when {
                branch 'main'
            }
            steps {
                dir('src') {
                    script {
                        dockerImage = docker.build(
                            "${DOCKER_REGISTRY}/${APP_NAME}:${env.BUILD_ID}",
                            "--build-arg PYTHON_VERSION=${PYTHON_VERSION} ."
                        )
                    }
                }
            }
        }

        // Stage 8: Container Tests
        stage('Container Validation') {
            when {
                branch 'main'
            }
            steps {
                script {
                    try {
                        sh """
                        docker run -d \
                            -p 5000:5000 \
                            --name test-container \
                            --env FLASK_ENV=test \
                            ${DOCKER_REGISTRY}/${APP_NAME}:${env.BUILD_ID}
                        
                        sleep 15  # Wait for app startup
                        
                        # Health check
                        curl -sSf http://localhost:5000/health || exit 1
                        
                        # API smoke test
                        curl -sS http://localhost:5000/api/v1/status | jq -e '.status == "OK"' || exit 1
                        """
                    } finally {
                        sh 'docker stop test-container || true'
                        sh 'docker rm test-container || true'
                    }
                }
            }
        }

        // Stage 9: Deployment
        stage('Deploy') {
            when {
                branch 'main'
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                script {
                    // Push to Docker Hub
                    docker.withRegistry("https://registry.hub.docker.com", DOCKER_HUB_CREDENTIALS) {
                        dockerImage.push()
                        
                        // Only tag as latest for verified releases
                        if (env.BUILD_SOURCE == 'release') {
                            dockerImage.push('latest')
                        }
                    }

                    // AWS ECR Example (uncomment if using AWS)
                    /*
                    sh """
                    aws ecr get-login-password | docker login \
                        --username AWS \
                        --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                    
                    docker tag ${DOCKER_REGISTRY}/${APP_NAME}:${env.BUILD_ID} \
                        ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}:${env.BUILD_ID}
                    
                    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}:${env.BUILD_ID}
                    """
                    */
                }
            }
        }
    }

    post {
        always {
            // Archive key files and reports
            archiveArtifacts artifacts: 'src/**/app.py,src/requirements.txt,src/test-reports/*.xml'
            
            // Cleanup Docker
            sh 'docker system prune -f || true'
            
            // Notify completion
            script {
                def duration = currentBuild.durationString.replace(' and counting', '')
                def msg = "${currentBuild.result}: Job ${env.JOB_NAME} #${env.BUILD_NUMBER} (${duration})"
                slackSend(color: currentBuild.result == 'SUCCESS' ? 'good' : 'danger',
                         message: msg,
                         channel: '#devops-alerts')
                
                // Additional notifications
                emailext(
                    subject: "Jenkins Build ${currentBuild.result}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: """
                    Check console output at ${env.BUILD_URL}console
                    """,
                    to: 'devops@yourcompany.com'
                )
            }
        }
        
        cleanup {
            cleanWs()
        }
    }
}
