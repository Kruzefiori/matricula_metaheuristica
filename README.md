# Matricula_metaheuristica

To run with the UI:
run with python src/__init__.py --run_cli_only n


To run with CLI only:
run with python src/__init__.py --dataset_name "historico_2021005488"

--dataset_name "historico_name" the .pdf must be under the datasets folder, otherwise the script won't find it

--update_json y/n Will read the whole pdf again if y and make a new Json file in order to create the Data Structure, if n it will only read the Json and create the structure, it's a lot faster without reading the whole pdf again. def = n

--run_cli_only y/n if n will execute the script using a UI, if y it will execute with the CLI only, def = y
