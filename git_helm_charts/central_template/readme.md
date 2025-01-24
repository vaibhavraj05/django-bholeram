ClusterSecretStore example

<!-- apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-ssm-secret-store
spec:
  provider:
    aws:
      service: SSM
      region: us-west-2
      auth:
        secretRef:
          accessKeyIDSecretRef:
            name: aws-credentials
            key: access-key-id
          secretAccessKeySecretRef:
            name: aws-credentials
            key: secret-access-key
      parameters:
        - name: /path/to/parameter
          recursive: true -->
