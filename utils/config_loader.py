import yaml
import warnings
warnings.filterwarnings("ignore")

def load_config(file_path:str = r"config/config.yaml")->dict:
    """
    Load the Config File in YAML Mode and return as Dictinory
    """
    with open(file_path , "r") as file:
        config = yaml.safe_load(file)
    return config


