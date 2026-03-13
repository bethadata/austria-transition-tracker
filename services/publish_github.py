import subprocess
from loguru import logger 

from config import BASEPATH 


def run(cmd):
    return subprocess.run(cmd, cwd=BASEPATH, capture_output=True, text=True)

def publish(): 
    # check if changes exist
    status = run(["git", "status", "--porcelain"])

    if status.stdout.strip() != "":
        logger.info("Pushing to github ...")
        run(["git", "add", "."])
        run(["git", "commit", "-m", "Automatic dashboard update"])
        run(["git", "push"])
        logger.info("Pushed changes to github")
    else:
        logger.info("No changes, no push.")


if __name__ == "__main__": 
    publish()


