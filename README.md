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
#(if number_of_islands == 2 then island = 0 or 1 or 2)
python run_algorithm.py <island> 
   ```

## Todo
1. Add information, from which island and which epoque comes migrant.
2. Add more configuration json files to match different topologies (star, ring, mesh).
3. Test for e.g. 10 islands
4. Add script for running multiple islands automatically.
5. Do some viusualisation on function Rastrigin 2-dim to show solutions and indicate migrants with different color.


------ 
Old ones:
1. Add creating queues using docker-compose. I tried to do that in 
`utils/prepare_queues.py` and `utils/Dockerfile_prepare_queues` but after
   adding service in docker-compose container exits. We should wait for rabbitmq being available.
   
2. Run islands from docker-compose as well as creating queues.
