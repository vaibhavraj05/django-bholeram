import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

export class BadCdkStack extends cdk.Stack {
    constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Hardcoded credentials - BAD PRACTICE
        const accessKey = 'AKIAFAKEACCESSKEY';
        const secretKey = 'FAKESECRETKEY12345';

        // S3 bucket with public read access - BAD SECURITY
        const bucket = new s3.Bucket(this, 'MyBadBucket', {
            publicReadAccess: true, // Security Risk: Publicly accessible
            removalPolicy: cdk.RemovalPolicy.DESTROY, // Destroys data when stack is deleted
        });

        // Overly permissive IAM policy - BAD PRACTICE
        const role = new iam.Role(this, 'MyBadRole', {
            assumedBy: new iam.AccountRootPrincipal(), // Overly permissive principal
        });

        role.addToPolicy(new iam.PolicyStatement({
            actions: ['s3:*', 'ec2:*', 'iam:*'], // Excessive permissions
            resources: ['*'], // Applies to ALL resources
            effect: iam.Effect.ALLOW,
        }));

        // Misconfigured EC2 instance - SECURITY RISK
        const vpc = new ec2.Vpc(this, 'MyBadVPC', { maxAzs: 1 });
        const instance = new ec2.Instance(this, 'MyBadInstance', {
            vpc,
            instanceType: ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
            machineImage: ec2.MachineImage.latestAmazonLinux(),
            keyName: 'hardcoded-key', // Potential security issue
        });
    }
}

const app = new cdk.App();
new BadCdkStack(app, 'BadCdkStack');
app.synth();
