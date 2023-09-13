output "network_id" {
  value = aws_vpc.main.id
}

output "public_subnetwork_id" {
  value = aws_subnet.public[0].id
}

output "private_subnetwork_id" {
  value = aws_subnet.private[0].id
}

output "private_subnet" {
  value = [for subnet in aws_subnet.private : subnet.id]
}

output "public_subnet" {
  value = [for subnet in aws_subnet.public : subnet.id]
}