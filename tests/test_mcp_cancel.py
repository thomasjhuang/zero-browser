"""MCP cancellation must wait for owned-process cleanup."""

import asyncio

import anyio

from scripts import mcp_server


def test_mcp_cancellation_waits_for_supervisor_cleanup(monkeypatch):
    class Process:
        returncode = None
        terminated = False

        async def wait(self):
            if self.terminated:
                await asyncio.sleep(0.01)
                self.returncode = 130
                return 130
            await asyncio.Event().wait()

        def terminate(self):
            self.terminated = True

    process = Process()

    async def start(*_args, **_kwargs):
        return process

    async def run():
        with anyio.move_on_after(0.02) as scope:
            await mcp_server.run_browser_goal("Open the fixture.", "http://localhost/")
        assert scope.cancel_called
        assert process.terminated
        assert process.returncode == 130

    monkeypatch.setattr(mcp_server.asyncio, "create_subprocess_exec", start)
    anyio.run(run)
