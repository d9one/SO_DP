# Jedzący Filozofowie

## Opis problemu

Problem jedzących filozofów to klasyczny problem synchronizacji w programowaniu współbieżnym. Pięciu filozofów siedzi przy okrągłym stole, na którym znajduje się pięć widelców. Każdy filozof na przemian myśli i je. Aby jeść, filozof musi podnieść dwa widelce znajdujące się po jego lewej i prawej stronie. Problem polega na zapobieganiu zakleszczeniom (deadlock) i zagłodzeniu (starvation) filozofów poprzez odpowiednie zarządzanie dostępem do widelców.

## Opis rozwiązania

Implementacja używa semaforów do synchronizacji dostępu do widelców oraz do kontroli liczby filozofów jednocześnie próbujących jeść. Główne mechanizmy to:

- **Tablica semaforów** - Każdy widelec jest reprezentowany przez semafor binarny.
- **Semafor stołu** - Ogranicza liczbę filozofów mogących jeść jednocześnie do `n - 1`, co zapobiega zakleszczeniom.
- **Wątki** - Każdy filozof działa jako osobny wątek, który myśli, następnie próbuje podnieść dwa widelce, je, a potem odkłada widelce i odchodzi od stołu.

## Sposób użycia

### Kompilacja

Aby skompilować program, użyj kompilatora g++:

```sh
 g++ -o dining_philosophers main.cpp -lpthread
```

### Uruchomienie

Aby uruchomić program, podaj liczbę filozofów jako argument:

```sh
 ./dining_philosophers <liczba_filozofow>
```

Przykład dla 5 filozofów:

```sh
./dining_philosophers 5
```

## Mechanizmy unikania zakleszczenia i zagłodzenia

- **Ograniczenie liczby jedzących filozofów** – Filozofowie mogą jeść tylko wtedy, gdy przy stole jest miejsce (n-1 zamiast n).
- **Kolejność podnoszenia widelców** – Zapobiega klasycznemu problemowi, w którym każdy filozof bierze jeden widelec i czeka na drugi.

## Wymagania
- **System operacyjny Linux**
- **Kompliator g++**

