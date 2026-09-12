import threading
import time
import random
from collections import deque
from datetime import datetime

# Configuration Constants (fixed values during execution)
BUFFER_SIZE = 5
NUM_SENSORS = 3
NUM_ANALYZERS = 2
READINGS_PER_SENSOR = 6
INTERSECTIONS = [
    "80th Ave & 33rd St",
    "70th Ave & 44th St",
    "10th St & 43rd Ave",
]

# Shared Resources & Concurrency Primitives (mutable state -> snake_case)
shared_buffer = deque()
mutex = threading.Semaphore(1)
empty_slots = threading.Semaphore(BUFFER_SIZE)
full_slots = threading.Semaphore(0)

# Active state tracking
counter_lock = threading.Lock()
active_sensors = NUM_SENSORS
exit_event = threading.Event()


def log(message):
    """Prints a timestamped log message with thread name for visual debugging."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {threading.current_thread().name:<12} | {message}")


def sensor(sensor_name, intersection):
    """Producer function that simulates collecting and emitting traffic data."""
    global active_sensors

    for i in range(1, READINGS_PER_SENSOR + 1):
        time.sleep(random.uniform(0.2, 0.8))

        data = {
            "sensor": sensor_name,
            "intersection": intersection,
            "vehicles": random.randint(0, 40),
            "avg_speed": round(random.uniform(10, 60), 1),
            "reading_num": i,
        }

        # 1. Wait for an available empty slot
        empty_slots.acquire()
        
        # 2. Critical section start
        mutex.acquire()
        try:
            shared_buffer.append(data)
            log(
                f"PRODUCE -> {intersection} | vehicles={data['vehicles']:>2} "
                f"| speed={data['avg_speed']:>5} km/h | buffer={len(shared_buffer)}/{BUFFER_SIZE}"
            )
        finally:
            mutex.release()
            
        # 3. Signal new data item available
        full_slots.release()

    log(f"{sensor_name} completed all readings.")

    # Graceful shutdown signaling
    with counter_lock:
        active_sensors -= 1
        if active_sensors == 0:
            exit_event.set()
            for _ in range(NUM_ANALYZERS):
                full_slots.release()


def analysis_module(module_name):
    """Consumer function that retrieves and processes traffic data."""
    while True:
        full_slots.acquire()

        mutex.acquire()
        try:
            if not shared_buffer:
                if exit_event.is_set():
                    break
                else:
                    continue
            data = shared_buffer.popleft()
            current_buffer_size = len(shared_buffer)
        finally:
            mutex.release()

        empty_slots.release()

        # Data processing outside critical section
        time.sleep(random.uniform(0.3, 0.9))
        status = "CONGESTED" if data["vehicles"] > 25 else "Flowing"
        log(
            f"CONSUME <- {data['intersection']} | vehicles={data['vehicles']:>2} "
            f"-> {status:<10} | buffer={current_buffer_size}/{BUFFER_SIZE}"
        )

    log(f"{module_name} finished: no remaining data to process.")


def main():
    log("=== Starting SIGET Simulation: Producer-Consumer with Semaphores ===")

    threads = []

    # Create sensor threads
    for idx in range(NUM_SENSORS):
        name = f"Sensor-{idx + 1}"
        intersection = INTERSECTIONS[idx % len(INTERSECTIONS)]
        t = threading.Thread(target=sensor, args=(name, intersection), name=name)
        threads.append(t)

    # Create analysis module threads
    for idx in range(NUM_ANALYZERS):
        name = f"Analysis-{idx + 1}"
        t = threading.Thread(target=analysis_module, args=(name,), name=name)
        threads.append(t)

    # Launch execution
    for t in threads:
        t.start()

    # Wait for completion
    for t in threads:
        t.join()

    log("=== Simulation Finished. All threads completed successfully. ===")
    log(f"Unprocessed elements remaining in buffer: {len(shared_buffer)}")


if __name__ == "__main__":
    main()