# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Michael Koefinger
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Plots for the filter TOP cell. There is no filter_top testbench yet, so this
#              delegates to plot_filter.py; it exists because the Makefile default is
#              SCRIPT ?= plot_$(CELL) and CELL defaults to filter_top.
# ============================================

from plot_filter import main

if __name__ == '__main__':
    main()
