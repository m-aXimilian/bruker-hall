import yaml
import logging

def loadYAMLConfig(_f):
    """Saveload yaml-config file
    Args: 
        _f (str): complete path to the configuration file (can be relative).
    """
    with open(_f,'r') as f:
        try:
            logging.debug('Config file {} loaded'.format(_f))
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            logging.debug('Cannot open config file {}'.format(e))

    
