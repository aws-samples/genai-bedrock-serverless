
data "aws_caller_identity" "current" {}

module "aws_load_balancer_controller_irsa_role" {

  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "5.3.1"

  role_name = "aws-load-balancer-controller"

  attach_load_balancer_controller_policy = true

  oidc_providers = {
    ex = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }
}

resource "helm_release" "aws_load_balancer_controller" {
  name = "aws-load-balancer-controller"

  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"

  set {
    name  = "clusterName"
    value = var.cluster_name
  }

  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = module.aws_load_balancer_controller_irsa_role.iam_role_arn
  }
}

resource "aws_iam_policy" "alb_add_tags_policy" {
  name        = "alb-add-tags-policy"
  description = "Allow LB Controller to add tags and describe listener attributes for ALB resources"
  policy      = jsonencode({
    Version: "2012-10-17",
    Statement: [
      {
        Effect: "Allow",
        Action: [
          "elasticloadbalancing:AddTags",
          "elasticloadbalancing:DescribeListenerAttributes"
        ],
        Resource: [
          "*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_alb_add_tags" {
  role       = module.aws_load_balancer_controller_irsa_role.iam_role_name
  policy_arn = aws_iam_policy.alb_add_tags_policy.arn
}
