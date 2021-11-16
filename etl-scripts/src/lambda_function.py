import psycopg2
import pandas as pd
import boto3
from io import BytesIO, StringIO
import os, json
import sys
import time

csv_buffer = StringIO()
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
table_name='data_table'
port=5432

#Defined a function to store database secrets in secret manager
def get_secret():
    sm_client = boto3.client('secretsmanager', region_name=os.getenv('region'))
    sm_data = sm_client.get_secret_value(SecretId=os.getenv('secrets'))
    secret_data = json.loads(sm_data.get('SecretString'))
    host_nm=secret_data.get('host')
    port_no=secret_data.get('ports')
    db=secret_data.get('database')
    user_nm=secret_data.get('username')
    passw=secret_data.get('password')
    #print (secret_)
    return secret_data

#Defined a a function to connect to database
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
    
#create_db_conn()

#Using lambda boto3 client, created a lambda function to injest data in s3
def lambda_handler(event, context):
    obj = s3_client.get_object(Bucket='sfl-s3', Key = 'raw-input/DATA.csv')
    #clean_up(obj)
    
    def clean_up(obj):
        df = pd.read_csv(obj['Body'])
        print('Dataframe Size is ', len(df))
        print(df.head(10))
    
        #Rename the columns
        df.columns=['ID','FIRST_NAME','LAST_NAME','EMAIL', 'GENDER', 'IP_ADDRESS']
    
        #Adds 2 colums together to creat an extra column
        df['FULL_NAME'] = df['FIRST_NAME'] + ' ' + df['LAST_NAME']
        print(df)
        
        #extract & drop  all duplicate values 
        print('dataframe size before drop duplicate:', len(df))
        df=df.drop_duplicates(subset=['EMAIL'])
        print('dataframe size after drop duplicate:', len(df))
        
        # function for vlookup Order Priority_key
        def Gender(x):
            if x == 'Agender':
                return 'A'
            elif x =='Bigender':
                return 'B'
            elif x == 'Female':
                return 'F'
            elif x == 'Genderfluid':
                return 'GF'
            elif x == 'Genderqueer':
                return 'GQ'
            elif x == 'Male':
                return 'M'
            elif x == 'Non-binary':
                return 'GQ'
        
        df['GENDER_KEY'] = df['GENDER'].apply(lambda x: Gender(x))
    
        #write dataframe to temporary directory as csv
        temp_dir='/tmp/dataclean.csv'
        df.to_csv(temp_dir, index=False, header=False)

        #load the DF into rds
        f = open(temp_dir, 'r')
        secret=get_secret()
        print('secret: ', secret)
        
        connection = create_db_conn(secret)
        cursor=connection.cursor()
        time.sleep(4)
        #print(testing)
        try:
            cursor.copy_from(f, table_name, sep=",")
            connection.commit()
            print ('ingestion sucessful')
            
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
