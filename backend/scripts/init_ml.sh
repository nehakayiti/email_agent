#!/bin/bash
# Initialize ML environment for the email agent
echo "Initializing ML environment..."

# Create models directory
mkdir -p "$(dirname "$0")/../models"
echo "✅ Created models directory"

# Set permissions
chmod 755 "$(dirname "$0")/../models"
echo "✅ Set directory permissions"

# Create .gitkeep file
touch "$(dirname "$0")/../models/.gitkeep"
echo "✅ Created .gitkeep file"

echo "ML environment initialized successfully!"
echo "You can now run the application and train the model through the UI." 