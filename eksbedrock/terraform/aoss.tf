resource "aws_opensearchserverless_security_policy" "aoss_network_policy" {
  name = "eksbedrock"
  type = "network"
  policy = jsonencode([
    {
      Description = "Allow access to the collection and dashboard",
      Rules = [
        {
          Resource = [
            "collection/${var.collection_name}"
          ],
          ResourceType = "collection"
        },
        {
          Resource = [
            "collection/${var.collection_name}"
          ],
          ResourceType = "dashboard"
        }
      ],
      AllowFromPublic = true
    }
  ])
}

resource "aws_opensearchserverless_security_policy" "aoss_encryption_policy" {
  name = "eksbedrock"
  type = "encryption"
  policy = jsonencode({
    Rules = [
      {
        Resource = [
          "collection/${var.collection_name}"
        ],
        ResourceType = "collection"
      }
    ],
    AWSOwnedKey = true
  })
}


resource "aws_opensearchserverless_collection" "eksbedrock" {
  name = var.collection_name
  standby_replicas = "DISABLED"
  type = "VECTORSEARCH"

  depends_on = [aws_opensearchserverless_security_policy.aoss_encryption_policy,
                aws_opensearchserverless_security_policy.aoss_network_policy]
}
