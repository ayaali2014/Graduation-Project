import subprocess
import shlex

project_path = r'C:\\Users\\Abdelrhman Ali\\Downloads\\graduation'
nb_id = 'WRITE_YOUR_NOTEBOOK_ID_HERE'


def execute_terminal_command(command):
    # Execute the command
    command_list = shlex.split(command)
    result = subprocess.run(command_list, shell=True, text=True, capture_output=True)
    # Print the output of the command
    return result.stdout

def init_kaggle_dataset():
    #command = fr'kaggle datasets init -p {project_path}\\dataset'
    command = fr'kaggle datasets init -p "C:\Users\Abdelrhman Ali\Downloads\graduation\dataset"'
    print(command)
    return execute_terminal_command(command)


def create_kaggle_dataset():
    command = fr'kaggle datasets create -p "C:\Users\Abdelrhman Ali\Downloads\graduation\dataset" -r tar'
    return execute_terminal_command(command)


def pull_kaggle_dataset(dataset_id):
    command = fr'kaggle datasets metadata -p "C:\Users\Abdelrhman Ali\Downloads\graduation\dataset" {dataset_id}'
    return execute_terminal_command(command)


def update_kaggle_dataset():
    command = fr'kaggle datasets version -p "C:\Users\Abdelrhman Ali\Downloads\graduation\dataset" -m "Updated dataset using kaggle API 2024" -r tar'
    return execute_terminal_command(command)

# def pull_kaggle_notebook():
#     command = fr'kaggle kernels pull "ayaali2002/final-nb" -p "C:\Users\Abdelrhman Ali\Downloads\graduation\notebook" -m'
#     return execute_terminal_command(command)


def push_kaggle_notebook():
    command = fr'kaggle kernels push -p "C:\Users\Abdelrhman Ali\Downloads\graduation\notebook"'
    return execute_terminal_command(command)


def get_notebook_status():
    command = fr'kaggle kernels status "ayaali2002/final-nb"'
    return execute_terminal_command(command)


def get_notebook_output():
    command = fr'kaggle kernels output "ayaali2002/final-nb" -p "C:\Users\Abdelrhman Ali\Downloads\graduation\nb_output"'
    return execute_terminal_command(command)

print(get_notebook_output())


    


#print("hello")