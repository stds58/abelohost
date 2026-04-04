import subprocess
import sys


def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)


if __name__ == "__main__":
    container_cmd = "cd backend && alembic upgrade head"
    full_cmd = f'docker exec -i preview-fastapi-app bash -c "{container_cmd}"'

    try:
        run_cmd(full_cmd)
        print("✅ Миграция успешно применена!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        sys.exit(1)
