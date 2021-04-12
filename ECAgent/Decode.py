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
    """Base decoder class:
    ECAgent decoders follow a specific decoding process. The process, as executed by the decoder, is as follows:

    * pre_model_decode(func, params)
    * model_init(params)
    * for each system in 'systems':
    *   pre_system_init(func, system, params)
    *   system_init(system, params)
    *   post_system_init(func, system, params)
    * for each agent in 'agents'
    *   pre_agent_init(func, agent, params)
    *   agent_init(agent, params)
    *   post_agent_init(func, agent, params)
    * post_model_decode(func, params)

    All pre and post methods invoke the method specified to func and supply the method with 'params' as an argument.

    If you want to create your own decoder, override the open_file function such that it creates a dictionary with
    the following content:

    {
        "model" : {
            "name" : Model_Name,
            "module(Optional)" : Module_Name,
            "params" : {
                params_1 : value_1,
                ...,
                params_n : value_n
            }
        },
        "systems": [
            system_1,
            ...,
            system_n,
        ],
        "agents" : [
            agent_type_1,
            ...,
            agent_type_n
        ],
        pre_model_decode(Optional): {
            "func" : FunctionName,
            "module(Optional)" : ModuleName,
            "params" : {
                params_1 : value_1,
                ...,
                params_n : value_n
            }
        },
        post_model_decode(Optional): {
            "func" : FunctionName,
            "module(Optional)" : ModuleName,
            "params" : {
                params_1 : value_1,
                ...,
                params_n : value_n
            }
        }
    }

    where both 'system' and 'agent_type' follow the same structure as 'model'
    """

    @staticmethod
    def str_to_class(class_name: str, module_name: str):
        return getattr(sys.modules[module_name], class_name, None)

    @staticmethod
    def str_to_func(func_name: str, module_name: str):
        return getattr(sys.modules[module_name], func_name, None)

    @staticmethod
    def get_module_name(d: dict, false_return: str = '__main__') -> str:
        return d['module'] if 'module' in d else false_return

    def open_file(self, file_name: str) -> dict:
        """You must overwrite this function if you make your own decoder"""
        raise NotImplementedError('You cannot invoke the open_file() method of the base decoder class')

    def decode(self, file_path: str) -> Model:

        # Get decode dictionary
        data = self.open_file(file_path)

        if data is None:
            raise Exception('Unable to open file %s for decoding' % file_path)

        # Invoke pre_model_decode
        if 'pre_model_decode' in data:
            func = Decoder.str_to_func(data['pre_model_decode']['func'],
                                       Decoder.get_module_name(data['pre_model_decode']))
            func(data['pre_model_decode']['params'])

        # Create Base Model
        generatedModel = Decoder.str_to_class(data['model']['name'], Decoder.get_module_name(data['model'])).decode(
            data['model']['params']
        )

        for systemDict in data['systems']:
            # Invoke pre_system_init
            if 'pre_system_init' in systemDict:
                func = Decoder.str_to_func(systemDict['pre_system_init']['func'],
                                           Decoder.get_module_name(systemDict['pre_system_init']))
                systemDict['pre_system_init']['params']['model'] = generatedModel
                func(systemDict['pre_system_init']['params'])

            # Add generated model to the systemDict
            systemDict['params']['model'] = generatedModel
            # Create system
            generatedModel.systemManager.addSystem(
                Decoder.str_to_class(systemDict['name'], Decoder.get_module_name(systemDict)).decode(
                    systemDict['params']
                )
            )

            # Invoke post_system_init
            if 'post_system_init' in systemDict:
                func = Decoder.str_to_func(systemDict['post_system_init']['func'],
                                           Decoder.get_module_name(systemDict['post_system_init']))
                systemDict['post_system_init']['params']['model'] = generatedModel
                func(systemDict['post_system_init']['params'])

        for agentDict in data['agents']:
            # Invoke pre_agent_init
            if 'pre_agent_init' in agentDict:
                func = Decoder.str_to_func(agentDict['pre_agent_init']['func'],
                                           Decoder.get_module_name(agentDict['pre_agent_init']))
                agentDict['pre_agent_init']['params']['model'] = generatedModel
                func(agentDict['pre_agent_init']['params'])

            # Add reference to the model in systemDict so that it can be used when creating the agents
            agentDict['params']['model'] = generatedModel

            # Create agents
            for i in range(0, agentDict['number']):
                # Add the index of the agent to the agentDict
                agentDict['params']['agent_index'] = i
                generatedModel.environment.addAgent(
                    Decoder.str_to_class(agentDict['name'], Decoder.get_module_name(agentDict)).decode(
                        agentDict['params']
                    )
                )

            if 'post_agent_init' in agentDict:
                func = Decoder.str_to_func(agentDict['post_agent_init']['func'],
                                           Decoder.get_module_name(agentDict['post_agent_init']))
                agentDict['post_agent_init']['params']['model'] = generatedModel
                func(agentDict['post_agent_init']['params'])

        # Invoke post_model_decode
        if 'post_model_decode' in data:
            func = Decoder.str_to_func(data['post_model_decode']['func'],
                                       Decoder.get_module_name(data['post_model_decode']))
            func(data['post_model_decode']['params'])

        return generatedModel


class JsonDecoder(Decoder):

    def open_file(self, file_name: str) -> dict:
        with open(file_name) as json_file:
            return json.load(json_file)
