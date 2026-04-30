import hashlib
import tarfile
import json
import os
import shutil

# Try to import blake3, fallback to sha256 to ensure functionality
try:
    import blake3
    def get_hash(filepath):
        h = blake3.blake3()
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
except ImportError:
    def get_hash(filepath):
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

def create_agentark_backup(source_dir: str, output_path: str):
    """
    Creates a .agentark backup (a renamed .tar.bz2).
    Includes a manifest.json with BLAKE3 (or SHA256) hashes.
    """
    manifest = {}
    
    # 1. Generate Manifest
    for root, _, files in os.walk(source_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, source_dir)
            manifest[rel_path] = get_hash(full_path)

    manifest_path = "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f)

    # 2. Archive
    tmp_archive = output_path + ".tar.bz2"
    with tarfile.open(tmp_archive, "w:bz2") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
        tar.add(manifest_path, arcname="manifest.json")

    # 3. Rename
    final_path = output_path + ".agentark"
    if os.path.exists(final_path):
        os.remove(final_path)
    shutil.move(tmp_archive, final_path)
    
    # 4. Cleanup
    os.remove(manifest_path)
    return final_path
