// Purpose: Utility functions for the CDK stack.
import * as cdk from "aws-cdk-lib";
import * as fs from "fs";
import * as yaml from "js-yaml";

// Function to create a parameter for the environment
export function claritasEnvironment(stack: cdk.Stack) {
  const environment = new cdk.CfnParameter(stack, "env", {
    default: "offshore", // Default value
    type: "String", // Type of the parameter
  });
  return environment;
}

// Function to create a parameter for the S3 bucket prefix
export function claritasSftpBucketPrefix(stack: cdk.Stack) {
  const bucketPrefix = new cdk.CfnParameter(stack, "pre", {
    default: "crx-new", // Default value
    type: "String", // Type of the parameter
  });
  return bucketPrefix;
}

// Define the type for your dictionary [clinets.yaml structure]
type clients = {
  root: string;
  crx: string;
  robot: string;
  vendors: string[];
};

// Function to read and parse the clients YAML file
export function readClientsFromFile(filePath: string): Record<string, clients> {
  try {
    const fileContents = fs.readFileSync(filePath, "utf8");
    const yamlData = yaml.load(fileContents) as Record<string, any>;

    // Convert the YAML data into the TypeScript dictionary
    const clients: Record<string, clients> = {};

    // Iterate over the keys in the YAML data
    for (const key of Object.keys(yamlData)) {
      const value = yamlData[key];
      if (value && typeof value === "object") {
        const { root, crx, robot, vendors } = value;
        if (root && crx && robot && Array.isArray(vendors)) {
          clients[key] = { root, crx, robot, vendors };
        }
      }
    }
    // Return the TypeScript dictionary
    return clients;
  } catch (e) {
    console.error("Error reading or parsing YAML file:", e);
    return {};
  }
}
