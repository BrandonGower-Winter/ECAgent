#Version: 0.5.0

##Features:

- Renamed several Environment functions to more 'pythonic' appropriate names. This set of features constitudes a major effort in reworking the core functionality provided by ECAgent. As such, the new update 'v0.5' will not be backwards compatible with other versions of ECAgent. All models made with previous versions of ECAgent should target 'v0.4' or lower. ([48636a](https://github.com/BrandonGower-Winter/ECAgent/commit/48636aad5814acc8d06304914f492573e2d101ca))
- Added SpaceWorld and DiscreteWorld which now act as the backbone for all spacial environments. ([f2dee9](https://github.com/BrandonGower-Winter/ECAgent/commit/f2dee98551818941d271b0711b2ee9fbc02df59f))
- Deprecated the addAgent and removeAgent Environment functions. Replaced them with the add_agent and remove_agent respectively ([d2fb79](https://github.com/BrandonGower-Winter/ECAgent/commit/d2fb7950a4d3442ff13013f502cbaaa826f27608))
- Added 'tag' attribute to the base Agent class. Added 'tag' kwarg to Environment.get_agents and Environment.get_random_agent. Updated documents to reflect how they should be used. ([815ff1](https://github.com/BrandonGower-Winter/ECAgent/commit/815ff1385754d20fbf13e11fe3a39879e60d999e))
- Added ECAgent.Tags module. It contains functionality that allows developers to assign a 'tag' to agents, it offers additional methods by which Agent objects can be grouped. ([6023fc](https://github.com/BrandonGower-Winter/ECAgent/commit/6023fc659c62dfd53e841c11f5914e628faad3a5))
- Added SystemNotFoundError which is raised whenever a System that doesn't exist is added. Modified SystemManager.removeSystem() to account for this change. ([e858f7](https://github.com/BrandonGower-Winter/ECAgent/commit/e858f73e7912486fbb6ea6a27c27ad580dc0459a))
- Added AgentNotFoundError which is raised when an agent cannot be found in an environment. Updated Environment.getAgent() and Environment.removeAgent() to reflect these changes. ([97c869](https://github.com/BrandonGower-Winter/ECAgent/commit/97c869ede8ae70d39acc9f120257e2e18e1fd7a4))
