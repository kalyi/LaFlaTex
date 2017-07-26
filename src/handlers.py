#!/usr/bin/env python3
# -*- coding: utf8; -*-
#
# Copyright (C) 2017 : Kathrin Hanauer
#
# This file is part of LaFlaTex.
#
# LaFlaTex is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""Handlers for LaTeX commands."""

import re


class LatexCmdHandler:
    def __init__(self):
        self._name = "CommandHandler"

    def __str__(self):
        return self._name


class LatexRegexCmdHandler(LatexCmdHandler):
    def __init__(self):
        super().__init__()
        self._pattern_optarg = "((?:\[[^\]]*\])?)"
        self._pattern_arg = "\{([^\{]*)\}"
        self._pattern_backslash = "\\\\"

    def _setPattern(self, pattern):
        self._pattern = pattern
        self._regex = re.compile(pattern)


class DocumentClassHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'DocumentClassHandler'
        pattern = (self._pattern_backslash + "documentclass" +
                   self._pattern_optarg + self._pattern_arg)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return line
        cls = m.group(2)
        print("Found documentclass with name {}.".format(cls))
        cls_file = cls + '.cls'
        cls_path = env.cwd / cls_file
        if cls_path.exists():
            env.files_to_copy.append((cls_path.resolve(), cls_file))
        return line


class GraphicsPathHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'GraphicsPathHandler'
        pattern = (self._pattern_backslash + "graphicspath" +
                   self._pattern_arg)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return line
        gp = m.group(1)
        print("Found graphicspath with value {}.".format(gp))
        gp_path = env.cwd / gp
        env.graphics_path = gp_path.resolve()
        # print("Setting graphics path to {}.".format(gp_path))
        return ''


class InputHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'InputHandler'
        pattern = (self._pattern_backslash + "(input|include)" +
                   self._pattern_arg)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return line
        inp = m.group(2)
        print("Found input/include with value {}.".format(inp))
        input_file = inp if inp.endswith(".tex") else inp + ".tex"
        input_path = env.cwd / input_file
        inp_masked = inp.replace('/', '_')
        inp_masked_file = (inp_masked if inp_masked.endswith(".tex") else
                           inp_masked + ".tex")
        env.files_to_process.append((input_path.resolve(), inp_masked_file))
        sub = '\\\\\\1{' + inp_masked + '}'
        n_input = self._regex.sub(sub, line)
        return n_input


class BibliographyHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'BibliographyHandler'
        pattern = (self._pattern_backslash + "bibliography" +
                   self._pattern_arg)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return line
        print("Found bibliography.")
        bib_file = env.main.stem + '.bbl'
        bib_path = env.cwd / bib_file
        env.files_to_copy.append((bib_path.resolve(), bib_file))
        sub = '\\\\bibliography{' + env.main.stem + '}'
        n_bib = self._regex.sub(sub, line)
        return n_bib


class IncludeGraphicsHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'IncludeGraphicsHandler'
        pattern = (self._pattern_backslash + "includegraphics" +
                   self._pattern_optarg + self._pattern_arg)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return line
        ig = m.group(2)
        print("Found includegraphics with value {}.".format(ig))
        graphics_file = ig if ig.endswith(".pdf") else ig + ".pdf"
        graphics_path = env.graphics_path / graphics_file
        ig_masked = ig.replace('/', '_')
        graphics_file_masked = (ig_masked if ig_masked.endswith(".pdf")
                                else ig_masked + ".pdf")
        env.files_to_copy.append((graphics_path.resolve(),
                                  graphics_file_masked))
        sub = '\\\\includegraphics\\1{' + ig_masked + '}'
        n_ig = self._regex.sub(sub, line)
        return n_ig


class InlineCommentHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'InlineCommentHandler'
        pattern = '^(.+)%(.*)$'
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.match(line)
        if m is None:
            return line
        sub = '\\1%'
        n_cmd = self._regex.sub(sub, line)
        return n_cmd


class LineCommentHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'LineCommentHandler'
        pattern = '^%(.*)'
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return line
        return ''