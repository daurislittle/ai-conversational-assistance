from aws_cdk import (
    aws_dynamodb as dynamodb,
    Stack,
    Duration,
    RemovalPolicy
)

from constructs import Construct

class DBStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.session_table = dynamodb.Table(
            self, "ConversationalSessionTable",
            table_name="ConversationalSessionTable",

            partition_key=dynamodb.Attribute(
                name="sessionId",
                type=dynamodb.AttributeType.STRING
            ),

            sort_key=dynamodb.Attribute(
                name="createdAt",
                type=dynamodb.AttributeType.STRING
            ),

            time_to_live_attribute="ttl",
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )