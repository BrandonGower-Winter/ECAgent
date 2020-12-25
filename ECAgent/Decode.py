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
    def str_to_class(class_name, module_name):
        return getattr(sys.modules[module_name], class_name)

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
            modelClass = JsonDecoder.str_to_class(data['model']['name'], data['model']['module'])
            generatedModel = modelClass.decode(data['model']['params'])

            # Add Systems

            # Add Agents

            return generatedModel
