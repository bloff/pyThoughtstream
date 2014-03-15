pyThoughtstream
===================

pyThoughtstream is a python program to interface with
[Mindplace Thoughtstream USB](http://www.mindplace.com/Mindplace-Thoughtstream-USB-Personal-Biofeedback/dp/B005NDGPLC).

It currently has only one feedback mode. Sounds are played on the
following events:
* Counter increases
* Counter decreases by less than 4 units
* Counter decreases more than 4 units

It checks for the last event every second. It checks for increease and
small decreases every 1 second for values less than 100, every 2
seconds for values between 200 and 300, every 3 seconds for values
between 300 and 400, etc.

The sounds can be readily customized to your preference by changing
the files in the snd directory.


It requires that you install [Python](http://www.python.org/), with
the following packages:
* wx
* serial
* pygame

All of these can be installed with the
[Pip package manager](http://www.pip-installer.org/).

Once your Python system has these packages installed, it should be
enough to run:

python pyThoughtstream.py


The program has been tested on linux, but not Windows or Mac OS. You
are welcome to test it and let me know if it works, and even fix
whatever it needs in order to get it to work and submit the changes to
the repository.

If you want to improve the program, the only condition I have is that
the current feedback mode remains easily accessible.



