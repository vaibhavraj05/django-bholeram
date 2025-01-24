#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { SftpStack } from "./scripts/sftpServer";
import { UserStack } from "./scripts/sftpS3";
import { SftpTransferStack } from "./scripts/sftpUser";

const app = new cdk.App();
const sftp = new SftpStack(app, "SftpStack");
const user = new UserStack(app, "UserStack");
const sftpTransferStack = new SftpTransferStack(app, "SftpTransferStack", {
  sftpServer: sftp.sftpServer,
});
