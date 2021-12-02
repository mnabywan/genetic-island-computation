# Genetic island computation

Project for IO 2021

## How to run
1. Run rabbitmq
```bash
docker-compose up
```
Rabbitmq is available on `localhost:15762`.

2. Create queues using command
```bash
cd utils
python prepare_queues_2.py 
   ```
It creates queues based on configurations file
`algorithm/configurations/algorithm_configuration.json`.
   You can also change that file (I will update instructions soon):

3. Run islands. In e.g. 3 (`number_of_islands` parameter in configuration json file) terminals run commands:
```bash
cd algorithm
python run_algorithm.py
   ```

## Todo
1. Add creating queues using docker-compose. I tried to do that in 
`utils/prepare_queues.py` and `utils/Dockerfile_prepare_queues` but after
   adding service in docker-compose container exits. We should wait for rabbitmq being available.
   
2. Run islands from docker-compose as well as creating queues.