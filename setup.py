#!/usr/bin/env python
#
# This file is part of victims-web.
#
# Copyright (C) 2013 The Victims Project
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Source build and installation script.
"""

from setuptools import setup


setup(
    name='victims_web',
    version='1.9.9',
    description='The victi.ms language package to CVE service.',
    author='Steve Milner',
    url='http://www.victi.ms',

    install_requires=[
        'Flask>=0.8',
        'Flask-Login>=0.1.1',
        'Flask-Bcrypt',
        'Flask-SeaSurf',
        'Flask-Cache',
        'Flask-Admin',
        'pymongo>=2.3',
        'Flask-Views',
        'Flask-MongoEngine',
        'blinker>=1.2',
        'PyYAML',
        'recaptcha-client'],
)
