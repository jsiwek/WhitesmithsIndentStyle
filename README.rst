======================
WhitesmithsIndentStyle
======================

A Sublime Text 3 plugin that simulates the `Whitesmiths`_ indentation style.

.. _Whitesmiths: https://en.wikipedia.org/wiki/Indent_style#Whitesmiths_style

Known Issues
============

Trying to edit the same buffer from multiple views has problems.  E.g. edits
and indentation to a buffer within a single view seem to work fine, but after
opening a second view to the same buffer, edits to the first view continue to
work while editing the second will not auto-indent correctly.

Installation
============

Clone this repository into one of the followed paths:

* Windows: %APPDATA%\Sublime Text 3\Packages
* OS X: ~/Library/Application Support/Sublime Text 3/Packages
* Linux: ~/.config/sublime-text-3/Packages
* Portable Installation: Sublime Text 3/Data/Packages

Configuration/Usage
===================

By default the plugin monitors **tab** and **enter** key strokes and depending
on the context (e.g. position of cursor in relation to a curly brace) will
correct Sublime's **auto_indent** functionality to mimic Whitesmiths indentation
style.

If you have the **trim_automatic_white_space** set to true, the plugin also
attempts to clean up after some of its orphaned/trailing whitespace (e.g. when
an auto- indent happens, but then the cursor is moved off the line).

The plugin has been tested with **auto_indent**, **smart_indent**, and
**indent_to_bracket** set to true; other combinations may or may not work.

The following plugin settings can be modified via user preferences:

**whitesmiths_enable** 

Whether the plugin is active or not.  This can also be toggled via a command
palette entry called "Whitesmiths Indent Style Toggle".

**whitesmiths_reindent_scopes**

The scopes (e.g. language syntaxes) where the plugin attempts to intelligently
auto-indent from an empty line -- it does this by looking for enclosing curly
braces and using that scope's indentation level to indent. This setting does not
alter the behavior of the plugin in the cases where the cursor is positioned
after a closing curly brace or before an opening curly brace.
