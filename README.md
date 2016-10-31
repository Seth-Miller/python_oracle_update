## Dependencies
Python2.7
cx_Oracle
PyYaml


cx_oracle is required. You can install it with Python install tools, install the pre-compiled RPM, or if you don't want to install it, follow these steps.
```
   curl -L -o ./#1#2 https://pypi.python.org/packages/0f/52/b441ff86b4ac71bcb324045f5898021fc1421f025d77e9932733815eaf48/{cx_Oracle}-5.2.1-12c-py27-1.x86_64{.rpm}#md5=0e8ef8de3d5475b02103760e80d6ad9c
   mkdir -p ./cx_Oracle
   cd ./cx_Oracle && rpm2cpio ../cx_Oracle.rpm | cpio -idmv && cd ../
```

Add the library path to the `PYTHONPATH` variable if cx_Oracle wasn't fully installed.
```
   export PYTHONPATH=${PYTHONPATH?}:${PWD}/cx_Oracle/usr/lib64/python2.7/site-packages
```

PyYaml is required. You can install it with Python install tools or if you don't want to install it, follow these steps.
```
   curl -L -o ./#1 http://pyyaml.org/download/pyyaml/{PyYAML-3.12.tar.gz}
   tar xzvf PyYAML-3.12.tar.gz
```

Add the library path to the `PYTHONPATH` variable if PyYaml wasn't fully installed.
```
   export PYTHONPATH=${PYTHONPATH?}:${PWD}/PyYAML-3.12/lib
```
