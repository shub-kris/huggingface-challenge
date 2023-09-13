## Question 2 - Resuming Training in HuggingFace Trainer

We have someone using HuggingFace Trainer to finetune our internal
cluster. If there is an error during the training job, any data not explicitly synced to external
storage is lost. This includes any model checkpoints. Design a recommended way for syncing
checkpoints to external storage (e.g., s3) instead of just writing them locally during training.


## Solution

I propose to create a custom callback named `S3SyncCallback`. It is inspired by the `TensorBoardCallback` that is provided by the Hugging Face Trainer. The `S3SyncCallback` would be responsible for synchronizing checkpoints with an Amazon S3 bucket. The callback would be triggered on each `on_save` which is the Event called after a checkpoint save.The callback would be responsible for uploading the checkpoint to the S3 bucket. This approach guarantees that critical data, such as checkpoints, remains consistently stored in an external repository like `S3`, mitigating the risk of data loss in the event of errors.
The code for the `S3SyncCallback` is available in the `s3_sync_callback.py` file. I have utilised `s3fs` python package to upload the checkpoints to the S3 bucket. The `s3fs` package is a pythonic file interface to `S3`.

The callback can be used as follows using the `Trainer` API:

``` python
    trainer = Trainer(...)
    trainer.add_callback(S3SyncCallback)
```

Note: One needs to make sure that the AWS credentials are set as environment variables. The `S3SyncCallback` would raise an error if the AWS credentials are not set. The `S3SyncCallback` would also raise an error if the `s3fs` package is not installed. Make sure that the `S3` bucket exists and the AWS credentials have proper rights to write to the bucket.
Snapshot of the code:

``` python
import importlib
import logging
import os
from transformers import TrainerCallback
import s3fs

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
    return (
        "AWS_ACCESS_KEY_ID" in os.environ
        and "AWS_SECRET_ACCESS_KEY" in os.environ
    )


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
                artifact_path, f"{self._bucket_name}/{args.output_dir}/{ckpt_dir}", recursive=True
            )


```

### Generic Solution
A more generic solution would have been to use `fsspec` python package which is a unified interface for cloud storage and other file systems. It provides a common pythonic interface to multiple file system types. One could have a single callback called `FSpecCallback` which would have taken the file system type as an argument. The callback would be responsible for uploading the checkpoints to the specified file system. One could have easily integrated the Cloud Storage like `S3`, `GCS` and `Azure` with the `FSpecCallback`.

``` python
    trainer = Trainer(...)
    trainer.add_callback(FsSpecSyncCallback)
```

### Another Approach

Use `s3fs-fuse` package to define the `S3fuseCallback`. `s3fs-fuse` package is a FUSE filesystem backed by Amazon `S3`. It allows you to mount an S3 bucket as a local filesystem. This approach is useful when you want to use the checkpoints in another machine. The checkpoints can be accessed as if they were local files. However it would require some efforts (using CLI) to mount the S3 bucket as a local filesystem.



