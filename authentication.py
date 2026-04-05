# Copyright (C) 2026  CODE3 Cooperative de solidarite
#
# This program is free software: you can redistribute it and/or modify
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask import session, abort
from functools import wraps

from db import get_db


def authentication_required(f):
    """
    Décorateur pour restreindre l'accès à une route aux utilisateurs connectés.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if is_authenticated(session):
            return f(*args, **kwargs)
        else:
            abort(401)

    return decorated


def is_authenticated(session):
    id_session = session.get("id")
    if not id_session:
        return False

    user = get_db().get_session_username(id_session)
    return user is not None
