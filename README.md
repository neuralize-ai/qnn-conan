# QNN Conan

Simply a Conan recipe for the QNN SDK for use with
[Edgerunner](https://github.com/neuralize-ai/edgerunner). Clone this repo and
run;

```bash
conan create all/conanfile.py --version <version>
```

from the root directory of the project to make it
available locally before trying to use Edgerunner with QNN support. For a list of versions see [config.yml](config.yml).

> [!NOTE]
> I am no lawyer and I'm not sure to what extent the QNN binaries can be made
  publicly available. For this reason, I am not currently planning to publish this
  to Conan Center.
