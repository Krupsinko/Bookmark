resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]
}




resource "aws_iam_role" "github_actions" {
  name = "bookmark-github-actions"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }

        Action = "sts:AssumeRoleWithWebIdentity"

        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
            "token.actions.githubusercontent.com:sub" = "repo:Krupsinko/Bookmark:ref:refs/heads/main"
          }
        }
      }
    ]
  })
}




resource "aws_iam_policy" "github_ecr_push" {
  name = "bookmark-github-ecr-push"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]

        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:DescribeRepositories",
          "ecr:DescribeImages",
          "ecr:InitiateLayerUpload",
          "ecr:CompleteLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:BatchGetImage",
          "ecr:PutImage"
        ]

        Resource = aws_ecr_repository.api.arn
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "github_ecr_push" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_ecr_push.arn
}




resource "aws_iam_policy" "github_terraform_state" {
  name = "bookmark-github-terraform-state"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]

        Resource = aws_s3_bucket.terraform_state.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]

        Resource = "${aws_s3_bucket.terraform_state.arn}/bookmark/dev/*"
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "github_terraform_state" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_terraform_state.arn
}




resource "aws_iam_policy" "github_terraform_apply" {
  name = "bookmark-github-terraform-apply"
  policy = jsonencode({

    Version = "2012-10-17"
    Statement = [{
      Sid    = "InfrastructureService"
      Effect = "Allow"
      Action = [
        "ecs:*",
        "ec2:*",
        "rds:*",
        "logs:*",
        "elasticache:*",
        "secretsmanager:*",
        "elasticloadbalancing:*"
      ],
      Resource = "*"
      },

      {
        Sid      = "ScreenshotBucket"
        Effect   = "Allow"
        Action   = "s3:*"
        Resource = "arn:aws:s3:::bookmark-screenshots-dev"
      },

      {
        Sid    = "ManageBookmarkIAM"
        Effect = "Allow"

        Action = [
          "iam:CreateRole",
          "iam:GetRole",
          "iam:DeleteRole",
          "iam:UpdateAssumeRolePolicy",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",

          "iam:CreatePolicy",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:ListPolicyVersions",
          "iam:CreatePolicyVersion",
          "iam:DeletePolicyVersion",
          "iam:DeletePolicy",
          "iam:TagPolicy",
          "iam:UntagPolicy",

          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy"
        ]

        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/bookmark-ecs-execution-role",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/bookmark-celery-role",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/bookmark-celery-s3",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/ecs-secrets-manager"
        ]
      },

      {
        Sid    = "PassBookmarkRolesToECS"
        Effect = "Allow"

        Action = "iam:PassRole"

        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/bookmark-ecs-execution-role",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/bookmark-celery-role"
        ]

        Condition = {
          StringEquals = {
            "iam:PassedToService" = "ecs-tasks.amazonaws.com"
          }
        }
      },

      {
        Sid    = "CreateRequiredServiceLinkedRoles"
        Effect = "Allow"

        Action = "iam:CreateServiceLinkedRole"

        Resource = "*"

        Condition = {
          StringEquals = {
            "iam:AWSServiceName" = [
              "ecs.amazonaws.com",
              "elasticloadbalancing.amazonaws.com",
              "rds.amazonaws.com",
              "elasticache.amazonaws.com"
            ]
          }
        }
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "github_terraform_apply" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_terraform_apply.arn
}








