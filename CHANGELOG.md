#Version: 0.2.2

##Features:

-  Added FileCollector class to ECAgent.Collectors. This class allows you to write records to a file and can be inherited to make custom file writers for your models. ([a76ae5](https://github.com/BrandonGower-Winter/ABMECS/commit/a76ae558ca5411dda3d635f16f9e6545388fe060))
-  ECAgent.Environments.getAgentAt now accepts 'leeway' properties which allow users to get a list of agents around a position on the discrete world. ([6e311f](https://github.com/BrandonGower-Winter/ABMECS/commit/6e311f2eee08b2d9a27e139f21eabce9c60953ca))
-  Model.logger added. This allows users to add logging functionality to their model. By default, the logger will print any logging.INFO or higher calls to the terminal. ([afe25f](https://github.com/BrandonGower-Winter/ABMECS/commit/afe25f76c5ca81e339df1809da99625688f1aca0))
-  Decoder base class has been modified such that it now only requires that users overwrite the open_file() method in order to write custom decoders. Decoders also support pre and post model, system and agent custom function calls. ([ce5723](https://github.com/BrandonGower-Winter/ABMECS/commit/ce5723c6ca1284c5f586abed72c73487db259e6f))
-  reverted Core.Environment __contains__ and __getitem__ functionality to that of its parent class Core.Agent ([8974bf](https://github.com/BrandonGower-Winter/ABMECS/commit/8974bfcd0972b8b59f840aa3df3bf311051ecb27))
