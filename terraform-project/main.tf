

# VPC
resource "aws_vpc" "my_vpc" {
  cidr_block = var.cidr_range_vpc
  tags = { Name = "my-vpc" }
}

# Public Subnet 1
resource "aws_subnet" "public_subnet_1" {
  vpc_id                  = aws_vpc.my_vpc.id
  cidr_block              = var.cidr_range_public_subnet
  availability_zone       = "us-east-2a"
  map_public_ip_on_launch = true
  tags = { Name = "public-subnet-1" }
}

# Public Subnet 2
resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = aws_vpc.my_vpc.id
  cidr_block              = var.cidr_range_public_subnet_2
  availability_zone       = "us-east-2b"
  map_public_ip_on_launch = true
  tags = { Name = "public-subnet-2" }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.my_vpc.id
  tags = { Name = "my-igw" }
}

# Public Route Table
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.my_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = { Name = "public-rt" }
}

# Associate both public subnets
resource "aws_route_table_association" "public_rt_assoc_1" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_rt_assoc_2" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_rt.id
}

# Security Group
resource "aws_security_group" "mysg" {
  name        = "my-first-sg"
  description = "My security group"
  vpc_id      = aws_vpc.my_vpc.id

  # Allow SSH
  ingress {
    description = "Allow SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTP
  ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "my-first-sg" }
}

resource "aws_s3_bucket" "s3" {
  bucket = "my-terraform-bucket-2026-prave"   

  tags = {
    Name = "my-s3-bucket"
  }
}


# First EC2 - Public Subnet 1
resource "aws_instance" "first-server" {
  ami                    = "ami-07062e2a343acc423"
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public_subnet_1.id
  vpc_security_group_ids = [aws_security_group.mysg.id]
  user_data              = file("userdata.sh")
  tags = { Name = "my-first-instance" }
}

# Second EC2 - Public Subnet 2
resource "aws_instance" "second-server" {
  ami                    = "ami-07062e2a343acc423"
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public_subnet_2.id
  vpc_security_group_ids = [aws_security_group.mysg.id]
  user_data              = file("userdata1.sh")
  tags = { Name = "my-second-instance" }
}

# Create ALB
resource "aws_lb" "my_alb" {
  name               = "my-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.mysg.id]
  subnets            = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]

  tags = { Name = "my-alb" }
}

# Create Target Group
resource "aws_lb_target_group" "my_target_group" {
  name     = "my-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.my_vpc.id

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200-399"
  }

  tags = { Name = "my-target-group" }
}

# Register EC2 instances with Target Group
resource "aws_lb_target_group_attachment" "first_server_attachment" {
  target_group_arn = aws_lb_target_group.my_target_group.arn
  target_id        = aws_instance.first-server.id
  port             = 80
}

resource "aws_lb_target_group_attachment" "second_server_attachment" {
  target_group_arn = aws_lb_target_group.my_target_group.arn
  target_id        = aws_instance.second-server.id
  port             = 80
}

# Create Listener
resource "aws_lb_listener" "my_listener" {
  load_balancer_arn = aws_lb.my_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.my_target_group.arn
  }

  tags = { Name = "my-listener" }
}   

# Output the ALB DNS name
output "alb_dns_name" {
  value = aws_lb.my_alb.dns_name
}

