# -*- coding: utf-8 -*-
#  Copyright (c) 2022 RaptorML authors.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import shutil
from typing import Dict

import attr
from bentoml import Bento
from bentoml._internal.bento.build_config import BentoBuildConfig

from .protocol import ModelServer


class Sagemaker(ModelServer):
    """Sagemaker model server."""

    BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sagemaker')

    @classmethod
    def inference_config(cls, **kwargs) -> Dict:
        return {
            'region': '$AWS_REGION',
            'executionRoleARN': '$AWS_EXECUTION_ROLE_ARN',
            'serverlessMaxConcurrency': '$AWS_SERVERLESS_MAX_CONCURRENCY',
            'serverlessMemorySizeInMB': '$AWS_SERVERLESS_MEMORY_SIZE_IN_MB',
        }

    @classmethod
    def apply_bento_config(cls, cfg: BentoBuildConfig) -> BentoBuildConfig:
        docker = attr.evolve(cfg.docker, dockerfile_template=os.path.join(cls.BASE_DIR, 'template.j2'))
        cfg = attr.evolve(cfg, docker=docker)
        return cfg

    @classmethod
    def post_build(cls, bento: Bento):
        shutil.copy(
            os.path.join(cls.BASE_DIR, 'sagemaker_service.py'),
            os.path.join(bento.path, 'sagemaker_service.py'),
        )

        serve_path = os.path.join(cls.BASE_DIR, 'serve')
        shutil.copy(serve_path, os.path.join(bento.path, 'serve'))
        # permission 755 is required for entry script 'serve'
        os.chmod(serve_path, 0o755)
