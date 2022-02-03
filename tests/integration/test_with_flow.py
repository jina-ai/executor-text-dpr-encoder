import subprocess

import pytest
from jina import Document, DocumentArray, Flow

from dpr_text import DPRTextEncoder

_EMBEDDING_DIM = 768


@pytest.mark.parametrize("request_size", [1, 10, 50, 100])
def test_integration(request_size: int):
    docs = DocumentArray(
        [Document(text="just some random text here") for _ in range(50)]
    )
    with Flow(return_results=True).add(uses=DPRTextEncoder) as flow:
        docs = flow.post(
            on="/index",
            inputs=docs,
            request_size=request_size,
            return_results=True,
        )

    assert len(docs) == 50
    for doc in docs:
        assert doc.embedding.shape == (_EMBEDDING_DIM,)


@pytest.mark.docker
def test_docker_runtime(build_docker_image: str):
    with pytest.raises(subprocess.TimeoutExpired):
        subprocess.run(
            [
                "jina",
                "executor",
                f"--uses=docker://{build_docker_image}",
            ],
            timeout=30,
            check=True,
        )


@pytest.mark.gpu
@pytest.mark.docker
def test_docker_runtime_gpu(build_docker_image_gpu: str):
    with pytest.raises(subprocess.TimeoutExpired):
        subprocess.run(
            [
                "jina",
                "pea",
                f"--uses=docker://{build_docker_image_gpu}",
                "--gpus",
                "all",
                "--uses-with",
                'device:"cuda"',
            ],
            timeout=30,
            check=True,
        )