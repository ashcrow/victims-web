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
Main web ui.
"""

import datetime
import os.path
import re

from flask import (
    Blueprint, current_app, render_template, helpers,
    url_for, request, redirect, flash)
from werkzeug import secure_filename

from flask.ext import login

from victims_web.errors import ValidationError
from victims_web.models import Hash
from victims_web.cache import cache


ui = Blueprint(
    'ui', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/')  # Last argument needed since we register on /


def _is_hash(data):
    """
    Verifies the hash is a sha1 hash.
    """
    if re.match('^([a-zA-Z0-9]{128})$', data):
        return True
    return False


@ui.route('/', methods=['GET'])
@cache.cached()
def index():
    released = Hash.objects(status='RELEASED')
    submitted = Hash.objects(status='SUBMITTED')

    kwargs = {
        'hashes': len(released),
        'pending': len(submitted),
        'jars': len(released.filter(format='Jar')),
        'pending_jars': len(submitted.filter(format='Jar')),
        'eggs': len(released.filter(format='Egg')),
        'pending_eggs': len(submitted.filter(format='Egg')),
    }
    return render_template('index.html', **kwargs)


@ui.route('/hashes/', methods=['GET'])
@ui.route('/hashes/<format>/', methods=['GET'])
@cache.memoize()
def hashes(format=None):
    hashes = Hash.objects(status='RELEASED')

    if format:
        if format not in Hash.objects.distinct('format'):
            flash('Format not found', 'error')
        else:
            hashes = hashes.filter(format=format)

    return render_template('hashes.html', hashes=hashes)


@ui.route('/hash/<hash>/', methods=['GET'])
def hash(hash):
    if _is_hash(hash):
        a_hash = Hash.objects.get_or_404(hashes__sha512__combined=hash)
        return render_template('onehash.html', hash=a_hash)
    flash('Not a valid hash', 'error')
    return redirect(url_for('ui.hashes'))


# TODO: NEEDS TESTING WITH MONGOENGINE
@ui.route('/submit_archive/', methods=['GET', 'POST'])
@login.login_required
def submit_archive():
    # If a file is submitted
    if request.method == "POST":
        if 'archive' in request.files.keys():
            archive = request.files['archive']
            try:
                suffix = archive.filename[archive.filename.rindex('.') + 1:]
                if suffix in current_app.config['ALLOWED_EXTENSIONS']:
                    filename = secure_filename(archive.filename)
                    archive.save(os.path.join(
                        current_app.config['UPLOAD_FOLDER'], filename))
                    cves = {}
                    now = datetime.datetime.utcnow()
                    for cve in request.form['cves'].split(','):
                        cves[cve] = now
                    new_hash = Hash()
                    new_hash.name = filename
#                    new_hash.date = datetime.datetime.utcnow()
                    new_hash.version = '1.0.0'
                    new_hash.format = suffix.lower().capitalize()
                    new_hash.cves = cves
                    new_hash.status = 'SUBMITTED'
                    new_hash.submitter = login.current_user.username
                    new_hash.hashes = {}
                    new_hash.validate()
                    new_hash.save()
                    flash('Archive Submitted for processing', 'info')
                else:
                    raise ValueError('No suffix')
            except ValueError:
                flash('Not a valid archive type.', 'error')
            except ValidationError, ve:
                flash(ve.message, 'error')
        else:
            flash('Unable to process the archive.', 'error')
    return render_template('submit_archive.html')


@ui.route('/<page>.html', methods=['GET'])
def static_page(page):
    # These are the only 'static' pages
    if page in ['about', 'client', 'bugs']:
        return render_template('%s.html' % page)
    return helpers.NotFound()
