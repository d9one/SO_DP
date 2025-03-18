#include <complex>
#include <iostream>
#include <mutex>
#include <unistd.h>
#include "pthread.h"
#include "semaphore.h"

#define RED "\033[31m"
#define GREEN "\033[32m"
#define RESET "\033[0m"

sem_t* forks; // semaphores for each fork
sem_t table; // semaphore for the table
int n; // number of philosophers
bool* isEating; // array to keep track of which philosophers are eating
pthread_mutex_t printMutex; // mutex to synchronize printing

struct PhilosopherData {
    int id;
};

void initialize_isEating(int n) { // initialize the isEating array
    isEating = new bool[n];
    for (int i = 0; i < n; i++) {
        isEating[i] = false;
    }
}

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

void printPhilosophers(int n) { // print the state of each philosopher
    pthread_mutex_lock(&printMutex);
    system("clear");

    std::cout << "+----+-------------------------+\n";
    for (int i = 0; i < n; i++) {
        std::cout << "| " << i + 1 << "  | ";
        if (isEating[i])
            std::cout << RED << "Philosopher is EATING  " << RESET;
        else
            std::cout << GREEN << "Philosopher is THINKING" << RESET;
        std::cout << " |\n";
    }
    std::cout << "+----+-------------------------+\n";
    pthread_mutex_unlock(&printMutex);
}


void* create_philosopher(void* arg) { // create a philosopher
    auto* data = (PhilosopherData*)arg;
    int id = data->id;

    while (true) {
        printPhilosophers(n);
        sleep(10);

        // get the forks and table
        sem_wait(&table);
        sem_wait(&forks[id]);
        sem_wait(&forks[(id + 1) % n]);

        isEating[id] = true;
        printPhilosophers(n);
        sleep(5);

        // free the forks and table
        sem_post(&forks[id]);
        sem_post(&forks[(id + 1) % n]);
        sem_post(&table);

        isEating[id] = false;
    }
}
int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <number of philosophers>\n";
        return 1;
    }
    n = std::stoi(argv[1]);
    if (n < 2) {
        std::cerr << "There must be at least 2 philosophers.\n";
        return 1;
    }
    initialize_forks(n);
    initialize_isEating(n);
    pthread_mutex_init(&printMutex, NULL);
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
    delete[] isEating;
    pthread_mutex_destroy(&printMutex);
    return 0;
}