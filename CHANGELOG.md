#Version: 0.0.8

##Features:

-  changelogger.py will now automatically stage, commit and tag new versions. ([15fd74](https://github.com/BrandonGower-Winter/ABMECS/commit/15fd74bd64e7ef64a3829f7fc4ab37f28093f069))
-  Changelogger.py now returns new version number as well as the markdown generated changelog as output. Will only update the package.json file and CHANGELOG.md file if it is run as the main application ([7c03c6](https://github.com/BrandonGower-Winter/ABMECS/commit/7c03c6a8182fcff3d02d618adea89d2ef949a892))
##Fixes:

- Fixed an issue where the changelogger was not adding the pakcage.json file ([703d6f](https://github.com/BrandonGower-Winter/ABMECS/commit/703d6f664685ad35070d84575b3bfd04a5b6b03c))
-  Modified changelogger to correctly truncate commit sha and add brackets around said sha. ([b118ce](https://github.com/BrandonGower-Winter/ABMECS/commit/b118ceb508aa074c8d9efd1314f0862d27ff4b70))
