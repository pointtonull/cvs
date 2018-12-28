#!/usr/bin/env python3
#-*- coding: UTF-8 -*-

"""
module description
"""

from textwrap import indent
import itertools
import os
import re
import sys

from collections import defaultdict
from subprocess import check_output, CalledProcessError
from sys import exit


TAG_REGEX = re.compile(r"""(?m)^.+%\s*(?P<group>\w+):(?P<tags>[\w,]+)$""")
TARGET = "_build"
PDFLATEX = "pdflatex -synctex=1 -interaction=nonstopmode -output-directory %s " % TARGET


def find_tags(master):
    text = "".join(master)
    all_tags = defaultdict(set)
    for match in TAG_REGEX.finditer(text):
        if match.group(0).startswith("%"):
            # ignore commented lines, even if tagged
            continue

        tags = match.group("tags")
        for tag in tags.split(","):
            all_tags[match.group("group")].add(tag)
    return all_tags


def versionize(text, tags):
    for group, tag in tags:
        tag_text = r"%s:[\w,]*%s[\w,]*" % (group, tag)
        tag_re = r"(?m)%%\s*%s$" % tag_text
        text = re.sub(tag_re, "%% selected bc: %s." % tag_text, text)
        group_re = r"(?m)^(.*)\s*%%\s*%s:[\w,]+$" % group
        text = re.sub(group_re, r"%% \1 %% commented bc: %s." % tag_text, text)
    return text


def pdflatex(filename):
    command = PDFLATEX + filename
    print("running '%s'" % command)
    check_output(command, shell=True)


def build(filename):
    master_prefix, master_extension = os.path.splitext(filename)
    master = open(filename).read()
    tags = find_tags(master)
    os.makedirs(TARGET, exist_ok=True)

    groups = sorted(tags)
    print("Creating permutations over groups: %s" % ", ".join(groups))
    versions = itertools.product(*([(group, tag)  for tag in tags[group]]
            for group in groups))

    filenames = []
    print("Creating custom versions:")
    for version in versions:
        sufix = "_".join(tag[-1]  for tag in version)
        version_name = "%s_%s%s" % (master_prefix, sufix, master_extension)
        filename = os.path.join(TARGET, version_name)
        print("  %s" % filename)
        versionized = versionize(master, version)
        with open(filename, "w") as file:
            file.write(versionized)
        filenames.append(filename)

    for filename in filenames:
        try:
            pdflatex(filename)
        except CalledProcessError as error:
            print("Failed building '%s' with error:" % filename)
            print(indent(error.output.decode(), "    "))
            print("Errorcode: %s" % error.returncode)
            print("Sourcecode: %s" % filename)
            return 1

        pdf_filename = filename.replace(master_extension, ".pdf")
        try:
            check_output("mv '%s' ./" % pdf_filename, shell=True)
        except CalledProcessError as error:
            print("Failed copying '%s' with error:" % pdf_filename)
            print(indent(error.output.decode(), "    "))
            print("Errorcode: %s" % error.returncode)
            return 1

    return 0


def main():
    """
    The main function.
    """
    filename = sys.argv[1]
    return build(filename)


if __name__ == "__main__":
    exit(main())
