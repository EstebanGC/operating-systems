# Laboratorios de Sistemas Operativos: Sistema de Control de Tráfico Concurrente (SIGET)

* **Institución:** Institución Universitaria Pascual Bravo
* **Curso:** Sistemas Operativos

Este repositorio contiene dos implementaciones en Python que demuestran la solución al problema clásico del Productor-Consumidor con un Búfer Acotado, simulado a través de un Sistema Inteligente de Gestión de Tráfico (SIGET).

---

## Resumen y Descripción del Problema

En la infraestructura de una ciudad inteligente, múltiples sensores ubicados en las vías (Productores) recolectan continuamente métricas del flujo vehicular en tiempo real (conteo de vehículos y velocidad promedio) en varias intersecciones. Simultáneamente, los módulos de análisis (Consumidores) procesan dicha información para evaluar la congestión vial y sugerir rutas de tráfico eficientes.

Para prevenir condiciones de carrera (race conditions), desbordamiento de memoria o pérdida de datos, ambas implementaciones aplican mecanismos strictly controlados de sincronización sobre un búfer compartido con capacidad limitada.

---

## Implementaciones del Proyecto

### Proyecto 1: Sincronización Explícita mediante Semáforos
* Enfoque: Control de concurrencia a bajo nivel utilizando primitivas del sistema operativo.
* Primitivas de sincronización utilizadas:
  * mutex (threading.Semaphore(1)): Garantiza la exclusión mutua al acceder al búfer compartido (deque).
  * empty_slots (threading.Semaphore(BUFFER_SIZE)): Rastrea las casillas disponibles, bloqueando a los sensores cuando la cola alcanza su capacidad máxima de 5 elementos.
  * full_slots (threading.Semaphore(0)): Rastrea las lecturas disponibles, bloqueando a los analistas cuando la cola está vacía.
  * exit_event (threading.Event): Coordina el cierre limpio (graceful shutdown), despertando a los consumidores en espera una vez que todos los sensores finalizan sus lecturas.

### Proyecto 2: Abstracción a Alto Nivel mediante queue.Queue
* Enfoque: Concurrencia idiomática a alto nivel en Python utilizando la clase queue.Queue.
* Mecanismo de sincronización:
  * Reemplaza los semáforos manuales por queue.Queue, la cual gestiona internamente los bloqueos de exclusión mutua y variables de condición.
  * Utiliza valores centinela (tokens de cierre) para notificar a los hilos de trabajo cuando no hay más datos por producir.
  * Simplifica la lógica de coordinación de hilos mientras mantiene exactamente el mismo rendimiento funcional.

---

## Demostraciones en Video (YouTube)

* Simulación de planificación de proyectos: https://youtu.be/DGT9toltn_s
* Implementación de concurrencia de módulos: https://youtu.be/SCoEuFR63T4

---

## Características Arquitectónicas Clave

* Desacoplamiento Operativo: La recolección de datos por parte de los sensores ocurre de forma independiente al análisis computacional.
* Optimización de Secciones Críticas: Las tareas computacionales pesadas (como retardos simulados de red o evaluación del estado del tráfico) se ejecutan fuera de la sección crítica para maximizar el uso paralelo de la CPU.
* Finalización Limpia de Hilos: Ambos proyectos garantizan la ausencia de bloqueos indefinidos o inanición de hilos (thread starvation) al completar la carga de trabajo.

---

## Métricas de Ejecución y Comparación

* Capacidad del búfer: 5 elementos (deque / queue.Queue)
* Productores (Sensores): 3 hilos activos
* Consumidores (Analizadores): 2 hilos activos
* Estilo de control: Primitivas explícitas de SO vs. Encapsulado de alto nivel
* Estrategia de finalización: Event + Liberación de semáforos vs. Tokens centinela

---

## Instrucciones de Ejecución

1. Clonar el repositorio:
   git clone https://github.com/EstebanGC/operating-systems.git
   cd operating-systems

2. Ejecutar la implementación con Semáforos:
   python project1_semaphores.py

3. Ejecutar la implementación con Queue:
   python project2_queue.py

---

## Licencia e Información Académica
Este proyecto es de código abierto y está destinado a fines académicos y educativos para el curso de Sistemas Operativos de la Institución Universitaria Pascual Bravo.