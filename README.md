# This is the read me file for how the project should be run.
# All files & packages needed are already in the github repo shared

# first deploy the s3 cloudformation stack:(you can deply via console or cli)
 - sfl-s3-cloudformation.yaml. 
 - This stack would create an s3 bucket in the specified region. The create a folder called raw-input where your csv file would be put.

# The next step is deploy vpc cloudformation stack.
- sfl-vpc-cloudformation.yaml
- This stack would deploy the vpc and the postgres RDS

# Now use AWS serverless application model(sam) to deploy the lambda cloudformation stack
- template.yaml
- All modules have been installed in the python folder called packages
- Activate a virtual environment
- Cd to the etl-scripts folder and start your servelss deployment
 - use the following command (note you should specify a different s3 bucket to store sam)
 'sam build'
 'sam deploy --stack-name lambda-etl2 --s3-bucket forex-bucket-samsideen --s3-prefix sam-content --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM'

# Once rds has been created, connect to the DB and create a table with the schema of our csv. Like below
    CREATE TABLE cleandata (
  id int NOT NULL,
  first_name int NOT NULL,
  last_name varchar NOT NULL,
  email varchar DEFAULT NULL,
  gender varchar NOT NULL,
  ip_address varchar NOT NULL,
  gender_category varchar NOT NULL,
  full_name varchar NOT NULL
	);
              
# Create a Trigger Rule
  Once lambda has been created successfully create a trigger rule from the console.
  Navigate to the function created (ETL_trigger) on the console, collaspe function overview section then click add trigger and follow the instruction
   - choose s3
   - choose the s3 bucket name created
   - select 'put' as your event type
   - let the prefixes be 'raw-input\'
   - let suffixes be '.csv'
   - then click add

# To test test the lambda, drop DATA.csv into the aqua-datasetset bucket under 'raw-input' folder then go to the database table created to see the file content ingested