# Taigabot

* Runs on Python 3
* Intuitive configuration
* Fully controlled from IRC
* Fully compatable with existing skybot plugins
* Easily extendable
* Muti-threaded, efficient
  * Automatic reloading
  * Little boilerplate
  * Misbehaving plugins don't crash the bot
* Extremely stable, has been running for literally over a decade
  * Project is 15+ years old [.](https://github.com/rmmh/skybot/commit/4b7cc141e5def027d2a562a1d53a2c465216fd9e)

### Installation
Taigabot runs only on Python 3.9 or 3.10. See [install.md](install.md#instructions) for [ubuntu](install.md#ubuntu) or [alpine](install.md#alpine) instructions.

Typically pip downloads whl files for lxml, bs4 and requests, so you don't need a compiler.

#### Other dependencies
Some plugins require extra python packages, more information can be found on [install.md § specific dependencies](install.md#specific-dependencies).

**Many** plugins require API keys from different services. Currently we have 34 api keys.


### Run
Once you have installed the required dependencies, you need to create a config file:

    cp config.default config
    vim config
    python3 bot.py

It is highly recommended to use a virtual environment.

## License

UguuBot (also taigabot) is **licensed** under the **GPL v3** license. The terms are as follows.

    UguuBot/DEV
    Copyright © 2013-2013 Infinity - <https://github.com/infinitylabs/UguuBot>
    Copyright © 2011-2012 Luke Rogers / ClouDev - <[cloudev.github.com](http://cloudev.github.com)>

    UguuBot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    UguuBot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with UguuBot.  If not, see <http://www.gnu.org/licenses/>.

## About this fork
wednesday (the dude who kept the bot running) went fucking missing and he stopped mantaining the bot and accepting merge requests, so i just kinda took over.

my first commit was d302369da2ddf5c74f485bd27c2c5f3ab84f2c49, thanks everyone who has contributed:
```
$ git shortlog -sn d302369da2..
   402  inexist3nce
    52  FrozenPigs
    50  wednesday
    22  Anthony DeDominic
    13  676339784
     6  ararouge
     5  adonut
     5  ineeee
     3  Jordan Koch
     3  adrift
     3  fishe
     2  inexistence
     1  Jesse Erwin
     1  blompf
```

## Help?

Open an issue in this github repo. Feel free to improve something and send a pull request.
