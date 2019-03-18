# HTTP сервер OTUSSERVER 
Данный сервер является простой реализацией HTTP сервера, поддерживающей два метода:
GET и HEAD.
В основе архитектуры сервера лежит пул потоков:
 - При запуске сервера создаётся пул с *N* потоками
 - Далее в главном цикле сервер принимает соединения
 - При успешном создании соединения оно незамедлительно отправляется в очередь,
 и управление возвращается в главный цикл
 - Из очереди же первый освободившийся поток забирает сообщение на обработку.

## Результаты нагрузочного теста
Нагрузочное тестирование сервера выполнялось утилитой **Apache Benchmark (ab)**
со следующими параметрами:<br/>
*Количество запросов: 50000*<br/>
*Количество конкурентных запросов: 100*<br/>
Сервер был запущен со следующими параметрами:<br/>
*Количество workers 20*<br/>

```
Server Software:        Python
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /
Document Length:        0 bytes

Concurrency Level:      100
Time taken for tests:   40.438 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      5050150 bytes
HTML transferred:       0 bytes
Requests per second:    1236.46 [#/sec] (mean)
Time per request:       80.876 [ms] (mean)
Time per request:       0.809 [ms] (mean, across all concurrent requests)
Transfer rate:          121.96 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    7 118.3      0    7232
Processing:     2   18 488.7      4   30640
Waiting:        2   18 488.9      4   30645
Total:          4   25 515.6      5   30640

Percentage of the requests served within a certain time (ms)
  50%      5
  66%      5
  75%      5
  80%      5
  90%      5
  95%      5
  98%      5
  99%      7
 100%  30640 (longest request)
```
Как видно из результатов теста среднее количество запросов в секунду состовляет 1236 штук.
Большая часть запросов (99%) выполнилась за 7 мс, и это при отсутствии каких-либо
ошибок обработки.
## Установка и запуск
Данный сервер запускается на локальном порту 8080, но для работы тестов необходимо, чтобы сервер
принимал содеинения на порту 80.
Для этого необходимо.
 - Остановить все локальные сервисы на 80 порту
 - Пробросить порт 80 командой:
```bash
sudo iptables -t nat -I OUTPUT -p tcp -d localhost --dport 80 -j REDIRECT --to-ports 8080
```

Сервер поддерживает следущие параметры запуска:
`-p` или `--port` для указания HTTP порта для работы
`-w` или `--workers` для указания количества потоков, обслуживающих соединение 
`-r` или `--rootdir` для указания для указания корневого каталога для работы веб сервера. 

### Примеры запуска сервера 
Запуск сервера с работой в 10 потоков на порту 8080.
```bash
python otus_server/httpd.py -w 10
```

## Запуск тестов
Для запуска тестов вначале необходимо обновить подмодули 
```bash
git submodule init
```
Далее запустить сам сервер в отдельном терминале
```bash
python otus_server/httpd.py
```
После этого запустить непосредственно сами тесты
```bash
python tests/http-test-suite/httptest.py
```
