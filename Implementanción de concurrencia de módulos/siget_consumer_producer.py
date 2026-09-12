import threading
import time
import random
from collections import deque
from datetime import datetime

# ------------------------------------------------------------------
# General Simulation Settings
# ------------------------------------------------------------------
BUFFER_SIZE = 5            # Maximum capacity of the shared buffer
NUM_SENSORS = 3            # Number of sensors (producers)
NUM_ANALYZERS = 2          # Number of analysis modules (consumers)
READINGS_PER_SENSOR = 6    # Total readings generated per sensor
INTERSECTIONS = [
    "80th Ave & 33rd St",
    "70th Ave & 44th St",
    "10th St & 43rd Ave",
]

# ------------------------------------------------------------------
# Shared Resources & Concurrency Control
# ------------------------------------------------------------------
shared_buffer = deque()              # Bounded buffer (FIFO queue)
mutex = threading.Semaphore(1)       # Mutual exclusion semaphore
empty_slots = threading.Semaphore(BUFFER_SIZE)  # Empty space counter
full_slots = threading.Semaphore(0)             # Data available counter

# Active sensor counter protected by its own lock.
# Used so consumers know when producers have finished to gracefully terminate.
counter_lock = threading.Lock()
active_sensors = NUM_SENSORS

# Shutdown flag + extra notification to wake up waiting consumers upon finish
exit_event = threading.Event()


def log(message):
    """Prints a timestamped log message with the thread name for clear visual debugging."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {threading.current_thread().name:<12} | {message}")


# ------------------------------------------------------------------
# SENSOR (Producer)
# ------------------------------------------------------------------
def sensor(sensor_name, intersection):
    global active_sensors

    for i in range(1, READINGS_PER_SENSOR + 1):
        # Simulate real-world sensor sampling time delay
        time.sleep(random.uniform(0.2, 0.8))

        data = {
            "sensor": sensor_name,
            "intersection": intersection,
            "vehicles": random.randint(0, 40),
            "avg_speed": round(random.uniform(10, 60), 1),
            "reading_num": i,
        }

        # 1) Wait for an empty slot in the buffer
        empty_slots.acquire()
        # 2) Enter critical section (mutual exclusion)
        mutex.acquire()
        try:
            shared_buffer.append(data)
            log(
                f"PRODUCE -> {intersection} | vehicles={data['vehicles']:>2} "
                f"| speed={data['avg_speed']:>5} km/h | buffer={len(shared_buffer)}/{BUFFER_SIZE}"
            )
        finally:
            # 3) Release critical section
            mutex.release()
        # 4) Signal that a new item is available in the buffer
        full_slots.release()

    log(f"{sensor_name} completed all readings.")

    # Decrement active sensors counter and notify when all sensors finish
    with counter_lock:
        active_sensors -= 1
        if active_sensors == 0:
            exit_event.set()
            # Release 'full_slots' to wake up any consumers blocked waiting for data
            for _ in range(NUM_ANALYZERS):
                full_slots.release()


# ------------------------------------------------------------------
# ANALYSIS MODULE (Consumer)
# ------------------------------------------------------------------
def analysis_module(module_name):
    while True:
        full_slots.acquire()

        mutex.acquire()
        try:
            if not shared_buffer:
                # Buffer is empty and producers are done -> cleanly exit loop
                if exit_event.is_set():
                    break
                else:
                    continue
            data = shared_buffer.popleft()
            current_buffer_size = len(shared_buffer)
        finally:
            mutex.release()

        empty_slots.release()

        # Data processing (executed outside critical section to optimize concurrency)
        time.sleep(random.uniform(0.3, 0.9))
        status = "CONGESTED" if data["vehicles"] > 25 else "Flowing"
        log(
            f"CONSUME <- {data['intersection']} | vehicles={data['vehicles']:>2} "
            f"-> {status:<10} | buffer={current_buffer_size}/{BUFFER_SIZE}"
        )

    log(f"{module_name} finished: no remaining data to process.")


# ------------------------------------------------------------------
# Main Execution Flow
# ------------------------------------------------------------------
def main():
    log("=== Starting SIGET Simulation: Producer-Consumer with Semaphores ===")

    threads = []

    # Initialize producer threads (Sensors)
    for idx in range(NUM_SENSORS):
        name = f"Sensor-{idx + 1}"
        intersection = INTERSECTIONS[idx % len(INTERSECTIONS)]
        t = threading.Thread(target=sensor, args=(name, intersection), name=name)
        threads.append(t)

    # Initialize consumer threads (Analysis Modules)
    for idx in range(NUM_ANALYZERS):
        name = f"Analysis-{idx + 1}"
        t = threading.Thread(target=analysis_module, args=(name,), name=name)
        threads.append(t)

    # Start all threads simultaneously
    for t in threads:
        t.start()

    # Join all threads to main execution
    for t in threads:
        t.join()

    log("=== Simulation Finished. All threads completed successfully. ===")
    log(f"Unprocessed elements remaining in buffer: {len(shared_buffer)}")


if __name__ == "__main__":
    main()