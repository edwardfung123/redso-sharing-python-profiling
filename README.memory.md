# Introduction

One of the PITAs about appengine is that the memory of F1 instance is really
low. It is 128MB. Your application can slightly use more than 128MB for a short
period of time. This is the so-called *soft* limit. If your application uses
more than that, the AppEngine system (Google) will kill your application
immediately. I guess the reason behind is to protect the AppEngine system.

As the application gets bigger and more complicated, you will eventually reach
the soft limit and have to deal with it. One easy way is to simply upgrade the
instance to F2. This is AKA *vertical scaling*. But again, eventually you will
reach the point that there is no more upgrade. Well. From the practical point of
view, it may take long enough to reach this point... From the theoretical POV,
I believe that we can do better if we can understand OUR APPLICATION more?

Let's do some *Memory Profiling*. Something I would like to know in order to
help me to fix this *Memory Limit Exceed (MLE)*.

1. where the application got killed by GAE
2. which objects used most of the memory
3. when the memory is allocated (the memory footprint, the
history)

For point 1, we can check the log. Done. Yeah~

For point 2 and 3, Google does not provide any tool for that. It has been
requested by user for years. _(you are not alone!!!)_ But as of 20180716, no
tool is given/suggested by Google. Althougt there are a few memory profile
tools for Python, it is not available in GAE as they used some low level
C-modules which is not *whitelisted*. It means you cannot use them in
production. But it does not mean we are done here.  That's why I am here doing
my sharing. We can do it in the local development server. Although the
`dev_appserver.py` is different from the real production env, I think it is
good enough to gain some insight.

# Memory profile tools

1. [memory_profiler](https://github.com/pythonprofilers/memory_profiler)
2. [guppy](http://guppy-pe.sourceforge.net/)

I tried to use `memory_profiler`, it can do (3) but not (2) *directly*. It can
give you a "line-by-line" profile. However, it use `psutil` module and GAE
standard env does not allow it even with my hack (I will show that in the
coming section). It works pretty well if you can isolate the code to a function
or at least not run in the `dev_appserver.py` environment.

I also tried to use `guppy`. It is pretty old but it somehow works in the
`dev_appserver.py` env with some hacks.

## Hacking the dev_appserver.py

It is required to hack the source code to smuggle guppy (ya. guppy is a kind of
fish actually). After `grep`-ing the source code in
`GCP_SDK_HOME/platform/google_appengine`, I learnt where and how the
*C-modules* whitelisting works in the `dev_appserver.py` env. The whitelisting is done in the file
`GCP_SDK_HOME/platform/google_appengine/google/appengine/tools/devappserver2/python/runtime/sandbox.py`.
In this file, there is an array of whitelisted C-modules called
`_WHITE_LIST_C_MODULES`. Add you modules to the list. The process of finding
the modules to be added is kind of painful as I used a trial-and-error
approach. Inside the class `CModuleImportHook`, I changed it to:

```
1095         self._modules_to_warn.remove(basename)
1096       return None
1097     if self._module_type(fullname, path) in [imp.C_EXTENSION, imp.C_BUILTIN]:
1098       if logging:
1099         logging.debug(fullname)
1100       return self
1101     return None
```

So run the `dev_appserver.py` with the arg `--log_level=debug`. Whenever a
forbidden c-module is imported, it will show the error `ImportError: No module
named guppy.heapy.heapyc` and print the module name before the error message.
Add the module name into the array. Repeat until no error.

# TODO:

add README and steps to use the profilers. currently the use case and
instructions in my brain and undocumented code only.
