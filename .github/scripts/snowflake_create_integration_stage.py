#!/usr/bin/env python3
"""
Snowflake Integration and External Stage Creation Script

This script creates a Snowflake storage integration and external stage
for multicloud environments (AWS, GCP, Azure).
"""

import os
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import snowflake.connector


def load_private_key(private_key_pem: str, passphrase: str):
    """
    Load and decode the private key for Snowflake authentication.
    
    Args:
        private_key_pem: PEM-encoded private key string
        passphrase: Passphrase for the private key
    
    Returns:
        Decoded private key bytes
    """
    private_key_bytes = private_key_pem.encode('utf-8')
    passphrase_bytes = passphrase.encode('utf-8') if passphrase else None
    
    private_key = serialization.load_pem_private_key(
        private_key_bytes,
        password=passphrase_bytes,
        backend=default_backend()
    )
    
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )


def connect_to_snowflake():
    """
    Establish connection to Snowflake using key-pair authentication.
    
    Returns:
        Snowflake connection object
    """
    account = os.environ['SNOWFLAKE_ACCOUNT']
    user = os.environ['SNOWFLAKE_USER']
    private_key_pem = os.environ['SNOWFLAKE_PRIVATE_KEY_PEM']
    passphrase = os.environ['SNOWFLAKE_PRIVATE_KEY_PASSPHRASE']
    role = os.environ.get('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
    warehouse = os.environ.get('SNOWFLAKE_WAREHOUSE', '')
    
    print(f"Connecting to Snowflake account: {account}")
    print(f"Using role: {role}")
    
    private_key_bytes = load_private_key(private_key_pem, passphrase)
    
    conn_params = {
        'account': account,
        'user': user,
        'private_key': private_key_bytes,
        'role': role,
    }
    
    if warehouse:
        conn_params['warehouse'] = warehouse
    
    return snowflake.connector.connect(**conn_params)


def create_aws_integration(cursor, integration_name: str, role_arn: str):
    """
    Create AWS storage integration in Snowflake.
    
    Args:
        cursor: Snowflake cursor object
        integration_name: Name of the storage integration
        role_arn: AWS IAM role ARN
    """
    print(f"\n=== Creating AWS Storage Integration: {integration_name} ===")
    
    sql = f"""
    CREATE OR REPLACE STORAGE INTEGRATION {integration_name}
      TYPE = EXTERNAL_STAGE
      STORAGE_PROVIDER = 'S3'
      ENABLED = TRUE
      STORAGE_AWS_ROLE_ARN = '{role_arn}'
      STORAGE_ALLOWED_LOCATIONS = ('*');
    """
    
    print(f"Executing SQL:\n{sql}")
    cursor.execute(sql)
    print("✓ AWS storage integration created successfully")
    
    # Retrieve integration details
    cursor.execute(f"DESC INTEGRATION {integration_name}")
    results = cursor.fetchall()
    
    snowflake_principal_arn = None
    snowflake_external_id = None
    
    for row in results:
        if row[0] == 'STORAGE_AWS_IAM_USER_ARN':
            snowflake_principal_arn = row[2]
        elif row[0] == 'STORAGE_AWS_EXTERNAL_ID':
            snowflake_external_id = row[2]
    
    print(f"\nSnowflake Principal ARN: {snowflake_principal_arn}")
    print(f"Snowflake External ID: {snowflake_external_id}")
    
    # Set GitHub Actions outputs
    print(f"::set-output name=snowflake_principal_arn::{snowflake_principal_arn}")
    print(f"::set-output name=snowflake_external_id::{snowflake_external_id}")
    
    return snowflake_principal_arn, snowflake_external_id


def create_gcp_integration(cursor, integration_name: str):
    """
    Create GCP storage integration in Snowflake.
    
    Args:
        cursor: Snowflake cursor object
        integration_name: Name of the storage integration
    """
    print(f"\n=== Creating GCP Storage Integration: {integration_name} ===")
    
    sql = f"""
    CREATE OR REPLACE STORAGE INTEGRATION {integration_name}
      TYPE = EXTERNAL_STAGE
      STORAGE_PROVIDER = 'GCS'
      ENABLED = TRUE
      STORAGE_ALLOWED_LOCATIONS = ('*');
    """
    
    print(f"Executing SQL:\n{sql}")
    cursor.execute(sql)
    print("✓ GCP storage integration created successfully")
    
    # Retrieve integration details
    cursor.execute(f"DESC INTEGRATION {integration_name}")
    results = cursor.fetchall()
    
    snowflake_gcs_service_account = None
    
    for row in results:
        if row[0] == 'STORAGE_GCP_SERVICE_ACCOUNT':
            snowflake_gcs_service_account = row[2]
    
    print(f"\nSnowflake GCS Service Account: {snowflake_gcs_service_account}")
    
    # Set GitHub Actions outputs
    print(f"::set-output name=snowflake_gcs_service_account::{snowflake_gcs_service_account}")
    
    return snowflake_gcs_service_account


def create_azure_integration(cursor, integration_name: str, tenant_id: str):
    """
    Create Azure storage integration in Snowflake.
    
    Args:
        cursor: Snowflake cursor object
        integration_name: Name of the storage integration
        tenant_id: Azure tenant ID
    """
    print(f"\n=== Creating Azure Storage Integration: {integration_name} ===")
    
    sql = f"""
    CREATE OR REPLACE STORAGE INTEGRATION {integration_name}
      TYPE = EXTERNAL_STAGE
      STORAGE_PROVIDER = 'AZURE'
      ENABLED = TRUE
      AZURE_TENANT_ID = '{tenant_id}'
      STORAGE_ALLOWED_LOCATIONS = ('*');
    """
    
    print(f"Executing SQL:\n{sql}")
    cursor.execute(sql)
    print("✓ Azure storage integration created successfully")
    
    # Retrieve integration details
    cursor.execute(f"DESC INTEGRATION {integration_name}")
    results = cursor.fetchall()
    
    azure_consent_url = None
    azure_app_name = None
    
    for row in results:
        if row[0] == 'AZURE_CONSENT_URL':
            azure_consent_url = row[2]
        elif row[0] == 'AZURE_MULTI_TENANT_APP_NAME':
            azure_app_name = row[2]
    
    print(f"\nAzure Consent URL: {azure_consent_url}")
    print(f"Azure Multi-Tenant App Name: {azure_app_name}")
    
    # Set GitHub Actions outputs
    print(f"::set-output name=azure_consent_url::{azure_consent_url}")
    print(f"::set-output name=azure_app_name::{azure_app_name}")
    
    return azure_consent_url, azure_app_name


def create_external_stage(cursor, stage_name: str, storage_url: str, integration_name: str, database: str, schema: str):
    """
    Create external stage in Snowflake.
    
    Args:
        cursor: Snowflake cursor object
        stage_name: Name of the external stage
        storage_url: Cloud storage URL
        integration_name: Name of the storage integration
        database: Snowflake database name
        schema: Snowflake schema name
    """
    print(f"\n=== Creating External Stage: {database}.{schema}.{stage_name} ===")
    
    # Use database and schema
    cursor.execute(f"USE DATABASE {database}")
    cursor.execute(f"USE SCHEMA {schema}")
    
    sql = f"""
    CREATE OR REPLACE STAGE {stage_name}
      URL = '{storage_url}'
      STORAGE_INTEGRATION = {integration_name};
    """
    
    print(f"Executing SQL:\n{sql}")
    cursor.execute(sql)
    print(f"✓ External stage '{stage_name}' created successfully")
    
    # Verify stage creation
    cursor.execute(f"DESC STAGE {stage_name}")
    print(f"✓ Stage verified: {database}.{schema}.{stage_name}")


def main():
    """Main execution function."""
    try:
        # Get environment variables
        cloud_provider = os.environ['CLOUD_PROVIDER'].lower()
        integration_name = os.environ['INTEGRATION']
        stage_name = os.environ['STAGE']
        database = os.environ['DB']
        schema = os.environ['SCHEMA']
        
        print(f"Cloud Provider: {cloud_provider}")
        print(f"Integration Name: {integration_name}")
        print(f"Stage Name: {stage_name}")
        print(f"Database: {database}")
        print(f"Schema: {schema}")
        
        # Connect to Snowflake
        conn = connect_to_snowflake()
        cursor = conn.cursor()
        
        # Create storage integration based on cloud provider
        if cloud_provider == 'aws':
            role_arn = os.environ['AWS_ROLE_ARN']
            storage_url = os.environ['STORAGE_URL_AWS']
            create_aws_integration(cursor, integration_name, role_arn)
            
        elif cloud_provider == 'gcp':
            storage_url = os.environ['STORAGE_URL_GCP']
            create_gcp_integration(cursor, integration_name)
            
        elif cloud_provider == 'azure':
            tenant_id = os.environ['AZURE_TENANT_ID']
            storage_url = os.environ['STORAGE_URL_AZURE']
            create_azure_integration(cursor, integration_name, tenant_id)
            
        else:
            raise ValueError(f"Unsupported cloud provider: {cloud_provider}")
        
        # Create external stage
        create_external_stage(cursor, stage_name, storage_url, integration_name, database, schema)
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n✓ All operations completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
