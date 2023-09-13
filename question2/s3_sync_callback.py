import importlib
import logging
import os

import s3fs
from transformers import TrainerCallback


def is_s3fs_available() -> bool:
    """
    Checks if the `s3fs` module is available in the Python
    environment.

    Returns:
      a boolean value indicating whether the "s3fs" module is available or not.
    """
    return importlib.util.find_spec("s3fs") is not None


def check_aws_credentials():
    """
    Check if AWS credentials are set as environment variables.

    Returns:
        bool: True if all required AWS credentials are present, False otherwise.
    """
    return "AWS_ACCESS_KEY_ID" in os.environ and "AWS_SECRET_ACCESS_KEY" in os.environ


class S3SyncCallback(TrainerCallback):
    """
    A [`TrainerCallback`] that sends checkpoints to [AWS-S3](https://aws.amazon.com/s3/).
    """

    def __init__(self):
        if not is_s3fs_available():
            raise RuntimeError(
                "S3SyncCallback requires s3fs to be installed. Run `pip install s3fs`."
            )
        if not check_aws_credentials():
            raise RuntimeError(
                "S3SyncCallback requires to set environment variables: AWS_SECRET_ACCESS_KEY, and AWS_ACCESS_KEY_ID."
            )
        import s3fs

        self._initialized = False

    def setup(self, args, state, model):
        self._initialized = True
        self._bucket_name = os.getenv("AWS_BUCKET_NAME", "huggingface-checkpoints")
        self._region = os.getenv("AWS_REGION", "eu-north-1")
        self._s3fs = s3fs.S3FileSystem(anon=False)

    def on_train_begin(self, args, state, control, model=None, **kwargs):
        if not self._initialized:
            self.setup(args, state, model)

    def on_save(self, args, state, control, model, **kwargs):
        if self._initialized and state.is_world_process_zero:
            ckpt_dir = f"checkpoint-{state.global_step}"
            artifact_path = os.path.join(args.output_dir, ckpt_dir)
            logging.info(
                f"Logging checkpoint artifacts in {ckpt_dir}. This may take time."
            )
            self._s3fs.put(
                artifact_path,
                f"{self._bucket_name}/{args.output_dir}/{ckpt_dir}",
                recursive=True,
            )
