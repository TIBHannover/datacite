#!/usr/bin/env python3
"""Copy and verify generated namespace files while preserving publication-owned roots."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

REQUIRED_DIRECTORIES = ("class", "property", "vocab", "context", "manifest", "dist", "mappings")
DIRECTORIES = (*REQUIRED_DIRECTORIES, "shapes", "schema-profiles")
INTEGRITY = "manifest/bundle-integrity.json"
ROOT_FILES = {"README.md", "LICENSE", ".nojekyll", "index.html"}


def generated_files(root):
    return sorted(p.relative_to(root).as_posix() for name in DIRECTORIES
                  for p in (root / name).rglob("*") if p.is_file() and p.relative_to(root).as_posix() != INTEGRITY)


def verify_integrity(root, publication=True):
    checksums = root / "CHECKSUMS.sha256"
    entries = checksums.read_text().splitlines()
    subprocess.run(["shasum", "-a", "256", "-c", "CHECKSUMS.sha256"], cwd=root,
                   check=True, stdout=subprocess.DEVNULL)
    metadata = json.loads((root / INTEGRITY).read_text())
    if metadata["artifactFileCount"] != len(entries):
        raise ValueError("Integrity artifact count differs from the checksum list")
    if metadata["bundleChecksum"] != hashlib.sha256(checksums.read_bytes()).hexdigest():
        raise ValueError("Integrity bundle checksum differs from the checksum-list hash")
    if publication:
        listed = [line.split("  ", 1)[1] for line in entries]
        if listed != generated_files(root):
            raise ValueError("Checksum list does not cover exactly the generated publication files")


def compare_source(source, target):
    expected = generated_files(source)
    if expected != generated_files(target):
        raise ValueError("Publication generated file list differs from the source bundle")
    for name in expected:
        if (source / name).read_bytes() != (target / name).read_bytes():
            raise ValueError(f"Publication differs from source: {name}")


def write_integrity(target, source_metadata):
    names = generated_files(target)
    content = "".join(hashlib.sha256((target / name).read_bytes()).hexdigest() + "  " + name + "\n" for name in names)
    (target / "CHECKSUMS.sha256").write_text(content)
    metadata = dict(source_metadata)
    metadata.update(artifactFileCount=len(names), bundleChecksumAlgorithm="sha256-of-CHECKSUMS.sha256",
                    bundleChecksum=hashlib.sha256(content.encode()).hexdigest(), checksumsFile="CHECKSUMS.sha256",
                    excludedFromChecksum=["CHECKSUMS.sha256", INTEGRITY, *sorted(ROOT_FILES)],
                    includedDirectories=list(DIRECTORIES))
    (target / INTEGRITY).write_text(json.dumps(metadata, indent=2) + "\n")


def sync(source, target):
    source, target = source.resolve(), target.resolve()
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("Source and target must be separate directories")
    verify_integrity(source, publication=False)
    unknown = {p.name for p in source.iterdir()} - set(DIRECTORIES) - ROOT_FILES - {"CHECKSUMS.sha256"}
    if unknown:
        raise ValueError(f"Unrecognized source bundle paths: {sorted(unknown)}")
    for name in REQUIRED_DIRECTORIES:
        if not (source / name).is_dir():
            raise ValueError(f"Missing required source directory: {name}")
    protected = {name: (target / name).read_bytes() for name in ROOT_FILES if (target / name).exists()}
    source_metadata = json.loads((source / INTEGRITY).read_text())
    for name in DIRECTORIES:
        destination = target / name
        if destination.exists():
            shutil.rmtree(destination)
        if (source / name).exists():
            shutil.copytree(source / name, destination)
    compare_source(source, target)
    write_integrity(target, source_metadata)
    verify_integrity(target)
    for name, content in protected.items():
        if (target / name).read_bytes() != content:
            raise ValueError(f"Publication-owned root file changed: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        verify_integrity(args.target)
        if args.source:
            compare_source(args.source, args.target)
    elif args.source:
        sync(args.source, args.target)
    else:
        parser.error("--source is required when syncing")
    print("Publication file coverage and integrity verified.")


if __name__ == "__main__":
    main()
