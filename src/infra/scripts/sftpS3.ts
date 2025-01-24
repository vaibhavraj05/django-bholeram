import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as iam from "aws-cdk-lib/aws-iam";
import { claritasEnvironment, claritasSftpBucketPrefix } from "../Utils";
import { readClientsFromFile } from "../Utils";
import { join } from "path";
import { Bucket, StorageClass } from "aws-cdk-lib/aws-s3";

// Below Class is used to create Sftp server
export class UserStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Fetching Environment
    const environment = claritasEnvironment(this).valueAsString;
    const bucketPrefix = claritasSftpBucketPrefix(this).valueAsString;

    // Fetching client data
    const clients = readClientsFromFile(
      join(__dirname, "..", "clients", "clients.yaml")
    );

    // Creating logging bucket
    const userLogBucketName = `${bucketPrefix}-user-s3-logs-${environment}`;
    const userLogBucket = new Bucket(this, "userLogBucket", {
      bucketName: userLogBucketName,
    });

    const userLogBucketPolicy = new iam.PolicyStatement({
      principals: [new iam.ServicePrincipal("logging.s3.amazonaws.com")],
      actions: ["s3:PutObject"],
      resources: [`arn:aws:s3:::${userLogBucketName}/*`],
    });

    userLogBucket.addToResourcePolicy(userLogBucketPolicy);
    cdk.Tags.of(userLogBucket).add("managedBy", "CDK");
    cdk.Tags.of(userLogBucket).add("env", environment);

    // Creating client bucket, vendors
    for (var client in clients) {
      const stackName = `UserS3Config-${client}`;
      const clientConfig = clients[client];
      const userBucketName = `${bucketPrefix}-${client}-${environment}`;
      const userBucket = new Bucket(this, stackName, {
        bucketName: userBucketName,
        versioned: true,
        serverAccessLogsBucket: userLogBucket,
        serverAccessLogsPrefix: userBucketName,
      });

      userBucket.addLifecycleRule({
        enabled: true,
        transitions: [
          {
            storageClass: StorageClass.GLACIER,
            transitionAfter: cdk.Duration.days(90),
          },
        ],
      });

      for (const vendor of clientConfig.vendors) {
        new cdk.aws_s3_deployment.BucketDeployment(
          this,
          `${stackName}-${vendor}`,
          {
            sources: [
              cdk.aws_s3_deployment.Source.asset(
                join(__dirname, "..", "clients", "sftp-folder-structure")
              ),
            ],
            destinationBucket: userBucket,
            destinationKeyPrefix: `sftp/${vendor}/`,
          }
        );
      }

      cdk.Tags.of(userBucket).add("managedBy", "CDK");
      cdk.Tags.of(userBucket).add("env", environment);
    }
  }
}
