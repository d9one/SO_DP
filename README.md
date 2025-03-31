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

# TCP Chat

## Opis problemu

TCP Chat to projekt implementujący serwer i klienta do komunikacji w czasie rzeczywistym przy użyciu protokołu TCP. W systemie klienci mogą dołączać do pokoi czatowych, wysyłać i odbierać wiadomości oraz przeglądać historię czatu. Problem synchronizacji dotyczy obsługi wielu klientów jednocześnie i zapewnienia bezpiecznej komunikacji między nimi.

## Opis rozwiązania

Projekt wykorzystuje wielowątkowość do zarządzania połączeniami klientów oraz kolejkę do obsługi wiadomości. Główne mechanizmy to:

- **Serwer TCP** – Obsługuje połączenia klientów i zarządza czatami.

- **Wielowątkowość** – Każdy klient ma dedykowany wątek do odbierania i wysyłania wiadomości.

- **Kolejka FIFO** – Buforuje wiadomości przed ich rozesłaniem do klientów.

- **Zapis historii czatu** – Każdy pokój czatowy ma swoją historię, zapisywaną w plikach tekstowych.

- **Synchronizacja** – Blokady (mutexy) zapobiegają równoczesnemu dostępowi do współdzielonych zasobów.


## Sposób użycia

### Uruchomienie

Aby uruchomić serwer:

```sh
python3 server.py
```
*Po uruchomieniu programu w interfejscie użytkownika wybrać ip oraz port następnie kliknąć "Start server".*

Aby uruchomić clienta:

```sh
python3 client.py
```

*Po uruchomieniu programu w interfejscie użytkownika wybrać ip oraz port następnie kliknąć "Connect", nastepnie wypisać nick oraz pokój do którego chcemy dołaczyć oraz kliknąć przycisk "Join.*

### Korzystanie 

*Aby wysłać wiadomośc należy wpisać ją w odpowiednimu miejscu oraz klkinąć przycisk "Send" albo kliknąć Enter.*

*Aby opuścić pokój rozmów należy nacisnąć przycisk "Quit".*

## Mechanizmy unikania problemów synchronizacji

- **Mutex na broadcast()** – Zapewnia, że wiadomości są wysyłane do klientów w sposób uporządkowany, zapobiegając sytuacji, w której wiele wątków jednocześnie próbuje wysłać wiadomości, co mogłoby prowadzić do niekontrolowanego przeplatania danych.

- **Mutex na save_message()** – Zapobiega równoczesnemu zapisywaniu do plików przez wiele wątków, co mogłoby prowadzić do uszkodzenia plików lub utraty wiadomości.

- **Wątki dla klientów** – Każdy klient ma osobny wątek, co zapobiega blokowaniu serwera.

- **Kolejka wiadomości** – FIFO queue zapobiega utracie wiadomości i pozwala na ich przetwarzanie w kolejności przybycia.

- **Obsługa rozłączania klientów** – Gdy klient opuszcza czat, jego gniazdo jest zamykane, a informacja o nim jest usuwana.

- **Mechanizm synchronizacji zakończenia wątków** – shutdown_event = threading.Event() sygnalizuje wątkom, że powinny zakończyć działanie. Dzięki temu można bezpiecznie zamknąć serwer/klienta i wszystkie wątki, zapobiegając błędom wynikającym z nagłego przerwania pracy serwera/klienta.

## Wymagania
-**Python 3**

-**Tkinter** – do obsługi GUI

-**System operacyjny:** Linux/Windows/MacOs
