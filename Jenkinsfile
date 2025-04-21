pipeline {
    agent any
    
    options {
        skipDefaultCheckout(true) // Crucial to prevent premature SCM setup
    }

    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs() // Requires Workspace Cleanup plugin
            }
        }
        
        stage('Checkout Code') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [
                        [$class: 'CleanBeforeCheckout'],
                        [$class: 'CloneOption', depth: 0, noTags: false, shallow: false]
                    ],
                    userRemoteConfigs: [[
                        url: 'https://github.com/its-sdj/live-stream-fina-.git'
                    ]]
                ])
            }
        }
        
        stage('Build') {
            steps {
                sh 'ls -la' // Verify files were cloned
                // Your build steps here
            }
        }
    }
}
