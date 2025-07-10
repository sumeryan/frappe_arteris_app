from .connection import AthenaConnection 

def query_data(
    query, 
    database, 
    output_location, 
    region_name, 
    aws_access_key_id, 
    aws_secret_access_key
):
    """
    Execute a query on AWS Athena and return the results as a pandas DataFrame.
    
    Args:
        query (str): SQL query to execute.
        database (str): The database to use for the query.
        output_location (str): S3 location where query results will be stored.
        region_name (str, optional): AWS region name. Defaults to None (uses env variable).
        aws_access_key_id (str, optional): AWS access key. Defaults to None (uses env variable).
        aws_secret_access_key (str, optional): AWS secret key. Defaults to None (uses env variable).
        
    Returns:
        pandas.DataFrame: Query results as a DataFrame.
    """
    # Create Athena connection
    connection = AthenaConnection(
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    # Execute query
    query_execution_id = connection.execute_query(
        query=query,
        database=database,
        output_location=output_location,
        wait=True
    )
    
    # Get query results
    results = connection.get_query_results(query_execution_id)
    
    return results

def list_databases(
    output_location, 
    region_name=None, 
    aws_access_key_id=None, 
    aws_secret_access_key=None
):
    """
    List all available databases in AWS Athena.
    
    Args:
        output_location (str): S3 location where query results will be stored.
        region_name (str, optional): AWS region name. Defaults to None (uses env variable).
        aws_access_key_id (str, optional): AWS access key. Defaults to None (uses env variable).
        aws_secret_access_key (str, optional): AWS secret key. Defaults to None (uses env variable).
        
    Returns:
        pandas.DataFrame: DataFrame containing database names.
    """
    query = "SHOW DATABASES"
    
    # Use a placeholder database for this query
    return query_data(
        query=query,
        database="default",
        output_location=output_location,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

def list_tables(
    database,
    output_location, 
    region_name=None, 
    aws_access_key_id=None, 
    aws_secret_access_key=None
):
    """
    List all tables in a specified database in AWS Athena.
    
    Args:
        database (str): The database to list tables from.
        output_location (str): S3 location where query results will be stored.
        region_name (str, optional): AWS region name. Defaults to None (uses env variable).
        aws_access_key_id (str, optional): AWS access key. Defaults to None (uses env variable).
        aws_secret_access_key (str, optional): AWS secret key. Defaults to None (uses env variable).
        
    Returns:
        pandas.DataFrame: DataFrame containing table names.
    """
    query = f"SHOW TABLES IN {database}"
    
    return query_data(
        query=query,
        database=database,
        output_location=output_location,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )