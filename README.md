# Taigabot

* 13+ year old code
* Runs on Python 3
* Extremely stable, has been running for literally over a decade
* Intuitive configuration
* Fully controlled from IRC
* Fully compatable with existing skybot plugins
* Easily extendable
* Muti-threaded, efficient
  * Automatic reloading
  * Little boilerplate
  * Misbehaving plugins don't crash the bot

### Installation
Taigabot runs only on Python 3.9 or 3.10. See [install.md](install.md#instructions) for [ubuntu](install.md#ubuntu) or [alpine](install.md#alpine) instructions.

The biggest hurdle is `lxml` which needs a compiler and a bunch of libraries.

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

## Help?

Open an issue in this github repo. Feel free to improve something and send a pull request.
