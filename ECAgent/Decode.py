import json
import sys

from ECAgent.Core import Model


class IDecodable:
    """This class serves as the base class for Decode submodel. By inheriting from this class your Components, Systems
     and Agents can be decoded from a text file and built into an executable model

     In order to implement this class, the decode() static function must be overwritten."""

    @staticmethod
    def decode(params: dict):
        raise NotImplementedError("Call to IDecodable.decode() not allowed.")


class Decoder:
    @staticmethod
    def str_to_class(class_name: str, module_name: str):
        return getattr(sys.modules[module_name], class_name, None)

    def __init__(self):
        self.iterations = -1
        self.epochs = -1
        self.custom_params = {}

    def decode(self, file_path: str) -> Model:
        raise NotImplementedError('Call to Decode.decode() not allowed.')


class JsonDecoder(Decoder):

    def __init__(self):
        super().__init__()

    def decode(self, file_path: str) -> Model:
        """This method takes a path to a json file and decodes it into an executable Model."""

        with open(file_path) as json_file:
            data = json.load(json_file)

            # Set Decoder settings
            self.iterations = data['iterations']
            self.epochs = data['epochs']
            self.custom_params = data['custom_params']

            # Create Base Model
            module_name = data['model']['module'] if 'module' in data['model'] else '__main__'

            modelClass = JsonDecoder.str_to_class(data['model']['name'], module_name)
            generatedModel = modelClass.decode(data['model']['params'])

            # Add Systems
            for systemDict in data['systems']:
                module_name = systemDict['module'] if 'module' in systemDict else '__main__'
                systemClass = JsonDecoder.str_to_class(systemDict['name'], module_name)
                # Add reference to the model in the systemDict so that it can be used when creating the system
                systemDict['params']['model'] = generatedModel

                system = systemClass.decode(systemDict['params'])
                generatedModel.systemManager.addSystem(system)

            # Add Agents
            for agentDict in data['agents']:
                module_name = agentDict['module'] if 'module' in agentDict else '__main__'
                agentClass = JsonDecoder.str_to_class(agentDict['name'], module_name)

                # Add reference to the model in systemDict so that it can be used when creating the agents
                agentDict['model'] = generatedModel

                # Create agents
                for i in range(0, agentDict['number']):
                    # Add the index of the agent to the agentDict
                    agentDict['agent_index'] = i
                    generatedModel.environment.addAgent(agentClass.decode(agentDict))

            return generatedModel
