import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as transfer from "aws-cdk-lib/aws-transfer";
import * as iam from "aws-cdk-lib/aws-iam";
import { claritasEnvironment, claritasSftpBucketPrefix } from "../Utils";

interface SftpServer extends cdk.StackProps {
  sftpServer: transfer.CfnServer;
}

// Below Class is used to create Sftp server
export class SftpTransferStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: SftpServer) {
    super(scope, id, props);

    // Fetching Environment
    const environment = claritasEnvironment(this).valueAsString;
    const bucketPrefix = claritasSftpBucketPrefix(this).valueAsString;

    const sftpRootRole = new iam.Role(this, "sftpRootRole", {
      description: "Sftp Root user role Role",
      assumedBy: new iam.ServicePrincipal("transfer.amazonaws.com"),
      roleName: environment + "SftpRootRole",
    });

    const userBucketName = `${bucketPrefix}-cdc16-${environment}`;

    const sftpListRootPolicy = new iam.PolicyStatement({
      actions: ["s3:ListBucket", "s3:GetBucketLocation"],
      resources: [`arn:aws:s3:::${userBucketName}`],
    });
    sftpRootRole.addToPolicy(sftpListRootPolicy);

    const sftpRootPolicy = new iam.PolicyStatement({
      actions: [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObjectVersion",
        "s3:DeleteObject",
        "s3:GetObjectVersion",
      ],
      resources: [`arn:aws:s3:::${userBucketName}/sftp/*`],
    });
    sftpRootRole.addToPolicy(sftpRootPolicy);
  }
}
