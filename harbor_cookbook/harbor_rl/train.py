# /// script
# dependencies = [
#     "harbor @ git+https://github.com/harbor-framework/harbor.git@feature/harbor-rl-4d0",
#     "tinker-cookbook",
# ]
# requires-python = ">=3.12"
# ///

import argparse
import asyncio
import logging
from pathlib import Path
from typing import Any, Sequence

from harbor import SandboxFactory
from harbor.models.task.task import Task
from harbor.registry.client import RegistryClientFactory
from harbor.rl import RLEnvironment, ToolInput
from harbor.rl.tools import BashTool

from tinker_cookbook.model_info import get_recommended_renderer_name
from tinker_cookbook.renderers import get_renderer
from tinker_cookbook.rl import Env, EnvGroupBuilder, RLDataset
from tinker_cookbook.rl import train
from tinker_cookbook.tokenizer_utils import get_tokenizer
from tinker_cookbook.tool_use import build_agent_tool_env, simple_tool_result, tool
from tinker_cookbook.tool_use.types import ToolResult

log = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a skilled software engineer working in a sandboxed Linux environment. "
    "You have access to a bash tool to execute commands. "
    "Complete the task described by the user."
)


def make_bash_tool(env: RLEnvironment):
    @tool
    async def bash(command: str) -> ToolResult:
        """Execute a bash command in the sandbox."""
        outputs = await env.step(
            [ToolInput(name="bash", arguments={"command": command})]
        )
        return simple_tool_result("\n".join(c.text for c in outputs[0].content))

    return bash


def make_reward_fn(env: RLEnvironment):
    async def reward_fn(
        messages: list[dict[str, Any]],
    ) -> tuple[float, dict[str, float]]:
        result = await env.grade()
        return result.rewards.get("reward", 0.0), result.rewards

    return reward_fn


class HarborEnvGroupBuilder(EnvGroupBuilder):
    def __init__(
        self,
        task_path: Path,
        model_name: str,
        group_size: int,
        max_turns: int = 10,
        sandbox_type: str = "modal",
    ):
        self.task_path = task_path
        self.model_name = model_name
        self.group_size = group_size
        self.max_turns = max_turns
        self.sandbox_type = sandbox_type
        self._envs: list[RLEnvironment] = []

    async def make_envs(self) -> Sequence[Env]:
        task = Task(self.task_path)
        renderer_name = get_recommended_renderer_name(self.model_name)
        tokenizer = get_tokenizer(self.model_name)
        renderer = get_renderer(renderer_name, tokenizer)

        envs: list[Env] = []
        for _ in range(self.group_size):
            sandbox = await SandboxFactory.create(task=task, type=self.sandbox_type)
            rl_env = RLEnvironment(sandbox=sandbox, task=task)
            await rl_env.start(tools=[BashTool()])
            self._envs.append(rl_env)

            bash = make_bash_tool(rl_env)
            messages = renderer.create_conversation_prefix_with_tools(
                tools=[bash.to_spec()], system_prompt=SYSTEM_PROMPT
            ) + [{"role": "user", "content": rl_env.get_prompt()}]

            envs.append(
                build_agent_tool_env(
                    renderer=renderer,
                    tools=[bash],
                    initial_messages=messages,
                    reward_fn=make_reward_fn(rl_env),
                    max_turns=self.max_turns,
                )
            )
        return envs

    async def cleanup(self) -> None:
        await asyncio.gather(*(e.stop() for e in self._envs), return_exceptions=True)
        self._envs.clear()

    def logging_tags(self) -> list[str]:
        return [self.task_path.name]


class HarborDataset(RLDataset):
    def __init__(self, builders: list[HarborEnvGroupBuilder], batch_size: int):
        self._builders = builders
        self._batch_size = batch_size

    def get_batch(self, index: int) -> Sequence[EnvGroupBuilder]:
        start = index * self._batch_size
        return self._builders[start : start + self._batch_size]

    def __len__(self) -> int:
        return -(-len(self._builders) // self._batch_size)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-m", "--model", default="moonshotai/Kimi-K2-Thinking")
    p.add_argument("-d", "--dataset", default="terminal-bench@2.0")
    p.add_argument("--group-size", type=int, default=4)
    p.add_argument("-b", "--batch-size", type=int, default=8)
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--lora-rank", type=int, default=32)
    p.add_argument("--max-tokens", type=int, default=8192)
    p.add_argument("--max-turns", type=int, default=10)
    p.add_argument("-s", "--sandbox", default="modal")
    p.add_argument("--log-path", default="logs/")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s"
    )

    log.info("Loading %s ...", args.dataset)
    items = asyncio.run(RegistryClientFactory.create().download_dataset(args.dataset))
    task_paths = [item.downloaded_path for item in items]
    log.info("Found %d tasks", len(task_paths))

    async def build_datasets():
        builders = [
            HarborEnvGroupBuilder(
                p, args.model, args.group_size, args.max_turns, args.sandbox
            )
            for p in task_paths
        ]
        return HarborDataset(builders, args.batch_size), None

    config = train.Config(
        model_name=args.model,
        renderer_name=get_recommended_renderer_name(args.model),
        dataset_builder=build_datasets,
        learning_rate=args.lr,
        lora_rank=args.lora_rank,
        max_tokens=args.max_tokens,
        log_path=args.log_path,
    )

    log.info("Starting training (model=%s, tasks=%d)", args.model, len(task_paths))
    asyncio.run(train.main(config))


if __name__ == "__main__":
    main()
