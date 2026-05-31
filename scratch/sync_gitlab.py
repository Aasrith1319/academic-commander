import subprocess
import os

def run_git(args):
    res = subprocess.run(args, capture_output=True, text=True)
    print("COMMAND:", " ".join(args))
    print("RETURN CODE:", res.returncode)
    if res.stdout.strip():
        print("STDOUT:", res.stdout.strip())
    if res.stderr.strip():
        print("STDERR:", res.stderr.strip())
    print("-" * 50)
    return res.returncode == 0

print("Fetching from GitLab remote...")
run_git(["git", "fetch", "gitlab"])

print("Creating a temporary branch from gitlab/main...")
run_git(["git", "checkout", "-b", "gitlab-merge", "gitlab/main"])

print("Merging local main with '-X theirs' to resolve conflicts in our favor...")
run_git(["git", "merge", "main", "--allow-unrelated-histories", "-m", "merge local main into gitlab main", "-X", "theirs"])

print("Pushing merged code to gitlab main...")
run_git(["git", "push", "gitlab", "gitlab-merge:main"])

print("Switching back to local main...")
run_git(["git", "checkout", "main"])

print("Deleting temporary branch...")
run_git(["git", "branch", "-D", "gitlab-merge"])
