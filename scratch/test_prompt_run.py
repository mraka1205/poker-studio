import asyncio
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path.cwd()))
import backend.antigravity_cli as cli

async def test():
    episode_id = "ep04-poker-hand"
    try:
        task = await cli.start_storyboard_generation(episode_id)
        print("Task status:", task.status)
        print("Task error:", task.error_message)
        print("Logs:", task.logs)
        print("Conv ID:", task.conversation_id)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    asyncio.run(test())
