# Snowflake External Stage Creation - GitHub Reusable Workflow

![Built with Kiro](https://img.shields.io/badge/Built_with-Kiro-8845f4?logo=robot&logoColor=white)&nbsp;![Commit Activity](https://img.shields.io/github/commit-activity/t/https://github.com/subhamay-bhattacharyya-gha/multicloud-snowflake-stages-wf)&nbsp;![Last Commit](https://img.shields.io/github/last-commit/subhamay-bhattacharyya-gha/multicloud-snowflake-stages-wf)&nbsp;![Release Date](https://img.shields.io/github/release-date/subhamay-bhattacharyya-gha/multicloud-snowflake-stages-wf)&nbsp;![Repo Size](https://img.shields.io/github/repo-size/subhamay-bhattacharyya-gha/multicloud-snowflake-stages-wf)&nbsp;![File Count](https://img.shields.io/github/directory-file-count/subhamay-bhattacharyya-gha/multicloud-snowflake-stages-wf)&nbsp;![Issues](https://img.shields.io/github/issues/subhamay-bhattacharyya-gha/multicloud-snowflake-stages-wf)&nbsp;![Top Language](https://img.shields.io/github/languages/top/subhamay-bhattacharyya-gha/multicloud-snowflake-stages-wf)&nbsp;![Custom Endpoint](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/bsubhamay/8d142a9345ac5cff42474d131f6713de/raw/multicloud-snowflake-stages-wf.json?)

A GitHub Reusable Workflow for creating Snowflake external stages in multicloud environments (AWS, GCP, Azure) with Terraform-managed infrastructure.

## Overview

This reusable workflow automates the creation of Snowflake storage integrations and external stages across multiple cloud providers. It handles:

- **Infrastructure provisioning** using Terraform
- **Snowflake integration** creation with proper authentication
- **External stage** setup with cloud storage
- **Trust policy finalization** for secure access

### Supported Cloud Providers

- ✅ **AWS** (Active)
- 🚧 **GCP** (Commented - ready for implementation)
- 🚧 **Azure** (Commented - ready for implementation)

---

## Workflow Architecture

The workflow follows a multi-step process:

1. **Validate Inputs** - Validates configuration and displays summary
2. **Provision Infrastructure** - Creates cloud storage and IAM resources via Terraform
3. **Create Snowflake Integration** - Sets up storage integration and external stage
4. **Finalize Trust Policy** - Updates IAM trust relationships with Snowflake principals

---

## Inputs

### Required Inputs

| Name | Type | Description |
|------|------|-------------|
| `cloud-provider` | string | Cloud provider: `aws`, `gcp`, or `azure` |
| `storage-name` | string | AWS/GCP bucket name OR Azure container name |
| `encryption-key-ref` | string | KMS key alias/name (AWS), KMS key ID (GCP), or Key Vault key ID (Azure) |
| `snowflake-account` | string | Snowflake account identifier |
| `snowflake-user` | string | Snowflake username |
| `snowflake-integration-name` | string | Name for the Snowflake storage integration |
| `snowflake-stage-name` | string | Name for the external stage |
| `snowflake-database` | string | Snowflake database name |
| `snowflake-schema` | string | Snowflake schema name |
| `tf-dir` | string | Path to Terraform directory for the selected cloud provider |

### Optional Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `storage-prefix` | string | `""` | Optional prefix for storage path (no leading slash) |
| `snowflake-role` | string | `ACCOUNTADMIN` | Snowflake role to use |
| `snowflake-warehouse` | string | `""` | Snowflake warehouse to use |
| `backend-type` | string | `local` | Terraform backend type: `local`, `remote`, `s3`, `gcs`, `azurerm` |
| `release-tag` | string | `""` | Git tag/branch to checkout (empty = current branch) |
| `python-version` | string | `3.12` | Python version for Snowflake connector |
| `ci-pipeline` | boolean | `false` | Include commit SHA in state key for CI/CD isolation |

### AWS-Specific Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `aws-region` | string | `us-east-1` | AWS region |
| `s3-bucket` | string | `""` | S3 bucket for Terraform state (if backend-type is `s3`) |
| `s3-region` | string | `""` | AWS region for S3 backend bucket |
| `s3-key-prefix` | string | `""` | Optional prefix for S3 state key |

### GCP-Specific Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `gcp-project-id` | string | `""` | GCP project ID |
| `gcp-location` | string | `US` | GCP location |

---

## Secrets

### Required Secrets

| Name | Description |
|------|-------------|
| `snowflake-private-key-pem` | Snowflake private key in PEM format |
| `snowflake-private-key-passphrase` | Passphrase for the private key |

### Cloud Provider Secrets

| Name | Required For | Description |
|------|--------------|-------------|
| `aws-role-to-assume` | AWS | IAM role ARN for OIDC authentication |
| `gcp-wif-provider` | GCP | Workload Identity Federation provider |
| `gcp-service-account` | GCP | GCP service account email |
| `azure-client-id` | Azure | Azure client ID for authentication |
| `azure-tenant-id` | Azure | Azure tenant ID |
| `azure-subscription-id` | Azure | Azure subscription ID |

### Optional Secrets

| Name | Description |
|------|-------------|
| `tfc-token` | Terraform Cloud/Enterprise API token (if backend-type is `remote`) |

---

## Example Usage

### AWS Example

```yaml
name: Create Snowflake External Stage - AWS

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment'
        required: true
        type: choice
        options:
          - dev
          - staging
          - prod

jobs:
  create-snowflake-stage:
    uses: your-org/your-repo/.github/workflows/create-snowflake-external-stage.yaml@v1
    with:
      # Cloud Provider
      cloud-provider: aws
      
      # Storage Configuration
      storage-name: my-snowflake-bucket
      storage-prefix: data/landing
      encryption-key-ref: alias/snowflake-kms-key
      
      # Snowflake Configuration
      snowflake-account: xy12345.us-east-1
      snowflake-user: TERRAFORM_USER
      snowflake-integration-name: AWS_S3_INTEGRATION
      snowflake-stage-name: EXTERNAL_STAGE_S3
      snowflake-database: MY_DATABASE
      snowflake-schema: MY_SCHEMA
      snowflake-role: SYSADMIN
      snowflake-warehouse: COMPUTE_WH
      
      # Terraform Configuration
      tf-dir: terraform/aws
      backend-type: s3
      s3-bucket: my-terraform-state-bucket
      s3-region: us-east-1
      s3-key-prefix: snowflake/stages
      
      # AWS Configuration
      aws-region: us-east-1
      
    secrets:
      # AWS Authentication
      aws-role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
      
      # Snowflake Authentication
      snowflake-private-key-pem: ${{ secrets.SNOWFLAKE_PRIVATE_KEY_PEM }}
      snowflake-private-key-passphrase: ${{ secrets.SNOWFLAKE_PRIVATE_KEY_PASSPHRASE }}
      
      # Terraform Backend (optional)
      tfc-token: ${{ secrets.TFC_TOKEN }}
```

### GCP Example (When Implemented)

```yaml
jobs:
  create-snowflake-stage:
    uses: your-org/your-repo/.github/workflows/create-snowflake-external-stage.yaml@v1
    with:
      cloud-provider: gcp
      storage-name: my-snowflake-bucket
      encryption-key-ref: projects/my-project/locations/us/keyRings/my-keyring/cryptoKeys/my-key
      snowflake-account: xy12345.us-east-1
      snowflake-user: TERRAFORM_USER
      snowflake-integration-name: GCP_GCS_INTEGRATION
      snowflake-stage-name: EXTERNAL_STAGE_GCS
      snowflake-database: MY_DATABASE
      snowflake-schema: MY_SCHEMA
      tf-dir: terraform/gcp
      gcp-project-id: my-gcp-project
      gcp-location: US
    secrets:
      gcp-wif-provider: projects/123456789/locations/global/workloadIdentityPools/my-pool/providers/my-provider
      gcp-service-account: github-actions@my-project.iam.gserviceaccount.com
      snowflake-private-key-pem: ${{ secrets.SNOWFLAKE_PRIVATE_KEY_PEM }}
      snowflake-private-key-passphrase: ${{ secrets.SNOWFLAKE_PRIVATE_KEY_PASSPHRASE }}
```

### Azure Example (When Implemented)

```yaml
jobs:
  create-snowflake-stage:
    uses: your-org/your-repo/.github/workflows/create-snowflake-external-stage.yaml@v1
    with:
      cloud-provider: azure
      storage-name: my-container
      encryption-key-ref: https://my-keyvault.vault.azure.net/keys/my-key
      snowflake-account: xy12345.us-east-1
      snowflake-user: TERRAFORM_USER
      snowflake-integration-name: AZURE_BLOB_INTEGRATION
      snowflake-stage-name: EXTERNAL_STAGE_AZURE
      snowflake-database: MY_DATABASE
      snowflake-schema: MY_SCHEMA
      tf-dir: terraform/azure
    secrets:
      azure-client-id: ${{ secrets.AZURE_CLIENT_ID }}
      azure-tenant-id: ${{ secrets.AZURE_TENANT_ID }}
      azure-subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      snowflake-private-key-pem: ${{ secrets.SNOWFLAKE_PRIVATE_KEY_PEM }}
      snowflake-private-key-passphrase: ${{ secrets.SNOWFLAKE_PRIVATE_KEY_PASSPHRASE }}
```

---

## Terraform Backend Support

The workflow supports multiple Terraform backend types:

### Local Backend (Default)

```yaml
with:
  backend-type: local
```

### Terraform Cloud/Enterprise

```yaml
with:
  backend-type: remote
secrets:
  tfc-token: ${{ secrets.TFC_TOKEN }}
```

### AWS S3 Backend

```yaml
with:
  backend-type: s3
  s3-bucket: my-terraform-state
  s3-region: us-east-1
  s3-key-prefix: snowflake/stages
  ci-pipeline: true  # Include commit SHA in state key
```

---

## Prerequisites

### Snowflake Setup

1. **Create a key pair** for authentication:
   ```bash
   # Generate private key
   openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out snowflake_key.p8 -nocrypt
   
   # Generate public key
   openssl rsa -in snowflake_key.p8 -pubout -out snowflake_key.pub
   ```

2. **Assign public key to Snowflake user**:
   ```sql
   ALTER USER TERRAFORM_USER SET RSA_PUBLIC_KEY='MIIBIjANBg...';
   ```

3. **Grant necessary privileges**:
   ```sql
   GRANT CREATE INTEGRATION ON ACCOUNT TO ROLE SYSADMIN;
   GRANT CREATE STAGE ON SCHEMA MY_DATABASE.MY_SCHEMA TO ROLE SYSADMIN;
   ```

### AWS Setup

1. **Create OIDC provider** for GitHub Actions
2. **Create IAM role** with trust policy for GitHub
3. **Attach policies** for S3, KMS, and IAM operations

### Terraform Structure

Your Terraform code should:
- Accept variables for all cloud-specific configurations
- Output `snowflake_access_role_arn` and `storage_url` (AWS)
- Support backend configuration via `-backend-config` flags

---

## Workflow Jobs

### 1. Validate Inputs & Display Configuration

- Validates cloud provider input
- Displays all configuration in GitHub Actions summary
- Shows secrets status (provided/not provided)
- Sets checkout ref for all subsequent jobs

### 2. Provision Infrastructure (AWS/GCP/Azure)

- Checks out repository
- Authenticates with cloud provider
- Initializes Terraform with selected backend
- Provisions cloud storage and IAM resources
- Outputs role ARN and storage URL

### 3. Create Snowflake Integration & Stage

- Connects to Snowflake using key-pair authentication
- Creates storage integration for the cloud provider
- Creates external stage pointing to cloud storage
- Outputs Snowflake-generated credentials for trust policy

### 4. Finalize Trust Policy (AWS/GCP/Azure)

- Re-runs Terraform with Snowflake credentials
- Updates IAM trust policy with Snowflake principal
- Completes the secure connection setup

---

## Outputs

The workflow provides outputs from the Snowflake integration job:

### AWS Outputs
- `snowflake_principal_arn` - Snowflake IAM user ARN
- `snowflake_external_id` - External ID for trust policy

### GCP Outputs
- `snowflake_gcs_service_account` - Snowflake GCS service account

### Azure Outputs
- `azure_consent_url` - URL for admin consent
- `azure_app_name` - Azure multi-tenant app name

---

## Troubleshooting

### Common Issues

**Issue**: Terraform state conflicts
- **Solution**: Use unique state keys with `ci-pipeline: true` or separate S3 prefixes

**Issue**: Snowflake authentication fails
- **Solution**: Verify private key format and passphrase, ensure public key is assigned to user

**Issue**: AWS trust policy errors
- **Solution**: Ensure Snowflake principal ARN and external ID are correctly passed to step 2

**Issue**: Permission denied errors
- **Solution**: Verify IAM role has necessary permissions for S3, KMS, and IAM operations

---

## Security Best Practices

1. **Use OIDC authentication** instead of long-lived credentials
2. **Store sensitive data** in GitHub Secrets
3. **Limit IAM permissions** to minimum required
4. **Enable encryption** for cloud storage and Terraform state
5. **Use separate environments** for dev/staging/prod
6. **Rotate Snowflake keys** regularly
7. **Review trust policies** before applying

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## License

MIT

---

## Support

For issues and questions:
- Open an issue in this repository
- Check existing issues for solutions
- Review Snowflake and cloud provider documentation

---

## Roadmap

- [x] AWS support
- [ ] GCP support (code ready, needs testing)
- [ ] Azure support (code ready, needs testing)
- [ ] Additional Terraform backends (GCS, Azure Storage)
- [ ] Enhanced error handling and retry logic
- [ ] Support for multiple stages in one workflow run
