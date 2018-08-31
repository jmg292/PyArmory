import pkgutil

__path__ = pkgutil.extend_path(__path__, __name__)
for importer, module_name, ispkg in pkgutil.walk_packages(path=__path__, prefix=__name__ + '.'):
    __import__(module_name)