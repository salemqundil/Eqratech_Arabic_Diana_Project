#!/bin/bash
# AWS EC2 GPU Training Setup Script

set -e

echo "====================================="
echo "AWS EC2 GPU Training Setup"
echo "====================================="

# Instance configuration
INSTANCE_TYPE=${INSTANCE_TYPE:-"p3.2xlarge"}
REGION=${REGION:-"us-east-1"}
AMI_ID=${AMI_ID:-"ami-0c7217cdde317cfec"}  # Deep Learning AMI (Ubuntu)
KEY_NAME=${KEY_NAME:-"arabic-bert-key"}

echo "Configuration:"
echo "  Instance Type: $INSTANCE_TYPE"
echo "  Region: $REGION"
echo "  AMI: $AMI_ID"

# Launch instance
echo ""
echo "Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type $INSTANCE_TYPE \
  --key-name $KEY_NAME \
  --region $REGION \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
echo "Waiting for instance to start..."
aws ec2 wait instance-running \
  --instance-ids $INSTANCE_ID \
  --region $REGION

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --region $REGION \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Instance started successfully!"
echo "Public IP: $PUBLIC_IP"

# Wait for SSH to be ready
echo ""
echo "Waiting for SSH to be ready..."
sleep 30

# Copy project files
echo ""
echo "Copying project files to instance..."
scp -r -o StrictHostKeyChecking=no \
  ../../* ubuntu@$PUBLIC_IP:/home/ubuntu/arabic-bert/

# Connect and run training
echo ""
echo "Connecting to instance and starting training..."
ssh -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP << 'EOF'
  cd /home/ubuntu/arabic-bert
  
  # Activate conda environment (if using Deep Learning AMI)
  source activate pytorch
  
  # Install dependencies
  pip install -r requirements.txt
  
  # Run training
  python cloud_training_launcher.py --provider aws
  
  # Copy results back
  tar -czf results.tar.gz output/ logs/
EOF

# Download results
echo ""
echo "Downloading results..."
scp ubuntu@$PUBLIC_IP:/home/ubuntu/arabic-bert/results.tar.gz ./

# Terminate instance
echo ""
echo "Training complete! Terminate instance? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
  echo "Terminating instance..."
  aws ec2 terminate-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION
  echo "Instance terminated."
else
  echo "Instance kept running. Remember to terminate manually:"
  echo "  aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION"
fi

echo ""
echo "Done! Results saved to results.tar.gz"
