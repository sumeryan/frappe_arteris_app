import time
import boto3
import pandas as pd

class AthenaConnection:
    """Class to handle AWS Athena connections and queries."""
    
    def __init__(self, region_name=None, aws_access_key_id=None, aws_secret_access_key=None):
        """
        Initialize the Athena connection.
        
        Args:
            region_name (str, optional): AWS region name. Defaults to value from environment variable.
            aws_access_key_id (str, optional): AWS access key. Defaults to value from environment variable.
            aws_secret_access_key (str, optional): AWS secret key. Defaults to value from environment variable.
        """
        # Get configuration from Kartado Config
        
        # Use provided parameters or get from environment variables
        self.region_name = region_name 
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key 
        
        # Initialize the Athena client
        self.client = boto3.client(
            'athena',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def execute_query(self, query, database, output_location, wait=True):
        """
        Execute a query on AWS Athena.
        
        Args:
            query (str): SQL query to execute.
            database (str): The database to use for the query.
            output_location (str): S3 location where query results will be stored.
            wait (bool, optional): Whether to wait for query completion. Defaults to True.
            
        Returns:
            str: Query execution ID
        """
        response = self.client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': database
            },
            ResultConfiguration={
                'OutputLocation': output_location
            }
        )
        
        query_execution_id = response['QueryExecutionId']
        
        if wait:
            self._wait_for_query_completion(query_execution_id)
            
        return query_execution_id
    
    def _wait_for_query_completion(self, query_execution_id, max_attempts=50):
        """
        Wait for a query to complete on Athena.
        
        Args:
            query_execution_id (str): Query execution ID.
            max_attempts (int, optional): Maximum number of status check attempts. Defaults to 50.
        
        Returns:
            str: Final query state ('SUCCEEDED', 'FAILED', 'CANCELLED')
            
        Raises:
            Exception: If the query fails or is cancelled.
        """
        state = 'RUNNING'
        attempts = 0
        
        while state in ['RUNNING', 'QUEUED'] and attempts < max_attempts:
            attempts += 1
            response = self.client.get_query_execution(QueryExecutionId=query_execution_id)
            state = response['QueryExecution']['Status']['State']
            
            if state in ['RUNNING', 'QUEUED']:
                time.sleep(2)  # Wait for 2 seconds before checking again
        
        if state == 'FAILED':
            reason = response['QueryExecution']['Status'].get('StateChangeReason', 'No reason provided')
            raise Exception(f"Query failed: {reason}")
        elif state == 'CANCELLED':
            raise Exception("Query was cancelled")
            
        return state
    
    def get_query_results(self, query_execution_id):
        """
        Get the results of a query as a pandas DataFrame.
        
        Args:
            query_execution_id (str): Query execution ID.
            
        Returns:
            pandas.DataFrame: Query results.
        """
        response = self.client.get_query_results(QueryExecutionId=query_execution_id)
        
        # Get column names from first row
        columns = [col['Label'] for col in response['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        
        # Extract data rows
        data_rows = []
        for row in response['ResultSet']['Rows'][1:]:  # Skip header row
            data_row = []
            for datum in row['Data']:
                data_row.append(datum.get('VarCharValue', ''))
            data_rows.append(data_row)
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=columns)
        return df