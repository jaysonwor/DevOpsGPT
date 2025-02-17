import boto3
from botocore.exceptions import ClientError
import datetime

# todo 未测试
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html
class CDAWS:    
    def triggerCD(self, image, serviceInfo, cdConfig):
        aws_service_name, aws_alb_name, aws_tg_name = self.generate_names_with_timestamp(serviceInfo["service_id"])
        print ('cdConfig : ', cdConfig ,
               'serviceInfo :' ,serviceInfo,
                "aws_alb_name :", aws_alb_name,
                "aws_tg_name :" ,aws_tg_name)
        # Create ALB and Target Group
        alb_arn, tg_arn, alb_dns_name, success = self.create_alb_and_target_group(cdConfig, serviceInfo, aws_alb_name, aws_tg_name)
        if not success:
            return f"Failed to create alb and target_grpup {alb_arn}", False

        # Create an ECS client
        client = boto3.client(
            'ecs',
            aws_access_key_id=cdConfig["ACCESS_KEY"],
            aws_secret_access_key=cdConfig["SECRET_KEY"],
            region_name=serviceInfo["cd_region"]
        )

        # Obtain the configured Secret value from AWS Secrets Manager for pulling the image of the private library
        secret_name = "Docker"
        secret_value = self.get_secret(secret_name, cdConfig, serviceInfo)

        # Create task definition
        container_definition = {
            "name": serviceInfo["cd_container_name"],
            "image": image,
            "cpu": 1024,  # 0.5 vCPU
            "memory": 2048,  # 2GB RAM
            "essential": True,
            "portMappings": [
                {'containerPort': 80,
                 'hostPort': 80,
                 'protocol': 'tcp'},
                ],
                 "environment": [  # Example: using secret_value as an environment variable
                    {
                        "name": "SECRET_KEY",
                        "value": secret_value
                    }
                ]
            }

        try:
            response = client.register_task_definition(
                family="testfamily",
                networkMode='awsvpc',
                requiresCompatibilities=['FARGATE'],
                cpu='2048',
                memory='4096',
                # https://cn-north-1.console.amazonaws.cn/iam/home#/roles/details/ecsTaskExecutionRole?section=permissions
                executionRoleArn=serviceInfo["cd_execution_role_arn"],
                containerDefinitions=[container_definition],
            )
        except Exception as e:
            return f"Error registering task definition: {str(e)}", False

        task_definition = response['taskDefinition']['taskDefinitionArn']

        print(f"Generated service_name: {aws_service_name}")
        try:
            # Create or update a service
            cd_cluster = 'KuaFuAIUser'
            existing_services = client.list_services(cluster=cd_cluster)
            if aws_service_name in existing_services["serviceArns"]:
                client.update_service(
                    cluster=cd_cluster,
                    service=aws_service_name,
                    desiredCount=1,  # Book 1 task
                    taskDefinition=task_definition,
                )
            else:
                client.create_service(
                    cluster=cd_cluster,
                    serviceName=aws_service_name,
                    taskDefinition=task_definition,
                    desiredCount=1,  # Book 1 task
                    launchType='FARGATE',
                    networkConfiguration={
                        'awsvpcConfiguration': {
                            'subnets': [serviceInfo["cd_subnet"], "subnet-02a884ac1c7bd0519"],
                            'securityGroups': [serviceInfo["cd_security_group"]],
                            'assignPublicIp': 'ENABLED'
                        }
                    },
                    loadBalancers=[
                        {
                            'targetGroupArn': tg_arn,
                            'containerName': serviceInfo["cd_container_name"],
                            'containerPort': 80     # Container listening port

                        }
                    ],
                )
        except Exception as e:
            return f"Error creating/updating service: {str(e)}", False

        return f'Visit URL：http://{alb_dns_name}:8086 （This environment is for experience only and will be deleted after 1 hour）', True
    
    def generate_names_with_timestamp(self, service_id):
        # Get the current time and format it into hours and minutes
        timestamp = datetime.datetime.now().strftime('%H%M')

        # Generate resource names, except the service name, which will be obtained from cdConfig
        albname = f"User-alb-{service_id}-{timestamp}"
        tgname = f"User-tg-{service_id}-{timestamp}"
        service_name = f"User-Service-{service_id}-{timestamp}"

        return service_name, albname, tgname,

    def create_alb_and_target_group(self, cdConfig, serviceInfo, albname, tgname):
        elbv2_client = boto3.client(
            'elbv2',
            aws_access_key_id=cdConfig["ACCESS_KEY"],
            aws_secret_access_key=cdConfig["SECRET_KEY"],
            region_name=serviceInfo["cd_region"]
        )

        try:
            # create ALB
            alb_response = elbv2_client.create_load_balancer(
                Name=albname,
                Subnets=[serviceInfo["cd_subnet"], serviceInfo["cd_subnet2"]],
                SecurityGroups=[serviceInfo["cd_security_group"]],
                Scheme='internet-facing',
                Tags=[{
                    'Key': 'Name',
                    'Value': 'my-alb'
                }]
            )
            alb_arn = alb_response['LoadBalancers'][0]['LoadBalancerArn']
            alb_dns_name = alb_response['LoadBalancers'][0]['DNSName']

            # create Target Group
            tg_response = elbv2_client.create_target_group(
                Name=tgname,
                Protocol='HTTP',
                Port=80,   # Note: Make sure this port number is consistent with the container listening port
                VpcId= serviceInfo["cd_vpc"],  # https://console.amazonaws.cn/vpc/home?region=cn-north-1#vpcs:
                TargetType='ip',
                HealthCheckProtocol='HTTP',  # Designated health screening protocol
                HealthCheckPort='80',  # Specify health check port
                HealthCheckPath='/',  # Specify health check path
                HealthCheckIntervalSeconds=30,  # Specify health check interval
                HealthCheckTimeoutSeconds=5,  # Specify health check timeout
                HealthyThresholdCount=2,  # Specify health threshold
                UnhealthyThresholdCount=2,  # Specify unhealthy threshold
            )

            tg_arn = tg_response['TargetGroups'][0]['TargetGroupArn']

            # 创建 Listener
            listener_response = elbv2_client.create_listener(
                LoadBalancerArn=alb_arn,
                Protocol='HTTP',
                Port=8086,  
                DefaultActions=[
                    {
                        'Type': 'forward',
                        'TargetGroupArn': tg_arn
                    }
                ]
            )

            return alb_arn, tg_arn, alb_dns_name, True
        except Exception as e:
            return f"Error creating ALB and Target Group: {str(e)}", None, None, False
    
    def get_secret(self, secret_name, cdConfig, serviceInfo):
        # Create an ECS client
        client = boto3.client(
            'secretsmanager',
            aws_access_key_id=cdConfig["ACCESS_KEY"],
            aws_secret_access_key=cdConfig["SECRET_KEY"],
            region_name=serviceInfo["cd_region"]
        )

        # Try retrieving the secret in a try block
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            # If the key is not found or another error occurs, print an error message
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager Unable to decrypt protected secret text
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An internal service error occurred
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                # The argument provided is invalid
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                # The request provided is invalid
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # The specified secret
                raise e
            else:
                # unknown error
                raise e
        else:
            # If the secret uses a string, return it directly
            if 'SecretString' in get_secret_value_response:
                return get_secret_value_response['SecretString']
            # Otherwise, return binary value
            else:
                return get_secret_value_response['SecretBinary']