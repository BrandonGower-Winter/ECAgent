#Version: 0.5.5

##Features:

-  Renamed PositionComponent.getPosition() to Position.get_component() ([1c0e68](https://github.com/BrandonGower-Winter/ECAgent/commit/1c0e68bc7bce60f3395e9211366699a2492d330d))
-  Implemented SystemManager 'getitem' which allows users to access systems or component pools more cleanly. ([f64c89](https://github.com/BrandonGower-Winter/ECAgent/commit/f64c89b633521b3d5a0d47e9f7ab88c9d122609a))
- Added TagLibrary.itemize() which will return a list of tags in the library and their values. ([48bb86](https://github.com/BrandonGower-Winter/ECAgent/commit/48bb86f6be4cd30e749ad1cf2707a0fd1ebb9754))
- Added Class Components to ECAgent. These work exactly like regular components except that are bound to an Agent ent's class as opposed to an Agent object. ([d0a1e0](https://github.com/BrandonGower-Winter/ECAgent/commit/d0a1e0cfe3a28ebcc80497e9eacb600c42c0eb0b))
##Fixes:

-  Fixed a few errors in the Agent and _MetaAgent docs. ([f2cb44](https://github.com/BrandonGower-Winter/ECAgent/commit/f2cb4445147ddb5c7c5141961c255f0fd61985ba))
- Fixed error where an error would be thrown if the width, height and depth of a SpaceWorld was 0 and the move_to method was called for a valid location. ([910d0b](https://github.com/BrandonGower-Winter/ECAgent/commit/910d0be48cbed8253d72023eafdedcf278497313))

#Version: 0.5.4


#Version: 0.5.3

##Fixes:

- Fixed error where an error would be thrown if the width, height and depth of a SpaceWorld was 0 and the move_to method was called for a valid location. ([910d0b](https://github.com/BrandonGower-Winter/ECAgent/commit/910d0be48cbed8253d72023eafdedcf278497313))
- Fixed bug where having a SpaceWorld with width, height or depth equal to 0 would prevent you from adding agents tos to the evironment. ([4d1141](https://github.com/BrandonGower-Winter/ECAgent/commit/4d1141e074efd8df40d5fe60f9cbbf40f23f5ce5))

#Version: 0.5.1

##Features:

- Deprecated SystemManager.getComponents. Use SystemManager.get_components instead. ([58a07c](https://github.com/BrandonGower-Winter/ECAgent/commit/58a07ccbc1c22dc34326adda3576329460ce7a36))
- Removed SystemManager.deregisterComponent. Replaced it with SystemManager.deregister_component. ([897e3e](https://github.com/BrandonGower-Winter/ECAgent/commit/897e3ef10e572a99c2d6efc01dc772d2196065ae))
- Removed SystemManager.registerComponent. Replaced it with SystemManager.register_component. Fixed a bug where components were being stored in the component pools despite the Agents, who owned said components,having been remove from the model. ([4ed019](https://github.com/BrandonGower-Winter/ECAgent/commit/4ed019342363b0e4ebb4584b3b84c313d0453678))
- Deprecated SystemManager.executeSystems. Use SystemManager.execute_systems instead. Also fixed a bug where Systems wouldn't execute correctly if their start value wasn't 0. ([861c1f](https://github.com/BrandonGower-Winter/ECAgent/commit/861c1fbbe27bb0d82bb79c3b9c64cc980fcbbdbf))
- Deprecated SystemManager.removeSystem. Use SystemManager.remove_system instead. ([d34907](https://github.com/BrandonGower-Winter/ECAgent/commit/d34907172876a74e21958d65a20a7245eddff004))
- System.execute will now throw a NotImplementedError if it has no implementation. Removed System.cleanUp. Use System.clean_up instead. ([be1146](https://github.com/BrandonGower-Winter/ECAgent/commit/be1146634ef1c2b4ca777f09c16b46ca7106c4db))
- Deprecated Agent.getComponent. Use Agent.get_component instead. ([4ba184](https://github.com/BrandonGower-Winter/ECAgent/commit/4ba184f038306ba6b61aff6604a9e99a1ddf15f0))
- Deprecated Agent.removeComponent. Use Agent.remove_component instead. ([ce8ae3](https://github.com/BrandonGower-Winter/ECAgent/commit/ce8ae37cca73b1cda9f0a806a0dacab2969400ff))
- Deprecated Agent.addComponent. Use Agent.add_component instead. ([a17499](https://github.com/BrandonGower-Winter/ECAgent/commit/a1749904bd53a2abb77405ddc1c8cea4be673235))
- Renamed Environment.setModel to Environment.set_model ([077c2c](https://github.com/BrandonGower-Winter/ECAgent/commit/077c2caf252d62094ecbfed75b90ccec63ad1de0))
-  Added Model.execute which acts as a wrapper for Model.systems.execute_systems(). Added Model.timestep which returns the value of Model.systems.timestep. ([87d47b](https://github.com/BrandonGower-Winter/ECAgent/commit/87d47b21c949af06c73fcf4075c0834234bf387e))
- Renamed Model.systemManager to Model.systems. ([586d08](https://github.com/BrandonGower-Winter/ECAgent/commit/586d080269f8e1493524d4ec29b37b408c087ec6))
- Added Model.set_environment as an alternative to setting the environment explicitly. ([ffe1d4](https://github.com/BrandonGower-Winter/ECAgent/commit/ffe1d43c636f3da58eead976e3963b7a527ab854))
- Added DiscreteWorld.get_neumann_neighbours. Added DiscreteWorld.get_neighbours that can swap between searching moore and neumann neighbourhoods. ([6bb354](https://github.com/BrandonGower-Winter/ECAgent/commit/6bb354ae2fdb2d9f99970becc8343fc81fc44607))
