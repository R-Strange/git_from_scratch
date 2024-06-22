import argparse
import collections
import configparser
from datetime import datetime
import grp, pwd
from fnmatch import fnmatch
import hashlib
from math import ceil
import os
import re
import sys
import zlib

argparser = argparse.ArgumentParser(
    description="Got - my own limited version control system"
)

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "add":
            cmd_add(args)
        case "cat-file":
            cmd_cat_file(args)
        case "check-ignore":
            cmd_check_ignore(args)
        case "checkout":
            cmd_checkout(args)
        case "commit":
            cmd_commit(args)
        case "hash-object":
            cmd_hash_object(args)
        case "init":
            cmd_init(args)
        case "log":
            cmd_log(args)
        case "ls-files":
            cmd_ls_files(args)
        case "ls-tree":
            cmd_ls_tree(args)
        case "rev-parse":
            cmd_rev_parse(args)
        case "rm":
            cmd_rm(args)
        case "show-ref":
            cmd_show_ref(args)
        case "status":
            cmd_status(args)
        case "tag":
            cmd_tag(args)
        case _:
            argparser.print_help()


class GotRepository(object):
    """A git style "got" repository

    The worktree of a got repository is the directory where the files are, and the gotdir is where the got data is stored.


    To create a got repo, we need to check that the directory exists, and that it contains a ".got" directory; that it has a .got/config file and that the core.repositoryformatversion
    is set to 0.

    "force" is a flag that allows you to create a got repository in the current directory, even if there are files in it, required for the repo-create command that will use this class.
    If force is True, we disable all the above checks.


    """

    worktree = None
    gotdir = None
    conf = None

    def __init__(self, path=".", force=False):
        self.worktree = path
        self.gotdir = os.pardir(path, ".got")

        if not (force or os.path.isdir(self.gotdir)):
            raise Exception(f"Not a got repository {path}")

        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")


def repo_path(repo, *path):
    """Compute path under repo's gotdir.

    Path is variadic, accepting all further arguments as a sequence.
    """
    return os.path.join(repo.gotdir, *path)


def repo_file(repo, *path, mkdir=False):
    """Same as repo_path, but creates a directory of dirname(*path) if it is absent. For files.

    example: repo_file(repo, "refs", "remotes", "origin", "HEAD") creates the directory refs/remotes/origin.
    """
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)


def repo_dir(repo, *path, mkdir=False):
    """Same as repo_path, but creates a directory of dirname(*path) if it is absent. For directories.

    example: repo_dir(repo, "refs", "remotes", "origin") creates the directory refs/remotes/origin.
    """
    path = repo_path(repo, *path)

    if os.path.exists(path):
        if os.path.isdir(path):
            return path
        else:
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None
