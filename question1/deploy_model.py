import os
from uuid import uuid4

import boto3
import sagemaker
from sagemaker.huggingface import HuggingFaceModel


def get_role(profile_name: str) -> str:
    """
    The function `get_role` returns the execution role associated with a specified AWS profile name.

    Args:
      profile_name (str): It represents the name of the AWS
    profile to use for authentication.

    Returns:
      the arn associated with the specified profile name.
    """
    session = boto3.Session(profile_name=profile_name)
    sagemaker_session = sagemaker.Session(session)
    role = sagemaker.get_execution_role(sagemaker_session=sagemaker_session)
    return role


def test_prediction(predictor: sagemaker.Predictor):
    data = {
        "inputs": {
            "question": "Which company would Shubham like to work for?",
            "context": "My name is Shubham Krishna. I come from India. I am a ML Engineer with expertise in NLP and would like to work for HuggingFace.",
        }
    }
    return predictor.predict(data)


def autoscale_endpoint(predictor: sagemaker.Predictor) -> None:
    """
    The function registers a scalable target and creates a scaling policy for a
    SageMaker endpoint based on CPU utilization.

    Args:
      predictor (sagemaker.Predictor): It represents the predictor object that is associated with the endpoint
    you want to autoscale.
    """
    autoscaling_client = boto3.client("application-autoscaling")
    resource_id = f"endpoint/{predictor.endpoint_name}/variant/AllTraffic"

    # scaling configuration
    response = autoscaling_client.register_scalable_target(
        ServiceNamespace="sagemaker",  #
        ResourceId=resource_id,
        ScalableDimension="sagemaker:variant:DesiredInstanceCount",
        MinCapacity=1,
        MaxCapacity=4,
    )

    response = autoscaling_client.put_scaling_policy(
        PolicyName=f"CPUUtilization-ScalingPolicy-{predictor.endpoint_name}",
        ServiceNamespace="sagemaker",
        ResourceId=resource_id,
        ScalableDimension="sagemaker:variant:DesiredInstanceCount",
        PolicyType="TargetTrackingScaling",
        TargetTrackingScalingPolicyConfiguration={
            "TargetValue": 50.0,  # threshold
            "CustomizedMetricSpecification": {
                "MetricName": "CPUUtilization",
                "Namespace": "/aws/sagemaker/Endpoints",
                "Dimensions": [
                    {"Name": "EndpointName", "Value": predictor.endpoint_name},
                    {"Name": "VariantName", "Value": "AllTraffic"},
                ],
                "Statistic": "Average",
                "Unit": "Percent",
            },
            "ScaleInCooldown": 300,  # duration between scale in
            "ScaleOutCooldown": 100,  # duration between scale out
        },
    )


if __name__ == "__main__":
    hub = {
        "HF_MODEL_ID": "distilbert-base-uncased-distilled-squad",
        "HF_TASK": "question-answering",
    }

    endpoint_name = f"bert-qa-dem-{str(uuid4())}"

    huggingface_model = HuggingFaceModel(
        env=hub,
        role=get_role(profile_name=os.environ.get("PROFILE_NAME", "sagemaker")),
        name=endpoint_name,
        transformers_version="4.6",
        pytorch_version="1.7",
        py_version="py36",
    )

    predictor = huggingface_model.deploy(
        initial_instance_count=1, instance_type="ml.c5.large"
    )
    response = test_prediction(predictor)
    print(response)
    autoscale_endpoint(predictor)
