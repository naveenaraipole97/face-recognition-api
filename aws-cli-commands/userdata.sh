#!/bin/bash
su ec2-user -c 'aws s3 cp s3://file-processing-app . --recursive &&  cd file_processing_app2 && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.bashrc && nvm install --lts && npm i && npm run start'

