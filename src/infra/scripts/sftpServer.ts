import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as transfer from "aws-cdk-lib/aws-transfer";
import * as iam from "aws-cdk-lib/aws-iam";
import { claritasEnvironment } from "../Utils";

// Below Class is used to create Sftp server
export class SftpStack extends cdk.Stack {
  public readonly sftpServer: transfer.CfnServer;
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Fetching Environment
    const environment = claritasEnvironment(this).valueAsString;
    //Creating IAM Role for the sftp server
    const sftpRole = new iam.Role(this, "sftpRole", {
      description: "Sftp Server Role ",
      assumedBy: new iam.ServicePrincipal("transfer.amazonaws.com"),
      roleName: environment + "SftpExecutionRoleCDK",
    });

    // Adding tags to sftp role
    cdk.Tags.of(sftpRole).add("managedBy", "CDK");
    cdk.Tags.of(sftpRole).add("env", environment);

    // Attaching policy to sftp role
    const policyStatement = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: ["*"],
      actions: [
        "logs:PutLogEvents",
        "logs:CreateLogStream",
        "logs:CreateLogGroup",
      ],
    });
    sftpRole.addToPolicy(policyStatement);

    // Creating sftp server and attacking role to sftp server
    this.sftpServer = new transfer.CfnServer(this, "sftpServer", {
      protocols: ["SFTP"],
      domain: "S3",
      loggingRole: sftpRole.roleArn,
      tags: [
        {
          key: "managedBy",
          value: "CDK",
        },
        {
          key: "env",
          value: `${environment}`,
        },
      ],
    });
  }
}
