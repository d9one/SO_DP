#include <complex>
#include <iostream>
#include <unistd.h>
#include "pthread.h"
#include "semaphore.h"

sem_t* forks; // semaphores for each fork
sem_t table; // semaphore for the table
int n; // number of philosophers

struct PhilosopherData {
    int id;
};

void initialize_forks(int n) { // initialize the semaphores
    forks = new sem_t[n];
    for (int i = 0; i < n; i++) {
        sem_init(&forks[i], 0, 1);
    }
    sem_init(&table, 0, n - 1);
}
void free_forks(int n) { // free the semaphores
    for (int i = 0; i < n; i++) {
        sem_destroy(&forks[i]);
    }
    delete[] forks;
    sem_destroy(&table);
}
void* create_philosopher(void* arg) { // create a philosopher
    auto* data = (PhilosopherData*)arg;
    int id = data->id;

    while (true) {
        std::cout << "Philosopher " << id << " is thinking" << std::endl;
        sleep(10);

        // get the forks and table
        sem_wait(&table);
        sem_wait(&forks[id]);
        sem_wait(&forks[(id + 1) % n]);
        std::cout << "Philosopher " << id << " is eating" << std::endl;
        sleep(5);

        // free the forks and table
        sem_post(&forks[id]);
        sem_post(&forks[(id + 1) % n]);
        sem_post(&table);

    }
}
int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <number of philosophers>\n";
        return 1;
    }
    n = std::stoi(argv[1]);
    initialize_forks(n);
    auto* threads = new pthread_t[n];
    for (int i = 0; i < n; i++) {
        auto* data = new PhilosopherData{i};
        pthread_create(&threads[i], NULL, create_philosopher, data);
    }

    for (int i = 0; i < n; i++) {
        pthread_join(threads[i], NULL);
    }

    free_forks(n);
    delete[] threads;
    return 0;
}