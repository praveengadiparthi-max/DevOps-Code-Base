output "public_ip" {
  value = aws_instance.Module_Example.public_ip
}

output "instance_id" {
  value = aws_instance.Module_Example.id
}

output "private_ip" {
  value = aws_instance.Module_Example.private_ip
}