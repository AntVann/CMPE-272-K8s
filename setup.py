import os
import subprocess
import sys
import shlex


def run_command(command):
    if sys.platform == "win32":
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    else:
        process = subprocess.Popen(
            shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(stderr.decode())
        sys.exit(1)
    return stdout.decode()


def setup_venv(path):
    venv_path = os.path.join(path, "venv")
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment in {path}")
        run_command(f'python -m venv "{venv_path}"')

    if sys.platform == "win32":
        activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
        pip_command = f'"{activate_script}" && pip'
    else:
        activate_script = os.path.join(venv_path, "bin", "activate")
        pip_command = f'source "{activate_script}" && pip'

    requirements_file = os.path.join(path, "requirements.txt")
    if os.path.exists(requirements_file):
        print(f"Installing dependencies for {path}")
        run_command(f'{pip_command} install -r "{requirements_file}"')
    else:
        print(f"No requirements.txt found in {path}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Setup main application
    setup_venv(base_dir)

    # Setup microservices
    services_dir = os.path.join(base_dir, "services")
    for service in os.listdir(services_dir):
        service_path = os.path.join(services_dir, service)
        if os.path.isdir(service_path):
            setup_venv(service_path)

    print("Setup complete. Virtual environments created and dependencies installed.")


if __name__ == "__main__":
    main()
