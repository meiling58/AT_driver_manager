import time
from src.driver_manager.retry import retry

counter = {"calls": 0}


@retry(times=3, delay=0.5)
def flaky_function():
    counter["calls"] += 1
    print("Attempt:", counter["calls"])
    if counter["calls"] < 3:
        raise ValueError("Failing on purpose")
    return "Success!"


def test_retry():
    result = flaky_function()
    print("Result:", result)


if __name__ == "__main__":
    print(f"==== Test Goal ==== \nconfirm that retry logic catches failures and retries. ====")
    print(f"===== Expected behavior ====")
    print(f"Attempt: 1")
    print(f"Attempt: 2")
    print(f"Attempt: 3")
    print(f"Success")
    print(f"\nTest starting.....\n")

    start_time = time.time()
    test_retry()
    end_time = time.time()
    total_seconds = round(end_time - start_time, 2)
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60

    print("\n⏱ Test completed!")
    print(f"Total runtime: {minutes} minutes {seconds:.2f} seconds")