import subprocess
from loguru import logger

from paths import BASEPATH


# The publish branch. A refresh fired from any other checkout used to push that
# checkout -- four "Automatic dashboard update" commits landed on a refactor
# branch that way, because the old code ran `git add .` and `git push` against
# whatever HEAD happened to be.
PUBLISH_BRANCH = "main"

# Named instead of `git add .` for the same reason: the pipeline commits its own
# output and nothing else. Anything else dirty in the tree is the author's, and
# an automated run has no business deciding to commit it.
PUBLISH_PATHS = [
    "docs/assets/data_charts",
    "docs/_includes",
    "services/data_raw",
]


def run(cmd, check=True):
    result = subprocess.run(cmd, cwd=BASEPATH, capture_output=True, text=True)
    # git failures are silent otherwise: a rejected commit still fell through to
    # `git push`, which then reported success for having pushed nothing.
    if check and result.returncode != 0:
        raise RuntimeError(
            "%s failed (%d): %s" % (" ".join(cmd), result.returncode, result.stderr.strip())
        )
    return result


def current_branch():
    return run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()


def publish():
    branch = current_branch()
    if branch != PUBLISH_BRANCH:
        logger.error(
            "Refusing to publish from '%s' -- only '%s' is published. "
            "Switch branches and re-run if this refresh was intended." % (branch, PUBLISH_BRANCH)
        )
        return False

    # Scoped to PUBLISH_PATHS so an unrelated edit elsewhere in the tree neither
    # triggers a publish nor produces an empty commit.
    status = run(["git", "status", "--porcelain", "--"] + PUBLISH_PATHS)

    if status.stdout.strip() == "":
        logger.info("No changes, no push.")
        return False

    logger.info("Pushing to github ...")
    run(["git", "add", "--"] + PUBLISH_PATHS)
    run(["git", "commit", "-m", "Automatic dashboard update"])
    run(["git", "push"])
    logger.info("Pushed changes to github")
    return True


if __name__ == "__main__":
    publish()
