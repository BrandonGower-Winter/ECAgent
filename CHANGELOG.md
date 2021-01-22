#Version: 0.1.0

##Features:

- Added JsonDecoder class. This class turns json data into an executable model. See the Wiki and Tutorials for more information. ([28b8e2](https://github.com/BrandonGower-Winter/ABMECS/commit/28b8e2874f5f8fbd44f1874a405aff5507f9c06c))
- Added Decoder base class. This the class that all decoders inherit from and can used to create your own custom decoders. ([7b5607](https://github.com/BrandonGower-Winter/ABMECS/commit/7b5607f18fc9f9e57113be9ad2d4468172e7d7fd))
-  Added IDecodable interface. This class needs to be inherited from if you want a Decoder to pick up your custom classes. ([d4a1cb](https://github.com/BrandonGower-Winter/ABMECS/commit/d4a1cb4e5718c336556b7dd09b067af5ea6b93a9))
- Added 3 commands to the makefile to allow for automated versioning of patches, minor updates and major updates respectively. They are 'prepare_patch', 'prepare_minor_update' and 'prepare_major_update' respectively. ([a4146a](https://github.com/BrandonGower-Winter/ABMECS/commit/a4146aef23e0a4161da3a37df93082192dc2c394))
