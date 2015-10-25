import sublime, sublime_plugin

class State:
    reindents = {}

def get_cursor(view):
    return view.sel()[0].begin()

def scope_matches(view, position, selectors):
    for selector in selectors:
        if view.match_selector(position, selector):
            return True

    return False

def get_start_of_line_text(view, until):
    line_region = view.line(until)
    line_region.b = until
    return view.substr(line_region)

class WhitesmithsEnterBlockCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        cursor_position = get_cursor(self.view)
        next_char = self.view.substr(cursor_position)

        if next_char == '}':
            self.view.run_command('insert', {'characters': '\n\n'})
            self.view.run_command('move', {'by': 'lines', 'forward': False})
            self.view.run_command('move_to', {'to': 'hardeol', 'extend': False})
            self.view.run_command('reindent', {'single_line': True})
            self.view.run_command('unindent')
        else:
            self.view.run_command('insert', {'characters': '\n'})
            self.view.run_command('reindent', {'single_line': True})
            self.view.run_command('unindent')

def focus_view_on_cursor(view):
    # TODO: using move_to command with long blocks can cause the view to
    # scroll, so center on the cursor to workaround that. (Using move_to
    # was just easier than writing the code to find balanced braces).
    view.run_command('center_on_cursor')

class WhitesmithsExitBlockCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        close_brace_position = get_cursor(self.view)
        self.view.run_command('move_to', {'to': 'brackets'})
        open_brace_position = get_cursor(self.view)

        if close_brace_position == open_brace_position:
            return

        indent_text = get_start_of_line_text(self.view, open_brace_position)

        if indent_text.isspace():
            prev_line_position = self.view.line(open_brace_position).a - 1
            prev_indent_level = self.view.indentation_level(prev_line_position)
        else:
            prev_indent_level = self.view.indentation_level(open_brace_position)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(close_brace_position))

        newline = '\n'

        for i in range(prev_indent_level):
            newline += '\t'

        self.view.insert(edit, close_brace_position, newline)
        State.reindents[self.view.buffer_id()] = get_cursor(self.view)
        focus_view_on_cursor(self.view)

class WhitesmithsEnterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        cursor_position = get_cursor(self.view)
        last_reindent = State.reindents.pop(self.view.buffer_id(), None)
        self.view.run_command('insert', {'characters': '\n'})

        if cursor_position == last_reindent:
            self.view.run_command('whitesmiths_erase_orphan_reindent',
                                  {'position': last_reindent,
                                   'line_before_cursor': True})

class WhitesmithsEraseOrphanReindentCommand(sublime_plugin.TextCommand):
    def run(self, edit, position, line_before_cursor = False):
        if self.view.settings().get('trim_automatic_white_space'):

            if line_before_cursor:
                # Sublime's builtin auto-indent may have removed it's own
                # automatic whitespace and invalidated our own reindent
                # tracking position.
                row = self.view.rowcol(get_cursor(self.view))[0] - 1
                indent_region = self.view.line(self.view.text_point(row, 0))
            else:
                indent_region = self.view.line(position)

            indent_text = self.view.substr(indent_region)

            if indent_text.isspace():
                self.view.erase(edit, indent_region)

class WhitesmithsReindentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        cursor_position = get_cursor(self.view)
        scopes = self.view.settings().get('whitesmiths_reindent_scopes')

        if not scope_matches(self.view, cursor_position, scopes):
            self.view.run_command('reindent', {'single_line': True})
            return

        self.view.run_command('move_to', {'to': 'brackets'})
        brace_position = get_cursor(self.view)

        if brace_position == cursor_position:
            self.view.run_command('reindent', {'single_line': True})
            return

        indent_text = get_start_of_line_text(self.view, brace_position)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(cursor_position))

        if not indent_text:
            self.view.insert(edit, cursor_position, '\t')
            State.reindents[self.view.buffer_id()] = get_cursor(self.view)
            focus_view_on_cursor(self.view)
            return

        if not indent_text.isspace():
            self.view.run_command('reindent', {'single_line': True})
            focus_view_on_cursor(self.view)
            return

        self.view.insert(edit, cursor_position, indent_text)
        State.reindents[self.view.buffer_id()] = get_cursor(self.view)
        focus_view_on_cursor(self.view)

class WhitesmithsListener(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        last_reindent = State.reindents.get(view.buffer_id(), None)

        if last_reindent is not None:
            cursor_position = get_cursor(view)

            if last_reindent != cursor_position:
                State.reindents.pop(view.buffer_id(), None)
                view.run_command('whitesmiths_erase_orphan_reindent',
                                 {'position': last_reindent})
