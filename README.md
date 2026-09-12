# Operating Systems Labs: Concurrent Traffic Control System (SIGET)

This repository contains two Python implementations demonstrating the **Producer-Consumer Problem** with a **Bounded Buffer**, simulated through an **Intelligent Traffic Management System (SIGET)**.

---

## 🔬 Overview & Problem Statement

In a smart city infrastructure, multiple roadside sensors (Producers) continuously collect real-time traffic flow data (vehicle count and average speed) across various intersections. Simultaneously, analysis modules (Consumers) consume this data to evaluate road congestion and route traffic efficiently.

To prevent race conditions, memory overflow, or data loss, both implementations enforce strict synchronization mechanisms over a shared bounded buffer.

---

## 🛠 Project Implementations

### Project 1: Explicit Synchronization via Semaphores
* **Focus:** Low-level concurrency control & operating system primitives.
* **Synchronization Primitives:**
  * `mutex` (`threading.Semaphore(1)`): Guarantees mutual exclusion when accessing the shared buffer (`deque`).
  * `empty_slots` (`threading.Semaphore(BUFFER_SIZE)`): Tracks available slots, blocking producers when the buffer reaches capacity (5 items).
  * `full_slots` (`threading.Semaphore(0)`): Tracks available readings, blocking consumers when the buffer is empty.
  * `exit_event` (`threading.Event`): Coordinates a **graceful shutdown**, waking waiting consumers when all sensors complete their readings.

### Project 2: High-Level Abstraction via Thread-Safe Queue
* **Focus:** Idiomatic, high-level Python concurrency using `queue.Queue`.
* **Synchronization Mechanism:**
  * Replaces explicit semaphores with `queue.Queue`, which internally handles locking and condition variables.
  * Utilizes `Sentinel Values` (e.g., `None` tokens) to notify worker threads when no further data will be produced.
  * Simplifies thread coordination and minimizes manual locking logic while preserving identical functional throughput.

---

## 🚀 Key Architectural Features

* **Decoupled Processing:** Data acquisition by sensors occurs independently of analytical processing.
* **Optimized Critical Sections:** Heavy computational tasks (such as simulated network delays or status evaluation) are executed outside critical sections to maximize parallel CPU utilization.
* **Graceful Thread Termination:** Both projects ensure zero memory leaks, preventing thread starvation or infinite blocking upon workload completion.

---

## 📊 Performance & Execution Metrics

| Feature | Project 1 (Semaphores) | Project 2 (`queue.Queue`) |
| :--- | :--- | :--- |
| **Buffer Capacity** | 5 items (`deque`) | 5 items (`queue.Queue`) |
| **Producers (Sensors)** | 3 active threads | 3 active threads |
| **Consumers (Analyzers)** | 2 active threads | 2 active threads |
| **Control Style** | Explicit OS Primitives | Encapsulated / High-Level |
| **Shutdown Strategy** | `Event` + Semaphore Release | Sentinel Token Passing |

---

## 💻 How to Run

1. Clone the repository:
   ```bash
   git clone [https://github.com/EstebanGC/operating-systems.git](https://github.com/EstebanGC/operating-systems.git)
   cd operating-systems