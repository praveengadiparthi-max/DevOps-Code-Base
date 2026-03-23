#!/bin/bash
# Update package list
apt-get update -y

# Install Apache2
apt-get install apache2 -y

# Ensure Apache is started and enabled at boot
systemctl start apache2
systemctl enable apache2

# Create a simple HTML page
cat <<EOF > /var/www/html/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Terraform EC2</title>
</head>
<body>
    <h1>Terraform</h1>
    <p>Apache server is running on this EC2 instance in second-server.</p>
</body>
</html>
EOF