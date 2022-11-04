import json
import boto3


rds_client = boto3.client('rds-data')
database_name = 'ipdatabase'
db_cluster_arn = 'arn:aws:rds:us-east-2:026802451096:cluster:ipdatabase-cluster'
db_credentials_secrets_store_arn = 'arn:aws:secretsmanager:us-east-2:026802451096:secret:rds-db-credentials/cluster-3V4ZRVTP2PSUNQKECQIA4RGFVY/admin/1666484218072-hdxza0'


def lambda_handler(event, context):
    # TODO implement
    
    path = event['path']
    httpmethod=event['httpMethod']
    user_id=event['queryStringParameters']['user_id']
    
    if path=='/gettask':
        task_id=event['queryStringParameters']['id']
        querystring = 'SELECT * FROM ipdatabase.tasks where task_id= %d'%(int(task_id))
    
    if path=='/getalltasks':
        querystring = 'SELECT * FROM ipdatabase.tasks where user_id= %d '%(int(user_id))
    
    if path=='/newtask':
        task_title=event['queryStringParameters']['title']
        task_description=event['queryStringParameters']['description']
        tasktime=event['queryStringParameters']['tasktime']
        querystring = 'insert into tasks (user_id,task_title,task_description,task_status,task_date) values ("%s","%s","%s","active","%s")'%(user_id,task_title,task_description,tasktime)
        
    if path=='/updatetask':
        task_id=event['queryStringParameters']['id']
        task_title=event['queryStringParameters']['title']
        tasktime=event['queryStringParameters']['tasktime']
        task_description=event['queryStringParameters']['description']
        querystring = 'UPDATE tasks SET task_title = "%s", task_description = "%s", task_date = "%s" WHERE task_id = %d;'%(task_title,task_description,tasktime,int(task_id))
        
    if path=='/completetask':
        task_id=event['queryStringParameters']['id']
        querystring = 'UPDATE tasks SET task_status = "completed" WHERE task_id = %d'%(int(task_id))
    
    if path=='/removetask':
        task_id=event['queryStringParameters']['id']
        querystring = 'DELETE FROM tasks WHERE task_id = %d'%(int(task_id))
    
    
    if path =='/getalltasks' or path == '/gettask':
        response = execute_statement(querystring)
        data2 = str(response).replace("'","\"")
        data = json.loads(data2)
        
        status_c = data['ResponseMetadata']['HTTPStatusCode']
        Tasks = []
        for record in data['records'] :
            task = {}
            task['id'] = record[0]['longValue']
            task['title'] = record[2]['stringValue']
            task['description'] = record[3]['stringValue']
            task['status'] = record[4]['stringValue']
            task['tasktime'] = record[5]['stringValue']
            Tasks.append(task)
        
        final = json.dumps(Tasks,indent=2)
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                
            },
            'body': final
            
        }
        
        
    else :
        response = execute_statement(querystring)
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                
            },
            'body': str(response)
            
        }

    
def execute_statement(sql):
    response = rds_client.execute_statement(
        secretArn=db_credentials_secrets_store_arn,
        database=database_name,
        resourceArn=db_cluster_arn,
        sql=sql
    )
    
    return response
    
            
    
    
