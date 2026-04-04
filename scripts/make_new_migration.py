import subprocess
import sys


def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)


if __name__ == "__main__":
    msg = input("Введите описание миграции либо нажмите ввод.: ")
    if not msg:
        msg = "Auto-generated migration"
    container_cmd = f"cd backend && alembic revision --autogenerate -m '{msg}' && alembic upgrade head"
    full_cmd = f'docker exec -i abelo-app bash -c "{container_cmd}"'

    try:
        run_cmd(full_cmd)
        print("✅ Миграция успешно создана и применена!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        sys.exit(1)
