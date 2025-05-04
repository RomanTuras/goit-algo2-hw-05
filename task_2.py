import time
import json
from hyper_log_log import HyperLogLog


def extract_ips_from_json_log(filepath):
    ips = []
    with open(filepath, "r") as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                ip = data.get("remote_addr", "")
                if ip.count(".") == 3:
                    ips.append(ip)
            except json.JSONDecodeError:
                continue  # пропустити некоректні рядки
    return ips


def exact_count(ips):
    uniq_ips = set()
    uniq_ips.update(ips)
    return len(uniq_ips)


def approximate_count(ips):
    hll = HyperLogLog(p=8)
    print("p=8 - точність алгоритму приємлива, заощаджуємо ОЗУ")
    for ip in ips:
        hll.add(ip)
    return hll.count()


def measure_time(func, *args):
    start = time.time()
    result = func(*args)
    end = time.time()
    return result, end - start


def main():
    log_file = "lms-stage-access.log"
    print("Завантаження IP-адрес із JSON лог-файлу...")
    ips = extract_ips_from_json_log(log_file)

    exact_result, exact_time = measure_time(exact_count, ips)
    approx_result, approx_time = measure_time(approximate_count, ips)

    print("\nРезультати порівняння:")
    print(f"{'':<30}{'Точний підрахунок':<20}{'HyperLogLog':<20}")
    print(f"{'Унікальні елементи':<30}{exact_result:<20}{round(approx_result, 1):<20}")
    print(
        f"{'Час виконання (сек.)':<30}{round(exact_time, 3):<20}{round(approx_time, 3):<20}"
    )


if __name__ == "__main__":
    main()
