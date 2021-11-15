import psycopg2
import pandas as pd
import boto3
from io import BytesIO, StringIO
import os, json
import sys

csv_buffer = StringIO()
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
table_name='cleandata'
port=5432

def get_secret():
    sm_client = boto3.client('secretsmanager', region_name=os.getenv('region'))
    sm_data = sm_client.get_secret_value(SecretId=os.getenv('secrets'))
    secret_data = json.loads(sm_data.get('SecretString'))
    host_nm=secret_data.get('host')
    port_no=secret_data.get('ports')
    db=secret_data.get('database')
    user_nm=secret_data.get('username')
    passw=secret_data.get('password')
    return secret_data

def create_db_conn(secret):
    '''
    Create RDS Database Connection
    '''
    host=secret.get('host')
    port=secret.get('ports')
    database=secret.get('database')
    user=secret.get('username')
    password=secret.get('password')
    
    
    try:
        conn= psycopg2.connect(host=host, port=port,user=user,password=password,database=database)
        print("Connection Established")
        return conn
    except Exception as e:
        print(e)
        print('Cannot Connect to DB')
    
create_db_conn()

def lambda_handler(event, context):
    s3= event['Records'][0]['s3']
    bucket_name = s3['bucket']['name']
    file_name = s3['object']['key']
    obj = s3_client.get_object(Bucket=bucket_name, Key = file_name)
    context=''
    def clean_up(obj):
        df = pd.read_csv(obj['Body'])
        print('Dataframe Size is ', len(df))

        #Rename the columns
        df.columns=['ID','FIRTS_NAME','LAST_NAME','EMAIL', 'GENDER', 'IP_ADDRESS']
        def remove_comma(strg):
            clean_str=strg.replace(',','')
            return clean_str

        #drop all invalid and incomplete rows 
        df.dropna(inplace=True)
        
    
        #extract & drop  all duplicate values 
        df.loc[df.duplicated(), :]
        df.duplicated()
        df.drop_duplicates()

        #Adds 2 colums together to creat an extra column
        df['full_name'] = df['first_name'] + ' ' + df['last_name']
        print(df)

        secret=get_secret()
    
    
        conn=create_db_conn(secret)
        cursor=conn.cursor()

        #write dataframe to temporary directory as csv
        temp_dir='/tmp/DataClean.csv'
        df.to_csv(temp_dir, index=False, header=False)

        #load the DF into rds
        #insertquery = "select * from mobile"
        f = open(temp_dir, 'r')
        connection = create_db_conn()
        cursor=connection.cursor()
        try:
            cursor.copy_from(f, table_name, sep=",")
            connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            os.remove(temp_dir)
            print("Error: %s" % error)
            connection.rollback()
            cursor.close()
            return 1
        print("copy_from_file() done")
        cursor.close()
        f.close()
        os.remove(temp_dir)

    clean_up(obj)
# # context=''
# # lambda_handler(event, context)