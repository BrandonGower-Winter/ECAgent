#Version: 0.1.1

##Features:

- Changed Gridworld, Lineworld and Cubeworld 'cells' property to pandas dataframes. This has increased the speed and memory efficiency of the objects by an order of magnitude. ([09a0ac](https://github.com/BrandonGower-Winter/ABMECS/commit/09a0ac124bb413590e24ec0314f6e525cb764f60))
##Performance:

- Changed LineWorld, GridWorld and CubeWorld's 'cells' properties to numpy arrays to improve performance. ([6fb4c8](https://github.com/BrandonGower-Winter/ABMECS/commit/6fb4c8dff19e8843234dbadd78e9e837a3d7ae94))
- Slotted the Lineworld, Gridworld and Cubeworld classes in ECAgent.Environments ([97bd0c](https://github.com/BrandonGower-Winter/ABMECS/commit/97bd0c1ad5211ceef1d1076a89e48aee1325a2f1))
- Slotted all of the ECAgent.Core base classes to allow for users to slott inherited classes for performance increases. ([aa5a08](https://github.com/BrandonGower-Winter/ABMECS/commit/aa5a08fbc884a930a973a901cb1642fd59ad1376))
- Slotted Position Component to speed up the inititalization process of the discrete environments for larger dimensions. ([219999](https://github.com/BrandonGower-Winter/ABMECS/commit/2199994695b4ece1d912147b65152a6b3c7e5e28))
