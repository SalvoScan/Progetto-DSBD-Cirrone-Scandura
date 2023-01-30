Build & Deploy --> Istruzioni

Per ogni microservizio è stata costruita appositamente la relativa immagine mediante Dockerfile.
Tutte le immagini sviluppate, utilizzate all’interno del file docker-compose.yml,
sono reperibili nel repository Docker hub “lucacirrone”, al seguente link: https://hub.docker.com/u/lucacirrone.
Altre immagini sono state utilizzate direttamente dal Docker hub.

Per quanto riguarda il deploy è stato scelto di utilizzare docker compose.
All’interno del file docker-compose.yml vengono definiti tutti i servizi e le relative configurazioni.
Inoltre è stata definita una rete custom di nome “ragnatela” per connettere i vari container.
Il comando per l’esecuzione è il seguente: docker compose up -d --build

Si noti che il pull delle varie immagini da Docker hub potrebbe fallire
in funzione del numero massimo di pull legate al corrente account nell’arco di 6 ore.
