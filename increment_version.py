import re

def increment_version(version):
    major, minor, patch = map(int, version.split('.'))
    patch += 1
    return f"{major}.{minor}.{patch}"

with open('setup.py', 'r') as file:
    setup_contents = file.read()

# Find the version line
version_pattern = re.compile(r"version='(\d+\.\d+\.\d+)'")
version_match = version_pattern.search(setup_contents)

if not version_match:
    raise ValueError("Version not found in setup.py")

current_version = version_match.group(1)
new_version = increment_version(current_version)

# Replace the old version with the new version
new_setup_contents = version_pattern.sub(f"version='{new_version}'", setup_contents)

# Write the updated setup.py file
with open('setup.py', 'w') as file:
    file.write(new_setup_contents)

print(f"Updated version from {current_version} to {new_version}")
