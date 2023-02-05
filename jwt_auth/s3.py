import random

import boto3
import botocore


def get_random_image(cfg: dict[str, str | None]) -> str:
    client = boto3.client(
        "s3",
        aws_access_key_id=cfg["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=cfg["AWS_SECRET_ACCESS_KEY"],
        region_name=cfg["AWS_REGION_NAME"],
        config=botocore.client.Config(signature_version="s3v4"),
    )

    response = client.list_objects(Bucket=cfg["AWS_BUCKET_NAME"])
    folder_name: str = cfg["AWS_FOLDER_NAME"]
    file_names: list[str] = list(
        filter(
            lambda file_name: file_name != folder_name + "/",
            [obj["Key"] for obj in response["Contents"] if obj["Key"].startswith(folder_name)],
        )
    )

    object_name = random.choice(file_names)

    return client.generate_presigned_url("get_object", Params={"Bucket": cfg["AWS_BUCKET_NAME"], "Key": object_name})
